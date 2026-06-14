"""
ANUSHKA Voice — Text to Speech Engine
"""

import threading
import re


class AnushkaVoice:
    def __init__(self):
        self.enabled = True
        self.engine = None
        self._speaking = False
        self._setup()

    def _setup(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 168)
            self.engine.setProperty('volume', 1.0)
            voices = self.engine.getProperty('voices')
            # Prefer female voice
            female_keywords = ['zira', 'hazel', 'female', 'woman', 'girl', 'susan', 'eva']
            for v in voices:
                if any(k in v.name.lower() for k in female_keywords):
                    self.engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            print(f"Voice init note: {e}")
            self.enabled = False

    def _clean_for_speech(self, text):
        # Remove markdown, emoji, special chars
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'#+', '', text)
        text = re.sub(r'`+', '', text)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'[^\x00-\x7F\u0980-\u09FF\s]', '', text)
        text = text.strip()
        return text[:500]  # Max 500 chars for speech

    def speak(self, text):
        if not self.enabled or not self.engine:
            return
        clean = self._clean_for_speech(text)
        if not clean:
            return
        try:
            self._speaking = True
            self.engine.say(clean)
            self.engine.runAndWait()
            self._speaking = False
        except Exception as e:
            self._speaking = False

    def speak_async(self, text):
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def is_speaking(self):
        return self._speaking
