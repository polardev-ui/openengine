# OpenEngine - Windows Installation Guide

## System Requirements
- Windows 10/11
- Python 3.11 (3.10 or 3.12 also work)
- Microphone
- Webcam (for vision features)
- Internet connection (for initial setup)

## Installation Steps

### 1. Install Python 3.11

Download from: https://www.python.org/downloads/

**Important**: During installation, check "Add Python to PATH"

### 2. Install Dependencies

Open PowerShell or Command Prompt:

```powershell
# Navigate to OpenEngine folder
cd "C:\Path\To\API AI Voice"

# Install required packages
pip install -r requirements.txt

# For vision capabilities
cd vision
pip install -r requirements.txt
cd ..
```

### 3. Install PyAudio (Windows-specific)

PyAudio requires Microsoft Visual C++ on Windows.

**Option A: Pre-built wheel (easiest)**
```powershell
pip install pipwin
pipwin install pyaudio
```

**Option B: Manual download**
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the appropriate `.whl` file for your Python version
3. Install: `pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl`

### 4. Test Installation

```powershell
# Test voice assistant
python voice_assistant.py

# Test vision assistant
python vision\vision_assistant.py
```

## Windows-Specific Notes

### Microphone Access
- Windows may prompt for microphone permissions
- Allow access in Windows Privacy Settings:
  - Settings → Privacy → Microphone → Allow apps to access microphone

### Camera Access
- Windows may prompt for camera permissions
- Allow access in Windows Privacy Settings:
  - Settings → Privacy → Camera → Allow apps to access camera

### Firewall
- Python may request network access for API calls
- Allow through Windows Firewall

### Voice Engine
- Edge TTS works natively on Windows (Microsoft technology)
- Voices may sound slightly different than macOS
- Recommended Windows voices:
  - `en-US-JennyNeural` - Professional female
  - `en-US-GuyNeural` - Professional male
  - `en-US-AriaNeural` - Warm female

## Troubleshooting

### "No module named 'pyaudio'"
- PyAudio installation failed
- Try the pipwin method above
- Or install Microsoft Visual C++ Build Tools

### "Camera not found"
- Check camera is connected and working
- Test with Windows Camera app first
- Update camera drivers

### "Permission denied" errors
- Run PowerShell/CMD as Administrator
- Check antivirus isn't blocking Python

### Edge TTS not working
- Check internet connection (needed for first download)
- Try: `pip install --upgrade edge-tts`

## Running on Startup (Optional)

### Task Scheduler Method
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start a program
5. Program: `C:\Path\To\Python\python.exe`
6. Arguments: `"C:\Path\To\voice_assistant.py"`

### Startup Folder Method
1. Press `Win + R`
2. Type: `shell:startup`
3. Create shortcut to `voice_assistant.py`

## Performance Tips

- Close unnecessary background apps
- Use SSD for faster model loading
- Disable Windows animations for better responsiveness
- Increase Python process priority in Task Manager (optional)

## Known Issues

- PyAudio installation can be tricky on Windows
- Some antivirus software may flag Python scripts
- Windows Defender may cause slowdowns (add Python to exclusions)

## Getting Help

If you encounter issues:
1. Check this guide first
2. Verify Python version: `python --version`
3. Check installed packages: `pip list`
4. Report issues on GitHub with error messages

## Differences from macOS Version

| Feature | Windows | macOS |
|---------|---------|-------|
| Voice Engine | Edge TTS | Edge TTS |
| Microphone | PyAudio | PyAudio |
| Camera | OpenCV | OpenCV |
| App Opening | Windows-specific | macOS-specific |
| Performance | Similar | Similar |

The core functionality is identical! 