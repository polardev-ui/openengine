# OpenEngine

An open-source multimodal AI engine that extends text-based AI chatbots with voice, vision, and speech capabilities.

## Overview

OpenEngine bridges the gap between text-only AI models and real-world interaction by providing a comprehensive framework for:

- **Speech Recognition**: Convert spoken language to text using Google Speech API
- **Text-to-Speech**: Natural voice synthesis using system-native TTS engines
- **Computer Vision**: Advanced object detection and scene recognition using YOLO and OpenCV
- **Multimodal Integration**: Seamlessly combine vision and conversation in a unified interface

## Architecture

The engine consists of three main components:

### 1. Voice Assistant (`voice_assistant.py`)
Core voice interaction system with:
- Real-time speech-to-text conversion
- Configurable silence detection
- Speech interruption handling
- System integration for opening applications and URLs
- **Realistic Google TTS voice** - Natural-sounding speech that's far more human than system voices
- **Human-like personality engine** with casual speech patterns, filler words, and natural pauses

### 2. Vision Engine (`vision/custom_vision.py`)
Advanced computer vision pipeline featuring:
- YOLO-based object detection (80+ object classes)
- Face detection and demographic estimation
- Scene classification (indoor/outdoor, nature, urban)
- Text region detection
- Color and lighting analysis
- Real-time bounding box visualization

### 3. Vision Voice Assistant (`vision/vision_assistant.py`)
Integrated multimodal assistant combining:
- Voice interaction from base assistant
- Real-time camera feed processing
- Object detection with visual feedback
- Context-aware responses using vision data

## Features

### Object Detection
- 80+ COCO dataset object classes
- Person detection with age/gender estimation
- Configurable confidence thresholds
- Non-maximum suppression for accuracy

### Scene Recognition
- Natural environment detection (ocean, forest, sky)
- Indoor/outdoor classification
- Lighting condition analysis
- Color distribution analysis

### Voice Interaction
- Configurable silence timeout (default 1.5 seconds)
- Real-time speech interruption
- System command execution
- Natural conversation flow

### Visual Feedback
- Live camera preview at 30 FPS
- Color-coded bounding boxes (green: faces, cyan: people, red: objects)
- Confidence scores and object labels
- Detection count display

## Installation

### Prerequisites
**Python 3.11 is required** for the advanced voice engine (pyttsx3).

```bash
brew install portaudio
```

### Python Dependencies
```bash
python3.11 -m pip install -r requirements.txt
```

For vision capabilities:
```bash
cd vision
python3.11 -m pip install -r requirements.txt
```

### YOLO Model Setup
Download YOLOv3-tiny weights and configuration:
```bash
cd vision
python3.11 download_yolo.py
```

Or manually download:
- `yolov3-tiny.weights` (33MB)
- `yolov3-tiny.cfg`

Place both files in the `vision/` directory.

## Usage

### Basic Voice Assistant
```bash
python3 voice_assistant.py
```

### Vision-Enabled Assistant
```bash
cd vision
python3 vision_assistant.py
```

### Voice Commands
- "exit", "quit", "stop" - End session
- "open [application]" - Launch macOS application
- "show me [website]" - Open URL in Safari
- "what do you see?" - Trigger vision analysis

## Configuration

### API Configuration
Edit `voice_assistant.py` or `vision/vision_assistant.py`:
```python
API_KEY = 'your_api_key'
API_URL = 'your_api_endpoint'
MODEL = 'your_model_name'
```

### Silence Detection
Adjust timeout in `voice_assistant.py`:
```python
max_silent_chunks = int(self.RATE / self.CHUNK * 1.5)
```

### Object Detection Threshold
Modify confidence threshold in `custom_vision.py`:
```python
if confidence > 0.25:
```

## System Requirements

- **Operating System**: macOS (tested), Linux (compatible), Windows (requires modifications)
- **Python**: 3.8 or higher
- **Camera**: Required for vision features
- **Microphone**: Required for voice interaction
- **Memory**: 2GB minimum, 4GB recommended for YOLO

## Technical Details

### Vision Pipeline
1. Image capture from camera or base64 input
2. Preprocessing and normalization
3. YOLO forward pass for object detection
4. Non-maximum suppression
5. Face detection using Haar Cascades
6. Scene analysis using HSV color space
7. Text region detection via edge analysis
8. Natural language description generation

### Speech Processing
1. Audio stream capture via PyAudio
2. Silence detection using amplitude threshold
3. WAV encoding
4. Google Speech API HTTP request
5. Text parsing and response generation
6. Text-to-speech synthesis
7. Interrupt monitoring during playback

## Performance

- **Object Detection**: ~30 FPS on modern CPUs
- **Speech Recognition**: <500ms latency
- **Speech Interruption**: ~100ms detection time
- **Silence Detection**: 1.5 second default timeout

## Limitations

- YOLO detection limited to 80 COCO classes
- Gender/age estimation uses heuristics
- Speech recognition requires internet connection
- macOS-specific TTS implementation
- Camera permissions required for vision features

## Contributing

Contributions are welcome. Please ensure:
- Code follows existing architecture patterns
- Changes maintain cross-platform compatibility where possible
- Performance impact is documented
- New features include appropriate error handling

## License

MIT License - See LICENSE file for details

## Acknowledgments

- YOLO object detection framework
- OpenCV computer vision library
- Google Speech Recognition API
- COCO dataset for object classes

## Version

Current Version: 1.0.0

## Contact

For issues, questions, or contributions, please open an issue on the GitHub repository.
