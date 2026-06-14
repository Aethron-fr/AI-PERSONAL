#!/usr/bin/env python3
"""
ANUSHKA — Your Personal AI Companion
100% FREE Version — Groq (LLaMA 3) + Microsoft Edge TTS
No OpenAI credits needed!
Run with: python jarvis_main.py [text|wake_word|continuous]
"""

import os
import sys

# Force UTF-8 encoding for Windows terminals to support emojis and symbols
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

import json
import asyncio
import datetime
import threading
import tempfile
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

load_dotenv(override=True)
console = Console()

# ══════════════════════════════════════════════════════════════════
# ANUSHKA VOICE — Microsoft Edge TTS (100% FREE, Neural Quality)
# Sounds like a real human. No API key, no cost, works offline.
# ══════════════════════════════════════════════════════════════════
class AnushkaVoice:
    def __init__(self):
        # Microsoft Edge Neural Voices (completely FREE)
        # en-IN-NeerjaNeural  = Indian English female (warm, natural)
        # en-US-JennyNeural   = American English female (friendly)
        # en-US-AriaNeural    = American English female (expressive)
        # en-GB-SoniaNeural   = British English female (elegant)
        self.voice = os.getenv('ANUSHKA_VOICE_FREE', 'en-IN-NeerjaNeural')
        self.rate  = os.getenv('ANUSHKA_VOICE_RATE', '+5%')
        self.pitch = os.getenv('ANUSHKA_VOICE_PITCH', '+0Hz')
        self._speaking = False
        console.print("[green]Voice engine ready — Microsoft Edge Neural TTS (FREE)[/green]")

    def speak(self, text):
        if not text or not text.strip():
            return
        # Strip markdown symbols so they don't get read aloud
        clean = text.replace('**', '').replace('*', '').replace('`', '').replace('#', '').strip()
        # Trim to reasonable length for voice
        if len(clean) > 400:
            clean = clean[:400] + '...'

        console.print(Panel(
            Text(clean, style="bold white"),
            title="[bold magenta]✦ ANUSHKA[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        ))

        def _speak_thread():
            try:
                tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                tmp_path = tmp.name
                tmp.close()

                # Generate speech using edge-tts
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._generate(clean, tmp_path))
                loop.close()

                # Play audio using Windows Media Player (built-in, no install needed)
                subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-Command',
                     f'$p = New-Object System.Windows.Media.MediaPlayer; '
                     f'Add-Type -AssemblyName PresentationCore; '
                     f'$p.Open([uri]"{tmp_path}"); $p.Play(); '
                     f'Start-Sleep -Milliseconds {max(2000, len(clean) * 55)}; $p.Close()'],
                    capture_output=True
                )
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            except Exception as e:
                console.print(f"[yellow]Voice note: {e}[/yellow]")

        t = threading.Thread(target=_speak_thread, daemon=True)
        t.start()
        t.join(timeout=30)

    async def _generate(self, text, output_path):
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(output_path)

    def speak_async(self, text):
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()


# ══════════════════════════════════════════════════════════════════
# ANUSHKA EARS — Speech Recognition (FREE - Google STT)
# Uses sounddevice to avoid PyAudio/PortAudio build errors on Windows
# ══════════════════════════════════════════════════════════════════
class AnushkaEars:
    def __init__(self):
        try:
            import speech_recognition as sr
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
            self.recognizer = sr.Recognizer()
            self.sr = sr
            self.sd = sd
            self.sf = sf
            self.np = np
            self.temp_wav = str(Path(tempfile.gettempdir()) / "anushka_listen_buffer.wav")
            console.print("[green]Microphone ready (sounddevice).[/green]")
            self.mic_available = True
        except Exception as e:
            console.print(f"[yellow]Mic unavailable: {e}[/yellow]")
            self.mic_available = False

    def listen_for_wake_word(self):
        if not self.mic_available:
            return False
        try:
            # Listen for 4 seconds
            recording = self.sd.rec(int(4.0 * 16000), samplerate=16000, channels=1, dtype='int16')
            self.sd.wait()
            rms = self.np.sqrt(self.np.mean(self.np.square(recording.astype(self.np.float32))))
            if rms < 100:
                return False
            self.sf.write(self.temp_wav, recording, 16000)
            with self.sr.AudioFile(self.temp_wav) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio, language='en-IN').lower()
            return 'anushka' in text
        except:
            return False

    def listen_command(self):
        if not self.mic_available:
            return None
        console.print("[yellow]Listening... (speak for up to 6 seconds)[/yellow]")
        try:
            recording = self.sd.rec(int(6.0 * 16000), samplerate=16000, channels=1, dtype='int16')
            self.sd.wait()
            rms = self.np.sqrt(self.np.mean(self.np.square(recording.astype(self.np.float32))))
            if rms < 100:
                return None
            self.sf.write(self.temp_wav, recording, 16000)
            with self.sr.AudioFile(self.temp_wav) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio, language='en-IN')
            console.print(f"[bold green]You:[/bold green] {text}")
            return text
        except Exception as e:
            if "UnknownValueError" not in str(type(e)):
                console.print(f"[red]Mic error: {e}[/red]")
            return None


