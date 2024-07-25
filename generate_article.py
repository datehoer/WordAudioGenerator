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
import os
import traceback
from json_repair import repair_json
# import epitran


def replace_multiple_spaces_with_single_space(text):
    return re.sub(r'\s+', ' ', text)


def execute_sql(data):
    cursor = conn.cursor()
    cursor.executemany("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", data)
    conn.commit()
    cursor.close()
    logging.info("Insert or Replace {} Data Success!".format(len(data)))


def fetch(url, headers, data):
    err = 3
    while err > 0:
        res = request(url, headers=headers, data=data)
        if res is not None and res.status_code == 200:
            res_json = res.json()
            try:
                content_json = res_json['choices'][0]['message']['content']
                content_json = json.loads(repair_json(content_json.replace("```json", "").replace("```", "").replace("\n", "")))
                return content_json
            except Exception as e:
                logging.error(f"Fetch Error: {e}, traceback: {traceback.format_exc()}")
        err -= 1
    return None

        
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
            logging.error(f"Translate Error: {e}, and traceback: {traceback.format_exc()}")
    if len(batch_data) > 0:
        execute_sql(batch_data)
    try:
        df = pd.DataFrame(word, columns=columns)
        df.to_excel('data/' + title.split(': ')[-1].replace(" ", "_") + '_output.xlsx', index=False)
    except Exception as e:
        logging.error(f"Write Excel Error: {e}, traceback: {traceback.format_exc()}")


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
            logging.error(f"Translate Error: {e}, traceback: {traceback.format_exc()}")
    if len(batch_data) > 0:
        execute_sql(batch_data)
    try:
        df = pd.DataFrame(word, columns=columns)
        df.to_excel('data/' + title.split(': ')[-1].replace(" ", "_") + '_output.xlsx', index=False)
    except Exception as e:
        logging.error(f"Write Excel Error: {e}, traceback: {traceback.format_exc()}")


def request(url, data, headers):
    err = 0
    while err < 3:
        try:
            res = requests.post(url, json=data, headers=headers)
            return res
        except Exception as e:
            logging.error(f"Request Error: {e}, traceback: {traceback.format_exc()}")
            err += 1
            time.sleep(3)
    return None


def get_word(word):
    messages = [
        {"role": "user", "content": "Please tell me the Chinese meaning and phonetic transcription of the word "+word+". Your output should be in JSON format. For example: {'word': '', 'meaning': '', 'phonetic': ''}"}
    ]
    chat_data = openai_text_data.copy()
    chat_data['messages'] = messages
    chat_data['model'] = "gpt-4o-mini"
    url = openai_text_url.replace("api.openai.com", token_url)
    content_json = fetch(url, openai_header, chat_data)
    if content_json:
        data = {
            "word": content_json['word'],
            "meaning": content_json['meaning'],
            "phonetic": "[{}]".format(content_json['phonetic']) if content_json['phonetic'] else ""
        }
        return data
    else:
        return None


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
        logging.error(f"Save Audio Error: {e}, traceback: {traceback.format_exc()}")


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
        {
            "role": "user",
            "content": "Please write an English article using the following words, ensuring that the sentences are coherent and the meaning is clear. Your output should be in JSON format. For example: {'title': 'A Story', 'content': 'hello'}." + words
        }
    ]
    chat_data = openai_text_data.copy()
    chat_data['messages'] = messages
    url = openai_text_url.replace("api.openai.com", token_url)
    content_json = fetch(url, openai_header, chat_data)
    if content_json:
        content = content_json['content']
        title = content_json['title']
        generate_and_save_audio(content, title)
        save_text_file(content, title)
        return content, title
    return None, None


def main():
    try:
        with open("words.txt", "r") as f:
            words = f.read().split("\n")
        words = replace_multiple_spaces_with_single_space(" ".join(words))
        while True:
            content, title = generate_article(words)
            if content is None:
                logging.error("Generate Article Error")
                break
            words = words.split(" ")
            word_count_plus, word_count_zero = count_words_in_article(words, content)
            translate_words(list(word_count_plus), title, word_count_plus)
            if len(word_count_zero) > 0:
                words = " ".join(list(word_count_zero))
            else:
                logging.info("All words translated")
                break
    except Exception as e:
        logging.error(f"Main Error: {e}, traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")
    conn = sqlite3.connect('words.db')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # epi = epitran.Epitran('eng-Latn')
    main()
    conn.close()
