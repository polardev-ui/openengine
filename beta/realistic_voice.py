import edge_tts
import pygame
import asyncio
import tempfile
import os
import re
import threading
import queue

class RealisticVoiceEngine:

    def __init__(self, voice='en-US-AriaNeural', style='chat', speed=1.05, pitch='+0Hz'):
        
        self.voice = voice
        self.style = style
        self.speed = speed
        self.pitch = pitch

        pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)
        
        print(f"🎤 Initializing Realistic Voice Engine")
        print(f"   Voice: {voice}")
        print(f"   Style: {style}")
        print(f"   Speed: {speed}x")
        print(f"✅ Ready! Ultra-realistic conversational voice activated")
        
        self.is_speaking = False
        self.stop_requested = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.temp_files = []
    
    def speak(self, text: str, async_mode: bool = False, style: str = None):
        
        if not text:
            return

        text = self._clean_text(text)
        
        print(f"🗣️  Maya: {text}")
        
        if async_mode:
            self.speech_queue.put((text, style))
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self._process_queue, daemon=True)
                self.speech_thread.start()
        else:
            self._speak_sync(text, style)
    
    def _clean_text(self, text: str) -> str:

        text = re.sub(r'\[\[.*?\]\]', '', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _speak_sync(self, text: str, style_override: str = None):
        
        self.is_speaking = True
        self.stop_requested = False
        
        try:
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            self.temp_files.append(temp_filename)

            asyncio.run(self._generate_speech(text, temp_filename, style_override))

            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self.stop_requested:
                    pygame.mixer.music.stop()
                    break
                pygame.time.Clock().tick(10)

            self._cleanup_temp_files()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_speaking = False
    
    async def _generate_speech(self, text: str, output_file: str, style_override: str = None):

        current_style = style_override if style_override else self.style

        ssml_text = self._create_ssml(text, current_style)

        communicate = edge_tts.Communicate(ssml_text, self.voice)
        await communicate.save(output_file)
    
    def _create_ssml(self, text: str, style: str) -> str:

        rate = f"+{int((self.speed - 1.0) * 100)}%" if self.speed > 1.0 else f"{int((self.speed - 1.0) * 100)}%"

        if 'Aria' in self.voice:
            ssml = f
        else:
            
            ssml = f
        
        return ssml
    
    def _process_queue(self):
        
        while not self.speech_queue.empty():
            if self.stop_requested:
                
                while not self.speech_queue.empty():
                    self.speech_queue.get()
                break
            
            text, style = self.speech_queue.get()
            self._speak_sync(text, style)
    
    def stop(self):
        
        self.stop_requested = True
        self.is_speaking = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def set_style(self, style: str):
        
        self.style = style
        print(f"✅ Style changed to: {style}")
    
    def set_speed(self, speed: float):
        
        self.speed = max(0.5, min(2.0, speed))
        print(f"✅ Speed set to: {self.speed}x")
    
    def set_pitch(self, pitch: str):
        
        self.pitch = pitch
        print(f"✅ Pitch set to: {pitch}")
    
    def _cleanup_temp_files(self):
        
        while len(self.temp_files) > 1:
            old_file = self.temp_files.pop(0)
            try:
                if os.path.exists(old_file):
                    os.remove(old_file)
            except Exception:
                pass
    
    def cleanup(self):
        
        self.stop()
        
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        
        self.temp_files.clear()
        
        try:
            pygame.mixer.quit()
        except Exception:
            pass

if __name__ == "__main__":
    print("\n🧪 Testing Enhanced Realistic Voice Engine (Sesame AI quality)...\n")

    engine = RealisticVoiceEngine(voice='en-US-AriaNeural', style='chat', speed=1.05)
    
    print("1️⃣ Testing casual chat style:")
    engine.speak("Hey there! I'm Maya, your AI assistant. I'm using the most advanced neural voice available, and I think you'll love how natural I sound!")
    
    print("\n2️⃣ Testing cheerful style:")
    engine.speak("This is amazing! I can express different emotions and speaking styles. It makes conversations feel so much more real and engaging!", style='cheerful')
    
    print("\n3️⃣ Testing friendly style:")
    engine.speak("I'm here to help you with whatever you need. Just ask me anything, and I'll do my best to assist you in a friendly and helpful way.", style='friendly')
    
    print("\n✅ Test complete! Notice the natural, conversational quality!")
    
    engine.cleanup()
