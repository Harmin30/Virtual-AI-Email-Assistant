# eva_voice.py

import pyttsx3
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os

# Text-to-Speech (TTS)
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    """Make EVA speak"""
    print(f"EVA says: {text}")
    engine.say(text)
    engine.runAndWait()

# Speech-to-Text (STT)
def listen():
    """Listen for voice input and convert to text using Google Speech API"""
    samplerate = 16000  # 16kHz is recommended
    duration = 5  # Record for 5 seconds

    speak("Listening...")
    print("🎤 Listening... (speak clearly into the mic)")

    # Record audio
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    # Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        write(tmp.name, samplerate, recording)
        temp_path = tmp.name

    # Use recognizer to transcribe
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        print("🧠 You said:", text)
        return text
    except sr.UnknownValueError:
        speak("Sorry, I couldn’t understand that.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return ""
    finally:
        os.remove(temp_path)  # Cleanup

