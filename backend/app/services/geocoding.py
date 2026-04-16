"""
Geocoding service - CleanGrid Phase 1
Reverse geocoding using Nominatim API
"""

import httpx
import structlog
from typing import Optional

logger = structlog.get_logger()


async def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    """
    Perform reverse geocoding to get address from coordinates
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Returns:
        Address string or None if failed
    """
    try:
        logger.info("Reverse geocoding", lat=lat, lng=lng)
        
        # Nominatim reverse geocoding API
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lng,
            "format": "json",
            "addressdetails": 1  # Get detailed address
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract address from response
            if "address" in data:
                address = data["address"]
                
                # Build formatted address
                if "house_number" in address:
                    parts = [address.get("house_number")]
                if "road" in address:
                    parts.append(address.get("road"))
                if "suburb" in address:
                    parts.append(address.get("suburb"))
                if "city" in address:
                    parts.append(address.get("city"))
                if "postcode" in address:
                    parts.append(address.get("postcode"))
                
                formatted_address = ", ".join(filter(None, parts))
                logger.info("Reverse geocoding successful", address=formatted_address)
                return formatted_address
            
            return None
            
    except httpx.TimeoutException:
        logger.warning("Reverse geocoding timeout", lat=lat, lng=lng)
        return None
        
    except Exception as e:
        logger.error("Reverse geocoding failed", lat=lat, lng=lng, error=str(e))
        return None
