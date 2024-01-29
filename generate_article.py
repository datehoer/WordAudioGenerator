import requests
import json
import re
import pandas as pd
from translate import google_translate
from config import *


def replace_multiple_spaces_with_single_space(text):
    return re.sub(r'\s+', ' ', text)


def translate_words(words):
    columns = ['No.', 'Word', 'Meaning']
    word = [[i, item, google_translate(item, proxy=proxy)] for i, item in enumerate(words.split(" "), start=1)]
    df = pd.DataFrame(word, columns=columns)
    df.to_excel('output.xlsx', index=False)


def generate_and_save_audio(content, title):
    url = openai_tts_url.replace("api.openai.com", token_url)
    data = openai_tts_data
    data['input'] = content
    try:
        res = requests.post(url, headers=openai_header, json=data)
        with open("{}.mp3".format(title.split(': ')[-1]), "wb") as f:
            f.write(res.content)
    except Exception as e:
        print("Error generating audio: ", e)


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

        chat_data = openai_text_data
        chat_data['messages'] = messages
        url = openai_text_url.replace("api.openai.com", token_url)
        res = requests.post(url, headers=openai_header, json=chat_data)
        res_json = res.json()

        content_json = res_json['choices'][0]['message']['content']
        content_json = json.loads(content_json.replace("```json", "").replace("```", "").replace("\n", ""))
        content = content_json['content']
        title = content_json['title']

        generate_and_save_audio(content, title)
        save_text_file(content, title)
    except Exception as e:
        print("Error: ", e)


if __name__ == "__main__":
    main()
