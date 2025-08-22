# First, ensure you have the required library installed:
# pip install google-genai

import google.genai as genai
from google.genai import types
import os

# The `google-generativeai` library is being replaced with `google-genai`.
# If you run into installation issues, you may need to uninstall the old one first.
# pip uninstall google-generativeai
# pip install google-genai

# --- Setup and Authentication ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual API key.
# A safer practice is to store your API key in an environment variable.
# For example, on a Linux/macOS terminal:
# export GOOGLE_API_KEY="your_api_key_here"
# On Windows Command Prompt:
# set GOOGLE_API_KEY="your_api_key_here"

# Try to get the API key from an environment variable first
try:
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not API_KEY:
        # Fallback if the environment variable is not set
        API_KEY = "YOUR_API_KEY" # Replace with your key
    
    # The client now uses the `google.genai` namespace
    client = genai.Client(api_key=API_KEY)
    
except Exception as e:
    print(f"An error occurred during API key configuration: {e}")
    print("Please make sure you have the 'google-genai' library installed and a valid API key.")
    exit()

# --- Main Program Logic ---
def get_info_with_web_search():
    """
    Prompts the user for a subject and uses the GenerativeModel to
    find and present information using a web search.
    """
    print("Welcome to the Web Search AI!")
    print("I can help you find information on any subject using the power of web search.")
    
    try:
        # Get the subject from the user
        user_subject = input("\nPlease enter the subject you would like to search for: ")
        
        if not user_subject:
            print("No subject entered. Exiting program.")
            return

        print(f"\nSearching for information on: '{user_subject}'...")
        
        # Construct the prompt for the model
        prompt = f"Find information about '{user_subject}' and summarize it concisely."
        
        # --- FIX: The `tools` parameter must be inside a `types.GenerateContentConfig` object.
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        # Print the final response from the model
        print("\n--- Search Results ---")
        print(response.text)
        print("\n--- End of Results ---")
        
    except Exception as e:
        print(f"\nAn error occurred during content generation: {e}")
        print("Please check your API key, internet connection, and try again.")

# Run the program
if __name__ == "__main__":
    get_info_with_web_search()

