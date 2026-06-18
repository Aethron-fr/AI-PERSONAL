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
        # Try to set up mediapipe face detection
        face_mesh = None
        try:
            import mediapipe as mp
            # mediapipe >= 0.10 uses mp.tasks API, older uses mp.solutions
            # Try the legacy solutions API first, fall back gracefully
            if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
                mp_face_mesh = mp.solutions.face_mesh
                face_mesh = mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            # If solutions API is gone, just do presence detection via haarcascade
        except Exception:
            face_mesh = None

        # Load fallback haarcascade detector
        haar = None
        try:
            import cv2
            haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            haar = cv2.CascadeClassifier(haar_path)
        except Exception:
            pass

        while self.running:
            try:
                import cv2
                cap = cv2.VideoCapture(self.camera_index)
                ret, frame = cap.read()
                cap.release()

                present = False
                if ret and frame is not None:
                    if face_mesh:
                        try:
                            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            results = face_mesh.process(rgb)
                            present = bool(results.multi_face_landmarks)
                        except Exception:
                            present = True  # Assume present on error
                    elif haar is not None:
                        # Fallback: haarcascade (always works, no mediapipe needed)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = haar.detectMultiScale(gray, 1.1, 4)
                        present = len(faces) > 0
                    else:
                        present = True  # Camera works, assume someone is there

                self.brain.update_biometrics(present=present, fatigue_level=0)

            except Exception:
                pass  # Never crash the background thread

            time.sleep(5)

    def stop(self):
        self.running = False
