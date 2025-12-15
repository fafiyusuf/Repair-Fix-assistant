"""
iFixit API integration tools.

This module provides clean, deterministic wrappers around the iFixit API
with proper response cleanup to prevent hallucination.
"""

import httpx
from typing import List, Dict, Optional, Any
import logging
import re

logger = logging.getLogger(__name__)

IFIXIT_API_BASE = "https://www.ifixit.com/api/2.0"


def convert_ifixit_markup_to_markdown(text: str) -> str:
    """
    Convert iFixit markup to proper Markdown.
    
    Converts:
    - [product|ID|text|new_window=true] -> [text](https://www.ifixit.com/products/ID)
    - [link|url|text|new_window=true] -> [text](url)
    - [guide|ID|text] -> [text](https://www.ifixit.com/Guide/ID)
    
    Args:
        text: Text with iFixit markup
        
    Returns:
        Text with proper Markdown links
    """
    if not text:
        return text
    
    # Convert product links: [product|IF442-000|iPhone 12 screen|new_window=true]
    text = re.sub(
        r'\[product\|([^|]+)\|([^|]+)(?:\|[^\]]+)?\]',
        r'[\2](https://www.ifixit.com/products/\1)',
        text
    )
    
    # Convert external links: [link|https://example.com|Link Text|new_window=true]
    text = re.sub(
        r'\[link\|([^|]+)\|([^|]+)(?:\|[^\]]+)?\]',
        r'[\2](\1)',
        text
    )
    
    # Convert guide links: [guide|12345|Guide Title]
    text = re.sub(
        r'\[guide\|([^|]+)\|([^|]+)(?:\|[^\]]+)?\]',
        r'[\2](https://www.ifixit.com/Guide/\1)',
        text
    )
    
    # Convert document links: [document|URL|Text]
    text = re.sub(
        r'\[document\|([^|]+)\|([^|]+)(?:\|[^\]]+)?\]',
        r'[\2](\1)',
        text
    )
    
    return text


