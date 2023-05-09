import pyttsx3
import time

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

    # Set eSpeak as the TTS engine
    engine.setProperty('voice', 'english+f2')  # Female voice (use 'english+m2' for male voice)

    engine.say(text)
    engine.runAndWait()
    # if not engine.isBusy():
    #     time.sleep(0.1)
    
if __name__ == "__main__":
    text = "Hello, I am an offline text-to-speech program running on Raspberry Pi."
    speak_text(text)
    print("done1")

    time.sleep(1)

    text = "This is another test"
    speak_text(text)

