"""
YOLOv8n inference wrapper for CleanGrid AI Service
Handles model loading and inference operations
"""

import io
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import structlog

from app.severity import compute_severity, filter_relevant_detections

logger = structlog.get_logger()


class YOLOInference:
    """
    YOLOv8n inference wrapper
    Loads model once on startup and provides inference methods
    """
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize YOLO inference
        
        Args:
            model_path: Path to YOLO model weights
        """
        self.model_path = model_path
        self.model = None
        self.model_loaded = False
        
    def load_model(self) -> bool:
        """
        Load YOLO model into memory
        Should be called once at startup
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            logger.info("Loading YOLO model", model_path=self.model_path)
            self.model = YOLO(self.model_path)
            self.model_loaded = True
            logger.info("YOLO model loaded successfully")
            return True
        except Exception as e:
            logger.error("Failed to load YOLO model", error=str(e))
            return False
    
    def preprocess_image(self, image_bytes: bytes, max_size: int = 1024) -> np.ndarray:
        """
        Preprocess image for inference
        
        Args:
            image_bytes: Raw image bytes
            max_size: Maximum dimension for resizing
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (for performance)
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to numpy array (OpenCV format)
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error("Failed to preprocess image", error=str(e))
            raise ValueError(f"Image preprocessing failed: {e}")
    
    def run_inference(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Run YOLO inference on image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with inference results
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_bytes)
            
            # Run inference
            results = self.model(image, verbose=False)
            
            # Extract detections
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection data
                        xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        label = self.model.names[cls]
                        
                        detection = {
                            "label": label,
                            "confidence": conf,
                            "box": [float(x) for x in xyxy]
                        }
                        detections.append(detection)
            
            # Filter for relevant waste classes
            relevant_detections = filter_relevant_detections(detections)
            
            # Compute severity
            waste_detected, severity, max_confidence = compute_severity(relevant_detections)
            
            result = {
                "detections": relevant_detections,
                "all_detections": detections,  # Include all detections for debugging
                "waste_detected": waste_detected,
                "severity": severity,
                "max_confidence": max_confidence,
                "detection_count": len(relevant_detections)
            }
            
            logger.info(
                "Inference completed",
                waste_detected=waste_detected,
                severity=severity,
                detection_count=len(relevant_detections),
                max_confidence=max_confidence
            )
            
            return result
            
        except Exception as e:
            logger.error("Inference failed", error=str(e))
            raise RuntimeError(f"Inference failed: {e}")
    
    def create_annotated_image(self, image_bytes: bytes, detections: List[Dict]) -> bytes:
        """
        Create annotated image with bounding boxes
        
        Args:
            image_bytes: Original image bytes
            detections: List of detection dictionaries
            
        Returns:
            Annotated image bytes
        """
        try:
            # Preprocess image
            image = self.preprocess_image(image_bytes)
            
            # Draw bounding boxes
            for detection in detections:
                box = detection["box"]
                label = detection["label"]
                confidence = detection["confidence"]
                
                x1, y1, x2, y2 = map(int, box)
                
                # Draw rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label_text = f"{label}: {confidence:.2f}"
                label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), (0, 255, 0), -1)
                cv2.putText(image, label_text, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # Convert back to bytes
            _, buffer = cv2.imencode('.jpg', image)
            return buffer.tobytes()
            
        except Exception as e:
            logger.error("Failed to create annotated image", error=str(e))
            raise RuntimeError(f"Annotated image creation failed: {e}")


# Global inference instance (loaded at startup)
inference_engine: Optional[YOLOInference] = None


def get_inference_engine() -> YOLOInference:
    """
    Get global inference engine instance
    
    Returns:
        YOLOInference instance
    """
    global inference_engine
    
    if inference_engine is None:
        raise RuntimeError("Inference engine not initialized")
    
    return inference_engine


def initialize_inference_engine(model_path: str = "yolov8n.pt") -> bool:
    """
    Initialize global inference engine
    
    Args:
        model_path: Path to YOLO model weights
        
    Returns:
        True if initialization successful, False otherwise
    """
    global inference_engine
    
    try:
        inference_engine = YOLOInference(model_path)
        return inference_engine.load_model()
    except Exception as e:
        logger.error("Failed to initialize inference engine", error=str(e))
        return False
