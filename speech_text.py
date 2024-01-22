import random
from scipy.io.wavfile import write
#import sounddevice as sd
import speech_recognition as sr

import os
#import pyaudio
import playsound  # to play saved mp3 file
from gtts import gTTS  # google text to speech

# Set your OpenAI API key here
# from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# Global variable to store audio data
# audio = []

# Adjectives to generate random names for voices
adjectives = ["beautiful", "sad", "mystical", "serene", "whispering", "gentle", "melancholic"]
nouns = ["sea", "love", "dreams", "song", "rain", "sunrise", "silence", "echo"]



is_text_gen_completed = False



def set_text_gen_required_status():
    global is_text_gen_completed
    is_text_gen_completed = True


def get_text_gen_required_status():
    return is_text_gen_completed

def speech_to_text(audio_path):
    print("entered transcribe: ", audio_path)
    # path = "E:/git_project/aiDemo/personal-chatgpt/voices/sad-sunrise.wav"
    # import pydub
    # audio_name = generate_random_name()
    # new_audio_path = "E:/git_project/aiDemo/personal-chatgpt/voices/{audio_name}.mp3"
    # sound = pydub.AudioSegment.from_wav(path)
    # sound.export(new_audio_path, format="mp3")

    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        try:
            output_text = r.recognize_google(audio_data)
        except Exception as e:
            print("Exception: " + str(e))

    # audio_file = open(audio_path, "rb")
    # print(audio_file)
    # transcript = openai.Audio.transcribe("whisper-1", audio_file)
    # print(transcript)
    # return transcript['text']
    print(output_text)
    return output_text



num = 1


def output_text_to_speak(output):
    global num

    # num to rename every audio file
    # with different name to remove ambiguity
    num += 1
    print("PerSon : ", output)

    toSpeak = gTTS(text=output, lang='en', slow=False)
    # saving the audio file given by google text to speech
    file = "voices/" + str(num) + ".mp3"
    toSpeak.save(file)

    # playsound package is used to play the same file.
    playsound.playsound(file, True)
    os.remove(file)


def get_audio_to_text():
    rObject = sr.Recognizer()
    audio = ''

    with sr.Microphone() as source:
        print("Speak...")

        # recording the audio using speech recognition
        audio = rObject.listen(source, phrase_time_limit=5)
    print("Stop.")  # limit 5 secs

    try:

        text = rObject.recognize_google(audio, language='en-US')
        print("You : ", text)
        return text

    except:

        output_text_to_speak("Could not understand your audio, PLease try again !")
        return 0

# if __name__ == "__main__":
