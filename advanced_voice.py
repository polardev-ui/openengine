import pyttsx3
import threading
import queue

class AdvancedVoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            if 'samantha' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
            elif 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 190)
        self.engine.setProperty('volume', 0.95)
        
        self.is_speaking = False
        self.stop_requested = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        
        print(f"✅ Advanced voice engine initialized with {len(voices)} voices")
    
    def speak(self, text: str, async_mode: bool = False):
        if not text:
            return
        
        print(f"🗣️  Maya: {text}")
        
        if async_mode:
            self.speech_queue.put(text)
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self._process_queue, daemon=True)
                self.speech_thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        self.is_speaking = True
        self.stop_requested = False
        
        try:
            print("🔊 Initializing speech...")
            self.engine.say(text)
            print("🔊 Running speech engine...")
            self.engine.runAndWait()
            print("✅ Speech completed")
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_speaking = False
    
    def _process_queue(self):
        while not self.speech_queue.empty():
            if self.stop_requested:
                while not self.speech_queue.empty():
                    self.speech_queue.get()
                break
            
            text = self.speech_queue.get()
            self._speak_sync(text)
    
    def stop(self):
        self.stop_requested = True
        self.is_speaking = False
        try:
            self.engine.stop()
        except Exception:
            pass
    
    def set_rate(self, rate: int):
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        self.engine.setProperty('volume', volume)
    
    def list_voices(self):
        voices = self.engine.getProperty('voices')
        print("\n🎙️ Available voices:")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name} ({voice.id})")
        return voices
