import cv2
import numpy as np
from typing import Dict, List, Optional
import os
import random

class CustomVisionEngine:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        
        self.coco_classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
            'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        self.yolo_net = None
        self.yolo_available = self._load_yolo()
        
        features = []
        if self.yolo_available:
            features.append("YOLO object detection")
        features.append("face detection")
        features.append("person analysis")
        features.append("scene recognition")
        
        print(f"✅ Vision engine initialized with {', '.join(features)}")
    
    def _load_yolo(self) -> bool:
        try:
            weights_path = os.path.join(os.path.dirname(__file__), 'yolov3-tiny.weights')
            config_path = os.path.join(os.path.dirname(__file__), 'yolov3-tiny.cfg')
            
            if not os.path.exists(weights_path) or not os.path.exists(config_path):
                print("⚠️  YOLO files not found, using basic detection")
                return False
            
            self.yolo_net = cv2.dnn.readNet(weights_path, config_path)
            self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            layer_names = self.yolo_net.getLayerNames()
            self.yolo_output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
            
            return True
        except Exception as e:
            print(f"⚠️  Could not load YOLO: {e}")
            return False
    
    def detect(self, img) -> Dict:
        if img is None or img.size == 0:
            return {'faces': [], 'people': [], 'objects': [], 'text_regions': [], 'scene': 'unknown'}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = img.shape[:2]
        
        result = {
            'faces': [],
            'people': [],
            'objects': [],
            'text_regions': [],
            'scene': self._detect_scene_type(img),
            'brightness': gray.mean()
        }
        
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            person_details = self._analyze_person_details(img, (x, y, w, h))
            
            result['faces'].append({
                'bbox': (int(x), int(y), int(w), int(h)),
                'confidence': 0.9 if len(eyes) >= 2 else 0.7,
                'details': person_details,
                'position': self._get_position(x, w, width)
            })
        
        if self.yolo_available:
            yolo_detections = self._detect_with_yolo(img)
            for det in yolo_detections:
                if det['label'] == 'person':
                    result['people'].append(det)
                else:
                    result['objects'].append(det)
        
        if not self.yolo_available and not result['faces']:
            bodies = self.body_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 100))
            for (x, y, w, h) in bodies:
                result['people'].append({
                    'label': 'person',
                    'bbox': (int(x), int(y), int(w), int(h)),
                    'confidence': 0.6,
                    'position': self._get_position(x, w, width)
                })
        
        text_regions = self._detect_text_regions(img, gray)
        result['text_regions'] = text_regions
        
        return result
    
    def _detect_with_yolo(self, img) -> List[Dict]:
        detections = []
        
        try:
            height, width = img.shape[:2]
            
            blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
            self.yolo_net.setInput(blob)
            outputs = self.yolo_net.forward(self.yolo_output_layers)
            
            boxes = []
            confidences = []
            class_ids = []
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.15:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.15, 0.5)
            
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    label = self.coco_classes[class_ids[i]]
                    confidence = confidences[i]
                    
                    position = self._get_position(x, w, width)
                    
                    detections.append({
                        'label': label,
                        'bbox': (x, y, w, h),
                        'confidence': confidence,
                        'position': position
                    })
        
        except Exception as e:
            print(f"YOLO detection error: {e}")
        
        return detections
    
    def _analyze_person_details(self, img, face_bbox) -> Dict:
        details = {}
        
        try:
            x, y, w, h = face_bbox
            face_roi = img[y:y+h, x:x+w]
            
            aspect_ratio = h / w if w > 0 else 1
            if aspect_ratio > 1.3:
                details['gender'] = 'male'
            else:
                details['gender'] = 'female'
            
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            
            if laplacian_var > 500:
                details['age_range'] = 'young adult'
            elif laplacian_var > 300:
                details['age_range'] = 'middle-aged'
            else:
                details['age_range'] = 'senior'
            
            hair_region_height = int(h * 0.3)
            hair_roi = face_roi[0:hair_region_height, :]
            
            if hair_roi.size > 0:
                avg_color = hair_roi.mean(axis=(0, 1))
                b, g, r = avg_color
                
                if r > 150 and g < 100 and b < 100:
                    details['hair_color'] = 'red/auburn'
                elif r > 200 and g > 180 and b < 150:
                    details['hair_color'] = 'blonde'
                elif r < 80 and g < 80 and b < 80:
                    details['hair_color'] = 'dark/black'
                elif r > 100 and g > 80 and b > 60:
                    details['hair_color'] = 'brown'
                else:
                    details['hair_color'] = 'dark'
        
        except Exception as e:
            pass
        
        return details
    
    def _detect_scene_type(self, img) -> str:
        try:
            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = gray.mean()
            
            if brightness < 60:
                return 'very dark'
            elif brightness < 100:
                return 'dim indoor'
            elif brightness > 200:
                return 'very bright'
            else:
                return 'normal indoor'
        
        except Exception:
            return 'unknown'
    
    def _get_position(self, x: int, w: int, img_width: int) -> str:
        center_x = x + w / 2
        
        if center_x < img_width * 0.33:
            return 'left'
        elif center_x > img_width * 0.67:
            return 'right'
        else:
            return 'center'
    
    def _detect_text_regions(self, img, gray) -> List[Dict]:
        text_regions = []
        
        try:
            height, width = img.shape[:2]
            
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=2)
            
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            min_area = (height * width) * 0.02
            min_width = width * 0.15
            min_height = 25
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if (aspect_ratio > 2 and w > min_width and h > min_height and 
                        x > width * 0.1 and x + w < width * 0.9):
                        text_regions.append({
                            'bbox': (x, y, w, h),
                            'area': area
                        })
        
        except Exception:
            pass
        
        return text_regions
    
    def _detect_text_regions(self, img, gray) -> List[Dict]:
        text_regions = []
        
        try:
            height, width = img.shape[:2]
            
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=2)
            
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            min_area = (height * width) * 0.02
            min_width = width * 0.15
            min_height = 25
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if (aspect_ratio > 2 and w > min_width and h > min_height and 
                        x > width * 0.1 and x + w < width * 0.9):
                        text_regions.append({
                            'bbox': (x, y, w, h),
                            'area': area
                        })
        
        except Exception:
            pass
        
        return text_regions
    
    def describe(self, img) -> str:
        detection_result = self.detect(img)
        
        faces = detection_result.get('faces', [])
        people = detection_result.get('people', [])
        objects = detection_result.get('objects', [])
        text_regions = detection_result.get('text_regions', [])
        brightness = detection_result.get('brightness', 128)
        
        parts = []
        
        if faces:
            for face in faces:
                details = face.get('details', {})
                position = face.get('position', 'center')
                
                desc = "Person"
                attrs = []
                if 'gender' in details:
                    attrs.append(details['gender'])
                if 'age_range' in details:
                    attrs.append(details['age_range'])
                
                if attrs:
                    desc = f"{' '.join(attrs)} person"
                
                parts.append(f"{desc} detected ({position}, confidence: {int(face.get('confidence', 0.5) * 100)}%)")
        
        elif people:
            for person in people:
                position = person.get('position', 'center')
                conf = int(person.get('confidence', 0.5) * 100)
                parts.append(f"Person detected ({position}, {conf}%)")
        
        if objects:
            obj_list = []
            for obj in objects[:5]:
                label = obj['label']
                position = obj.get('position', 'center')
                confidence = int(obj.get('confidence', 0) * 100)
                bbox = obj.get('bbox', (0, 0, 100, 100))
                
                size = 'large' if bbox[2] * bbox[3] > 150000 else 'medium' if bbox[2] * bbox[3] > 50000 else 'small'
                
                obj_list.append(f"{size} {label} ({position}, {confidence}%)")
            
            if obj_list:
                parts.append("Objects: " + "; ".join(obj_list))
        
        if text_regions and len(text_regions) >= 2:
            parts.append(f"{len(text_regions)} text regions")
        
        if brightness < 60:
            parts.append("Very dark lighting")
        elif brightness < 100:
            parts.append("Dim lighting")
        elif brightness > 180:
            parts.append("Bright lighting")
        
        if not parts:
            if brightness < 60:
                return "VISION: Extremely dark - no objects visible"
            elif brightness < 100:
                return "VISION: Dim lighting - no clear objects detected"
            else:
                return "VISION: No people or objects currently detected in frame"
        
        return "VISION: " + " | ".join(parts)
