import cv2
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
from gtts import gTTS
import os
import time
import pygame
from googletrans import Translator
import serial # Add Serial Communication

arduino = serial.Serial("/dev/serial0", 9600)


# Initialize pygame mixer
pygame.mixer.init()

# Picovoice Access Key
ACCESS_KEY = "IJ7NcAg+PsPwSUE+BGFbHRqRviMpXcsbjPi/wxnsBwpUCHcNqtL9KA=="

# Face Detection Setup (Using OpenCV Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Supported languages
LANG_CODES = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "kannada": "kn-IN"
}

# Global variable for chosen language
selected_language = "en-IN"

# Function to detect a face before activating wake word listening
def detect_face():
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        print("❌ Error: Could not open webcam.")
        return

    print("🔍 Waiting for face detection...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to capture frame.")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        cv2.imshow("Face Detection", frame)  # Open camera window

        if len(faces) > 0:
            print("😀 Face detected! Starting voice assistant...")
            cap.release()  # Close webcam after detecting face
            cv2.destroyAllWindows()  # Ensure all OpenCV windows close properly
            arduino.write(b'1')  # Signal to Arduino to wave
            speak("Face detected! Please say the wake word 'echobot' to begin.", "en")
            listen_for_wakeup()
            break

        # Exit the loop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("🚪 Exiting face detection...")
            break

    cap.release()  # Ensure the webcam closes correctly
    cv2.destroyAllWindows()  # Close OpenCV windows properly


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

    print("🎤 Waiting for wake word: 'echobot'...")

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
from googletrans import Translator  # Ensure Translator is imported

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

            # Translate response **back into the selected language**
            translated_response = translator.translate(response, src="en", dest=selected_language.split("-")[0]).text
            print("🌐 Translated Response:", translated_response)

            # Speak the translated response
            speak(translated_response, selected_language.split("-")[0])

            # **Trigger Explanation Gesture**
            arduino.write(b'2')

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
    else:
        return "Sorry, I don't have information about that yet."

# Speak using gTTS
def speak(text, lang_code):
    try:
        lang_code = lang_code.split("-")[0] if "-" in lang_code else lang_code

        tts = gTTS(text=text, lang=lang_code)
        filename = "response.mp3"
        tts.save(filename)

        # Wait for the file to be saved before playing
        time.sleep(1)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        os.remove(filename)

    except Exception as e:
        print("TTS Error:", e)

# Start: First detect a face before proceeding
if __name__ == "__main__":
    detect_face()
