import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os

# --- Configuration ---
try:
    gemini_api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
except KeyError:
    print("Error: 'GEMINI_API_KEY' environment variable not set.")
    print("Please set the environment variable or hardcode your API key in the script.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during API configuration: {e}")
    exit()

# --- Functions ---

def speak_text(text):
    """Converts text to speech and plays it."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    """
    Listens for user's voice and returns it as a text string,
    listening until the user says "finished".
    """
    r = sr.Recognizer()
    full_query = ""
    print("Listening... Say 'finished' when you are done speaking.")

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        while True:
            try:
                # Listen for a single phrase. This is the key change.
                audio = r.listen(source)
                print("Recognizing phrase...")
                phrase = r.recognize_google(audio, language='en-US')
                
                # Check if the user said the keyword
                if "finished" in phrase.lower():
                    print("Keyword 'finished' detected. Processing query.")
                    # Remove the keyword from the final query
                    full_query = full_query.replace("finished", "").strip()
                    return full_query
                
                # If not the keyword, append the phrase to the full query
                full_query += " " + phrase
                print(f"Current query: {full_query}")
            
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that phrase.")
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return ""
            except Exception as e:
                print(f"An unexpected error occurred during speech recognition: {e}")
                return ""

def get_gemini_response(user_input):
    """Sends user input to Gemini and returns the text response."""
    if not user_input:
        return "I'm sorry, I didn't hear anything to respond to."
    
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return "I'm sorry, I encountered an error and cannot respond at this time."

# --- Main Program Loop ---

def main():
    """Main function to run the voice assistant."""
    speak_text("Hello, I am a voice assistant powered by Gemini. Please start speaking and say 'finished' when you are done.")
    while True:
        user_input = listen_for_command()

        # Check for exit commands and empty input
        if "exit" in user_input.lower() or "goodbye" in user_input.lower() or "bye" in user_input.lower():
            speak_text("Goodbye! Have a great day.")
            break
        
        # Get and speak Gemini's response
        ai_response = get_gemini_response(user_input)
        print(f"Gemini says: {ai_response}")
        speak_text(ai_response)

if __name__ == "__main__":
    main()


