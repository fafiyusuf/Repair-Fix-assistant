"""
iFixit API integration tools.

This module provides clean, deterministic wrappers around the iFixit API
with proper response cleanup to prevent hallucination.
"""

import httpx
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

IFIXIT_API_BASE = "https://www.ifixit.com/api/2.0"


class IFixitTools:
    """Wrapper for iFixit API with response cleanup."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    @staticmethod
    def cleanup_search_results(raw_results: List[Dict]) -> List[Dict]:
        """
        Clean search results to only essential fields.
        
        Args:
            raw_results: Raw API response
            
        Returns:
            List of cleaned device entries with only title and type
        """
        cleaned = []
        for item in raw_results:
            cleaned.append({
                "title": item.get("title", ""),
                "dataType": item.get("dataType", ""),
                "url": item.get("url", "")
            })
        return cleaned
    
    @staticmethod
    def cleanup_guides_list(raw_guides: List[Dict]) -> List[Dict]:
        """
        Clean guides list to only essential fields.
        
        Args:
            raw_guides: Raw API response
            
        Returns:
            List of cleaned guides with title, ID, and subject
        """
        cleaned = []
        for guide in raw_guides:
            cleaned.append({
                "guideid": guide.get("guideid"),
                "title": guide.get("title", ""),
                "subject": guide.get("subject", ""),
                "type": guide.get("type", ""),
                "difficulty": guide.get("difficulty", "")
            })
        return cleaned
    
    @staticmethod
    def cleanup_repair_guide(raw_guide: Dict) -> Dict:
        """
        Clean repair guide to only step-by-step instructions and images.
        
        Removes: author info, revisions, comments, metadata
        Keeps: steps (order, text, images)
        
        Args:
            raw_guide: Raw API response
            
        Returns:
            Cleaned guide with only essential repair information
        """
        steps = []
        for step in raw_guide.get("steps", []):
            cleaned_step = {
                "orderby": step.get("orderby", 0),
                "title": step.get("title", ""),
                "text": step.get("text", ""),
                "images": []
            }
            
            # Extract image URLs
            for line in step.get("lines", []):
                if line.get("level") == "full" and line.get("image"):
                    img = line["image"]
                    cleaned_step["images"].append({
                        "url": img.get("standard", ""),
                        "thumbnail": img.get("thumbnail", "")
                    })
            
            steps.append(cleaned_step)
        
        return {
            "guideid": raw_guide.get("guideid"),
            "title": raw_guide.get("title", ""),
            "subject": raw_guide.get("subject", ""),
            "introduction": raw_guide.get("introduction_raw", ""),
            "difficulty": raw_guide.get("difficulty", ""),
            "time_required": raw_guide.get("time_required", ""),
            "steps": steps,
            "tools": [tool.get("text", "") for tool in raw_guide.get("tools", [])],
            "parts": [part.get("text", "") for part in raw_guide.get("parts", [])]
        }
    
    async def search_devices(self, query: str) -> Optional[Dict]:
        """
        Search for devices on iFixit.
        
        Args:
            query: Search query (e.g., "PlayStation 5")
            
        Returns:
            Cleaned search results or None if search fails
        """
        try:
            url = f"{IFIXIT_API_BASE}/search/{query}"
            params = {"filter": "device"}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.info(f"No devices found for query: {query}")
                return None
            
            cleaned = self.cleanup_search_results(results)
            logger.info(f"Found {len(cleaned)} devices for query: {query}")
            
            return {
                "query": query,
                "devices": cleaned[:5]  # Top 5 results
            }
            
        except Exception as e:
            logger.error(f"Error searching devices: {e}")
            return None
    
    async def list_guides(self, device_title: str) -> Optional[Dict]:
        """
        List available repair guides for a device.
        
        Args:
            device_title: Canonical device title (e.g., "PlayStation 5")
            
        Returns:
            Cleaned list of guides or None if request fails
        """
        try:
            # Format device title for URL
            formatted_title = device_title.replace(" ", "_")
            url = f"{IFIXIT_API_BASE}/wikis/CATEGORY/{formatted_title}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            guides = data.get("guides", [])
            
            if not guides:
                logger.info(f"No guides found for device: {device_title}")
                return None
            
            cleaned = self.cleanup_guides_list(guides)
            logger.info(f"Found {len(cleaned)} guides for device: {device_title}")
            
            return {
                "device": device_title,
                "guides": cleaned
            }
            
        except Exception as e:
            logger.error(f"Error listing guides for {device_title}: {e}")
            return None
    
    async def fetch_repair_guide(self, guide_id: int) -> Optional[Dict]:
        """
        Fetch detailed repair guide with steps and images.
        
        Args:
            guide_id: iFixit guide ID
            
        Returns:
            Cleaned repair guide or None if request fails
        """
        try:
            url = f"{IFIXIT_API_BASE}/guides/{guide_id}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            cleaned = self.cleanup_repair_guide(data)
            
            logger.info(f"Fetched repair guide {guide_id}: {cleaned.get('title')}")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error fetching guide {guide_id}: {e}")
            return None


# Singleton instance
_ifixit_tools: Optional[IFixitTools] = None


def get_ifixit_tools() -> IFixitTools:
    """Get singleton iFixit tools instance."""
    global _ifixit_tools
    if _ifixit_tools is None:
        _ifixit_tools = IFixitTools()
    return _ifixit_tools
