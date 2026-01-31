#!/usr/bin/env python3.11

import edge_tts
import pygame
import asyncio
import tempfile
import os
import re
import threading
import queue


class EmotionalVoiceEngine:
    """
    Ultra-realistic emotional voice engine using Microsoft Edge TTS.
    Features natural intonation, enthusiasm, and human-like expression.
    Completely FREE with no API key required!
    """
    
    def __init__(self, voice='en-US-AvaMultilingualNeural'):
        """
        Initialize the emotional voice engine.
        
        Popular female voices (realistic & emotional):
        - 'en-US-AvaMultilingualNeural' - Young, enthusiastic, natural (RECOMMENDED)
        - 'en-US-JennyNeural' - Warm, friendly, expressive
        - 'en-US-AriaNeural' - Professional, clear, engaging
        - 'en-US-SaraNeural' - Energetic, youthful, emotional
        - 'en-GB-SoniaNeural' - British, warm, natural
        - 'en-AU-NatashaNeural' - Australian, friendly, upbeat
        """
        self.voice = voice
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        self.is_speaking = False
        self.stop_requested = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.temp_files = []
        
        print(f"✅ Emotional voice engine initialized ({voice})")
        print("   Ultra-realistic neural voice with natural emotion!")
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Speak with realistic emotion and enthusiasm.
        
        Args:
            text: The text to speak
            async_mode: If True, queue the speech and return immediately
        """
        if not text:
            return
        
        # Remove prosody markers (not needed with Edge TTS)
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
        """Remove prosody markers and clean text."""
        # Remove [[slnc XXX]] markers
        text = re.sub(r'\[\[slnc \d+\]\]', '', text)
        # Remove other bracket markers
        text = re.sub(r'\[\[.*?\]\]', '', text)
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _speak_sync(self, text: str):
        """Speak synchronously with emotion."""
        self.is_speaking = True
        self.stop_requested = False
        
        try:
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            self.temp_files.append(temp_filename)
            
            # Generate speech with Edge TTS (async operation)
            asyncio.run(self._generate_speech(text, temp_filename))
            
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
    
    async def _generate_speech(self, text: str, output_file: str):
        """Generate speech using Edge TTS."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
    
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
    
    def set_voice(self, voice: str):
        """
        Change the voice.
        
        Popular options:
        - 'en-US-AvaMultilingualNeural' - Young, enthusiastic
        - 'en-US-JennyNeural' - Warm, friendly
        - 'en-US-AriaNeural' - Professional, engaging
        - 'en-US-SaraNeural' - Energetic, youthful
        """
        self.voice = voice
        print(f"✅ Voice changed to: {voice}")
    
    def _cleanup_temp_files(self):
        """Clean up old temporary audio files."""
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
    # Test the emotional voice engine
    print("\n🧪 Testing emotional voice with different personalities...\n")
    
    # Test 1: Enthusiastic voice
    engine = EmotionalVoiceEngine(voice='en-US-AvaMultilingualNeural')
    print("1️⃣ Ava (Young & Enthusiastic):")
    engine.speak("Hi! I'm Maya, and I'm super excited to help you today! This voice is way more human!")
    engine.cleanup()
    
    print("\n")
    
    # Test 2: Warm friendly voice
    engine2 = EmotionalVoiceEngine(voice='en-US-JennyNeural')
    print("2️⃣ Jenny (Warm & Friendly):")
    engine2.speak("Hey there! I sound really natural and conversational, don't you think?")
    engine2.cleanup()
    
    print("\n✅ All tests complete! Much more human, right?")
