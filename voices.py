# A program to list and play all available text-to-speech voices
# using the pyttsx3 library.

# Import the pyttsx3 library. If you don't have it, install it with:
# pip install pyttsx3
import pyttsx3

try:
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Get the list of all available voices on the system
    voices = engine.getProperty('voices')

    # Check if any voices were found
    if not voices:
        print("No voices found on your system. Please check your system's text-to-speech settings.")
    else:
        print(f"Found {len(voices)} voice(s). Playing a sample from each one...")

        # Loop through each voice in the list
        for i, voice in enumerate(voices):
            # Print details about the current voice
            print(f"\n--- Voice {i+1} ---")
            print(f"ID: {voice.id}")
            print(f"Name: {voice.name}")
            print(f"Languages: {voice.languages}")
            print(f"Gender: {voice.gender}")
            
            # Set the engine to use the current voice
            engine.setProperty('voice', voice.id)
            
            # Speak a sample sentence
            sentence = f"Hello! This is a test of the {voice.name} voice."
            engine.say(sentence)

            # Run the engine and wait for the speech to complete before moving to the next voice
            engine.runAndWait()

except Exception as e:
    # Catch any potential errors, like if the library isn't installed or configured correctly
    print(f"An error occurred: {e}")
    print("Please make sure you have pyttsx3 installed and that a compatible text-to-speech engine is set up on your operating system.")

finally:
    # Stop the engine to release system resources,
    # This is a good practice to ensure the program exits cleanly.
    if 'engine' in locals():
        engine.stop()


