import speech_recognition as sr
from fuzzywuzzy import process

quranic_verses = {
    1: "In the name of Allah, the Most Gracious, the Most Merciful.",
    2: "Praise be to Allah, the Lord of all the worlds.",
    3: "The Most Gracious, the Most Merciful.",
    4: "Master of the Day of Judgment.",
    5: "You alone we worship, and You alone we ask for help.",
    6: "Guide us on the Straight Path,",
    7: "the path of those who have received Your grace; not the path of those who have brought down wrath upon themselves, nor of those who have gone astray."
}


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please recite a Quranic verse in English:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language="en-US") 
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def find_closest_match(spoken_text, verses):
    matches = process.extractOne(spoken_text, verses.values())
    if matches:
        verse_number = list(verses.keys())[list(verses.values()).index(matches[0])]
        return verse_number, matches[0], matches[1]
    return None, None, 0

if __name__ == "__main__":
    spoken_text = recognize_speech()
    if spoken_text:
        verse_number, verse_text, confidence = find_closest_match(spoken_text, quranic_verses)
        if confidence > 50:  
            print(f"Matched Verse (#{verse_number}): {verse_text} (Confidence: {confidence}%)")
        else:
            print("Sorry, I could not match your recitation to a verse.")
