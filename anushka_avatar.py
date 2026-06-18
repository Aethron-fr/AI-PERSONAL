"""
ANUSHKA AVATAR — Live Graphical Overlay
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import math
import os

class AnushkaAvatar:
    def __init__(self, voice_engine=None):
        self.voice = voice_engine
        self.running = False
        self.pulse_phase = 0.0
        self.is_speaking = False
        
        # We start the avatar in a separate thread so it doesn't block the main GUI loop,
        # but Tkinter doesn't like running in multiple threads.
        # Actually, since the main app runs a Tk() loop, we can just run this as a Toplevel 
        # attached to the main root, but the user wants a "floating overlay".
        # We'll define a setup method that takes the main root.
        
        self.window = None
        self.canvas = None
        self.base_image = None
        self.tk_image = None
        
    def attach_to(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Anushka Live")
        
        # Make borderless and floating
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        
        # Set transparent color (magenta)
        TRANS_COLOR = '#ff00ff'
        self.window.attributes("-transparentcolor", TRANS_COLOR)
        self.window.config(bg=TRANS_COLOR)
        
        # Size and Position (Bottom Right corner)
        self.size = 300
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.window.geometry(f"{self.size}x{self.size}+{sw - self.size - 50}+{sh - self.size - 80}")
        
        self.canvas = tk.Canvas(self.window, width=self.size, height=self.size, bg=TRANS_COLOR, highlightthickness=0)
        self.canvas.pack()
        
        # Load and mask image into a circle
        self._load_avatar()
        
        # Start animation loop
        self.running = True
        self._animate()
        
    def _load_avatar(self):
        img_path = "assets/avatar_idle.png"
        if not os.path.exists(img_path):
            print(f"Avatar image not found at {img_path}")
            return
            
        try:
            # Load and resize
            img = Image.open(img_path).convert("RGBA")
            # Crop to square center
            w, h = img.size
            s = min(w, h)
            left = (w - s) / 2
            top = (h - s) / 2
            img = img.crop((left, top, left + s, top + s))
            img = img.resize((self.size - 40, self.size - 40), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            
            # Apply mask
            circular_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            circular_img.paste(img, (0, 0), mask)
            
            self.base_image = circular_img
            self.tk_image = ImageTk.PhotoImage(self.base_image)
            
            # Draw initial glow ring
            self.glow = self.canvas.create_oval(10, 10, self.size-10, self.size-10, outline="#8b5cf6", width=4)
            # Draw image
            self.img_id = self.canvas.create_image(self.size//2, self.size//2, image=self.tk_image)
            
        except Exception as e:
            print(f"Failed to load avatar: {e}")

    def _animate(self):
        if not self.running or not self.window.winfo_exists():
            return
            
        # Check voice state
        speaking = self.voice.is_speaking() if self.voice else False
        
        if speaking:
            # Fast pulse when talking
            self.pulse_phase += 0.4
            glow_width = 4 + math.sin(self.pulse_phase) * 6
            glow_color = "#ec4899" # Pink when talking
            
            # Slight "bounce" to simulate breathing/talking
            y_offset = math.sin(self.pulse_phase * 2) * 2
            self.canvas.coords(self.img_id, self.size//2, self.size//2 + y_offset)
            
        else:
            # Slow, gentle breath when idle
            self.pulse_phase += 0.05
            glow_width = 4 + math.sin(self.pulse_phase) * 2
            glow_color = "#8b5cf6" # Purple when idle
            
            self.canvas.coords(self.img_id, self.size//2, self.size//2)
            
        self.canvas.itemconfig(self.glow, width=max(1, glow_width), outline=glow_color)
        
        self.window.after(30, self._animate)
        
    def close(self):
        self.running = False
        if self.window:
            self.window.destroy()