class IFixitTools:
    """Wrapper for iFixit API with response cleanup."""
    
    def __init__(self):
        # Add User-Agent header to prevent rate limiting
        headers = {
            "User-Agent": "RepairFixAssistant/1.0 (https://github.com/fafiyusuf/Repair-Fix-assistant)"
        }
        self.client = httpx.AsyncClient(timeout=30.0, headers=headers)
    
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
            # Convert iFixit markup to markdown in step text
            step_text = convert_ifixit_markup_to_markdown(step.get("text", ""))
            
            cleaned_step = {
                "orderby": step.get("orderby", 0),
                "title": step.get("title", ""),
                "text": step_text,
                "images": []
            }
            
            # Extract images from media array (correct location)
            media = step.get("media", {})
            if isinstance(media, dict):
                # Media can be a dict with type and data
                if media.get("type") == "image" and media.get("data"):
                    for img in media["data"]:
                        cleaned_step["images"].append({
                            "url": img.get("standard", img.get("original", "")),
                            "thumbnail": img.get("thumbnail", "")
                        })
            
            # Fallback: Also check lines array for older API format
            for line in step.get("lines", []):
                if line.get("level") == "full" and line.get("image"):
                    img = line["image"]
                    cleaned_step["images"].append({
                        "url": img.get("standard", ""),
                        "thumbnail": img.get("thumbnail", "")
                    })
            
            steps.append(cleaned_step)
        
        # Convert iFixit markup to markdown in introduction
        introduction = convert_ifixit_markup_to_markdown(raw_guide.get("introduction_raw", ""))
        
        return {
            "guideid": raw_guide.get("guideid"),
            "title": raw_guide.get("title", ""),
            "subject": raw_guide.get("subject", ""),
            "introduction": introduction,
            "difficulty": raw_guide.get("difficulty", ""),
            "time_required": raw_guide.get("time_required", ""),
            "steps": steps,
            "tools": [tool.get("text", "") for tool in raw_guide.get("tools", [])],
            "parts": [part.get("text", "") for part in raw_guide.get("parts", [])]
        }
    
    async def search_devices(self, query: str) -> Optional[Dict]:
        """
        Search for devices on iFixit using the official search endpoint.
        
        Endpoint: GET https://www.ifixit.com/api/2.0/search/{QUERY}?filter=device
        
        Args:
            query: Search query (e.g., "PlayStation 5")
            
        Returns:
            Cleaned search results or None if search fails
        """
        try:
            # Use official search API with device filter as per requirements
            search_url = f"{IFIXIT_API_BASE}/search/{query}"
            
            response = await self.client.get(search_url, params={
                "filter": "device"
            })
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                logger.info(f"iFixit search API for '{query}': {len(results)} results")
                
                if results:
                    # Filter and clean device results
                    cleaned = []
                    for r in results[:10]:  # Check top 10 results
                        title = r.get("title", r.get("name", ""))
                        data_type = r.get("dataType", r.get("type", "device"))
                        
                        # Skip guide-like results (troubleshooting, replacement, repair guides)
                        title_lower = title.lower()
                        
                        # Expanded list of guide/component indicators to skip
                        skip_words = [
                            "troubleshooting", "replacement", "repair", "disassembly", 
                            "teardown", "install", "won't", "doesn't", "not working",
                            "disk drive", "power supply", "fan", "motherboard", "battery",
                            "screen", "lcd", "controller", "charging port", "hdmi",
                            "optical drive", "hard drive", "ssd", "cooling", "heatsink"
                        ]
                        
                        if any(skip_word in title_lower for skip_word in skip_words):
                            logger.info(f"Skipping component/guide result: {title}")
                            continue
                        
                        # Add valid device results
                        cleaned.append({
                            "title": title,
                            "dataType": data_type,
                            "url": r.get("url", "")
                        })
                    
                    if cleaned:
                        logger.info(f"Filtered to {len(cleaned)} device results")
                        return {
                            "query": query,
                            "devices": cleaned[:5]  # Top 5 results
                        }
                    else:
                        logger.warning("All search results were guide/component-type")
            
            # If search failed or returned no valid devices, create synthetic device entry
            # This allows us to skip directly to searching for guides
            logger.info(f"Creating synthetic device entry for '{query}' to search guides directly")
            return {
                "query": query,
                "devices": [{
                    "title": query,  # Use the clean device name directly
                    "dataType": "synthetic",
                    "url": ""
                }]
            }
            
        except Exception as e:
            logger.error(f"Error searching devices: {e}")
            # Return synthetic device entry as fallback
            return {
                "query": query,
                "devices": [{
                    "title": query,
                    "dataType": "synthetic",
                    "url": ""
                }]
            }
    
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
            
            # Try category endpoint first
            url = f"{IFIXIT_API_BASE}/wikis/CATEGORY/{formatted_title}"
            
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                guides = data.get("guides", [])
                
                if guides:
                    cleaned = self.cleanup_guides_list(guides)
                    logger.info(f"Found {len(cleaned)} guides for category: {device_title}")
                    return {
                        "device": device_title,
                        "guides": cleaned
                    }
            
            # Category not found, try direct search for guides
            logger.info(f"Category not found, searching for '{device_title}' guides directly")
            
            search_url = f"{IFIXIT_API_BASE}/search/{formatted_title}"
            response = await self.client.get(search_url, params={"filter": "guide"})
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    # Filter to only guides for this device
                    device_guides = []
                    for r in results:
                        # Check if guide is for this device
                        subject = r.get("subject", "").lower()
                        title_check = device_title.lower()
                        
                        if title_check in subject or title_check in r.get("title", "").lower():
                            device_guides.append(r)
                    
                    if device_guides:
                        cleaned = self.cleanup_guides_list(device_guides)
                        logger.info(f"Found {len(cleaned)} guides via search for: {device_title}")
                        return {
                            "device": device_title,
                            "guides": cleaned
                        }
            
            logger.info(f"No guides found for device: {device_title}")
            return None
            
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
