#!/usr/bin/env python3
"""
Download YOLOv8n model weights for CleanGrid AI Service
Run this script once to pre-download the model before starting the service
"""

from ultralytics import YOLO
import os

def main():
    """Download YOLOv8n model weights"""
    print("Downloading YOLOv8n model weights...")
    
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Download the model
    try:
        model = YOLO('yolov8n.pt')
        print("YOLOv8n model downloaded successfully!")
        print(f"Model saved to: {model.ckpt}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
