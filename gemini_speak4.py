# A voice assistant that uses the Gemini API for conversational responses
# and the Gemini TTS API for high-quality, natural text-to-speech,
# all within a user-friendly Tkinter GUI.

# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import google.generativeai as genai
import requests
import base64
import json
import pyaudio
import time
import threading
import os # Import the os module to access environment variables

# You will need to install the following libraries:
# pip install SpeechRecognition google-generativeai pyaudio numpy requests

class GeminiVoiceAssistant(tk.Tk):
    """
    Main application class for the Gemini Voice Assistant GUI.
    """
    def __init__(self):
        super().__init__()
        self.title("Gemini Voice Assistant")
        self.geometry("600x400")
        self.resizable(False, False)

        # --- State Variables ---
        self.gemini_api_key = None
        self.gemini_chat = None
        self.selected_voice = tk.StringVar(self)

        # --- Gemini Voices Dictionary ---
        self.voices = {
            "Zephyr": "Bright", "Puck": "Upbeat", "Kore": "Firm",
            "Leda": "Youthful", "Charon": "Informative", "Fenrir": "Excitable",
            "Algenib": "Gravelly",
        }

        # --- Initialize GUI Components ---
        self.create_widgets()
        
        # Start the application logic
        self.get_api_key_from_env()

    def create_widgets(self):
        """
        Creates and lays out all the GUI widgets.
        """
        # Main frame for padding and organization
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Control Frame (Top) ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)

        # Voice selection dropdown
        ttk.Label(control_frame, text="Select Voice:").pack(side="left", padx=(0, 10))
        voice_combobox = ttk.Combobox(
            control_frame, 
            textvariable=self.selected_voice, 
            values=list(self.voices.keys()),
            state="readonly" # Prevent user from typing
        )
        voice_combobox.pack(side="left")
        voice_combobox.set("Kore") # Set a default voice

        # --- Status Label ---
        self.status_label = ttk.Label(main_frame, text="Status: Ready", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # --- Response Display (Text Widget) ---
        self.response_text = tk.Text(main_frame, wrap="word", height=10, width=60)
        self.response_text.pack(pady=10)
        self.response_text.insert(tk.END, "Gemini: Hello! How can I help you today?")
        self.response_text.config(state="disabled") # Make it read-only

        # --- Input Frame (Middle) ---
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)

        self.user_input = ttk.Entry(input_frame, width=40)
        self.user_input.pack(side="left", padx=(0, 10), ipady=5)
        self.user_input.bind("<Return>", lambda event: self.handle_text_input())

        self.send_button = ttk.Button(input_frame, text="Send Text", command=self.handle_text_input)
        self.send_button.pack(side="left")

        # --- Action Buttons Frame (Bottom) ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=10)

        self.speak_button = ttk.Button(action_frame, text="Speak to Gemini", command=self.start_voice_thread)
        self.speak_button.pack(side="left", padx=5)

        self.exit_button = ttk.Button(action_frame, text="Exit", command=self.on_exit)
        self.exit_button.pack(side="left", padx=5)

    def get_api_key_from_env(self):
        """
        Attempts to get the API key from an environment variable.
        Initializes the Gemini model if a valid key is found.
        """
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_chat = genai.GenerativeModel('gemini-1.5-flash').start_chat(history=[])
            except Exception as e:
                messagebox.showerror("Initialization Error", f"Failed to initialize Gemini. Check your API key.\nError: {e}")
                self.on_exit()
        else:
            messagebox.showerror(
                "API Key Missing",
                "The GEMINI_API_KEY environment variable is not set. "
                "Please set it and restart the application."
            )
            self.on_exit()

    def update_status(self, message):
        """
        Updates the status label in the GUI.
        """
        self.status_label.config(text=f"Status: {message}")
        self.update_idletasks() # Force GUI update

    def display_message(self, speaker, message):
        """
        Displays a new message in the conversation text area.
        """
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, f"\n\n{speaker}: {message}")
        self.response_text.see(tk.END) # Auto-scroll to the bottom
        self.response_text.config(state="disabled")

    def handle_text_input(self):
        """
        Handles user input from the text entry field.
        """
        user_text = self.user_input.get().strip()
        if user_text:
            self.display_message("You", user_text)
            self.user_input.delete(0, tk.END) # Clear the entry field
            self.start_gemini_response_thread(user_text)

    def handle_voice_input(self):
        """
        Handles user input from the microphone. This runs in a separate thread.
        """
        self.update_status("Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                self.update_status("Recognizing...")
                user_text = recognizer.recognize_google(audio)
                self.display_message("You", user_text)
                self.start_gemini_response_thread(user_text)
            except sr.UnknownValueError:
                messagebox.showerror("Speech Error", "Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                messagebox.showerror("API Error", f"Could not request results from the speech recognition service; {e}")
            except sr.WaitTimeoutError:
                messagebox.showinfo("Timeout", "Listening timed out. Please try again.")
            finally:
                self.update_status("Ready")

    def start_voice_thread(self):
        """
        Starts a new thread to handle voice input to keep the GUI responsive.
        """
        voice_thread = threading.Thread(target=self.handle_voice_input, daemon=True)
        voice_thread.start()

    def start_gemini_response_thread(self, user_text):
        """
        Starts a new thread to get and speak Gemini's response.
        """
        response_thread = threading.Thread(target=self.get_and_speak_response, args=(user_text,), daemon=True)
        response_thread.start()

    def get_and_speak_response(self, user_text):
        """
        Sends user text to Gemini, gets the response, displays it, and then speaks it.
        This function runs in a separate thread.
        """
        try:
            self.update_status("Thinking...")
            # Step 1: Get the text response from Gemini
            response = self.gemini_chat.send_message(user_text)
            gemini_text = response.text
            
            # Step 2: Immediately display the text response in the GUI
            self.display_message("Gemini", gemini_text)
            
            # Step 3: Now, generate and play the voice in the background
            self.update_status("Generating and playing voice...")
            self.speak_with_gemini(gemini_text, self.selected_voice.get())

        except genai.APIError as e:
            messagebox.showerror("Gemini API Error", f"An API error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            self.update_status("Ready")

    def speak_with_gemini(self, text, voice_name):
        """
        Sends text to the Gemini TTS API and plays the resulting audio.
        """
        model_name = "gemini-2.5-flash-preview-tts"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
                }
            },
            "model": model_name
        }

        # Use a retry mechanism with exponential backoff
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                if response.status_code == 200:
                    result = response.json()
                    break
                elif response.status_code == 429:
                    retry_after = 2 ** attempt
                    self.update_status(f"Rate limited. Retrying in {retry_after}s...")
                    time.sleep(retry_after)
                else:
                    raise Exception(f"API returned status code: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1: raise
                self.update_status(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        else: # This block is executed if the loop completes without a 'break'
            raise Exception("All API call attempts failed.")
        
        part = result['candidates'][0]['content']['parts'][0]
        audio_data_base64 = part['inlineData']['data']
        audio_data_bytes = base64.b64decode(audio_data_base64)
        
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            output=True)
            stream.write(audio_data_bytes)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            messagebox.showerror("Audio Playback Error", f"Error playing audio: {e}")

    def on_exit(self):
        """
        Handles the exit button, closes the application gracefully.
        """
        self.destroy()

if __name__ == "__main__":
    app = GeminiVoiceAssistant()
    app.mainloop()

