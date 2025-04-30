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
import serial
import random  # Import the random module

# Initialize pygame mixer
pygame.mixer.init()

# Picovoice Access Key
ACCESS_KEY = "YOUR_ACCESS_KEY"  # Replace with your actual Picovoice Access Key

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
# Global variable for serial port
SERIAL_PORT = '/dev/ttyACM0'  # Replace with the correct serial port for your Arduino

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
        keyword_paths=["models/echo_bot_windows.ppn"]  # Make sure you have the correct path to the wake word file
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
                # Include the wave_hi() function call here:
                wave_hi()  # Make the robot wave
                speak("Hello! Please choose your language: English, Hindi, or Kannada.", "en")
                select_language()
                listen_and_respond()
                break  # Exit the wake word loop after detecting the word and waving
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



# Global serial port object
ser = None

def connect_to_arduino():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)  # Adjust baud rate if needed
        print("✅ Connected to Arduino!")
    except serial.SerialException as e:
        print(f"❌ Error: Could not connect to Arduino.  Check the port and connection: {e}")
        ser = None # make sure ser is None if connection fails
        # Don't exit here,  allow the program to continue, user may not use the chat functionality
        #exit()

def send_command_to_arduino(command):
    if ser is not None: # Check if the serial connection is established
        try:
            ser.write(command.encode())
            print(f"Sent command: {command}")  # Keep the print statement for debugging
            time.sleep(0.1)  # Add a small delay to allow the Arduino to process the command
        except serial.SerialException as e:
            print(f"❌ Error sending command: {e}")
    else:
        print(f"❌ Error: Not connected to Arduino.  Command {command} not sent.")

def wave_hi():
    """
    Sends commands to the Arduino to make the robot wave its right arm.
    Adjust the motor numbers and angles according to your robot's configuration.
    """
    if ser is not None:
        print("🤖 Waving hi...")
        send_command_to_arduino("M1=90,M2=90,M3=90,M4=90,M5=90,M6=90\n")  # Initial position
        time.sleep(1)
        send_command_to_arduino("M1=120,M2=60,M3=90,M4=90,M5=90,M6=90\n")  # Wave out
        time.sleep(0.5)
        send_command_to_arduino("M1=60,M2=120,M3=90,M4=90,M5=90,M6=90\n")  # Wave in
        time.sleep(0.5)
        send_command_to_arduino("M1=120,M2=60,M3=90,M4=90,M5=90,M6=90\n")  # Wave out
        time.sleep(0.5)
        send_command_to_arduino("M1=90,M2=90,M3=90,M4=90,M5=90,M6=90\n")  # Return to initial
        time.sleep(1)
    else:
        print("❌ Error: Arduino not connected.  Cannot wave.")

def random_action():
    """
    Sends random commands to the Arduino to make the robot perform a small,
    randomized movement.  This adds a bit of liveliness.  Adjust motor numbers
    and angle ranges for your robot.
    """
    if ser is not None:
        print("🤖 Performing random action...")
        for _ in range(3):  # Perform a short sequence of random movements
            motor1_angle = random.randint(60, 120)
            motor2_angle = random.randint(60, 120)
            motor3_angle = random.randint(60, 120)
            command = f"M1={motor1_angle},M2={motor2_angle},M3={motor3_angle},M4=90,M5=90,M6=90\n"
            send_command_to_arduino(command)
            time.sleep(0.3)  # Short delay between movements
    else:
        print("❌ Error: Arduino not connected. Cannot perform random action.")

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

def explain_response(query, response):
    """
    Adds explanatory text to the response, providing more context.
    """
    explanation = ""
    if "department" in query or "विभाग" in query or "ವಿಭಾಗ" in query:
        explanation = "MVJ College of Engineering has several departments, including Computer Science, Electronics and Communication, Mechanical Engineering, and others.  These departments offer various undergraduate and postgraduate programs."
    elif "canteen" in query or "कैंटीन" in query or "ಕ್ಯಾಂಟೀನ್" in query:
        explanation = "The canteen provides food and refreshments for students and staff.  It's a place to relax and have meals."
    elif "principal" in query or "प्रधानाचार्य" in query or "ಮುಖ್ಯಾಧಿಕಾರಿ" in query:
        explanation = "The principal is the head of the institution, responsible for its overall administration and academic activities."
    elif "library" in query or "पुस्तकालय" in query or "ಲೈಬ್ರರಿ" in query:
        explanation = "The library offers a wide range of resources, including books, journals, and digital materials, to support learning and research."
    else:
        explanation = "I am still under development and learning to provide more detailed information."

    return f"{explanation}  {response}"  # Combine explanation and original response

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
            # Add explanation to the response
            response = explain_response(query, response)
            print("🤖 Response before translation:", response)

            # Translate the response back into the selected language
            translated_response = translator.translate(response, src="en",
                                                     dest=selected_language.split("-")[0]).text
            print("🌐 Translated Response:", translated_response)

            # Speak the translated response
            speak(translated_response, selected_language.split("-")[0])
            # Perform a random action
            random_action()

        except sr.UnknownValueError:
            print("🤷‍♂️ Sorry, I didn’t catch that.")
            speak("Sorry, I didn’t catch that.", selected_language.split("-")[0])
        except Exception as e:
            print("Error:", e)



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
    connect_to_arduino() # Connect to Arduino at the start
    detect_face()
    if ser is not None:
        ser.close()
