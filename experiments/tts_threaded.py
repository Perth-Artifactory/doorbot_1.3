import pyttsx3
import threading

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.setProperty('voice', 'english+f2')

    engine.say(text)
    engine.runAndWait()

def non_blocking_speak(text):
    speak_thread = threading.Thread(target=speak_text, args=(text,))
    speak_thread.start()

if __name__ == "__main__":
    text = "Hello, I am an offline text-to-speech program running on Raspberry Pi."
    non_blocking_speak(text)

    # Your other code here
    print("This text will be printed while the TTS is running.")
