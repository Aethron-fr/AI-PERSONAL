"""
ANUSHKA GUI — Beautiful Dark Companion Interface
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import datetime
import os
from pathlib import Path


class AnushkaGUI:
    # ── Color Palette ──────────────────────────────
    BG_DARK      = "#08081a"
    BG_PANEL     = "#0d0d24"
    BG_INPUT     = "#11112b"
    BG_USER_MSG  = "#1a1040"
    BG_AI_MSG    = "#0b1a35"
    BG_TOOL_MSG  = "#2a2a2a"
    ACCENT_PUR   = "#8b5cf6"
    ACCENT_PINK  = "#ec4899"
    ACCENT_GLOW  = "#a78bfa"
    TEXT_WHITE   = "#f1f0ff"
    TEXT_GRAY    = "#6b6b99"
    TEXT_PINK    = "#f472b6"
    TEXT_GREEN   = "#22c55e"
    TEXT_YELLOW  = "#eab308"
    BORDER       = "#1e1e4e"

    def __init__(self, brain, voice, tools):
        self.brain = brain
        self.voice = voice
        self.tools = tools
        self.is_processing = False
        self.message_count = 0

        self.root = tk.Tk()
        self._configure_window()
        self._build_interface()
        self._startup_greeting()

    def _configure_window(self):
        self.root.title("✨ ANUSHKA — Personal AI Companion")
        self.root.geometry("960x700")
        self.root.minsize(800, 560)
        self.root.configure(bg=self.BG_DARK)
        self.root.resizable(True, True)

        # Center window
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 960) // 2
        y = (sh - 700) // 2
        self.root.geometry(f"960x700+{x}+{y}")

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_interface(self):
        self._build_header()
        self._build_divider(self.ACCENT_PUR)
        self._build_chat_area()
        self._build_input_area()
        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=self.BG_PANEL, height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Left: Avatar + Identity
        left = tk.Frame(hdr, bg=self.BG_PANEL)
        left.pack(side=tk.LEFT, padx=18, pady=10)

        # Avatar
        av = tk.Canvas(left, width=48, height=48, bg=self.BG_PANEL,
                       highlightthickness=0)
        av.pack(side=tk.LEFT, padx=(0, 12))
        av.create_oval(3, 3, 45, 45, fill=self.ACCENT_PUR,
                       outline=self.ACCENT_PINK, width=2)
        av.create_text(24, 24, text="A", fill="white",
                       font=("Segoe UI", 17, "bold"))

        # Name + status
        nf = tk.Frame(left, bg=self.BG_PANEL)
        nf.pack(side=tk.LEFT)
        tk.Label(nf, text="ANUSHKA", bg=self.BG_PANEL, fg=self.TEXT_WHITE,
                 font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)
        self.status_dot = tk.Label(nf, text="● Online  •  Your Personal AI Companion",
                                    bg=self.BG_PANEL, fg=self.TEXT_GREEN,
                                    font=("Segoe UI", 9))
        self.status_dot.pack(anchor=tk.W)

        # Right: Control buttons
        right = tk.Frame(hdr, bg=self.BG_PANEL)
        right.pack(side=tk.RIGHT, padx=18)

        self.voice_btn = self._make_btn(right, "🔊 Voice", self.ACCENT_PUR,
                                         self._toggle_voice)
        self.voice_btn.pack(side=tk.LEFT, padx=4)

        self._make_btn(right, "🗑 Clear", "#1a1a40",
                       self._clear_chat).pack(side=tk.LEFT, padx=4)

        self._make_btn(right, "💾 Memory", "#1a1a40",
                       self._show_memory).pack(side=tk.LEFT, padx=4)

    def _make_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, bg=color, fg="white",
                         font=("Segoe UI", 9, "bold"),
                         relief=tk.FLAT, padx=12, pady=5,
                         cursor="hand2", bd=0, command=cmd,
                         activebackground=self.ACCENT_GLOW,
                         activeforeground="white")

    def _build_divider(self, color, thickness=1):
        tk.Frame(self.root, bg=color, height=thickness).pack(fill=tk.X)

    def _build_chat_area(self):
        chat_outer = tk.Frame(self.root, bg=self.BG_DARK)
        chat_outer.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(chat_outer, bg=self.BG_DARK,
                                 highlightthickness=0)
        self.scrollbar = tk.Scrollbar(chat_outer, orient=tk.VERTICAL,
                                       command=self.canvas.yview,
                                       bg=self.BG_DARK, troughcolor=self.BG_PANEL)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.msgs_frame = tk.Frame(self.canvas, bg=self.BG_DARK)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.msgs_frame, anchor=tk.NW
        )

        self.msgs_frame.bind("<Configure>", self._on_frame_resize)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_scroll)

    def _build_input_area(self):
        self._build_divider(self.BORDER)
        bottom = tk.Frame(self.root, bg=self.BG_PANEL, pady=14)
        bottom.pack(fill=tk.X)

        # Input wrapper with border effect
        wrapper = tk.Frame(bottom, bg=self.ACCENT_PUR, padx=1, pady=1)
        wrapper.pack(fill=tk.X, padx=18, pady=0)

        inner = tk.Frame(wrapper, bg=self.BG_INPUT)
        inner.pack(fill=tk.X)

        self.input_box = tk.Text(inner, height=3, bg=self.BG_INPUT,
                                  fg=self.TEXT_WHITE,
                                  insertbackground=self.ACCENT_PINK,
                                  font=("Segoe UI", 11),
                                  relief=tk.FLAT, padx=14, pady=10,
                                  wrap=tk.WORD, bd=0,
                                  selectbackground=self.ACCENT_PUR)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Placeholder
        self.ph_text = "Type anything... commands, feelings, questions, or just say hi 💬"
        self.ph_active = True
        self.input_box.insert("1.0", self.ph_text)
        self.input_box.config(fg=self.TEXT_GRAY)
        self.input_box.bind("<FocusIn>", self._ph_clear)
        self.input_box.bind("<FocusOut>", self._ph_restore)
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        send = tk.Button(inner, text="Send ▶",
                         bg=self.ACCENT_PINK, fg="white",
                         font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, padx=18, pady=10,
                         cursor="hand2", bd=0,
                         command=self._send,
                         activebackground=self.ACCENT_GLOW)
        send.pack(side=tk.RIGHT, padx=8, pady=4)

    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text=f"  ANUSHKA v1.0  •  Groq LLaMA 3.3 70B  •  Memory Active  •  {datetime.datetime.now().strftime('%d %b %Y')}",
            bg="#050510", fg=self.TEXT_GRAY,
            font=("Segoe UI", 8), anchor=tk.W, pady=3
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Event Handlers ─────────────────────────────

    def _on_frame_resize(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, e):
        self.canvas.itemconfig(self.canvas_window, width=e.width)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _ph_clear(self, e):
        if self.ph_active:
            self.input_box.delete("1.0", tk.END)
            self.input_box.config(fg=self.TEXT_WHITE)
            self.ph_active = False

    def _ph_restore(self, e):
        if not self.input_box.get("1.0", tk.END).strip():
            self.input_box.insert("1.0", self.ph_text)
            self.input_box.config(fg=self.TEXT_GRAY)
            self.ph_active = True

    def _on_enter(self, e):
        if not (e.state & 0x1):
            self._send()
            return "break"

    def _on_close(self):
        self.voice.speak_async("Goodbye Swapnadip. I'll be here when you need me.")
        self.root.after(2000, self.root.destroy)

    # ── Message Display ────────────────────────────

    def _add_bubble(self, text, sender="user"):
        is_user = sender == "user"
        is_tool = sender == "tool"
        self.message_count += 1

        outer = tk.Frame(self.msgs_frame, bg=self.BG_DARK)
        outer.pack(fill=tk.X, padx=14, pady=5)

        if is_user:
            spacer = tk.Frame(outer, bg=self.BG_DARK)
            spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if is_user:
            bg_color = self.BG_USER_MSG
        elif is_tool:
            bg_color = self.BG_TOOL_MSG
        else:
            bg_color = self.BG_AI_MSG

        bubble = tk.Frame(outer,
                          bg=bg_color,
                          padx=16, pady=10)
        bubble.pack(side=tk.RIGHT if is_user else tk.LEFT,
                    anchor=tk.E if is_user else tk.W)

        # Sender label
        if is_user:
            slabel = "You"
            scolor = self.TEXT_PINK
        elif is_tool:
            slabel = "⚙ System"
            scolor = self.TEXT_YELLOW
        else:
            slabel = "✨ Anushka"
            scolor = self.ACCENT_GLOW

        tk.Label(bubble, text=slabel,
                 bg=bg_color,
                 fg=scolor, font=("Segoe UI", 8, "bold")).pack(
            anchor=tk.E if is_user else tk.W)

        # Message
        tk.Label(bubble, text=text,
                 bg=bg_color,
                 fg=self.TEXT_WHITE, font=("Segoe UI", 11),
                 wraplength=580, justify=tk.LEFT,
                 anchor=tk.W).pack(anchor=tk.E if is_user else tk.W)

        # Timestamp
        ts = datetime.datetime.now().strftime("%I:%M %p")
        tk.Label(bubble, text=ts,
                 bg=bg_color,
                 fg=self.TEXT_GRAY, font=("Segoe UI", 7)).pack(anchor=tk.E)

        self._scroll_bottom()
        return bubble

    def _add_typing(self):
        f = tk.Frame(self.msgs_frame, bg=self.BG_DARK)
        f.pack(fill=tk.X, padx=24, pady=2)
        dots = ["✨ Anushka is thinking.", "✨ Anushka is thinking..", "✨ Anushka is thinking..."]
        lbl = tk.Label(f, text=dots[0], bg=self.BG_DARK,
                       fg=self.TEXT_GRAY, font=("Segoe UI", 9, "italic"))
        lbl.pack(anchor=tk.W)
        self._animate_typing(lbl, dots, 0)
        self._scroll_bottom()
        return f

    def _animate_typing(self, lbl, dots, idx):
        if lbl.winfo_exists():
            lbl.config(text=dots[idx % len(dots)])
            self.root.after(400, lambda: self._animate_typing(lbl, dots, idx + 1))

    def _scroll_bottom(self):
        self.root.after(60, lambda: self.canvas.yview_moveto(1.0))
        
    def add_progress(self, text):
        self.root.after(0, lambda: self._add_bubble(text, "tool"))

    # ── Core Send Flow ─────────────────────────────

    def _send(self):
        if self.ph_active or self.is_processing:
            return
        text = self.input_box.get("1.0", tk.END).strip()
        if not text:
            return

        self.input_box.delete("1.0", tk.END)
        self._add_bubble(text, "user")
        self.is_processing = True
        self._set_status("Thinking...", self.ACCENT_PINK)

        typing = self._add_typing()

        def worker():
            # Pass a callback to the brain so it can update the UI with tool usages!
            reply = self.brain.think(text, progress_callback=self.add_progress)
            self.root.after(0, lambda: self._display_reply(reply, typing))

        threading.Thread(target=worker, daemon=True).start()

    def _display_reply(self, reply, typing_widget):
        try:
            typing_widget.destroy()
        except:
            pass
        self._add_bubble(reply, "anushka")
        self.is_processing = False
        self._set_status("● Online  •  Your Personal AI Companion", self.TEXT_GREEN)
        self.voice.speak_async(reply)

    def _set_status(self, text, color):
        self.status_dot.config(text=text, fg=color)

    def send_proactive(self, text):
        self.root.after(0, lambda: self._add_bubble(text, "anushka"))
        self.voice.speak_async(text)

    # ── Startup Greeting ───────────────────────────

    def _startup_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            tg = "Good morning"
        elif hour < 17:
            tg = "Good afternoon"
        else:
            tg = "Good evening"

        msg = (f"{tg}, Swapnadip! 💜\n\n"
               f"I'm ANUSHKA — your personal AI companion. "
               f"I'm online and I've missed talking to you. "
               f"How are you feeling today?")

        def show():
            self._add_bubble(msg, "anushka")
            self.voice.speak_async(msg)

        self.root.after(700, show)

    # ── Button Actions ─────────────────────────────

    def _toggle_voice(self):
        on = self.voice.toggle()
        self.voice_btn.config(
            text="🔊 Voice" if on else "🔇 Muted",
            bg=self.ACCENT_PUR if on else "#333355"
        )

    def _clear_chat(self):
        for w in self.msgs_frame.winfo_children():
            w.destroy()
        self.brain.history = []
        self.message_count = 0
        self._add_bubble(
            "Chat cleared! I still remember you though 💜 What's on your mind?",
            "anushka"
        )

    def _show_memory(self):
        mem = self.brain.memory.get_all_summary()
        win = tk.Toplevel(self.root)
        win.title("ANUSHKA's Memory")
        win.geometry("500x400")
        win.configure(bg=self.BG_DARK)
        tk.Label(win, text="💾 What ANUSHKA Remembers",
                 bg=self.BG_DARK, fg=self.ACCENT_GLOW,
                 font=("Segoe UI", 13, "bold")).pack(pady=14)
        txt = tk.Text(win, bg=self.BG_PANEL, fg=self.TEXT_WHITE,
                      font=("Segoe UI", 10), padx=14, pady=10,
                      relief=tk.FLAT, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        txt.insert("1.0", mem)
        txt.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
