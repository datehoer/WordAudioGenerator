# Word Audio Generator

One-click generation of English-Chinese Excel word lists and audio files of articles composed of words.
[Chinese Introduce](https://github.com/datehoer/WordAudioGenerator/blob/main/readme.md)|English Introduce
### 💬 Introduction

I recently found a post on v2ex introducing [English improvement techniques](https://www.v2ex.com/t/940277). Besides getting familiar with the words by sight, I believe it's also important to get familiar with them by sound. I came across New Oriental's 100 sentences for IELTS vocabulary, and decided to use ChatGPT to generate articles based on the words, then create audio files to listen to during commutes.

The feature of generating Excel files came about because I found that exporting words in List required an additional fee. So I added this feature. Initially, I planned to use a dictionary to write the meanings of the words, but later I felt it would be better to use ~~Google Translate~~ SQLite3 for queries. ~~The translation utilizes the `translate.py` file. Of course, to use Google Translate, a proper network environment is necessary~~ Query existing data, and if not found, generate using ChatGPT/Google/Youdao Translate.

### 🚀 Features
- English-Chinese Excel word list generation: Organizes words, translations, and phonetic symbols into Excel format for easy memorization and review.
- Article text and audio generation: Generates English articles based on given words and converts them to audio files (openai/pyttsx3/gTTS) for listening practice.

### ✨ Installation and Usage
1. Install Python 3.11
2. Install necessary Python libraries with `pip install -r requirements.txt`
3. Place the word file into `words.txt` (words separated by spaces)
4. Fill in your OpenAI token in `config.py`
5. Run the `generate_article.py` file to generate articles and audio

### 📚 Dependencies

- `requests`: For handling requests
- `pandas`: For generating Excel files
- `epitran`: For generating word pronunciations (not recommended)
- `sqlite3`: For storing word pronunciations (recommended)
- `pyttsx3`: For generating audio files, use openai/gTTS for non-Windows platforms
- `json_repair`: For handling JSON format errors
- Other dependencies can be found in the `requirements.txt` file

### 🏊 Future Plans
- [ ] Optimize word phonetics
  - [ ] Collect more phonetic data
  - [x] Obtain phonetics through ChatGPT
- [ ] Optimize word translations
  - [ ] Collect more word data
  - [x] Obtain translations through ChatGPT

### 🛠️ Frequently Asked Questions

- If you encounter issues during installation or execution, please check if your Python version is 3.11
- Ensure all dependencies are correctly installed via `requirements.txt`
- If you face network connection issues, check your network settings and proxy configuration

### 📜 Phonetic Acquisition Instructions
#### 1. Epitran Installation Issues

Successfully used on Linux, failed on Windows

Linux installation tutorial reference: [Installation of Flite](https://github.com/dmort27/epitran?tab=readme-ov-file#installation-of-flite-for-english-g2p)

Preprocessing and result handling reference: [Preprocessors and postprocessors](https://github.com/dmort27/epitran?tab=readme-ov-file#preprocesssors-and-postprocessors)
#### 2. SQLite3 for Storing Phonetics
Approximately 40,000 word phonetic translations were obtained and stored in SQLite3, with queries used to retrieve word phonetics.