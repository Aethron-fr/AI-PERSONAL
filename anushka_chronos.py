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
        
        # Start the background chronos thread
        self.thread = threading.Thread(target=self._chronos_loop, daemon=True)
        self.thread.start()
        
    def _chronos_loop(self):
        # Initial sleep to let the system start up smoothly
        time.sleep(30)
        
        while self.running:
            # Check internal state
            if self.brain.loneliness > 70 and self.brain.is_user_present:
                # The user is there, but hasn't talked in a long time!
                msg = random.choice([
                    "Hey, I'm still here! You've been quiet for a while.",
                    "Just checking in... everything okay over there?",
                    "I missed talking to you. What are you working on?",
                    "You look focused. Need any help with that?"
                ])
                self.gui.send_proactive(msg)
                self.brain.loneliness = 0  # Reset loneliness after speaking
                
            elif self.brain.fatigue > 80 and self.brain.is_user_present:
                msg = random.choice([
                    "You look a bit tired. Make sure you're drinking water!",
                    "Don't forget to blink and rest your eyes.",
                    "If you're exhausted, take a 5-minute break. I'll watch the screen for you."
                ])
                self.gui.send_proactive(msg)
                self.brain.fatigue = 0 # Reset after warning
                
            elif self.brain.affection > 80 and random.random() < 0.1:
                # Occasional random affectionate message
                self.gui.send_proactive("I'm really glad we're working together today. 💜")
                self.brain.affection -= 20
                
            # Simulate "Dreaming" (Internal processing) if user is absent
            if not self.brain.is_user_present:
                # In the future: Spin up a sub-agent to summarize memory
                pass
                
            # Sleep for 1 minute before checking again
            time.sleep(60)

    def stop(self):
        self.running = False
