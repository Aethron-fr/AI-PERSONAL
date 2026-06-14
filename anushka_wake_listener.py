#!/usr/bin/env python3
"""
ANUSHKA Wake Listener
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This script runs silently in the background at all times.
It listens ONLY for the wake phrase "hey anushka" or "anushka".
When heard, it launches the full ANUSHKA agent automatically.

Run this script to start Anushka in always-listening mode:
    python anushka_wake_listener.py
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════
# LIGHTWEIGHT WAKE WORD LISTENER
# ══════════════════════════════════════════════

# Wake phrases — any of these will activate Anushka
WAKE_PHRASES = [
    'hey anushka',
    'anushka wake up',
    'anushka',
    'ok anushka',
    'hi anushka',
    'hello anushka',
    'anushka are you there',
    'anushka i need you',
]

anushka_process = None
is_anushka_running = False


def show_tray_notification(title, message):
    """Show a Windows system tray notification."""
    try:
        script = f'''
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipTitle = "{title}"
$notify.BalloonTipText = "{message}"
$notify.Visible = $True
$notify.ShowBalloonTip(3000)
Start-Sleep -s 4
$notify.Dispose()
'''
        subprocess.Popen(
            ['powershell', '-WindowStyle', 'Hidden', '-Command', script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except:
        pass


def play_activation_sound():
    """Play a short chime to signal Anushka is waking up."""
    try:
        import winsound
        # Pleasant double-beep
        winsound.Beep(880, 200)
        time.sleep(0.1)
        winsound.Beep(1100, 300)
    except:
        pass


def launch_anushka():
    """Launch the full ANUSHKA agent in a new terminal window."""
    global anushka_process, is_anushka_running

    if is_anushka_running:
        print("⚡ Anushka is already running.")
        return

    print("\n🌸 Wake word detected! Launching Anushka...")
    play_activation_sound()
    show_tray_notification("✦ Anushka", "Waking up... I'm here! 💕")

    script_dir = Path(__file__).parent.absolute()
    venv_python = script_dir / 'jarvis_env' / 'Scripts' / 'python.exe'

    if not venv_python.exists():
        venv_python = sys.executable

    # Launch Anushka in a new visible terminal window
    cmd = f'start "✦ Anushka — Your AI Companion" cmd /k ""{venv_python}" "{script_dir / "jarvis_main.py"}" wake_word"'
    anushka_process = subprocess.Popen(cmd, shell=True, cwd=str(script_dir))
    is_anushka_running = True

    # Monitor if the window is closed
    def monitor():
        global is_anushka_running
        if anushka_process:
            anushka_process.wait()
        is_anushka_running = False
        print("\n💤 Anushka went to sleep. Listening for wake word again...")

    threading.Thread(target=monitor, daemon=True).start()


def listen_for_wake_word():
    """
    Continuously listen in the background for the wake word.
    Uses minimal resources — only processes audio when speech is detected.
    """
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ speech_recognition not installed. Run: pip install speechrecognition")
        sys.exit(1)

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.6

    print("\n╔══════════════════════════════════════════════╗")
    print("║  ✦ ANUSHKA Wake Listener — Active           ║")
    print("║  Say 'Hey Anushka' to wake her up!         ║")
    print("║  Press Ctrl+C to stop.                     ║")
    print("╚══════════════════════════════════════════════╝")
    print("\nListening in background... (minimal CPU usage)")

    consecutive_errors = 0

    while True:
        try:
            with sr.Microphone() as source:
                if consecutive_errors == 0:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen with short timeout to keep it lightweight
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            # Try to recognize speech
            try:
                text = recognizer.recognize_google(audio, language='en-IN').lower().strip()
                print(f"   Heard: '{text}'")

                # Check if any wake phrase was said
                for phrase in WAKE_PHRASES:
                    if phrase in text or text in phrase:
                        launch_anushka()
                        # After launch, wait before listening again
                        time.sleep(5)
                        break

                consecutive_errors = 0

            except sr.UnknownValueError:
                # Normal — couldn't understand audio (silence, noise)
                consecutive_errors = 0
                pass
            except sr.RequestError as e:
                print(f"   ⚠️ Recognition error: {e}")
                consecutive_errors += 1
                time.sleep(2)

        except sr.WaitTimeoutError:
            # Normal — no speech detected in timeout window
            consecutive_errors = 0
            pass
        except OSError:
            print("   ⚠️ Microphone not accessible. Retrying in 5s...")
            time.sleep(5)
            consecutive_errors += 1
        except KeyboardInterrupt:
            print("\n\n💤 Wake listener stopped. Goodbye!")
            break
        except Exception as e:
            print(f"   Error: {e}")
            consecutive_errors += 1
            if consecutive_errors > 10:
                print("   Too many errors. Waiting 30s before retrying...")
                time.sleep(30)
                consecutive_errors = 0
            time.sleep(1)


if __name__ == '__main__':
    listen_for_wake_word()
