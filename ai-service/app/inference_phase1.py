"""
Phase 1 inference implementation - Mock YOLOv8n for development
Simulates YOLOv8n inference without OpenCV dependencies
"""

import io
import random
from typing import List, Dict, Any, Optional
from PIL import Image
import structlog

from app.severity import compute_severity

logger = structlog.get_logger()


# Relevant waste classes from COCO
RELEVANT_CLASSES = ["bottle", "cup", "bag", "banana", "can", "backpack", "suitcase"]


class Phase1Inference:
    """
    Phase 1 inference engine that simulates YOLOv8n results
    For development without OpenCV dependencies
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize Phase 1 inference
        
        Args:
            model_path: Not used in Phase 1 mock
        """
        self.model_path = model_path
        self.model_loaded = True
        
    def load_model(self) -> bool:
        """Mock model loading - always successful"""
        logger.info("Phase 1 inference engine initialized (mock mode)")
        return True
    
    def run_inference(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Run mock inference on image bytes
        
        Returns simulated YOLOv8n results with realistic severity scoring
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary with inference results
        """
        try:
            # Get image size for realistic bounding boxes
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            # Simulate random detections (0-4 detections)
            num_detections = random.randint(0, 4)
            
            detections = []
            for i in range(num_detections):
                # Generate random bounding box within image bounds
                x1 = random.uniform(0, width * 0.8)
                y1 = random.uniform(0, height * 0.8)
                box_width = random.uniform(width * 0.1, width * 0.3)
                box_height = random.uniform(height * 0.1, height * 0.3)
                
                detection = {
                    "label": random.choice(RELEVANT_CLASSES),
                    "confidence": random.uniform(0.3, 0.95),
                    "box": [x1, y1, x1 + box_width, y1 + box_height]
                }
                detections.append(detection)
            
            # Use real severity computation logic
            waste_detected, severity, max_confidence = compute_severity(detections)
            
            result = {
                "detections": detections,
                "waste_detected": waste_detected,
                "severity": severity,
                "max_confidence": max_confidence,
                "image_size": (width, height),
                "inference_time_ms": random.randint(800, 2000)  # Realistic timing
            }
            
            logger.info(
                "Mock inference completed",
                waste_detected=waste_detected,
                severity=severity,
                detection_count=len(detections),
                max_confidence=max_confidence
            )
            
            return result
            
        except Exception as e:
            logger.error("Mock inference failed", error=str(e))
            # Return safe default
            return {
                "detections": [],
                "waste_detected": False,
                "severity": "None",
                "max_confidence": 0.0,
                "image_size": (640, 640),
                "inference_time_ms": 1000
            }


# Global instance
inference_engine = Phase1Inference()


def get_inference_engine() -> Phase1Inference:
    """Get the global inference engine instance"""
    return inference_engine


def initialize_inference_engine(model_path: str = None) -> bool:
    """
    Initialize the inference engine
    
    Args:
        model_path: Path to YOLO model file
        
    Returns:
        bool: True if initialization successful
    """
    logger.info("Initializing Phase 1 inference engine (mock mode)")
    return True

