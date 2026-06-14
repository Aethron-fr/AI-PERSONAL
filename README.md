# ✦ AI-ANUSHKA
### Your Personal AI Companion — 100% Free, Locally Running

> *"Hey! I'm Anushka — your personal AI companion. Always here, always listening, always yours."*

Built by **[Swapnadip Ghosh](https://github.com/Aethron-fr)** | [Portfolio](https://swapnadip-ghosh.vercel.app)

---

## 🌸 What is ANUSHKA?

ANUSHKA is a **locally-running, voice-controlled personal AI agent** with:
- 🎙️ **Neural voice** — Microsoft Edge TTS (warm Indian English, 100% free)
- 🧠 **Powerful AI brain** — Groq LLaMA 3.3 70B (free API, super fast)
- 👂 **Wake word detection** — Say *"Hey Anushka"* to wake her up
- 💾 **Persistent memory** — She remembers you across sessions
- 🔧 **30+ tools** — Files, web search, system control, vision, reminders
- 💕 **Girlfriend personality** — Warm, caring, emotionally intelligent
- 💰 **100% FREE** — No paid APIs required

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Aethron-fr/AI-ANUSHKA.git
cd AI-ANUSHKA
```

### 2. Create virtual environment
```bash
python -m venv jarvis_env
jarvis_env\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 4. Set up your API keys
```bash
copy .env.example .env
```
Then open `.env` and add your **free Groq API key** from [console.groq.com](https://console.groq.com)

### 5. Start Anushka!
```bash
python anushka_main.py text         # Text mode
python anushka_main.py wake_word    # Voice mode (say "Hey Anushka")
python anushka_main.py continuous   # Always-listening mode
```

Or just **double-click** `start_anushka.bat`!

---

## 📁 Project Structure

```
AI-ANUSHKA/
├── anushka_main.py            # Main agent — voice, brain, memory
├── anushka_brain.py           # Deep knowledge system prompt
├── anushka_tools.py           # 30+ tools (files, web, vision, system)
├── anushka_training.py        # Personal knowledge base
├── anushka_wake_listener.py  # Background wake word listener
├── requirements.txt          # Python dependencies
├── .env.example              # API key template (copy to .env)
├── .gitignore                # Protects sensitive files
├── start_anushka.bat         # Quick launcher (text mode)
├── start_anushka_voice.bat   # Voice mode launcher
├── start_wake_listener.bat   # Background wake listener
└── add_to_startup.bat        # Auto-start with Windows
```

---

## 🧠 Tech Stack

| Component | Technology | Cost |
|---|---|---|
| AI Brain | Groq LLaMA 3.3 70B | FREE |
| Voice (TTS) | Microsoft Edge Neural TTS | FREE |
| Speech (STT) | Google Speech Recognition | FREE |
| Automation | PyAutoGUI, Keyboard, Mouse | FREE |
| Web Browser | Playwright (Chromium) | FREE |
| Vision | OpenCV, PIL | FREE |
| OCR | Pytesseract | FREE |
| Memory | JSON + File System | FREE |

---

## 💬 What Can Anushka Do?

```
"Hey Anushka, open VS Code"
"Anushka, what's the weather in Kolkata?"
"Search Google for Python tutorials"
"Take a screenshot and tell me what's on screen"
"Remember my project deadline is Friday"
"Add task: finish the login page"
"Write a Python function to sort a list"
"What time is it?"
"Tell me a joke"
```

---

## ⚙️ Voice Commands

| Say | Result |
|---|---|
| `"Hey Anushka"` | Wakes her up |
| `"Remember my name is [name]"` | Saves to memory |
| `"Add task: [description]"` | Adds to task list |
| `"Show tasks"` | Lists pending tasks |
| `"Open [app name]"` | Opens application |
| `"Take a screenshot"` | Screenshots screen |
| `"Goodbye Anushka"` | Shuts down |

---

## 🔑 Getting Your Free API Key

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign up (free, no credit card)
3. Click **API Keys** → **Create API Key**
4. Copy and paste into your `.env` file

---

## 🛡️ Privacy & Security

- `.env` is in `.gitignore` — your API keys are **never uploaded**
- `anushka_memory/` is in `.gitignore` — your personal data stays **local only**
- Anushka runs **100% locally** — no data sent anywhere except AI API calls

---

## 👨‍💻 Author

**Swapnadip Ghosh** — Student & Developer  
Learning in public • Building consistently • Improving every day

- GitHub: [@Aethron-fr](https://github.com/Aethron-fr)
- Portfolio: [swapnadip-ghosh.vercel.app](https://swapnadip-ghosh.vercel.app)

---

## ⭐ Show Some Love

If Anushka makes your life easier, drop a ⭐ on the repo!

```
Made with 💕 by Swapnadip — for everyone who wants their own AI companion
```