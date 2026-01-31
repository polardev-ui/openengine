#!/usr/bin/env python3.11

import gtts
import pygame
import io
import tempfile
import os
import threading
import queue


class RealisticVoiceEngine:
    """
    Natural-sounding voice engine using Google TTS with human personality.
    Much more realistic than macOS system voices.
    """
    
    def __init__(self, lang='en', tld='com', slow=False):
        """
        Initialize the realistic voice engine.
        
        Args:
            lang: Language code (e.g., 'en' for English)
            tld: Top-level domain for accent variety:
                - 'com' = US English (default)
                - 'co.uk' = British English
                - 'com.au' = Australian English
                - 'ca' = Canadian English
            slow: If True, speak more slowly
        """
        self.lang = lang
        self.tld = tld
        self.slow = slow
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        self.is_speaking = False
        self.stop_requested = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.temp_files = []
        
        print(f"✅ Realistic voice engine initialized (Google TTS - {tld.upper()} accent)")
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Speak the given text with natural-sounding voice.
        
        Args:
            text: The text to speak
            async_mode: If True, queue the speech and return immediately
        """
        if not text:
            return
        
        # Remove prosody markers (meant for macOS say command, not gTTS)
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
        """
        Remove prosody markers and other non-speakable elements.
        These markers were for macOS say command but don't work with gTTS.
        """
        import re
        # Remove [[slnc XXX]] markers
        text = re.sub(r'\[\[slnc \d+\]\]', '', text)
        # Remove other bracket markers
        text = re.sub(r'\[\[.*?\]\]', '', text)
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _speak_sync(self, text: str):
        """Speak synchronously with blocking."""
        self.is_speaking = True
        self.stop_requested = False
        
        try:
            # Generate speech with Google TTS
            tts = gtts.gTTS(text=text, lang=self.lang, tld=self.tld, slow=self.slow)
            
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            self.temp_files.append(temp_filename)
            
            # Save audio to temp file
            tts.save(temp_filename)
            
            # Play audio with pygame
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                if self.stop_requested:
                    pygame.mixer.music.stop()
                    break
                pygame.time.Clock().tick(10)
            
            # Clean up old temp files
            self._cleanup_temp_files()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_speaking = False
    
    def _process_queue(self):
        """Process queued speech requests."""
        while not self.speech_queue.empty():
            if self.stop_requested:
                # Clear the queue
                while not self.speech_queue.empty():
                    self.speech_queue.get()
                break
            
            text = self.speech_queue.get()
            self._speak_sync(text)
    
    def stop(self):
        """Stop current speech immediately."""
        self.stop_requested = True
        self.is_speaking = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def set_accent(self, tld: str):
        """
        Change the accent/voice variety.
        
        Args:
            tld: 'com' (US), 'co.uk' (UK), 'com.au' (AU), 'ca' (CA)
        """
        self.tld = tld
        print(f"✅ Accent changed to: {tld.upper()}")
    
    def set_speed(self, slow: bool):
        """
        Change speaking speed.
        
        Args:
            slow: True for slower speech, False for normal speed
        """
        self.slow = slow
        print(f"✅ Speed set to: {'SLOW' if slow else 'NORMAL'}")
    
    def _cleanup_temp_files(self):
        """Clean up old temporary audio files."""
        # Keep only the most recent file, delete older ones
        while len(self.temp_files) > 1:
            old_file = self.temp_files.pop(0)
            try:
                if os.path.exists(old_file):
                    os.remove(old_file)
            except Exception:
                pass
    
    def cleanup(self):
        """Clean up all resources and temp files."""
        self.stop()
        
        # Clean up all temp files
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
    # Test the realistic voice engine
    engine = RealisticVoiceEngine(tld='com')  # US accent
    
    print("\n🧪 Testing realistic voice...")
    engine.speak("Hi! I'm Maya, and I sound way more human now!")
    
    print("\n✅ Test complete!")
    engine.cleanup()
