import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
from gtts import gTTS
import os
import time
import pygame
from googletrans import Translator

# Initialize pygame mixer
pygame.mixer.init()

# Picovoice Access Key
ACCESS_KEY = "IJ7NcAg+PsPwSUE+BGFbHRqRviMpXcsbjPi/wxnsBwpUCHcNqtL9KA=="

# Supported languages
LANG_CODES = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "kannada": "kn-IN"
}

# Global variable for chosen language
selected_language = "en-IN"

# Wake word listener
def listen_for_wakeup():
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=["models/echo_bot_windows.ppn"]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(rate=porcupine.sample_rate,
                     channels=1,
                     format=pyaudio.paInt16,
                     input=True,
                     frames_per_buffer=porcupine.frame_length)

    print("Listening for wake word: 'echobot'...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)

            if result >= 0:
                print("✅ Wake word detected!")
                speak("Hello! Please choose your language: English, Hindi, or Kannada.", "en")
                select_language()
                listen_and_respond()
    except KeyboardInterrupt:
        print("❌ Stopped by user.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

# Language selection function
def select_language():
    global selected_language
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            print("🎤 Listening for language preference...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            print("🧠 Recognizing language choice...")
            choice = recognizer.recognize_google(audio, language="en-IN").lower()
            print(f"🔹 User selected: {choice}")

            if "english" in choice:
                selected_language = LANG_CODES["english"]
                speak("You have selected English. How can I assist you?", "en")
                break
            elif "hindi" in choice:
                selected_language = LANG_CODES["hindi"]
                speak("आपने हिंदी चुनी है। मैं आपकी कैसे मदद कर सकता हूँ?", "hi")
                break
            elif "kannada" in choice:
                selected_language = LANG_CODES["kannada"]
                speak("ನೀವು ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಿ. ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?", "kn")
                break
            else:
                speak("I couldn't recognize your choice. Please say English, Hindi, or Kannada.", "en")
        except sr.UnknownValueError:
            speak("I didn't catch that. Please say English, Hindi, or Kannada.", "en")

# Recognize queries and respond
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    translator = Translator()

    while True:  # Continuously listen for queries
        with mic as source:
            print("🎤 Listening for your query...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            print("🧠 Recognizing...")
            query = recognizer.recognize_google(audio, language=selected_language)
            print(f"🔹 You said ({selected_language}):", query)

            # Get response in English
            response = handle_query(query)
            print("🤖 Response before translation:", response)

            # Translate response to the selected language
            translated_response = translator.translate(response, src="en", dest=selected_language.split("-")[0]).text
            print("🌐 Translated Response:", translated_response)

            # Speak the translated response
            speak(translated_response, selected_language.split("-")[0])

        except sr.UnknownValueError:
            print("🤷‍♂️ Sorry, I didn’t catch that.")
            speak("Sorry, I didn’t catch that.", selected_language.split("-")[0])
        except Exception as e:
            print("Error:", e)

# Response logic
def handle_query(query):
    query = query.lower()

    if "department" in query or "विभाग" in query or "ವಿಭಾಗ" in query:
        return "MVJ College of Engineering has departments like CSE, ECE, ME, and more."
    elif "canteen" in query or "कैंटीन" in query or "ಕ್ಯಾಂಟೀನ್" in query:
        return "The canteen is located near the auditorium."
    elif "principal" in query or "प्रधानाचार्य" in query or "ಮುಖ್ಯಾಧಿಕಾರಿ" in query:
        return "The principal of MVJ College is Dr. K. Ramesh Babu."
    elif "library" in query or "पुस्तकालय" in query or "ಲೈಬ್ರರಿ" in query:
        return "The library is on the first floor with thousands of books and journals."
    elif "bus" in query or "बस" in query or "ಬಸ" in query:
        return "The college has a fleet of buses for students and staff."
    else:
        return "Sorry, I don't have information about that yet."

# Speak using gTTS
def speak(text, lang_code):
    try:
        # Extract primary language (like 'hi', 'kn', 'en') from 'hi-IN', 'kn-IN', etc.
        lang_code = lang_code.split("-")[0] if "-" in lang_code else lang_code

        tts = gTTS(text=text, lang=lang_code)
        filename = "response.mp3"
        tts.save(filename)

        # Wait for the file to be saved before playing
        time.sleep(1)

        # Play the audio using pygame.mixer
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait for the sound to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Stop and unload the audio file
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        # Try deleting the file after ensuring it's not in use
        os.remove(filename)

    except Exception as e:
        print("TTS Error:", e)

# Start
if __name__ == "__main__":
    listen_for_wakeup()
