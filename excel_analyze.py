import pandas
import sqlite3
import glob
conn = sqlite3.connect('words.db')
cursor = conn.cursor()
file_path = 'EnglishDataBase\含音标（新版）'


def find_xlsx_files(folder_path):
    xlsx_files = glob.glob(f"{folder_path}/**/*.xlsx", recursive=True)
    return xlsx_files


files = find_xlsx_files(file_path)
for file in files:
    if "~$" in file:
        continue
    data = pandas.read_excel(file)
    try:
        words = data['单词']
        pronunciations = data['美音']
        parts_of_speech = data['释义']
        word = zip(words, pronunciations, parts_of_speech)
        cursor.executemany("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", word)
        conn.commit()
    except Exception as e:
        print(f"Error inserting {file}: {e}")
conn.close()