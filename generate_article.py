import time
import logging
import requests
import json
import re
import pandas as pd
from translate import google_translate, YoudaoTranslater
from config import *
import sqlite3
import pyttsx3
# import epitran


def replace_multiple_spaces_with_single_space(text):
    return re.sub(r'\s+', ' ', text)


def execute_sql(data):
    cursor = conn.cursor()
    cursor.executemany("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", data)
    conn.commit()
    cursor.close()
    logging.info("Insert or Replace {} Data Success!".format(len(data)))


def translate_words(words, title, word_count):
    columns = ['No.', 'Word', 'Meaning', 'Pronunciation', 'Count']
    word = []
    batch_data = []
    for i, item in enumerate(words, start=1):
        try:
            word_meaning = get_word_meaning(item)
            word_phonetic = get_word_phonetic(item)
            if not word_meaning:
                word_meaning = google_translate(item, toLan="zh-CN", proxy=proxy)
                word_data = get_word(item)
                if word_data and word_data['meaning'] and word_data['phonetic']:
                    word_meaning = word_data['meaning']
                    word_phonetic = word_data['phonetic']
                    batch_data.append((item, word_phonetic, word_meaning))
                    # cursor.execute("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", (item, word_phonetic, word_meaning))
            word.append([i, item, word_meaning, word_phonetic, word_count[item]])
        except Exception as e:
            logging.error(f"Translate Error: {e}")
    if len(batch_data) > 0:
        execute_sql(batch_data)
    try:
        df = pd.DataFrame(word, columns=columns)
        df.to_excel('data/' + title.split(': ')[-1].replace(" ", "_") + '_output.xlsx', index=False)
    except Exception as e:
        logging.error(f"Write Excel Error: {e}")


def translate_words_youdao(words, title, word_count):
    translate_youdao = YoudaoTranslater(proxy=proxy)
    columns = ['No.', 'Word', 'Meaning', 'Pronunciation', 'Count']
    word = []
    batch_data = []
    for i, item in enumerate(words, start=1):
        try:
            word_meaning = get_word_meaning(item)
            word_phonetic = get_word_phonetic(item)
            if not word_meaning:
                word_meaning = translate_youdao.translate(item, toLan="zh-CHS")
                if word_meaning and word_meaning.get("code") == 0:
                    dict_result = word_meaning.get("dictResult")
                    ec = dict_result.get("ec")
                    ec_word = ec.get("word")
                    word_phonetic = "[" + ec_word.get("usphone") + "]"
                    word_meaning = word_meaning.get("translateResult")[0].get("tgt")
                    batch_data.append((item, word_phonetic, word_meaning))
            word.append([i, item, word_meaning, word_phonetic, word_count[item]])
        except Exception as e:
            logging.error(f"Translate Error: {e}")
    if len(batch_data) > 0:
        execute_sql(batch_data)
    try:
        df = pd.DataFrame(word, columns=columns)
        df.to_excel('data/' + title.split(': ')[-1].replace(" ", "_") + '_output.xlsx', index=False)
    except Exception as e:
        logging.error(f"Write Excel Error: {e}")


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
        {"role": "user", "content": "请告诉我{}的中文意思以及音标,返回的数据为json格式数据，包含word,meaning,phonetic".format(word)}
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


def generate_and_save_audio_microsoft(content, title):
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    engine.setProperty('volume', 1.0)
    engine.save_to_file(content, "data/{}.mp3".format(title.split(': ')[-1]))
    engine.runAndWait()


def generate_and_save_audio(content, title):
    url = openai_tts_url.replace("api.openai.com", token_url)
    data = openai_tts_data
    data['input'] = content
    try:
        res = request(url, headers=openai_header, data=data)
        if res:
            with open("data/{}.mp3".format(title.split(': ')[-1]), "wb") as f:
                f.write(res.content)
    except Exception as e:
        logging.error(f"Save Audio Error: {e}")


def save_text_file(content, title):
    with open("data/{}.txt".format(title.split(': ')[-1]), "w", encoding='utf-8') as file:
        file.write(content)


def count_words_in_article(word_list, article):
    word_count_plus = {}
    word_count_zero = {}
    for word in word_list:
        count = len(re.findall(word, article, re.IGNORECASE))
        if count > 0:
            word_count_plus[word] = count
        else:
            word_count_zero[word] = count
    return word_count_plus, word_count_zero


def generate_article(words):
    messages = [
        {"role": "user",
         "content": "请通过下面的单词写一篇英文文章必须包含所有的单词，语句通顺意思明确,返回的数据为json格式数据，包含title,content。{}".format(words)
         }
    ]
    chat_data = openai_text_data.copy()
    chat_data['messages'] = messages
    url = openai_text_url.replace("api.openai.com", token_url)
    try:
        res = request(url, headers=openai_header, data=chat_data)
        if res is None:
            return None, None
        res_json = res.json()
        content_json = res_json['choices'][0]['message']['content']
        content_json = json.loads(content_json.replace("```json", "").replace("```", "").replace("\n", ""))
        content = content_json['content']
        title = content_json['title']
        generate_and_save_audio(content, title)
        save_text_file(content, title)
        return content, title
    except Exception as e:
        logging.error(f"Generate Article Error: {e}")
        return None, None


def main():
    try:
        with open("words.txt", "r") as f:
            words = f.read().split("\n")
        words = replace_multiple_spaces_with_single_space(" ".join(words))
        content, title = generate_article(words)
        if content is None:
            return
        words = words.split(" ")
        word_count_plus, word_count_zero = count_words_in_article(words, content)
        translate_words(list(word_count_plus), title, word_count_plus)
        if len(word_count_zero) > 0:
            words = list(word_count_zero)
            content, title = generate_article(" ".join(words))
            if content is None:
                return
            word_count_plus, word_count_zero = count_words_in_article(words, content)
            word_count = {**word_count_plus, **word_count_zero}
            translate_words(words, title, word_count)
            return
    except Exception as e:
        logging.error(f"Main Error: {e}")


if __name__ == "__main__":
    conn = sqlite3.connect('words.db')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # epi = epitran.Epitran('eng-Latn')
    main()
    conn.close()
