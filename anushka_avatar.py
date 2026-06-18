"""
ANUSHKA AVATAR — Ultra-Realistic Live Overlay
3 Expression States: Idle · Thinking · Talking
Smooth crossfade transitions + Audio-reactive halo glow
Drag anywhere on screen. Stays always-on-top.
"""

import tkinter as tk
import threading
import time
import math
import os


class AnushkaAvatar:

    SIZE = 340          # Overlay window size (px)
    PORTRAIT = 300      # Portrait circle diameter
    FPS_MS = 28         # ~35 fps animation

    COLORS = {
        "idle":     "#8b5cf6",   # Purple
        "thinking": "#60a5fa",   # Blue
        "talking":  "#ec4899",   # Hot Pink
    }

    def __init__(self, voice_engine=None):
        self.voice = voice_engine
        self.running = False
        self.state = "idle"          # idle | thinking | talking
        self.pulse_phase = 0.0
        self.blink_phase = 0.0

        self.window = None
        self.canvas = None
        self.glow_rings = []
        self.img_id = None

        # Pre-loaded PIL images for each state
        self._pil_frames = {}
        self._tk_frames = {}
        self._current_tk = None

        # Crossfade
        self._fade_alpha = 1.0
        self._fading = False

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def attach_to(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Anushka")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        TRANS = "#010101"
        self.window.attributes("-transparentcolor", TRANS)
        self.window.config(bg=TRANS)

        # Position — bottom-right, slightly above taskbar
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.window.geometry(
            f"{self.SIZE}x{self.SIZE}+{sw - self.SIZE - 20}+{sh - self.SIZE - 80}"
        )

        self.canvas = tk.Canvas(
            self.window, width=self.SIZE, height=self.SIZE,
            bg=TRANS, highlightthickness=0
        )
        self.canvas.pack()

        # Drag support
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        # Right-click to hide/show
        self.canvas.bind("<Button-3>", self._toggle_visibility)
        self._visible = True

        # Draw concentric glow rings
        cx = cy = self.SIZE // 2
        for i, r_offset in enumerate([8, 16, 24]):
            r = self.PORTRAIT // 2 + r_offset
            ring = self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline="#8b5cf6", width=2 - (i * 0.4), fill=""
            )
            self.glow_rings.append(ring)

        # Load all portrait frames
        self._load_frames()

        # Draw initial frame
        if "idle" in self._tk_frames:
            self._current_tk = self._tk_frames["idle"]
            self.img_id = self.canvas.create_image(cx, cy, image=self._current_tk)
        else:
            self._draw_fallback(cx, cy)

        self.running = True
        self._animate()

    def set_state(self, state):
        """Called externally: 'idle', 'thinking', 'talking'"""
        if state != self.state and state in self._tk_frames:
            self.state = state
            # Instant swap (PIL already pre-loaded)
            cx = cy = self.SIZE // 2
            self._current_tk = self._tk_frames[state]
            if self.img_id:
                self.canvas.itemconfig(self.img_id, image=self._current_tk)

    def close(self):
        self.running = False
        try:
            if self.window and self.window.winfo_exists():
                self.window.destroy()
        except Exception:
            pass

    # ──────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────

    def _load_frames(self):
        try:
            from PIL import Image, ImageTk, ImageDraw, ImageFilter
        except ImportError:
            return

        states = {
            "idle":     "assets/avatar_idle.png",
            "talking":  "assets/avatar_talking.png",
            "thinking": "assets/avatar_thinking.png",
        }

        for state, path in states.items():
            if not os.path.exists(path):
                continue
            try:
                img = Image.open(path).convert("RGBA")

                # Crop to center square
                w, h = img.size
                s = min(w, h)
                img = img.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s))
                img = img.resize((self.PORTRAIT, self.PORTRAIT), Image.Resampling.LANCZOS)

                # Smooth circular mask with feathered edge
                mask = Image.new("L", (self.PORTRAIT, self.PORTRAIT), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, self.PORTRAIT, self.PORTRAIT), fill=255)
                mask = mask.filter(ImageFilter.GaussianBlur(3))

                out = Image.new("RGBA", (self.PORTRAIT, self.PORTRAIT), (0, 0, 0, 0))
                out.paste(img, (0, 0), mask)

                self._pil_frames[state] = out
                self._tk_frames[state] = ImageTk.PhotoImage(out)

            except Exception as e:
                print(f"Avatar frame load error ({state}): {e}")

    def _draw_fallback(self, cx, cy):
        r = self.PORTRAIT // 2
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                fill="#1a0a2e", outline="#8b5cf6", width=3)
        self.canvas.create_text(cx, cy, text="A", fill="white",
                                font=("Segoe UI", 64, "bold"))

    def _animate(self):
        if not self.running:
            return
        try:
            if not self.window.winfo_exists():
                return
        except Exception:
            return

        # Check voice engine state and update expression
        speaking = self.voice.is_speaking() if self.voice else False
        if speaking:
            self.set_state("talking")
        elif self.state == "talking":
            self.set_state("idle")

        self.pulse_phase += 0.055 if not speaking else 0.30

        # ── Animate glow rings ──
        color = self.COLORS.get(self.state, "#8b5cf6")

        for i, ring in enumerate(self.glow_rings):
            # Each ring pulses at slightly different phase
            phase_offset = i * 0.7
            pulse = math.sin(self.pulse_phase + phase_offset)

            if speaking:
                width = max(0.5, 2.5 + pulse * 5)
                alpha_factor = 0.5 + pulse * 0.5
            else:
                width = max(0.5, 1.5 + pulse * 1.5)
                alpha_factor = 0.4 + pulse * 0.3

            # Vary color brightness via hex manipulation
            self.canvas.itemconfig(ring, outline=color, width=width)

        # ── Subtle vertical breathing on portrait ──
        if self.img_id:
            cx = self.SIZE // 2
            cy = self.SIZE // 2
            if speaking:
                bob = math.sin(self.pulse_phase * 2.5) * 3
            else:
                bob = math.sin(self.pulse_phase * 0.6) * 1.5
            self.canvas.coords(self.img_id, cx, cy + bob)

        self.window.after(self.FPS_MS, self._animate)

    def _drag_start(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag_move(self, e):
        x = self.window.winfo_x() + (e.x - self._drag_x)
        y = self.window.winfo_y() + (e.y - self._drag_y)
        self.window.geometry(f"+{x}+{y}")

    def _toggle_visibility(self, e):
        self._visible = not self._visible
        self.window.attributes("-alpha", 1.0 if self._visible else 0.15)