# ══════════════════════════════════════════════════════════════════
# ANUSHKA MEMORY — Persistent Storage
# ══════════════════════════════════════════════════════════════════
class AnushkaMemory:
    def __init__(self):
        self.memory_path = Path(os.getenv('ANUSHKA_MEMORY_PATH', './anushka_memory'))
        self.memory_path.mkdir(exist_ok=True)
        self.memories = self._load()

    def _load(self):
        f = self.memory_path / 'core_memory.json'
        return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}

    def _save_to_disk(self):
        f = self.memory_path / 'core_memory.json'
        f.write_text(json.dumps(self.memories, ensure_ascii=False, indent=2), encoding='utf-8')

    def save(self, key, value):
        self.memories[key] = {'value': value, 'timestamp': datetime.datetime.now().isoformat()}
        self._save_to_disk()
        return f"Remembered: {key}"

    def recall(self, key):
        return self.memories.get(key, {}).get('value')

    def get_relevant(self, query):
        query_words = set(query.lower().split())
        hits = []
        for key, data in self.memories.items():
            if query_words & set(key.lower().split()):
                hits.append(f"{key}: {data['value']}")
        return ' | '.join(hits[:5]) if hits else None

    def save_conversation(self, role, content):
        log_file = self.memory_path / 'conversation_log.jsonl'
        entry = {'role': role, 'content': content, 'timestamp': datetime.datetime.now().isoformat()}
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ══════════════════════════════════════════════════════════════════
# ANUSHKA TASK MANAGER
# ══════════════════════════════════════════════════════════════════
class AnushkaTaskManager:
    def __init__(self, memory_path):
        self.task_file = Path(memory_path) / 'tasks.json'
        self.tasks = self._load()

    def _load(self):
        return json.loads(self.task_file.read_text(encoding='utf-8')) if self.task_file.exists() else []

    def _save(self):
        self.task_file.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2), encoding='utf-8')

    def add_task(self, description, priority='normal'):
        task = {'id': len(self.tasks) + 1, 'description': description, 'priority': priority,
                'done': False, 'created': datetime.datetime.now().isoformat()}
        self.tasks.append(task)
        self._save()
        return f"Task #{task['id']} added: {description}"

    def list_tasks(self):
        active = [t for t in self.tasks if not t['done']]
        if not active:
            return "No pending tasks."
        lines = []
        for t in active:
            icon = "🔴" if t['priority'] == 'high' else "🟡"
            lines.append(f"#{t['id']} {icon} {t['description']}")
        return '\n'.join(lines)

    def complete_task(self, task_id):
        for t in self.tasks:
            if t['id'] == int(task_id):
                t['done'] = True
                self._save()
                return f"Task #{task_id} done!"
        return f"Task #{task_id} not found."


