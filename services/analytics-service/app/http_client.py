"""
HTTP Client for Analytics Service
Handles communication with other microservices
"""

from typing import Dict, List, Optional, Any
from datetime import date
import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


class ServiceClient:
    """Base client for microservice communication"""
    
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": f"analytics-service/{settings.VERSION}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Execute GET request to service endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error to {self.service_name}",
                         url=url, error=str(e))
            msg = f"{self.service_name} unavailable"
            raise ServiceUnavailableError(msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from {self.service_name}",
                         url=url, status=e.response.status_code,
                         response=e.response.text)
            msg = f"{self.service_name} returned {e.response.status_code}"
            raise ServiceError(msg)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """Execute POST request to service endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error to {self.service_name}",
                         url=url, error=str(e))
            msg = f"{self.service_name} unavailable"
            raise ServiceUnavailableError(msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from {self.service_name}",
                         url=url, status=e.response.status_code,
                         response=e.response.text)
            msg = f"{self.service_name} returned {e.response.status_code}"
            raise ServiceError(msg)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class UserManagementClient(ServiceClient):
    """Client for User Management Service"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.USER_MANAGEMENT_URL,
            service_name="user-management"
        )
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile data"""
        return await self.get(f"/api/users/{user_id}")
    
    async def get_daily_fitness_data(
        self, 
        user_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Get enhanced daily fitness data"""
        params = {
            "user_id": user_id,
            "limit": limit
        }
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        response = await self.get("/api/fitness/daily-data", params=params)
        return response.get("data", [])
    
    async def get_user_activities(
        self, 
        user_id: str,
        activity_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get enhanced user activities"""
        params = {
            "user_id": user_id,
            "limit": limit
        }
        if activity_type:
            params["activity_type"] = activity_type
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        response = await self.get("/api/activities", params=params)
        return response.get("activities", [])
    
    async def get_fitness_history(
        self, 
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive fitness history with activities"""
        params = {
            "user_id": user_id,
            "days": days
        }
        return await self.get("/api/fitness/history", params=params)


# Custom Exceptions
class ServiceError(Exception):
    """Service communication error"""
    pass


class ServiceUnavailableError(ServiceError):
    """Service unavailable error"""  
    pass


# Singleton instances
user_management_client = UserManagementClient()


async def cleanup_clients():
    """Cleanup all HTTP clients"""
    await user_management_client.close()
