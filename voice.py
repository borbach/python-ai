import pyttsx3


def Voice():
    print("hello world")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    i = 0
    for voice in voices:
        print(f"Voice ID: {voice.id}, Name: {voice.name}, Gender: {voice.gender}")
        print( "id is " + str( i ) )
        i += 1
    for voice in voices:
        if voice.gender == 'female': # or check voice.name for specific female voices
            print(f"Found female voice: {voice.name} (ID: {voice.id})")
            # You can store the ID of the first female voice found
            female_voice_id = voice.id
            break # Exit loop once a suitable voice is found


if __name__ =="__main__":
    Voice()

