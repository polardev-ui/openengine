# Vision Assistant Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd vision
pip install -r requirements.txt
```

### 2. Download YOLO Model for Advanced Object Detection
```bash
python3 download_yolo.py
```

This downloads YOLOv3-tiny (~35MB) which enables Maya to identify **80+ different objects** including:
- 🧍 **People & Animals**: person, cat, dog, bird, horse, etc.
- 🚗 **Vehicles**: car, bicycle, motorcycle, bus, truck, boat, train
- 📱 **Electronics**: cell phone, laptop, keyboard, mouse, remote, TV
- 🍽️ **Household**: bottle, cup, fork, knife, bowl, chair, couch, bed
- 🍕 **Food**: banana, apple, sandwich, pizza, cake, orange
- And many more!

### 3. Grant Camera Permissions

Go to **System Preferences > Security & Privacy > Camera** and enable access for Terminal or your Python application.

### 4. Run Maya
```bash
python3 vision_assistant.py
```

## Camera Preview

The live camera window shows:
- 🟢 **Green boxes** = Faces detected
- 🔵 **Cyan boxes** = People (full body)
- 🔴 **Red boxes** = Objects (bottle, laptop, phone, etc.)

Each box shows:
- Object name (e.g., "bottle", "laptop", "person")
- Confidence score (e.g., "0.85" means 85% confident)
- Total detection count at bottom

## Vision Commands

Ask Maya things like:
- "What do you see?"
- "What's in my hand?" (hold up a bottle, phone, etc.)
- "How many people are here?"
- "What objects are on the table?"
- "Describe what's in front of you"

## Troubleshooting

### Camera Won't Open
- Check System Preferences > Security & Privacy > Camera
- Try running: `python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`
- Restart Terminal after granting permissions

### Python Logo Bouncing (Window Won't Open)
This is fixed! The camera now:
- Checks permissions before opening
- Tests camera read before starting preview
- Runs preview in background thread at 30 FPS
- Provides clear error messages

### YOLO Not Loading
Without YOLO, Maya falls back to basic detection. To enable advanced detection:
```bash
python3 download_yolo.py
```

### Slow Detection
- YOLO tiny runs at ~30 FPS on most machines
- If too slow, you can adjust confidence threshold in custom_vision.py (line with `if confidence > 0.3`)
- Higher threshold = fewer but more confident detections

## Performance

- **With YOLO**: Detects 80+ object types, ~30 FPS, high accuracy
- **Without YOLO**: Basic face/body detection, faster but limited

## What Makes This Advanced?

1. **Real Object Recognition**: Instead of saying "dark room", Maya now says "I see a bottle, a laptop, and a cup"
2. **80+ Object Classes**: Can identify specific items, not just generic shapes
3. **Live Visual Feedback**: See exactly what Maya detects with bounding boxes
4. **High Accuracy**: YOLO with 30-85% confidence scores
5. **Smart Descriptions**: "I see 2 bottles and a laptop" instead of vague descriptions
