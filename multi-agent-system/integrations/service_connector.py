from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import aiohttp
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
NEWSAPI_BASE_URL = "https://newsapi.org/v2"
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
TWITTER_API_BASE_URL = "https://api.twitter.com/2"
REDDIT_API_BASE_URL = "https://oauth.reddit.com"

class ServiceConnector(ABC):
    """Base class for all service connectors and integrations."""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the service."""
        pass

class CrewAIConnector(ServiceConnector):
    """Connector for CrewAI service."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.crewai.com")  # Replace with actual CrewAI API URL
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/auth",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"CrewAI authentication error: {e}")
            return False

    async def create_agent(self, agent_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new agent in CrewAI."""
        try:
            async with self.session.post(
                f"{self.base_url}/agents",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=agent_config
            ) as response:
                if response.status == 201:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"CrewAI agent creation error: {e}")
            return None

class TaskadeConnector(ServiceConnector):
    """Connector for Taskade service."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.taskade.com")  # Replace with actual Taskade API URL
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/auth",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Taskade authentication error: {e}")
            return False

    async def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new task in Taskade."""
        try:
            async with self.session.post(
                f"{self.base_url}/tasks",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=task_data
            ) as response:
                if response.status == 201:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Taskade task creation error: {e}")
            return None

class NewsAPIConnector(ServiceConnector):
    """Connector for NewsAPI service."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, NEWSAPI_BASE_URL)
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/top-headlines",
                params={"apiKey": self.api_key, "pageSize": 1}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"NewsAPI authentication error: {e}")
            return False

    async def get_trending_news(self, categories: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get trending news articles."""
        try:
            params = {
                "apiKey": self.api_key,
                "language": "en",
                "sortBy": "popularity"
            }
            if categories:
                params["category"] = ",".join(categories)
                
            async with self.session.get(
                f"{self.base_url}/top-headlines",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"NewsAPI trending news error: {e}")
            return None

class BinanceConnector(ServiceConnector):
    """Connector for Binance cryptocurrency exchange."""
    
    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, BINANCE_BASE_URL)
        self.secret_key = secret_key
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/ping",
                headers={"X-MBX-APIKEY": self.api_key}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Binance authentication error: {e}")
            return False

    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data for a specific trading pair."""
        try:
            async with self.session.get(
                f"{self.base_url}/ticker/24hr",
                params={"symbol": symbol}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Binance market data error: {e}")
            return None

    async def execute_trade(self, symbol: str, side: str, quantity: float) -> Optional[Dict[str, Any]]:
        """Execute a trade on Binance."""
        try:
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": "MARKET",
                "quantity": quantity,
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            
            async with self.session.post(
                f"{self.base_url}/order",
                headers={"X-MBX-APIKEY": self.api_key},
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Binance trade execution error: {e}")
            return None

class SocialMediaConnector(ServiceConnector):
    """Connector for social media trend monitoring."""
    
    def __init__(self, twitter_api_key: str, reddit_api_key: str):
        self.twitter_connector = TwitterConnector(twitter_api_key)
        self.reddit_connector = RedditConnector(reddit_api_key)
        
    async def authenticate(self) -> bool:
        twitter_auth = await self.twitter_connector.authenticate()
        reddit_auth = await self.reddit_connector.authenticate()
        return twitter_auth and reddit_auth

    async def get_trending_topics(self) -> Dict[str, Any]:
        """Get trending topics from multiple social media platforms."""
        twitter_trends = await self.twitter_connector.get_trends()
        reddit_trends = await self.reddit_connector.get_trends()
        
        return {
            "twitter": twitter_trends,
            "reddit": reddit_trends,
            "timestamp": datetime.now().isoformat()
        }

class TwitterConnector(ServiceConnector):
    """Connector for Twitter API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, TWITTER_API_BASE_URL)
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/tweets/search/recent",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Twitter authentication error: {e}")
            return False

    async def get_trends(self) -> Optional[Dict[str, Any]]:
        """Get trending topics on Twitter."""
        try:
            async with self.session.get(
                f"{self.base_url}/trends/place",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"id": 1}  # 1 for worldwide trends
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Twitter trends error: {e}")
            return None

class RedditConnector(ServiceConnector):
    """Connector for Reddit API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, REDDIT_API_BASE_URL)
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/me",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Reddit authentication error: {e}")
            return False

    async def get_trends(self) -> Optional[Dict[str, Any]]:
        """Get trending topics on Reddit."""
        try:
            async with self.session.get(
                f"{self.base_url}/r/all/hot",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"limit": 25}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Reddit trends error: {e}")
            return None

class AbacusConnector(ServiceConnector):
    """Connector for Abacus service."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.abacus.ai")
        
    async def authenticate(self) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}/auth",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Abacus authentication error: {e}")
            return False

    async def get_model_prediction(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get predictions from Abacus AI models."""
        try:
            async with self.session.post(
                f"{self.base_url}/predict",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Abacus prediction error: {e}")
            return None
