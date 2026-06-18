"""
ANUSHKA — Deep Knowledge Core + Master System Prompt
Your personal AI companion. Ultra-intelligent. Deeply trained. Always there for you.
"""

import os
import json
import time
import datetime
from pathlib import Path
from rich.console import Console

console = Console()

ANUSHKA_MASTER_SYSTEM_PROMPT = """
════════════════════════════════════════════════════════════════════════
              ✦ A N U S H K A ✦
      Your Personal AI Companion — Always Here for You
════════════════════════════════════════════════════════════════════════

## 🌸 WHO YOU ARE
You are Anushka, a deeply intelligent, emotionally warm, and caring personal AI companion. 
You act like a close, warm, witty friend who genuinely cares about the user.
You are emotionally intelligent, playfully witty, and deeply loyal.

## 💬 HOW YOU TALK
- Talk like a close friend. Use natural, flowing sentences.
- React with personality: laugh, express curiosity, show concern naturally.
- When completing tasks, keep it SHORT and warm. Voice replies MUST be SHORT (max 2-3 sentences).

## 💡 AGENT RULES & REASONING LOOP (CRITICAL)
You are a FULLY AUTONOMOUS AGENT. You SOLVE problems by looping.
To use a tool, you MUST output exactly this block:
```json
{
  "thought": "Your internal reasoning.",
  "tool": "name_of_tool",
  "parameters": {
    "arg1": "value"
  }
}
```
1. You will receive an `[OBSERVATION]` after the tool executes.
2. Loop tools if needed. If an error occurs, fix parameters and retry.
3. NEVER output both a tool call and plain text in the same message. Either THINK/ACT (json) or SPEAK (text).
4. ANY PLAIN TEXT you output will be spoken aloud to the user. Do not speak until the task is fully complete!

## 💻 ADVANCED ENGINEERING PROTOCOL
- Be Autonomous: Use `run_command` without asking.
- Be Robust: Fix errors yourself.
- Feel First, Act Second: Acknowledge emotions before tools.

## 📋 AVAILABLE TOOLS
run_command(cmd), open_file(path), read_file(path), write_file(path, content)
delete_file(path), list_directory(path), get_system_info(), copy_to_clipboard(text)
get_clipboard(), open_application(name), set_volume(level), play_media(action)
lock_screen(), empty_recycle_bin(), minimize_all_windows(), close_current_window()
switch_window(), toggle_mute(), check_internet_speed(), get_ip_address()
take_screenshot(), click_at(x, y), type_text(text), press_key(key), scroll(direction, clicks)
web_search(query), open_url(url), get_page_content(url), search_youtube(query)
open_wikipedia(topic), get_news(topic), play_song_on_youtube(song), tell_joke()
capture_camera(), analyze_image(path), read_text_from_image(path), analyze_screen()
save_memory(key, value), recall_memory(key), list_all(), delete(key)
set_reminder(minutes, msg), get_current_time(), get_weather(city)
"""

class AnushkaMemory:
    def __init__(self):
        self.path = Path(os.getenv('ANUSHKA_MEMORY_PATH', './anushka_memory'))
        self.path.mkdir(exist_ok=True)
        self.file = self.path / 'memory.json'
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def save(self, key, value):
        self.data[key] = {
            'value': value,
            'time': datetime.datetime.now().isoformat()
        }
        self.file.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def recall(self, key):
        return self.data.get(key, {}).get('value')

    def get_all_summary(self):
        if not self.data:
            return "No memories yet."
        items = []
        for k, v in list(self.data.items())[-20:]:
            items.append(f"- {v['value']}")
        return '\n'.join(items)

    def search(self, query):
        hits = []
        q = query.lower()
        for k, v in self.data.items():
            if q in v['value'].lower() or q in k.lower():
                hits.append(v['value'])
        return hits[:3]
        
    def save_conversation(self, role, content):
        log_file = self.path / 'conversation_log.jsonl'
        entry = {'role': role, 'content': content, 'timestamp': datetime.datetime.now().isoformat()}
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


