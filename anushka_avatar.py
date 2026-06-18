"""
ANUSHKA AVATAR — Live Graphical Overlay
Transparent circular portrait that floats on your desktop.
Audio-reactive: breathes when idle, pulses pink when speaking.
"""

import tkinter as tk
import threading
import time
import math
import os


class AnushkaAvatar:
    def __init__(self, voice_engine=None):
        self.voice = voice_engine
        self.running = False
        self.pulse_phase = 0.0
        self.window = None
        self.canvas = None
        self.tk_image = None
        self.glow = None
        self.img_id = None
        self.size = 280

    def attach_to(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Anushka")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        TRANS = '#010101'
        self.window.attributes("-transparentcolor", TRANS)
        self.window.config(bg=TRANS)

        # Position: bottom-right corner
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.window.geometry(f"{self.size}x{self.size}+{sw - self.size - 30}+{sh - self.size - 90}")

        self.canvas = tk.Canvas(
            self.window, width=self.size, height=self.size,
            bg=TRANS, highlightthickness=0
        )
        self.canvas.pack()

        # Allow dragging the avatar
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)

        self._load_avatar(TRANS)
        self.running = True
        self._animate()

    def _drag_start(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag_move(self, e):
        x = self.window.winfo_x() + (e.x - self._drag_x)
        y = self.window.winfo_y() + (e.y - self._drag_y)
        self.window.geometry(f"+{x}+{y}")

    def _load_avatar(self, trans_color):
        try:
            from PIL import Image, ImageTk, ImageDraw

            img_path = os.path.join("assets", "avatar_idle.png")
            if not os.path.exists(img_path):
                self._draw_fallback()
                return

            img = Image.open(img_path).convert("RGBA")

            # Crop to centered square
            w, h = img.size
            s = min(w, h)
            img = img.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))

            avatar_size = self.size - 20
            img = img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

            # Circular mask
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

            # Slightly soften edges
            from PIL import ImageFilter
            mask = mask.filter(ImageFilter.GaussianBlur(2))

            circular = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            circular.paste(img, (0, 0), mask)

            self.tk_image = ImageTk.PhotoImage(circular)
            cx = self.size // 2
            cy = self.size // 2

            # Draw glow ring first (behind portrait)
            self.glow = self.canvas.create_oval(6, 6, self.size - 6, self.size - 6,
                                                 outline="#8b5cf6", width=4)
            # Draw portrait
            self.img_id = self.canvas.create_image(cx, cy, image=self.tk_image)

        except Exception as e:
            print(f"Avatar load error: {e}")
            self._draw_fallback()

    def _draw_fallback(self):
        """Draw a simple glowing circle if the image fails to load."""
        cx = cy = self.size // 2
        r = self.size // 2 - 10
        self.glow = self.canvas.create_oval(10, 10, self.size - 10, self.size - 10,
                                             outline="#8b5cf6", width=4)
        self.canvas.create_oval(20, 20, self.size - 20, self.size - 20,
                                fill="#1a0a2e", outline="#8b5cf6")
        self.canvas.create_text(cx, cy, text="A", fill="white",
                                font=("Segoe UI", 48, "bold"))
        self.img_id = None

    def _animate(self):
        if not self.running:
            return
        try:
            if not self.window.winfo_exists():
                return
        except Exception:
            return

        speaking = self.voice.is_speaking() if self.voice else False

        if speaking:
            self.pulse_phase += 0.35
            glow_w = 5 + math.sin(self.pulse_phase) * 6
            color = "#ec4899"  # Pink when talking
            if self.img_id:
                offset = math.sin(self.pulse_phase * 2) * 2
                self.canvas.coords(self.img_id, self.size // 2, self.size // 2 + offset)
        else:
            self.pulse_phase += 0.04
            glow_w = 3 + math.sin(self.pulse_phase) * 2
            color = "#8b5cf6"  # Purple when idle
            if self.img_id:
                self.canvas.coords(self.img_id, self.size // 2, self.size // 2)

        if self.glow:
            self.canvas.itemconfig(self.glow, width=max(1, glow_w), outline=color)

        self.window.after(30, self._animate)

    def close(self):
        self.running = False
        try:
            if self.window:
                self.window.destroy()
        except Exception:
            pass
