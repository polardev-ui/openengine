import urllib.request
import os
import sys

def download_file(url, filename):
    print("\n" + "="*60)
    print("YOLO Model Downloader")
    print("="*60)
    print("\nThis will download YOLOv3-tiny model files (~35MB total)")
    print("for advanced object detection with 80+ object classes.\n")
    
    weights_url = "https://github.com/patrick013/Object-Detection---Yolov3/raw/master/model/yolov3-tiny.weights"
    config_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg"
    
    weights_file = "yolov3-tiny.weights"
    config_file = "yolov3-tiny.cfg"
    
    if os.path.exists(weights_file) and os.path.exists(config_file):
        print("✅ YOLO model files already exist!")
        print("\nTo re-download, delete the existing files first.")
        return
    
    if not os.path.exists(weights_file):
        success = download_file(weights_url, weights_file)
        if not success:
            print("\n⚠️  Failed to download weights file.")
            return
    else:
        print(f"✅ {weights_file} already exists")
    
    if not os.path.exists(config_file):
        success = download_file(config_url, config_file)
        if not success:
            print("\n⚠️  Failed to download config file.")
            return
    else:
        print(f"✅ {config_file} already exists")
    
    print("\n" + "="*60)
    print("✅ YOLO model setup complete!")
    print("="*60)
    print("\nYou can now run vision_assistant.py with advanced object detection.")
    print("Maya will be able to identify 80+ different types of objects including:")
    print("- People, animals, vehicles")
    print("- Household items (bottles, cups, phones, laptops, etc.)")
    print("- Furniture, electronics, food items, and more!")
    print("\n")

if __name__ == "__main__":
    main()
