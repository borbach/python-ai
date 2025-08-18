# A voice assistant that uses the Gemini API for conversational responses
# and the Gemini TTS API for high-quality, natural text-to-speech.

# Import necessary libraries
import speech_recognition as sr
import google.generativeai as genai
import requests # New library for making HTTP requests
import os
import base64
import json
import io
import wave
import pyaudio # Requires 'pip install pyaudio'
import numpy as np # Requires 'pip install numpy'
import time

# You will need to install the following libraries:
# pip install SpeechRecognition google-generativeai pyaudio numpy requests

def select_voice():
    """
    Prompts the user to select a voice from a pre-defined list of Gemini voices.
    Returns the selected voice name.
    """
    # A dictionary of prebuilt Gemini voices and their characteristics
    voices = {
        "Zephyr": "Bright",
        "Puck": "Upbeat",
        "Kore": "Firm",
        "Leda": "Youthful",
        "Charon": "Informative",
        "Fenrir": "Excitable",
        "Algenib": "Gravelly",
    }
    
    print("Available Gemini voices:")
    voice_list = list(voices.keys())
    for i, name in enumerate(voice_list):
        print(f"[{i}] {name} ({voices[name]})")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the voice you want to use: "))
            if 0 <= choice < len(voice_list):
                selected_voice = voice_list[choice]
                print(f"You have selected: {selected_voice} ({voices[selected_voice]})")
                return selected_voice
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def speak_with_gemini(text, voice_name):
    """
    Sends text to the Gemini TTS API, gets the audio data, and plays it.
    """
    print("Generating voice...")
    
    # API call details for Gemini TTS
    model_name = "gemini-2.5-flash-preview-tts"
    api_key = os.getenv("GEMINI_API_KEY") # Get API key from environment variable
    if not api_key:
        print("API key is not set. Please set the GEMINI_API_KEY environment variable.")
        return

    # Construct the payload for the API call
    payload = {
        "contents": [
            {"parts": [{"text": text}]}
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        },
        "model": model_name
    }

    # API endpoint URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    # Use a simple retry mechanism with exponential backoff for robustness
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                break # Exit the retry loop
            elif response.status_code == 429:
                # Handle rate limiting with exponential backoff
                retry_after = 2 ** attempt
                print(f"Rate limited. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise Exception(f"API returned status code: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed due to a request error: {e}")
            if attempt == max_retries - 1:
                raise # Re-raise if all attempts fail
            time.sleep(1) # Simple delay before next retry

    # Process the audio response
    part = result['candidates'][0]['content']['parts'][0]
    audio_data_base64 = part['inlineData']['data']
    audio_data_bytes = base64.b64decode(audio_data_base64)
    
    # The API returns raw PCM audio. We need to play it.
    # pyaudio is a good choice for playing raw audio streams.
    try:
        p = pyaudio.PyAudio()
        # The API returns signed 16-bit PCM at a sample rate of 16000 Hz
        stream = p.open(format=pyaudio.paInt16,
                        channels=1, # The API always returns mono audio
                        rate=16000,
                        output=True)
        
        # Write the audio data to the stream
        stream.write(audio_data_bytes)
        
        # Wait for the stream to finish and then clean up
        stream.stop_stream()
        stream.close()
        p.terminate()

    except Exception as e:
        print(f"Error playing audio: {e}")
        print("Please ensure you have a working audio output device and that PyAudio is correctly installed.")


def listen_for_input():
    """
    Uses the SpeechRecognition library to listen for user input.
    Returns the recognized text or None if an error occurs.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            print("Recognizing...")
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return None

def main():
    """
    Main function to run the voice assistant.
    """
    # --- Part 1: Setup Text-to-Speech ---
    selected_voice = select_voice()
    
    # --- Part 2: Setup Gemini API ---
    # NOTE: Set your API key as an environment variable named GEMINI_API_KEY
    genai.configure()
    
    # Initialize the GenerativeModel and start a chat session
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    
    print("\n\nReady to chat! Press Ctrl+C to exit.")
    speak_with_gemini("Hello! I am ready to talk. How can I help you?", selected_voice)

    # --- Part 3: Main conversational loop ---
    while True:
        try:
            # Get user input from either voice or text
            user_input_mode = input("\nType 'speak' to talk or 'text' to type (or 'exit' to quit): ").strip().lower()

            user_text = ""
            if user_input_mode == 'speak':
                user_text = listen_for_input()
                if not user_text:
                    continue  # Skip to the next loop iteration if speech recognition fails
            elif user_input_mode == 'text':
                user_text = input("You: ")
            elif user_input_mode == 'exit':
                print("Goodbye!")
                break
            else:
                print("Invalid input mode. Please choose 'speak' or 'text'.")
                continue

            # Send the user's message to Gemini
            response = chat.send_message(user_text)
            gemini_response = response.text
            
            # Print and speak Gemini's response
            print(f"Gemini: {gemini_response}")
            speak_with_gemini(gemini_response, selected_voice)

        except genai.APIError as e:
            print(f"An API error occurred: {e}")
            speak_with_gemini("I am sorry, I am having trouble connecting to Gemini. Please check your API key.", selected_voice)
        except KeyboardInterrupt:
            print("\nExiting program.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            speak_with_gemini("I encountered an issue. Please try again.", selected_voice)

if __name__ == "__main__":
    main()

