"""
ANUSHKA Tools — Every action ANUSHKA can perform
Complete toolkit: system, screen, web, vision, schedule, communication
"""

import os
import subprocess
import platform
import datetime
import json
import webbrowser
import pyperclip
import psutil
from pathlib import Path


class AnushkaTools:
    """All tools available to ANUSHKA. Named AnushkaTools for backward compatibility."""

    # ─── SYSTEM TOOLS ─────────────────────────────────────────────

    def run_command(self, cmd):
        """Run a shell/terminal command and return the output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=60, encoding='utf-8', errors='replace'
            )
            output = result.stdout or result.stderr
            return output.strip() if output else "Command executed with no output."
        except subprocess.TimeoutExpired:
            return "Command timed out after 60 seconds."
        except Exception as e:
            return f"Command error: {e}"

    def open_file(self, path):
        """Open a file or application using the default OS handler."""
        try:
            path = os.path.expanduser(path)
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
            return f"Opened: {path}"
        except Exception as e:
            return f"Could not open: {e}"

    def read_file(self, path):
        """Read and return the text content of a file."""
        try:
            path = os.path.expanduser(path)
            content = Path(path).read_text(encoding='utf-8')
            # Limit to first 3000 chars to avoid context overflow
            return content[:3000] + ("\n...[truncated]" if len(content) > 3000 else "")
        except Exception as e:
            return f"Could not read file: {e}"

    def write_file(self, path, content):
        """Write content to a file, creating it if it doesn't exist."""
        try:
            path = os.path.expanduser(path)
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return f"Written to: {path}"
        except Exception as e:
            return f"Write error: {e}"

    def delete_file(self, path):
        """Delete a file. Always confirm with user before calling this."""
        try:
            path = os.path.expanduser(path)
            p = Path(path)
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
                return f"Deleted directory: {path}"
            else:
                p.unlink()
                return f"Deleted: {path}"
        except Exception as e:
            return f"Delete error: {e}"

    def list_directory(self, path='.'):
        """List files and folders in a directory."""
        try:
            path = os.path.expanduser(path)
            items = sorted(Path(path).iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            output = []
            for item in items[:40]:
                if item.is_dir():
                    output.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = f"{size // 1024}KB" if size > 1024 else f"{size}B"
                    output.append(f"📄 {item.name} ({size_str})")
            if len(list(Path(path).iterdir())) > 40:
                output.append("... and more items")
            return '\n'.join(output)
        except Exception as e:
            return f"Directory error: {e}"

    def get_system_info(self):
        """Return current system stats: CPU, RAM, battery, disk."""
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\' if platform.system() == 'Windows' else '/')
            battery = psutil.sensors_battery()
            info = {
                'cpu_usage': f"{cpu}%",
                'ram_total': f"{ram.total // (1024**3)} GB",
                'ram_used': f"{ram.percent}% ({ram.used // (1024**3)} GB)",
                'ram_free': f"{ram.available // (1024**3)} GB",
                'disk_total': f"{disk.total // (1024**3)} GB",
                'disk_used': f"{disk.percent}%",
                'disk_free': f"{disk.free // (1024**3)} GB",
            }
            if battery:
                info['battery'] = f"{battery.percent}%"
                info['charging'] = "Yes" if battery.power_plugged else "No"
            else:
                info['battery'] = "No battery (desktop)"
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"System info error: {e}"

    def copy_to_clipboard(self, text):
        """Copy text to the system clipboard."""
        try:
            pyperclip.copy(text)
            return "Copied to clipboard."
        except Exception as e:
            return f"Clipboard error: {e}"

    def get_clipboard(self):
        """Get current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception as e:
            return f"Could not get clipboard: {e}"

    # ─── SCREEN TOOLS ─────────────────────────────────────────────

    def take_screenshot(self, save_path=None):
        """Take a screenshot and save it. Returns the file path."""
        try:
            import pyautogui
            img = pyautogui.screenshot()
            path = save_path or f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(path)
            return f"Screenshot saved: {path}"
        except Exception as e:
            return f"Screenshot error: {e}"

    def click_at(self, x, y):
        """Click the mouse at specific screen coordinates."""
        try:
            import pyautogui
            pyautogui.click(int(x), int(y))
            return f"Clicked at ({x}, {y})"
        except Exception as e:
            return f"Click error: {e}"

    def type_text(self, text):
        """Type text using the keyboard at the current cursor position."""
        try:
            import pyautogui
            pyautogui.write(text, interval=0.03)
            return f"Typed: {text}"
        except Exception as e:
            return f"Type error: {e}"

    def press_key(self, key):
        """Press a key or keyboard shortcut. Use + for combos (e.g. ctrl+c)."""
        try:
            import pyautogui
            keys = key.split('+')
            pyautogui.hotkey(*keys)
            return f"Pressed: {key}"
        except Exception as e:
            return f"Key error: {e}"

    def scroll(self, direction='down', clicks=3):
        """Scroll up or down on screen."""
        try:
            import pyautogui
            amount = clicks if direction == 'up' else -clicks
            pyautogui.scroll(amount)
            return f"Scrolled {direction} by {clicks}"
        except Exception as e:
            return f"Scroll error: {e}"

    # ─── WEB TOOLS ────────────────────────────────────────────────

    def web_search(self, query):
        """Open a Google search for the given query in the browser."""
        import urllib.parse
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Opened Google search for: {query}"

    def open_url(self, url):
        """Open a URL in the default browser."""
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return f"Opened: {url}"

    def get_page_content(self, url):
        """Fetch and return the text content of a webpage."""
        import requests
        from bs4 import BeautifulSoup
        try:
            r = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(r.text, 'html.parser')
            # Remove scripts, styles, nav, footers
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            paragraphs = [p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
                         if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30]
            content = ' '.join(paragraphs[:50])
            return content[:4000] if content else "No readable content found."
        except Exception as e:
            return f"Could not fetch page: {e}"

    def search_youtube(self, query):
        """Open YouTube search."""
        import urllib.parse
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Opened YouTube search: {query}"

    def open_wikipedia(self, topic):
        """Open Wikipedia for a topic."""
        import urllib.parse
        url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(topic.replace(' ', '_'))}"
        webbrowser.open(url)
        return f"Opened Wikipedia: {topic}"

    # ─── VISION TOOLS ─────────────────────────────────────────────

    def capture_camera(self, save_path=None):
        """Take a photo using the webcam."""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            time.sleep(0.5)  # Let camera warm up
            ret, frame = cap.read()
            cap.release()
            if ret:
                path = save_path or f"camera_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(path, frame)
                return f"Photo saved: {path}"
            return "Failed to capture from camera."
        except Exception as e:
            return f"Camera error: {e}"

    def analyze_image(self, image_path):
        """Send an image to GPT-4o Vision and get a detailed description."""
        try:
            import base64
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            with open(image_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            ext = Path(image_path).suffix.lower().replace('.', '')
            mime = f"image/{ext if ext in ['jpeg', 'png', 'gif', 'webp'] else 'jpeg'}"
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": "Analyze this image thoroughly. Describe everything you see."}
                ]}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Image analysis error: {e}"

    def read_text_from_image(self, image_path):
        """Extract text from an image using OCR (Tesseract)."""
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip() if text.strip() else "No text found in image."
        except Exception as e:
            return f"OCR failed: {e}"

    def analyze_screen(self):
        """Take a screenshot and analyze what's on screen using AI vision."""
        screenshot_path = self.take_screenshot()
        if 'saved:' in screenshot_path:
            path = screenshot_path.split('saved: ')[1]
            return self.analyze_image(path)
        return "Could not take screenshot for analysis."

    # ─── SCHEDULE & TIME TOOLS ────────────────────────────────────

    def get_current_time(self):
        """Return the current date and time."""
        now = datetime.datetime.now()
        return now.strftime("It's %I:%M %p on %A, %B %d, %Y")

    def set_reminder(self, minutes, message):
        """Set a reminder that fires after N minutes."""
        import threading
        def remind():
            import time
            time.sleep(int(minutes) * 60)
            print(f"\n⏰ ANUSHKA REMINDER: {message}")
            if platform.system() == 'Windows':
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, f"⏰ {message}", "ANUSHKA Reminder", 0x40)
        t = threading.Thread(target=remind, daemon=True)
        t.start()
        return f"Reminder set for {minutes} minute(s) from now: '{message}'"

    def get_weather(self, city="Kolkata"):
        """Fetch current weather for a city using OpenWeatherMap."""
        import requests
        key = os.getenv('WEATHER_API_KEY', '')
        if not key or key == 'your-openweathermap-key-here':
            # Fallback: open weather website
            self.open_url(f"https://wttr.in/{city.replace(' ', '+')}")
            return f"Opened weather for {city} in browser (no API key configured)."
        try:
            r = requests.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": key, "units": "metric"},
                timeout=10
            )
            d = r.json()
            if d.get('cod') == 200:
                temp = d['main']['temp']
                feels_like = d['main']['feels_like']
                desc = d['weather'][0]['description']
                humidity = d['main']['humidity']
                wind = d['wind']['speed']
                return (f"{city}: {temp:.1f}°C (feels like {feels_like:.1f}°C), "
                        f"{desc}, humidity {humidity}%, wind {wind} m/s")
            return f"Could not get weather for {city}: {d.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Weather error: {e}"

    def get_news(self, topic="technology"):
        """Open Google News for a topic."""
        import urllib.parse
        url = f"https://news.google.com/search?q={urllib.parse.quote(topic)}"
        webbrowser.open(url)
        return f"Opened Google News for: {topic}"

    # ─── COMMUNICATION TOOLS ──────────────────────────────────────

    def send_notification(self, message, title="ANUSHKA"):
        """Send a desktop notification."""
        try:
            if platform.system() == 'Windows':
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, f"🤖 {title}", 0x40)
            elif platform.system() == 'Darwin':
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
            else:
                os.system(f'notify-send "{title}" "{message}"')
            return f"Notification sent: {message}"
        except Exception as e:
            return f"Notification error: {e}"

    def open_application(self, app_name):
        """Open a common application by name."""
        apps = {
            'vscode': 'code',
            'vs code': 'code',
            'notepad': 'notepad',
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'firefox': 'firefox',
            'calculator': 'calc',
            'paint': 'mspaint',
            'explorer': 'explorer',
            'file explorer': 'explorer',
            'task manager': 'taskmgr',
            'cmd': 'cmd',
            'powershell': 'powershell',
            'spotify': 'spotify',
            'discord': 'discord',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
        }
        name_lower = app_name.lower()
        cmd = apps.get(name_lower, app_name)
        return self.run_command(f'start {cmd}')

    # ─── HUMAN-LIKE & ADVANCED SYSTEM TOOLS ───────────────────────

    def set_volume(self, level):
        """Set system volume (0 to 100). Windows only."""
        try:
            if platform.system() == 'Windows':
                # Using PowerShell to set volume via NirCmd or built-in audio objects is complex,
                # but we can simulate volume up/down keypresses.
                # A simpler approach using SoundVolumeView or pycaw.
                # Let's use PyAutoGUI to just press VolumeUp/VolumeDown.
                import pyautogui
                # Reset to 0 then go up
                for _ in range(50):
                    pyautogui.press('volumedown')
                target = int(level) // 2
                for _ in range(target):
                    pyautogui.press('volumeup')
                return f"Volume set to approximately {level}%"
            return "Volume control is currently supported on Windows."
        except Exception as e:
            return f"Volume error: {e}"

    def play_media(self, action="playpause"):
        """Control media: playpause, nexttrack, prevtrack."""
        try:
            import pyautogui
            if action in ['play', 'pause', 'playpause']:
                pyautogui.press('playpause')
                return "Toggled play/pause."
            elif action in ['next', 'nexttrack']:
                pyautogui.press('nexttrack')
                return "Playing next track."
            elif action in ['prev', 'prevtrack']:
                pyautogui.press('prevtrack')
                return "Playing previous track."
            return "Unknown media action."
        except Exception as e:
            return f"Media control error: {e}"

    def play_song_on_youtube(self, song_name):
        """Search and instantly play a song on YouTube."""
        try:
            import urllib.parse
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_name)}"
            webbrowser.open(url)
            import time
            time.sleep(3) # Wait for page to load
            import pyautogui
            # Click the first video (approximate center of screen, a bit down)
            # Or better, just press Tab and Enter a few times to select the first video
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('enter')
            return f"Playing {song_name} on YouTube!"
        except Exception as e:
            return f"Could not play song: {e}"

    def lock_screen(self):
        """Lock the computer screen."""
        try:
            if platform.system() == 'Windows':
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return "Screen locked."
            elif platform.system() == 'Darwin':
                os.system('pmset displaysleepnow')
                return "Screen locked."
            return "Lock screen not supported on this OS."
        except Exception as e:
            return f"Lock error: {e}"

    def empty_recycle_bin(self):
        """Empty the Windows Recycle Bin."""
        try:
            if platform.system() == 'Windows':
                import ctypes
                SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
                result = SHEmptyRecycleBin(None, None, 7) # 7 = No confirmation, no progress UI, no sound
                if result == 0:
                    return "Recycle bin emptied."
                return "Recycle bin was already empty or could not be emptied."
            return "Only supported on Windows."
        except Exception as e:
            return f"Recycle bin error: {e}"

    def tell_joke(self):
        """Fetch a random joke."""
        import requests
        try:
            r = requests.get('https://v2.jokeapi.dev/joke/Any?safe-mode')
            data = r.json()
            if data['type'] == 'single':
                return data['joke']
            else:
                return f"{data['setup']} ... {data['delivery']}"
        except Exception:
            return "Why did the AI cross the road? To optimize the path on the other side! (Sorry, my joke API is down)."

    # ─── ULTIMATE PC CONTROL TOOLS ────────────────────────────────

    def minimize_all_windows(self):
        """Minimize all open windows (Show Desktop)."""
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')
            return "Minimized all windows (Show Desktop)."
        except Exception as e:
            return f"Error minimizing windows: {e}"

    def close_current_window(self):
        """Close the currently active window (Alt+F4)."""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            return "Closed current window."
        except Exception as e:
            return f"Error closing window: {e}"

    def switch_window(self):
        """Switch to the previous window (Alt+Tab)."""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            return "Switched window."
        except Exception as e:
            return f"Error switching window: {e}"

    def open_system_settings(self, setting_name=""):
        """Open Windows settings (e.g. 'display', 'bluetooth', 'wifi', or empty for main)."""
        try:
            setting_map = {
                'display': 'ms-settings:display',
                'bluetooth': 'ms-settings:bluetooth',
                'wifi': 'ms-settings:network-wifi',
                'network': 'ms-settings:network-status',
                'sound': 'ms-settings:sound',
                'update': 'ms-settings:windowsupdate',
            }
            target = setting_map.get(setting_name.lower(), 'ms-settings:')
            self.run_command(f'start {target}')
            return f"Opened {setting_name if setting_name else 'system'} settings."
        except Exception as e:
            return f"Error opening settings: {e}"

    def toggle_mute(self):
        """Mute or unmute the system volume."""
        try:
            import pyautogui
            pyautogui.press('volumemute')
            return "Toggled system mute."
        except Exception as e:
            return f"Mute error: {e}"

    def check_internet_speed(self):
        """Check internet download and upload speed."""
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1024 / 1024
            upload = st.upload() / 1024 / 1024
            return f"Download: {download:.2f} Mbps | Upload: {upload:.2f} Mbps"
        except ImportError:
            return "Speedtest-cli module not installed. Run: pip install speedtest-cli"
        except Exception as e:
            return f"Speed test error: {e}"

    def get_ip_address(self):
        """Get the public and local IP address."""
        try:
            import socket
            import requests
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=5).text
            except:
                public_ip = "Unknown"
            return f"Local IP: {local_ip} | Public IP: {public_ip}"
        except Exception as e:
            return f"Error getting IP: {e}"

    def pc_power_action(self, action="sleep"):
        """Control PC power: sleep, restart, shutdown. (Requires confirmation)"""
        try:
            if platform.system() == 'Windows':
                if action == "sleep":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                    return "Going to sleep..."
                elif action == "restart":
                    # os.system("shutdown /r /t 5")
                    return "Restart initiated (currently disabled for safety)."
                elif action == "shutdown":
                    # os.system("shutdown /s /t 5")
                    return "Shutdown initiated (currently disabled for safety)."
            return f"Action {action} not supported or safely disabled."
        except Exception as e:
            return f"Power action error: {e}"


import time
