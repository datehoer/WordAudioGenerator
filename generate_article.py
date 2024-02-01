import time
import logging
import requests
import json
import re
import pandas as pd
from translate import google_translate
from config import *
import sqlite3
# import epitran


def replace_multiple_spaces_with_single_space(text):
    return re.sub(r'\s+', ' ', text)


def translate_words(words):
    columns = ['No.', 'Word', 'Meaning', 'Pronunciation']
    word = []
    batch_data = []
    for i, item in enumerate(words.split(" "), start=1):
        word_meaning = get_word_meaning(item)
        word_phonetic = get_word_phonetic(item)
        if not word_meaning:
            word_meaning = google_translate(item, proxy=proxy)
            word_data = get_word(item)
            if word_data and word_data['meaning'] and word_data['phonetic']:
                word_meaning = word_data['meaning']
                word_phonetic = word_data['phonetic']
                batch_data.append((item, word_phonetic, word_meaning))
                # cursor.execute("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", (item, word_phonetic, word_meaning))
        word.append([i, item, word_meaning, word_phonetic])
    if batch_data:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", batch_data)
        conn.commit()
        cursor.close()
    df = pd.DataFrame(word, columns=columns)
    df.to_excel('output.xlsx', index=False)


def request(url, data, headers):
    err = 0
    while err < 3:
        try:
            res = requests.post(url, json=data, headers=headers)
            return res
        except Exception as e:
            logging.error(f"Request Error: {e}")
            err += 1
            time.sleep(3)
    return None


def get_word(word):
    messages = [
        {"role": "user", "content": "请告诉我{}的中文意思以及音标,返回的数据为json格式数据，包含word,meaning,phonetic。".format(word)}
    ]
    chat_data = openai_text_data.copy()
    chat_data['messages'] = messages
    chat_data['model'] = "gpt-3.5-turbo-1106"
    url = openai_text_url.replace("api.openai.com", token_url)
    res = request(url, headers=openai_header, data=chat_data)
    if res is None:
        return None
    res_json = res.json()
    content_json = res_json['choices'][0]['message']['content']
    content_json = json.loads(content_json.replace("```json", "").replace("```", "").replace("\n", ""))
    data = {
        "word": content_json['word'],
        "meaning": content_json['meaning'],
        "phonetic": "[{}]".format(content_json['phonetic']) if content_json['phonetic'] else ""
    }
    return data


def get_word_phonetic(word):
    cursor = conn.cursor()
    cursor.execute("SELECT pronunciation FROM words WHERE word=?", (word,))
    pronunciation = cursor.fetchone()
    if pronunciation:
        pronunciation = pronunciation[0]
    else:
        pronunciation = None
    return pronunciation
    # phonetic = epi.transliterate(word)
    # return phonetic


def get_word_meaning(word):
    cursor = conn.cursor()
    cursor.execute("SELECT part_of_speech FROM words WHERE word=?", (word,))
    part_of_speech = cursor.fetchone()
    if part_of_speech:
        part_of_speech = part_of_speech[0]
    else:
        part_of_speech = None
    return part_of_speech


def generate_and_save_audio(content, title):
    url = openai_tts_url.replace("api.openai.com", token_url)
    data = openai_tts_data
    data['input'] = content
    try:
        res = request(url, headers=openai_header, data=data)
        if res:
            with open("{}.mp3".format(title.split(': ')[-1]), "wb") as f:
                f.write(res.content)
    except Exception as e:
        logging.error(f"Save Audio Error: {e}")


def save_text_file(content, title):
    with open("{}.txt".format(title.split(': ')[-1]), "w", encoding='utf-8') as file:
        file.write(content)


def main():
    try:
        with open("words.txt", "r") as f:
            words = f.read().split("\n")
        words = replace_multiple_spaces_with_single_space(" ".join(words))
        translate_words(words)

        messages = [
            {"role": "user", "content": "请通过下面的单词写一篇英文文章，语句通顺意思明确,返回的数据为json格式数据，包含title,content。{}".format(words)}
        ]

        chat_data = openai_text_data.copy()
        chat_data['messages'] = messages
        url = openai_text_url.replace("api.openai.com", token_url)
        res = request(url, headers=openai_header, data=chat_data)
        if res is None:
            return
        res_json = res.json()
        content_json = res_json['choices'][0]['message']['content']
        content_json = json.loads(content_json.replace("```json", "").replace("```", "").replace("\n", ""))
        content = content_json['content']
        title = content_json['title']
        generate_and_save_audio(content, title)
        save_text_file(content, title)
    except Exception as e:
        logging.error(f"Main Error: {e}")


if __name__ == "__main__":
    conn = sqlite3.connect('words.db')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # epi = epitran.Epitran('eng-Latn')
    main()
    conn.close()
