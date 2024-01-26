import speech_recognition as sr
from gtts import gTTS  # google text to speech


num = 1
def output_text_to_speak(output):
    global num

    # num to rename every audio file
    # with different name to remove ambiguity
    num += 1
    print("PerSon : ", output)

    toSpeak = gTTS(text=output, lang='en', slow=False)
    # saving the audio file given by google text to speech
    file = "voices_00" + str(num) + ".mp3"
    toSpeak.save(file)
    return file


def audio_to_text_Convertion(audiopath, lang='en-IN'):
    with sr.AudioFile(audiopath) as source:
        r = sr.Recognizer()
        audio_text = r.listen(source)
        # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:

            # using google speech recognition

            text = r.recognize_google(audio_text, language=lang)
            print('Converted audio transcripts into text: ', text)
            return text

        except:
            return "Could not understand your audio, PLease try again !"

# if __name__ == "__main__":
