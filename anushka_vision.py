"""
ANUSHKA VISION — Biometric Empathy & Real-Time Presence
Gracefully degrades if no webcam is found.
"""

import threading
import time


class AnushkaVision:
    def __init__(self, brain):
        self.brain = brain
        self.running = True
        self.camera_index = 0
        self.available = False

        # Test if camera is accessible before starting thread
        self._check_camera()

        if self.available:
            self.thread = threading.Thread(target=self._observer_loop, daemon=True)
            self.thread.start()

    def _check_camera(self):
        try:
            import cv2
            cap = cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                self.available = True
                cap.release()
            else:
                print("Vision: No webcam found. Biometrics disabled.")
        except Exception as e:
            print(f"Vision: camera check failed — {e}")

    def _observer_loop(self):
        try:
            import mediapipe as mp
            import cv2
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except ImportError:
            face_mesh = None

        while self.running:
            try:
                import cv2
                cap = cv2.VideoCapture(self.camera_index)
                ret, frame = cap.read()
                cap.release()

                if ret:
                    if face_mesh:
                        import cv2
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = face_mesh.process(rgb)
                        present = bool(results.multi_face_landmarks)
                    else:
                        present = True  # Camera works, assume present if no MediaPipe

                    self.brain.update_biometrics(present=present, fatigue_level=0)
                else:
                    self.brain.update_biometrics(present=False, fatigue_level=0)

            except Exception as e:
                # Never crash the background thread
                pass

            time.sleep(5)

    def stop(self):
        self.running = False
