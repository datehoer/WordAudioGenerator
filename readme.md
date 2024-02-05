# Word Audio Generator
一键生成单词英汉Excel以及通过单词组成的文章音频文件

### 💬 介绍
最近在v2ex上搜到了一篇帖子介绍了[英语提升技巧](https://www.v2ex.com/t/940277)，我认为除了在混眼熟的情况下还应该混个耳熟，并且正好看到了新东方100句子背雅思单词，于是就准备利用ChatGPT根据单词生成文章然后再生成音频文件之后在通勤的路上听

生成Excel文件这个功能是因为我用List背单词的时候，发现它导出单词要另外收费，于是就加上了这个功能，本身想的是通过字典查询来写单词的意思，后来感觉不如直接~~利用谷歌翻译~~通过SQLite3进行查询。~~这里翻译利用到了`translate.py`这个文件，当然要使用谷歌翻译，必然要有配套的网络环境~~通过已有数据进行查询，如果未找到则利用Chat GPT生成/通过谷歌翻译获取

### 🚀 功能列表
- 英汉Excel单词表生成：将单词、翻译以及音标整理为Excel格式，方便背诵和复习
- 文章文本和音频生成：根据给定的单词，生成英语文章，并转换为音频文件(openai/pyttsx3/gTTS)，便于听力练习

### ✨ 安装使用
1. 安装Python 3.11
2. 通过`pip install -r requirements.txt`安装必要的Python库
3. 将单词文件放入`words.txt`中（单词间由空格分隔）
4. 在`config.py`中填入您的OpenAI token
5. 运行`generate_article.py`文件来生成文章和音频

### 📚 依赖库说明

- `requests`: 用于处理请求
- `pandas`: 用于Excel文件生成
- `epitran`: 用于单词发音生成 (不建议使用)
- `sqlite3`: 存储单词发音 (推荐使用)
- `pyttsx3`: 用于生成音频文件，如果为非Windows建议使用gTTS
- 其他依赖请参考`requirements.txt`文件


### 🏊 未来
- [ ] 优化单词音标
  - [ ] 采集更多音标数据
  - [x] 通过ChatGPT获取音标
- [ ] 优化单词翻译
  - [ ] 采集更多音标数据
  - [x] 通过ChatGPT获取单词翻译


### 🛠️ 常见问题

- 如果在安装或运行时遇到问题，请检查您的Python版本是否为3.11
- 确保所有依赖都已通过`requirements.txt`正确安装
- 如果遇到网络连接问题，请检查您的网络设置和代理配置

### 📜 音标获取说明
#### 1. epitran安装问题

这里我是在Linux上使用成功，在Windows上安装失败

Linux安装教程参考[Installation of Flite](https://github.com/dmort27/epitran?tab=readme-ov-file#installation-of-flite-for-english-g2p)

预处理以及结果处理参考[Preprocessors and postprocessors](https://github.com/dmort27/epitran?tab=readme-ov-file#preprocesssors-and-postprocessors)
#### 2. sqlite3存储音标
大约获取了4w左右的单词音标翻译，并将其存储在sqlite3中，通过查询来获取单词音标