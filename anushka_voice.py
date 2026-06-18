"""
ANUSHKA Voice — Text to Speech Engine using gTTS and pygame
"""

import threading
import re
import os
import tempfile
import time

class AnushkaVoice:
    def __init__(self):
        self.enabled = True
        self._speaking = False
        self._setup()

    def _setup(self):
        try:
            import pygame
            pygame.mixer.init()
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
        if not self.enabled:
            return
        clean = self._clean_for_speech(text)
        if not clean:
            return
        
        self._speaking = True
        try:
            from gtts import gTTS
            import pygame
            
            # Generate speech
            tts = gTTS(text=clean, lang='en', slow=False)
            
            # Create a temporary file
            fd, tmp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            
            tts.save(tmp_path)
            
            # Play with pygame
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Cleanup
            pygame.mixer.music.unload()
            try:
                os.remove(tmp_path)
            except:
                pass
                
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self._speaking = False

    def speak_async(self, text):
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def is_speaking(self):
        return self._speaking
