# A voice assistant that uses the Gemini API for conversational responses
# and pyttsx3 for text-to-speech.

# Import necessary libraries
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
import os

def list_voices():
    """
    Initializes the text-to-speech engine and lists all available voices.
    Returns the engine and the list of voices.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return engine, voices

def select_voice(voices):
    """
    Prompts the user to select a voice from the available list.
    Returns the selected voice object.
    """
    print("Available voices:")
    for i, voice in enumerate(voices):
        print(f"[{i}] Name: {voice.name} | ID: {voice.id}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the voice you want to use: "))
            if 0 <= choice < len(voices):
                print(f"You have selected: {voices[choice].name}")
                return voices[choice]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def speak(engine, text):
    """
    Uses the pyttsx3 engine to speak the given text.
    """
    engine.say(text)
    engine.runAndWait()

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
    engine, voices = list_voices()
    if not voices:
        print("No voices found. Cannot proceed with the program.")
        return
    
    selected_voice = select_voice(voices)
    engine.setProperty('voice', selected_voice.id)
    
    # --- Part 2: Setup Gemini API ---
    api_key = os.getenv( "GEMINI_API_KEY" ) 
#    api_key = input("Enter your Gemini API key: ")
    genai.configure(api_key=api_key)
    
    # Initialize the GenerativeModel and start a chat session
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    
    print("\n\nReady to chat! Press Ctrl+C to exit.")
    speak(engine, "Hello! I am ready to talk. How can I help you?")

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
            speak(engine, gemini_response)

        except genai.APIError as e:
            print(f"An API error occurred: {e}")
            speak(engine, "I am sorry, I am having trouble connecting to Gemini. Please check your API key.")
        except KeyboardInterrupt:
            print("\nExiting program.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            speak(engine, "I encountered an issue. Please try again.")

if __name__ == "__main__":
    main()

