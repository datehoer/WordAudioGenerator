token = "sk-"
text_model_name = "gpt-4-turbo-preview"
tts_model_name = "tts-1-1106"
token_url = ""
proxy = {'http':'http://127.0.0.1:7890', 'https':'http://127.0.0.1:7890'}
openai_text_url = "https://api.openai.com/v1/chat/completions"
openai_tts_url = "https://api.openai.com/v1/audio/speech"
openai_header = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(token)
}
openai_text_data = {
     "model": text_model_name,
     "messages": [{"role": "user", "content": "Say this is a test!"}],
     "temperature": 0.7
}
openai_tts_data = {
    "model": tts_model_name,
    "input": "The quick brown fox jumped over the lazy dog.",
    "voice": "alloy"
}