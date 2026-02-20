# voice/speech_to_text.py
import speech_recognition as sr

def listen_voice():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
        return r.recognize_google(audio)
    except Exception as e:
        print(e)
        return "Hello"   # test fallback