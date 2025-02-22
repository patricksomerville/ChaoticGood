import aiohttp
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlackBoxConnector:
    """Connector for BlackBox AI API integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.useblackbox.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def code_completion(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get code completion from BlackBox AI."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/code-completion",
                    headers=self.headers,
                    json={"prompt": prompt}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"BlackBox API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling BlackBox API: {e}")
            return None

    async def code_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Search code using BlackBox AI."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/code-search",
                    headers=self.headers,
                    json={"query": query}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"BlackBox API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling BlackBox API: {e}")
            return None

    async def generate_documentation(self, code: str) -> Optional[Dict[str, Any]]:
        """Generate documentation for code using BlackBox AI."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate-docs",
                    headers=self.headers,
                    json={"code": code}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"BlackBox API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling BlackBox API: {e}")
            return None
