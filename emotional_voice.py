import edge_tts
import pygame
import asyncio
import tempfile
import os
import re
import threading
import queue

class EmotionalVoiceEngine:

    def __init__(self, voice='en-US-AvaMultilingualNeural'):
        
        self.voice = voice

        pygame.mixer.init()
        
        self.is_speaking = False
        self.stop_requested = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.temp_files = []
        
        print(f"✅ Emotional voice engine initialized ({voice})")
        print("   Ultra-realistic neural voice with natural emotion!")
    
    def speak(self, text: str, async_mode: bool = False):
        
        if not text:
            return

        text = self._clean_text(text)
        
        print(f"🗣️  Maya: {text}")
        
        if async_mode:
            self.speech_queue.put(text)
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self._process_queue, daemon=True)
                self.speech_thread.start()
        else:
            self._speak_sync(text)
    
    def _clean_text(self, text: str) -> str:

        text = re.sub(r'\[\[slnc \d+\]\]', '', text)
        
        text = re.sub(r'\[\[.*?\]\]', '', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _speak_sync(self, text: str):
        
        self.is_speaking = True
        self.stop_requested = False
        
        try:
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            self.temp_files.append(temp_filename)

            asyncio.run(self._generate_speech(text, temp_filename))

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
    
    async def _generate_speech(self, text: str, output_file: str):
        
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
    
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
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def set_voice(self, voice: str):
        
        self.voice = voice
        print(f"✅ Voice changed to: {voice}")
    
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
    
    print("\n🧪 Testing emotional voice with different personalities...\n")

    engine = EmotionalVoiceEngine(voice='en-US-AvaMultilingualNeural')
    print("1️⃣ Ava (Young & Enthusiastic):")
    engine.speak("Hi! I'm Maya, and I'm super excited to help you today! This voice is way more human!")
    engine.cleanup()
    
    print("\n")

    engine2 = EmotionalVoiceEngine(voice='en-US-JennyNeural')
    print("2️⃣ Jenny (Warm & Friendly):")
    engine2.speak("Hey there! I sound really natural and conversational, don't you think?")
    engine2.cleanup()
    
    print("\n✅ All tests complete! Much more human, right?")