# ══════════════════════════════════════════════════════════════════
# ANUSHKA BRAIN — Groq AI (FREE, Super Fast, LLaMA 3.3 70B)
# Get your free API key at: https://console.groq.com
# ══════════════════════════════════════════════════════════════════
class AnushkaBrain:
    def __init__(self, memory: AnushkaMemory):
        from jarvis_brain import ANUSHKA_MASTER_SYSTEM_PROMPT
        self.system_prompt = ANUSHKA_MASTER_SYSTEM_PROMPT
        self.history = []
        self.memory = memory
        self.max_history = 20

        groq_key = os.getenv('GROQ_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')

        self.provider = None

        # Try Groq first (free)
        if groq_key and groq_key != 'your-groq-key-here':
            try:
                from groq import Groq
                self.client = Groq(api_key=groq_key)
                self.model = 'llama-3.3-70b-versatile'
                self.provider = 'groq'
                console.print("[green]Brain: Groq LLaMA 3.3 70B (FREE)[/green]")
            except Exception as e:
                console.print(f"[yellow]Groq error: {e}[/yellow]")

        # Fallback: OpenAI if credits available
        if not self.provider and openai_key and 'your-' not in openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.model = 'gpt-4o'
                self.provider = 'openai'
                console.print("[green]Brain: OpenAI GPT-4o[/green]")
            except Exception as e:
                console.print(f"[yellow]OpenAI error: {e}[/yellow]")

        if not self.provider:
            console.print("[red]No AI provider configured! Add GROQ_API_KEY to .env[/red]")
            console.print("[cyan]Get free key at: https://console.groq.com[/cyan]")

    def think(self, user_input):
        if not self.provider:
            return "I need an AI brain to work! Please add your free Groq API key to the .env file. Get it free at console.groq.com"

        context = self.memory.get_relevant(user_input)
        message = f"[MEMORY: {context}]\n\n{user_input}" if context else user_input
        self.history.append({"role": "user", "content": message})
        self.memory.save_conversation("user", user_input)

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        for _ in range(10): # ReAct Loop: Max 10 steps
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.history
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Hmm, I ran into a small issue: {e}. Check your API key in the .env file."
                self.history.append({"role": "assistant", "content": reply})
                self.memory.save_conversation("anushka", reply)
                return reply

            self.history.append({"role": "assistant", "content": reply})

            # Detect Agentic Tool Call JSON
            start_idx = reply.find('{')
            end_idx = reply.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and '"tool"' in reply[start_idx:end_idx+1]:
                try:
                    call = json.loads(reply[start_idx:end_idx+1])
                    if 'tool' in call:
                        tool_name = call['tool']
                        thought = call.get('thought', 'Analyzing...')
                        console.print(f"[bold yellow]✦ Thinking:[/bold yellow] [dim]{thought}[/dim]")
                        console.print(f"[bold cyan]✦ Action:[/bold cyan] [dim]Running {tool_name}...[/dim]")
                        
                        result = self.execute_tool(call)
                        
                        # Add observation back to the LLM and loop again
                        observation = f"[OBSERVATION]\n{result}"
                        self.history.append({"role": "user", "content": observation})
                        continue
                except json.JSONDecodeError:
                    pass

            # If we didn't loop (no valid tool call found), this is the final answer!
            self.memory.save_conversation("anushka", reply)
            return reply

        final_msg = "I'm sorry, I've had to think about this too much and ran out of time. Let's try something else."
        self.memory.save_conversation("anushka", final_msg)
        return final_msg

    def execute_tool(self, tool_call: dict):
        from jarvis_tools import JarvisTools
        tools = JarvisTools()
        name = tool_call.get('tool')
        params = tool_call.get('parameters', {})
        if hasattr(tools, name):
            try:
                return getattr(tools, name)(**params)
            except Exception as e:
                return f"Tool error '{name}': {e}"
        return f"Tool not found: {name}"


