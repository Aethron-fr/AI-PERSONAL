"""
ANUSHKA VISION — Biometric Empathy & Real-Time Presence
"""

import cv2
import threading
import time

class AnushkaVision:
    def __init__(self, brain):
        self.brain = brain
        self.running = True
        self.camera_index = 0
        self.last_seen = time.time()
        self.is_user_present = False
        
        # Start the background observer thread
        self.thread = threading.Thread(target=self._observer_loop, daemon=True)
        self.thread.start()
        
    def _observer_loop(self):
        try:
            import mediapipe as mp
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except ImportError:
            print("MediaPipe not installed. Vision module degraded to basic presence.")
            face_mesh = None

        cap = cv2.VideoCapture(self.camera_index)
        
        # We don't want to lock the camera 100% of the time. 
        # We sample it briefly every few seconds to save resources.
        
        while self.running:
            if not cap.isOpened():
                cap.open(self.camera_index)
                
            ret, frame = cap.read()
            if ret:
                # Analyze frame
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                if face_mesh:
                    results = face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        self.is_user_present = True
                        self.last_seen = time.time()
                        
                        # In the future: Add Eye Aspect Ratio (EAR) calculation here 
                        # to detect blinking/fatigue.
                        
                        # Update Anushka's internal state
                        self.brain.update_biometrics(present=True, fatigue_level=0)
                    else:
                        self.is_user_present = False
                        self.brain.update_biometrics(present=False, fatigue_level=0)
            
            # Release camera temporarily to free up OS resources
            cap.release()
            
            # Sleep for 5 seconds before checking again (stealth mode)
            time.sleep(5)
            
    def stop(self):
        self.running = False
