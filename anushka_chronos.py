"""
ANUSHKA CHRONOS — Background Dreaming & Proactive Autonomy
"""

import threading
import time
import random


class AnushkaChronos:
    def __init__(self, brain, gui):
        self.brain = brain
        self.gui = gui
        self.running = True

        self.thread = threading.Thread(target=self._chronos_loop, daemon=True)
        self.thread.start()

    def _chronos_loop(self):
        # Initial sleep — let the app fully start before Chronos intervenes
        time.sleep(45)

        while self.running:
            try:
                loneliness = getattr(self.brain, 'loneliness', 0)
                fatigue = getattr(self.brain, 'fatigue', 0)
                affection = getattr(self.brain, 'affection', 50)
                present = getattr(self.brain, 'is_user_present', False)

                if loneliness > 70 and present:
                    msg = random.choice([
                        "Hey, I'm still here! You've been quiet for a while 💜",
                        "Just checking in... everything okay over there?",
                        "I missed talking to you. What are you working on?",
                        "You look focused. Need any help with that?"
                    ])
                    self.gui.send_proactive(msg)
                    self.brain.loneliness = 0

                elif fatigue > 80 and present:
                    msg = random.choice([
                        "You look a bit tired. Make sure you're drinking water! 💧",
                        "Don't forget to blink and rest your eyes.",
                        "If you're exhausted, take a 5-minute break."
                    ])
                    self.gui.send_proactive(msg)
                    self.brain.fatigue = 0

                elif affection > 85 and present and random.random() < 0.15:
                    self.gui.send_proactive("I'm really glad we're working together today 💜")
                    self.brain.affection = max(50, affection - 20)

            except Exception:
                # Never let the background thread crash
                pass

            time.sleep(60)

    def stop(self):
        self.running = False
