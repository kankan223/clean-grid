"""
AI Service Client - CleanGrid Phase 1
HTTP client for communicating with AI inference service
"""

import httpx
import structlog
from typing import Dict, Any

from app.core.config import settings

logger = structlog.get_logger()


async def call_ai_service(image_url: str) -> Dict[str, Any]:
    """
    Call AI service for image inference
    
    Args:
        image_url: URL of image to analyze
        
    Returns:
        AI inference results dictionary
    """
    try:
        logger.info("Calling AI service", image_url=image_url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/infer",
                json={"image_url": image_url},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(
                "AI service response received",
                waste_detected=result.get("waste_detected"),
                severity=result.get("severity"),
                confidence=result.get("confidence")
            )
            
            return result
            
    except httpx.TimeoutException:
        logger.error("AI service timeout", image_url=image_url)
        return {
            "waste_detected": False,
            "confidence": None,
            "severity": "None",
            "detections": []
        }
        
    except httpx.ConnectError as e:
        logger.error("AI service connection failed", error=str(e))
        return {
            "waste_detected": False,
            "confidence": None,
            "severity": "None",
            "detections": []
        }
        
    except Exception as e:
        logger.error("AI service call failed", error=str(e))
        return {
            "waste_detected": False,
            "confidence": None,
            "severity": "None",
            "detections": []
        }


class AIClient:
    """AI Service Client for image analysis"""
    
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL
    
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze image using AI service
        
        Args:
            image_url: URL of image to analyze
            
        Returns:
            AI inference results dictionary
        """
        return await call_ai_service(image_url)


# Create singleton instance
ai_client = AIClient()
