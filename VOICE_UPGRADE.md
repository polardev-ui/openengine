# Voice Engine Upgrade - gTTS Implementation

## What Changed

### Before (pyttsx3)
- Used macOS system voices (Samantha, etc.)
- Same robotic quality as `say` command
- 143 voices but all sound mechanical
- Offline, but poor quality

### After (Google TTS)
- **Realistic neural voice synthesis**
- Natural human-like intonation and rhythm
- Much more expressive and pleasant to listen to
- Still completely FREE
- Requires brief internet connection to generate speech (then cached)

## Voice Quality Comparison

| Feature | pyttsx3 (Old) | gTTS (New) |
|---------|---------------|------------|
| **Sound Quality** | Robotic, mechanical | Natural, human-like |
| **Intonation** | Flat, monotone | Dynamic, expressive |
| **Pronunciation** | Often poor | Excellent |
| **Speed Control** | Yes | Yes (slow mode) |
| **Offline** | 100% | Needs internet for generation |
| **Accents** | Limited | US, UK, AU, CA, and more |

## How It Works

1. Text is sent to Google TTS API (free, no key needed)
2. Returns high-quality MP3 audio
3. Saved to temporary file
4. Played with pygame mixer
5. Temp files auto-cleaned

## Accent Options

You can change Maya's accent by editing the voice engine initialization:

```python
# In voice_assistant.py or vision_assistant.py
self.voice_engine = RealisticVoiceEngine(tld='com')  # US (default)
# self.voice_engine = RealisticVoiceEngine(tld='co.uk')  # British
# self.voice_engine = RealisticVoiceEngine(tld='com.au')  # Australian  
# self.voice_engine = RealisticVoiceEngine(tld='ca')  # Canadian
```

## Speed Control

```python
# Slower, more deliberate speech
self.voice_engine = RealisticVoiceEngine(slow=True)
```

## Combined with Human Personality

The realistic voice works **with** the human_voice.py personality engine:

1. **human_voice.py** adds:
   - Filler words (um, uh, like)
   - Reactions (oh wow, hmm, interesting)
   - Casual speech patterns
   - Prosody markers

2. **realistic_voice.py** speaks it with:
   - Natural intonation
   - Human-like rhythm
   - Proper emotional expression
   - Clear pronunciation

Result: **Maya sounds genuinely human!**

## Testing

Run the voice assistant:
```bash
python3.11 voice_assistant.py
```

The first speech will download the audio from Google TTS, then it's cached locally for faster playback.

## Dependencies

- `gtts==2.5.4` - Google Text-to-Speech
- `pygame==2.6.1` - Audio playback
- Python 3.11 (required)

No API keys needed! Completely free!
