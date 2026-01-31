#!/usr/bin/env python3.11

import requests
import json
from typing import Optional
import sys
import pyaudio
import wave
import io
import subprocess
import platform
import threading
import time
import re
import random
import cv2
import numpy as np
from custom_vision import CustomVisionEngine
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from human_voice import HumanVoiceEngine
from emotional_voice import EmotionalVoiceEngine

API_KEY = 'api_76o5jqwkjq45zowrj0r8j2dk72a1c4a8'
API_URL = f'https://api.wsgpolar.me/v1/ai/chat?API={API_KEY}'
MODEL = 'llama-3.1-8b-instant'
MAX_TOKENS = 2048
TEMPERATURE = 0.7


class VisionAssistant:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        self.os_type = platform.system()
        
        self.is_speaking = False
        self.speech_process = None
        self.interrupt_speech = False
        
        self.cap = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.preview_running = False
        self.preview_thread = None
        
        self.vision_engine = CustomVisionEngine()
        self.human_voice = HumanVoiceEngine()
        self.voice_engine = EmotionalVoiceEngine(voice='en-US-AvaMultilingualNeural')  # Young, enthusiastic
        
        print("Vision assistant initialized!")
    
    def start_camera(self):
        if self.cap is not None:
            return True
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Could not open camera")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.preview_running = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
        
        print("✅ Camera started")
        return True
    
    def _preview_loop(self):
        print("📹 Camera preview disabled (GUI compatibility issue)")
        print("   Vision analysis is still active and working")
        
        while self.preview_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                with self.frame_lock:
                    self.current_frame = frame.copy()
                
                time.sleep(0.033)
                
            except Exception as e:
                print(f"Preview error: {e}")
                break
    
    def stop_camera(self):
        self.preview_running = False
        
        if self.preview_thread:
            self.preview_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        cv2.destroyAllWindows()
        print("✅ Camera stopped")
    
    def capture_and_describe(self) -> Optional[str]:
        if self.cap is None or not self.cap.isOpened():
            return "Camera is not available"
        
        with self.frame_lock:
            if self.current_frame is None:
                return "No frame available"
            frame = self.current_frame.copy()
        
        description = self.vision_engine.describe(frame)
        
        if description:
            print(f"👁️  Vision: {description}")
            return description
        else:
            return "I cannot identify what I'm seeing right now"
    
    def listen(self) -> Optional[str]:
        print("\n🎤 Listening... (speak now)")
        
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            frames = []
            silent_chunks = 0
            silence_threshold = 500
            max_silent_chunks = int(self.RATE / self.CHUNK * 1.5)
            recording_started = False
            
            print("🔴 Recording...")
            
            try:
                while True:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    
                    amplitude = sum(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                  for i in range(0, len(data), 2)) / (len(data) / 2)
                    
                    if amplitude > silence_threshold:
                        recording_started = True
                        silent_chunks = 0
                    else:
                        if recording_started:
                            silent_chunks += 1
                            if silent_chunks > max_silent_chunks:
                                print("⏹️  Silence detected, stopping...")
                                break
                    
            except KeyboardInterrupt:
                print("\n⏹️  Recording stopped by user")
            
            stream.stop_stream()
            stream.close()
            
            if not recording_started:
                print("❌ No speech detected")
                return None
            
            return self._recognize_google_speech(frames)
            
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            return None
    
    def _recognize_google_speech(self, frames) -> Optional[str]:
        try:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
            
            wav_data = wav_buffer.getvalue()
            
            url = "https://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-US&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
            headers = {'Content-Type': 'audio/l16; rate=16000'}
            
            response = requests.post(url, data=wav_data, headers=headers, timeout=10)
            
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        result = json.loads(line)
                        if 'result' in result and result['result']:
                            transcript = result['result'][0]['alternative'][0]['transcript']
                            print(f"✅ You said: {transcript}")
                            return transcript
                    except json.JSONDecodeError:
                        continue
            
            print("❌ Could not understand audio")
            return None
            
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def get_ai_response(self, user_message: str, vision_context: Optional[str] = None) -> Optional[str]:
        try:
            system_prompt = 'You are Maya, a friendly young adult AI assistant with vision capabilities. Speak naturally like a real person - use contractions, be enthusiastic and warm. Keep responses brief (1-2 sentences). Avoid formal or robotic language. Never use markdown formatting.'
            
            if vision_context:
                system_prompt += f' Current camera view analysis: {vision_context}. CRITICAL: Only describe what is explicitly listed in the analysis. Do NOT invent, assume, or hallucinate any objects, people, measurements, or details not present in the data. If no objects are detected, simply describe the lighting and colors. Never make up specific measurements or object names.'
            
            messages = [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
            
            payload = {
                'model': MODEL,
                'messages': messages,
                'max_tokens': MAX_TOKENS,
                'temperature': TEMPERATURE
            }
            
            response = requests.post(
                API_URL,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            ai_message = data['choices'][0]['message']['content']
            ai_message = self.human_voice.make_conversational(ai_message, user_message)
            print(f"💬 Maya: {ai_message}")
            return ai_message
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {e}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"❌ Error parsing API response: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def _detect_and_execute_command(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        
        url_patterns = [
            r'(?:show me|open|go to|visit)\s+(?:the\s+)?(?:website\s+)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+)',
            r'(?:show me|open|go to|visit)\s+([a-zA-Z0-9-]+\s+(?:com|org|net|edu|gov))',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, text_lower)
            if match:
                domain = match.group(1).replace(' ', '')
                if not domain.startswith('http'):
                    domain = f'https://{domain}'
                
                if self._open_url(domain):
                    responses = [
                        "Sure thing! All done!",
                        "Opening it now!",
                        "On it! Done!",
                        "You got it!"
                    ]
                    return random.choice(responses)
        
        app_pattern = r'open\s+(?:the\s+)?(?:app\s+)?(.+?)(?:\s+for me|\s+please)?$'
        match = re.search(app_pattern, text_lower)
        if match:
            app_name = match.group(1).strip()
            app_name = self._normalize_app_name(app_name)
            if self._open_application(app_name):
                responses = [
                    "Sure thing! All done!",
                    "Opening it now!",
                    "On it! Done!",
                    "You got it!",
                    "All set!"
                ]
                return random.choice(responses)
        
        return None
    
    def _normalize_app_name(self, app_name: str) -> str:
        app_mapping = {
            'messages': 'Messages',
            'message': 'Messages',
            'text': 'Messages',
            'imessage': 'Messages',
            'safari': 'Safari',
            'browser': 'Safari',
            'chrome': 'Google Chrome',
            'mail': 'Mail',
            'email': 'Mail',
            'calendar': 'Calendar',
            'notes': 'Notes',
            'note': 'Notes',
            'music': 'Music',
            'spotify': 'Spotify',
            'finder': 'Finder',
            'terminal': 'Terminal',
            'settings': 'System Settings',
            'preferences': 'System Settings',
            'photos': 'Photos',
            'photo': 'Photos',
            'facetime': 'FaceTime',
            'calculator': 'Calculator',
            'calc': 'Calculator',
            'maps': 'Maps',
            'map': 'Maps'
        }
        
        normalized = app_mapping.get(app_name.lower(), app_name)
        return normalized
    
    def _open_url(self, url: str) -> bool:
        try:
            if self.os_type == 'Darwin':
                applescript = f'''
                tell application "Safari"
                    activate
                    open location "{url}"
                end tell
                '''
                subprocess.run(['osascript', '-e', applescript], check=True)
            else:
                subprocess.run(['xdg-open', url], check=True)
            return True
        except Exception as e:
            print(f"❌ Error opening URL: {e}")
            return False
    
    def _open_application(self, app_name: str) -> bool:
        try:
            if self.os_type == 'Darwin':
                subprocess.run(['open', '-a', app_name], check=True)
            else:
                subprocess.run([app_name], check=True)
            return True
        except Exception as e:
            print(f"❌ Error opening application: {e}")
            return False
    
    def speak(self, text: str):
        if not text:
            return
        
        self.is_speaking = True
        self.interrupt_speech = False
        
        try:
            print("🔊 Speaking...")
            self.voice_engine.speak(text)
        except Exception as e:
            print(f"❌ Error during text-to-speech: {e}")
            print(f"💬 Maya: {text}")
        finally:
            self.is_speaking = False
    
    def run(self):
        print("\n" + "="*60)
        print("👁️  OPENENGINE - AI VISION ASSISTANT")
        print("="*60)
        print("\nBuilt by OpenEngine")
        print("\nCommands:")
        print("  - Say 'exit', 'quit', or 'stop' to end the conversation")
        print("  - Say 'what do you see' for vision analysis")
        print("  - Say 'show me [website]' or 'open [app]' for computer control")
        print("  - Just speak naturally to chat with Maya")
        print("  - Recording auto-stops after 1.5 seconds of silence")
        print("\n" + "="*60 + "\n")
        
        if not self.start_camera():
            print("❌ Failed to start camera. Exiting.")
            return
        
        time.sleep(1)
        
        self.speak("Hi! I'm Maya, one of the many models available from OpenEngine, but I can now see you. How may I help you?")
        
        while True:
            if self.is_speaking:
                interrupt_thread = threading.Thread(target=self._check_for_interrupt)
                interrupt_thread.daemon = True
                interrupt_thread.start()
            
            user_text = self.listen()
            
            if user_text is None:
                continue
            
            if self.is_speaking:
                self.stop_speaking()
            
            if user_text.lower() in ['exit', 'quit', 'stop', 'goodbye', 'bye']:
                goodbye_message = "Goodbye!"
                print(f"💬 Maya: {goodbye_message}")
                self.speak(goodbye_message)
                break
            
            command_result = self._detect_and_execute_command(user_text)
            if command_result:
                self.speak(command_result)
                continue
            
            vision_context = None
            if any(word in user_text.lower() for word in ['see', 'look', 'show', 'what', 'this', 'that', 'there']):
                vision_context = self.capture_and_describe()
            
            ai_response = self.get_ai_response(user_text, vision_context)
            
            if ai_response is None:
                error_message = "Sorry, something went wrong. Try again?"
                self.speak(error_message)
                continue
            
            self.speak(ai_response)
        
        self.stop_camera()
    
    def _check_for_interrupt(self):
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            consecutive_speech = 0
            
            while self.is_speaking:
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    amplitude = sum(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                  for i in range(0, len(data), 2)) / (len(data) / 2)
                    
                    if amplitude > 600:
                        consecutive_speech += 1
                        if consecutive_speech >= 2:
                            print("\n🛑 Interruption detected - stopping...")
                            self.stop_speaking()
                            break
                    else:
                        consecutive_speech = 0
                    
                    time.sleep(0.05)
                except Exception:
                    break
            
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
    
    def stop_speaking(self):
        if self.is_speaking:
            self.interrupt_speech = True
            self.voice_engine.stop()
            print("\n⏹️  Speech interrupted")
    
    def cleanup(self):
        self.stop_speaking()
        self.voice_engine.cleanup()
        self.stop_camera()
        self.audio.terminate()


def main():
    assistant = None
    try:
        assistant = VisionAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if assistant:
            assistant.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()
