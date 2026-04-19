"""
CleanGrid AI Service - FastAPI Main Application
YOLOv8n inference microservice for waste detection
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import httpx
import structlog
import uvicorn
import os
from urllib.parse import urlparse, urlunparse

from app.inference import initialize_inference_engine, get_inference_engine
from app.severity import calculate_severity, get_severity_description
from app.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

IMAGE_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}


def resolve_image_url(image_url: str) -> str:
    """Resolve relative or localhost image URLs to the backend service URL."""
    parsed = urlparse(image_url)

    if not parsed.scheme:
        return f"{settings.BACKEND_BASE_URL.rstrip('/')}/{image_url.lstrip('/')}"

    if parsed.hostname in {"localhost", "127.0.0.1"}:
        backend_parsed = urlparse(settings.BACKEND_BASE_URL)
        return urlunparse(
            (
                backend_parsed.scheme or parsed.scheme,
                backend_parsed.netloc or parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    return image_url


# Pydantic schemas
class Detection(BaseModel):
    """Individual detection result"""
    label: str = Field(..., description="Detected object class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    box: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class InferenceRequest(BaseModel):
    """Request schema for inference"""
    image_url: str = Field(..., description="URL of image to analyze")


class InferenceResponse(BaseModel):
    """Response schema for inference results"""
    waste_detected: bool = Field(..., description="Whether waste was detected")
    confidence: Optional[float] = Field(None, description="Maximum confidence of waste detections")
    severity: Literal["None", "Low", "Medium", "High"] = Field(..., description="Waste severity level")
    detections: List[Detection] = Field(..., description="List of waste detections")
    description: str = Field(..., description="Human-readable severity description")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Whether YOLO model is loaded")
    version: str = Field(..., description="Service version")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles model loading at startup
    """
    # Startup
    logger.info("Starting CleanGrid AI Service")
    
    # Get model path from environment
    model_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    
    # Initialize inference engine
    success = initialize_inference_engine(model_path)
    
    if not success:
        logger.error("Failed to initialize inference engine - shutting down")
        raise RuntimeError("Failed to load YOLO model")
    
    logger.info("CleanGrid AI Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CleanGrid AI Service")


# Create FastAPI application
app = FastAPI(
    title="CleanGrid AI Service",
    version="1.0.0",
    description="YOLOv8n inference microservice for waste detection",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # AI service can be called by any backend
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred during inference"
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns the status of the AI service and model
    """
    try:
        inference_engine = get_inference_engine()
        model_loaded = inference_engine.model_loaded
    except RuntimeError:
        model_loaded = False
    
    status = "healthy" if model_loaded else "unhealthy"
    
    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        version="1.0.0"
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    Returns basic service information
    """
    return {
        "name": "CleanGrid AI Service",
        "version": "1.0.0",
        "description": "YOLOv8n inference microservice for waste detection",
        "docs": "/docs",
        "health": "/health"
    }


# Inference endpoint
@app.post("/infer", response_model=InferenceResponse, tags=["Inference"])
async def infer_waste(request: InferenceRequest):
    """
    Run waste detection inference on an image
    
    Args:
        request: Inference request with image URL
        
    Returns:
        Inference results with severity classification
    """
    logger.info("Starting inference", image_url=request.image_url)
    
    try:
        resolved_image_url = resolve_image_url(request.image_url)

        # Download image from URL
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=IMAGE_FETCH_HEADERS) as client:
            response = await client.get(resolved_image_url)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"URL does not point to an image. Content type: {content_type}"
                )
            
            # Check file size (10MB limit)
            content_length = len(response.content)
            max_size = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB
            
            if content_length > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too large. Maximum size: {max_size // 1024 // 1024}MB"
                )
            
            image_bytes = response.content
        
        logger.info("Image downloaded successfully", size_bytes=content_length, resolved_image_url=resolved_image_url)
        
        # Run inference
        inference_engine = get_inference_engine()
        result = inference_engine.run_inference(image_bytes)
        
        # Convert detections to response format
        detections = [
            Detection(
                label=detection["label"],
                confidence=detection["confidence"],
                box=detection["box"]
            )
            for detection in result["detections"]
        ]
        
        # Build response
        response_data = InferenceResponse(
            waste_detected=result["waste_detected"],
            confidence=result["max_confidence"] if result["waste_detected"] else None,
            severity=result["severity"],
            detections=detections,
            description=get_severity_description(result["severity"])
        )
        
        logger.info(
            "Inference completed successfully",
            waste_detected=result["waste_detected"],
            severity=result["severity"],
            detection_count=len(detections)
        )
        
        return response_data
        
    except httpx.HTTPStatusError as e:
        logger.error("Failed to download image", url=request.image_url, status_code=e.response.status_code)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download image: {e.response.status_code}"
        )
    except httpx.TimeoutException:
        logger.error("Image download timeout", url=request.image_url)
        raise HTTPException(
            status_code=408,
            detail="Image download timeout"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Inference failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )


# Development server configuration
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info",
        access_log=True
    )
