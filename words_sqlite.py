import sqlite3

conn = sqlite3.connect('words.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS words
                  (word TEXT PRIMARY KEY, pronunciation TEXT, part_of_speech TEXT)''')

with open("word.txt", "r", encoding="utf-8") as f:
    words = f.read().split("\n")
    for line in words:
        parts = line.split(" ", 1)
        if len(parts) == 2:
            word, pronunciation = parts[0], parts[1]
            if "]" in pronunciation:
                pronunciation, part_of_speech = pronunciation.split("]", 1)
                pronunciation = pronunciation + "]"
                if pronunciation == "[]":
                    continue
                if ") [" in part_of_speech:
                    pronunciation = part_of_speech.split(") [", 1)[1]
                    pronunciation = "[" + pronunciation
                if not pronunciation.startswith("["):
                    continue
            else:
                part_of_speech = ""
            try:
                if not pronunciation.startswith("["):
                    continue
                if "(" in word:
                    word = word.split("(", 1)[0]
                cursor.execute("INSERT OR REPLACE INTO words VALUES (?, ?, ?)", (word, pronunciation, part_of_speech))
            except sqlite3.IntegrityError as e:
                print(f"Error inserting {word}: {e}")

conn.commit()
conn.close()
