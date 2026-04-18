"""
Severity scoring logic for CleanGrid AI Service
Computes waste severity based on YOLOv8n detection results
"""

from typing import List, Tuple, Set, Dict
from app.config import settings

# Import settings from main config to avoid duplication


def compute_severity(detections: List[dict]) -> Tuple[bool, str, float]:
    """
    Compute waste severity from YOLO detections
    
    Args:
        detections: List of detection dictionaries with 'label', 'confidence', 'box'
        
    Returns:
        Tuple of (waste_detected, severity_label, max_confidence)
    """
    # Filter for relevant classes above threshold
    relevant_detections = [
        detection for detection in detections
        if (
            detection['label'].lower() in settings.RELEVANT_CLASSES and
            detection['confidence'] >= settings.YOLO_CONFIDENCE_THRESHOLD
        )
    ]
    
    # No waste detected
    if not relevant_detections:
        return False, "None", 0.0
    
    # Get maximum confidence
    max_confidence = max(detection['confidence'] for detection in relevant_detections)
    detection_count = len(relevant_detections)
    
    # Determine severity
    if max_confidence >= settings.HIGH_CONFIDENCE_THRESHOLD or detection_count >= settings.HIGH_DETECTION_COUNT:
        return True, "High", max_confidence
    elif max_confidence >= settings.YOLO_CONFIDENCE_THRESHOLD or detection_count == 2:
        return True, "Medium", max_confidence
    else:
        return True, "Low", max_confidence


def filter_relevant_detections(detections: List[dict]) -> List[dict]:
    """
    Filter detections to only include relevant waste classes above threshold
    
    Args:
        detections: List of detection dictionaries
        
    Returns:
        Filtered list of detections
    """
    return [
        detection for detection in detections
        if (
            detection['label'].lower() in settings.RELEVANT_CLASSES and
            detection['confidence'] >= settings.YOLO_CONFIDENCE_THRESHOLD
        )
    ]


def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level (for UI display)
    
    Args:
        severity: Severity level string
        
    Returns:
        Hex color code
    """
    colors = {
        "None": "#9E9E9E",
        "Low": "#4CAF50", 
        "Medium": "#F9A03F",
        "High": "#E84855"
    }
    return colors.get(severity, "#9E9E9E")


def calculate_severity(detections: List[Dict], confidence_threshold: float = 0.45) -> str:
    """
    Calculate severity level based on YOLO detections
    
    Deterministic severity scoring as specified in tech-stake.md:
    - High: Confidence >= 0.7 OR >= 3 trash detections
    - Medium: Confidence 0.45-0.69 OR 2 detections  
    - Low: Otherwise (if above threshold)
    - None: Below threshold
    
    Args:
        detections: List of detection dictionaries
        confidence_threshold: Minimum confidence threshold (default 0.45)
        
    Returns:
        Severity level: "None", "Low", "Medium", or "High"
    """
    # Filter relevant detections above threshold
    relevant_detections = [
        d for d in detections 
        if d.get("label") in settings.RELEVANT_CLASSES and d.get("confidence", 0) >= confidence_threshold
    ]
    
    if not relevant_detections:
        return "None"
    
    # Get max confidence and count
    max_confidence = max(d.get("confidence", 0) for d in relevant_detections)
    detection_count = len(relevant_detections)
    
    # Deterministic severity computation per tech-stake.md
    if max_confidence >= 0.7 or detection_count >= 3:
        return "High"
    elif max_confidence >= 0.45 or detection_count == 2:
        return "Medium"
    else:
        return "Low"


def get_severity_description(severity: str) -> str:
    """
    Get human-readable description for severity level
    
    Args:
        severity: Severity level string
        
    Returns:
        Description string
    """
    descriptions = {
        "None": "No waste detected",
        "Low": "Minor waste detected - low priority",
        "Medium": "Moderate waste detected - medium priority", 
        "High": "Significant waste detected - high priority"
    }
    return descriptions.get(severity, "Unknown severity")
