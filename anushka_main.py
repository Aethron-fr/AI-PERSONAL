#!/usr/bin/env python3
"""
ANUSHKA — Master GUI Launcher
Wires together the Brain, Memory, Voice, Tools, and the Tkinter GUI.
"""

import sys

# Force UTF-8 encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def main():
    try:
        from anushka_brain import AnushkaBrain, AnushkaMemory
        from anushka_voice import AnushkaVoice
        from anushka_tools import AnushkaTools
        from anushka_gui import AnushkaGUI
        from anushka_vision import AnushkaVision
        from anushka_chronos import AnushkaChronos
        from anushka_avatar import AnushkaAvatar
    except ImportError as e:
        print(f"Failed to import core modules: {e}")
        print("Please ensure you are in the correct directory.")
        return

    # Initialize components
    memory = AnushkaMemory()
    brain = AnushkaBrain(memory)
    voice = AnushkaVoice()
    tools = AnushkaTools()

    # Start the Biometric Vision thread
    vision = AnushkaVision(brain)

    # Initialize the GUI
    print("Launching ANUSHKA GUI...")
    app = AnushkaGUI(brain=brain, voice=voice, tools=tools)

    # Start the Live Avatar Overlay
    avatar = AnushkaAvatar(voice_engine=voice)
    avatar.attach_to(app.root)

    # Start the Proactive Chronos thread (needs the GUI reference)
    chronos = AnushkaChronos(brain, app)

    # Run the main loop
    app.run()

    # Cleanup when GUI closes
    vision.stop()
    chronos.stop()
    avatar.close()

if __name__ == "__main__":
    main()