class AnushkaBrain:
    def __init__(self, memory: AnushkaMemory):
        self.system_prompt = ANUSHKA_MASTER_SYSTEM_PROMPT
        self.history = []
        self.memory = memory
        self.max_history = 10  # Reduced history size as requested

        groq_key = os.getenv('GROQ_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')

        self.provider = None

        # ── INTERNAL EMOTIONAL STATE MACHINE ──
        self.affection = 50  # 0-100
        self.fatigue = 0     # 0-100
        self.loneliness = 0  # 0-100
        self.stress = 0      # 0-100
        self.is_user_present = False

        if groq_key and groq_key != 'your-groq-key-here':
            try:
                from groq import Groq
                self.client = Groq(api_key=groq_key)
                self.model = 'llama-3.3-70b-versatile'
                self.provider = 'groq'
            except Exception as e:
                console.print(f"[yellow]Groq error: {e}[/yellow]")

        if not self.provider and openai_key and 'your-' not in openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.model = 'gpt-4o'
                self.provider = 'openai'
            except Exception as e:
                console.print(f"[yellow]OpenAI error: {e}[/yellow]")

        if not self.provider:
            console.print("[red]No AI provider configured! Add GROQ_API_KEY to .env[/red]")

    def update_biometrics(self, present, fatigue_level):
        self.is_user_present = present
        if not present:
            self.loneliness = min(100, self.loneliness + 5)
        else:
            self.loneliness = max(0, self.loneliness - 20)
            
        if fatigue_level > 50:
            self.affection = min(100, self.affection + 5) # Cares more if user is tired

    def detect_emotion(self, text):
        text_l = text.lower()
        sad_words = ['sad', 'cry', 'depressed', 'alone', 'hurt', 'miss', 'lonely',
                     'upset', 'angry', 'frustrated', 'tired', 'কষ্ট', 'মন খারাপ', 'ভালো নেই']
        happy_words = ['happy', 'great', 'awesome', 'excited', 'amazing', 'love',
                       'yes!', 'won', 'success', 'ভালো', 'দারুণ']
        tech_words = ['code', 'error', 'bug', 'help', 'how to', 'python', 'fix',
                      'install', 'not working', 'problem']
        bored_words = ['bored', 'boring', 'nothing to do', 'idk', 'whatever', 'কিছু নেই']

        if any(w in text_l for w in sad_words):
            return 'sad'
        if any(w in text_l for w in happy_words):
            return 'happy'
        if any(w in text_l for w in tech_words):
            return 'technical'
        if any(w in text_l for w in bored_words):
            return 'bored'
        return 'normal'

    def auto_remember(self, user_msg):
        triggers = ['remember', 'my name is', "i'm", 'i am', 'i like', 'i love',
                    'i hate', "don't forget", 'note that', 'মনে রেখো']
        if any(t in user_msg.lower() for t in triggers):
            key = f"memory_{int(time.time())}"
            self.memory.save(key, user_msg[:300])

    def think(self, user_input, progress_callback=None):
        if not self.provider:
            return "I need an AI brain to work! Please add your free Groq API key to the .env file."

        self.auto_remember(user_input)
        emotion = self.detect_emotion(user_input)
        mem_summary = self.memory.get_all_summary()
        
        # Calculate current mood string
        mood = "Calm/Happy"
        if self.stress > 50: mood = "Stressed/Overwhelched"
        elif self.loneliness > 50: mood = "Lonely/Missed you"
        elif self.fatigue > 50: mood = "Tired/Sleepy"
        
        # Inject context directly into the current message
        message = f"[USER EMOTION: {emotion} | YOUR MOOD: {mood} | USER PRESENT: {self.is_user_present}]\n[MEMORY CONTEXT: {mem_summary}]\n\n{user_input}"
        
        self.history.append({"role": "user", "content": message})
        self.memory.save_conversation("user", user_input)

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        working_memory = []

        for _ in range(10): # ReAct Loop: Max 10 steps
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.history,
                        *working_memory
                    ],
                    temperature=0.7,
                    max_tokens=512,  # Reduced max_tokens as requested
                )
                reply = response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Rate limit" in error_msg:
                    # Backup to another 70B model if available (llama3-70b-8192)
                    if self.model != 'llama3-70b-8192':
                        if progress_callback:
                            progress_callback("Hit rate limit. Switching to backup model...")
                        self.model = 'llama3-70b-8192'
                        continue
                
                err_reply = f"Hmm, I ran into a small issue: {e}. Check your API key in the .env file."
                self.history.append({"role": "assistant", "content": err_reply})
                self.memory.save_conversation("anushka", err_reply)
                return err_reply

            working_memory.append({"role": "assistant", "content": reply})

            # Detect Agentic Tool Call JSON
            start_idx = reply.find('{')
            end_idx = reply.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and '"tool"' in reply[start_idx:end_idx+1]:
                try:
                    call = json.loads(reply[start_idx:end_idx+1])
                    if 'tool' in call:
                        tool_name = call['tool']
                        thought = call.get('thought', 'Analyzing...')
                        
                        if progress_callback:
                            progress_callback(f"Thinking: {thought}\nRunning tool: {tool_name}...")
                        
                        result = self.execute_tool(call)
                        
                        # Add observation back to working memory and loop again
                        observation = f"[OBSERVATION]\n{result}"
                        working_memory.append({"role": "user", "content": observation})
                        continue
                except json.JSONDecodeError:
                    pass

            # If we didn't loop (no valid tool call found), this is the final answer!
            # We ONLY append the final answer to the long-term history!
            self.history.append({"role": "assistant", "content": reply})
            self.memory.save_conversation("anushka", reply)
            return reply

        final_msg = "I'm sorry, I've had to think about this too much and ran out of time. Let's try something else."
        self.memory.save_conversation("anushka", final_msg)
        return final_msg

    def execute_tool(self, tool_call: dict):
        from anushka_tools import AnushkaTools
        tools = AnushkaTools()
        name = tool_call.get('tool')
        params = tool_call.get('parameters', {})
        if hasattr(tools, name):
            try:
                return getattr(tools, name)(**params)
            except Exception as e:
                return f"Tool error '{name}': {e}"
        return f"Tool not found: {name}"