# ══════════════════════════════════════════════════════════════════
# ANUSHKA AGENT — Main Control Loop
# ══════════════════════════════════════════════════════════════════
class AnushkaAgent:
    def __init__(self):
        console.print(Panel.fit(
            "[bold magenta]A N U S H K A[/bold magenta]\n"
            "[dim]Your Personal AI Companion[/dim]\n"
            "[dim]Powered by Groq LLaMA 3 + Microsoft Edge TTS[/dim]\n"
            "[bold green]100% FREE[/bold green]",
            border_style="magenta",
            box=box.DOUBLE_EDGE
        ))

        self.voice = AnushkaVoice()
        self.ears  = AnushkaEars()
        self.memory = AnushkaMemory()
        self.tasks  = AnushkaTaskManager(os.getenv('ANUSHKA_MEMORY_PATH', './anushka_memory'))
        self.brain  = AnushkaBrain(self.memory)
        self.running = True

        greeting = self._get_greeting()
        self.voice.speak(greeting)

    def _get_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            tod = "Good morning"
        elif hour < 17:
            tod = "Good afternoon"
        elif hour < 21:
            tod = "Good evening"
        else:
            tod = "Hey, it's late"

        name = self.memory.recall('user_name')
        n = f", {name}" if name else ""

        provider_info = f" I am running on {self.brain.model}." if self.brain.provider else " I need an API key to think properly."
        return f"{tod}{n}! I am Anushka, your personal AI companion.{provider_info} What can I do for you today?"

    def process(self, command: str):
        if not command or not command.strip():
            return
        cmd_lower = command.lower().strip()

        # Quick built-in commands (no AI needed)
        if cmd_lower.startswith('remember my name is '):
            name = command[len('remember my name is '):].strip()
            self.memory.save('user_name', name)
            self.voice.speak(f"Got it! I will always remember that your name is {name}.")
            return

        if cmd_lower in ['show tasks', 'list tasks', 'my tasks', 'what are my tasks', 'tasks']:
            result = self.tasks.list_tasks()
            console.print(f"\n[bold cyan]Tasks:[/bold cyan]\n{result}")
            self.voice.speak("No pending tasks!" if 'No pending' in result else f"You have {len([t for t in self.tasks.tasks if not t['done']])} pending tasks. Check the screen.")
            return

        if cmd_lower.startswith('add task'):
            desc = command[8:].strip().lstrip(':').strip()
            if desc:
                self.tasks.add_task(desc)
                self.voice.speak(f"Added to your task list: {desc}")
                return

        if cmd_lower == 'help':
            self._show_help()
            return

        # Pass to AI brain (Now fully Agentic and handles its own loops!)
        reply = self.brain.think(command)
        self.voice.speak(reply)

    def run(self, mode: str = 'text'):
        console.print(Panel(
            f"[bold green]ANUSHKA ONLINE[/bold green]\n"
            f"Mode: [yellow]{mode}[/yellow]  |  Brain: [cyan]{self.brain.model if self.brain.provider else 'NOT CONFIGURED'}[/cyan]\n"
            f"[dim]Type 'help' for commands. Type 'exit' to quit.[/dim]",
            border_style="green", box=box.ROUNDED
        ))

        if mode == 'wake_word':
            console.print("[cyan]Say 'Anushka' to wake me up...[/cyan]")
            while self.running:
                if self.ears.listen_for_wake_word():
                    self.voice.speak("Yes? I am here.")
                    cmd = self.ears.listen_command()
                    if cmd:
                        if any(w in cmd.lower() for w in ['goodbye', 'shut down', 'bye anushka']):
                            self.voice.speak("Okay, going to sleep. Call me anytime!")
                            break
                        self.process(cmd)

        elif mode == 'continuous':
            console.print("[cyan]Continuous mode — always listening...[/cyan]")
            while self.running:
                cmd = self.ears.listen_command()
                if cmd:
                    if any(w in cmd.lower() for w in ['goodbye anushka', 'shut down']):
                        self.voice.speak("See you later!")
                        break
                    self.process(cmd)

        else:  # text mode
            console.print("[cyan]Text mode — type your message below.[/cyan]\n")
            while self.running:
                try:
                    console.print("[bold magenta]You >[/bold magenta] ", end="")
                    cmd = input().strip()
                    if not cmd:
                        continue
                    if cmd.lower() in ['exit', 'quit', 'bye', 'goodbye', 'shutdown']:
                        self.voice.speak("Okay, shutting down. I will miss you. Goodbye!")
                        break
                    self.process(cmd)
                except (KeyboardInterrupt, EOFError):
                    self.voice.speak("Bye!")
                    break

    def _show_help(self):
        console.print("""
[bold cyan]ANUSHKA — Commands[/bold cyan]

[bold]Chat:[/bold] Just type anything naturally!
[bold]Memory:[/bold] "remember my name is [name]"
[bold]Tasks:[/bold] "add task: [description]" | "show tasks"
[bold]Files:[/bold] "open VS Code" | "take a screenshot" | "list files in Downloads"
[bold]Web:[/bold] "search Google for [topic]" | "open YouTube"
[bold]System:[/bold] "show system stats" | "what time is it?"
[bold]Exit:[/bold] type 'exit'
""")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else 'text'
    agent = AnushkaAgent()
    agent.run(mode=mode)
