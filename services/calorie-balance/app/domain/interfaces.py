"""
Domain interfaces for calorie-balance service.

This module defines abstract interfaces that represent the contracts
for the domain layer, following Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.entities import UcalorieUbalanceEntity


class IUcalorieUbalanceRepository(ABC):
    """
    Abstract interface for UcalorieUbalance repository operations.
    
    This interface defines the contract that any UcalorieUbalance repository
    implementation must follow, regardless of the underlying data store.
    """
    
    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> UcalorieUbalanceEntity:
        """
        Create a new calorie-balance entity.
        
        Args:
            entity_data: Dictionary containing the entity data
            
        Returns:
            Created UcalorieUbalanceEntity
            
        Raises:
            RepositoryException: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[UcalorieUbalanceEntity]:
        """
        Retrieve a calorie-balance entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            UcalorieUbalanceEntity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[UcalorieUbalanceEntity]:
        """
        Retrieve all calorie-balance entities for a specific user.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            List of UcalorieUbalanceEntity objects
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[UcalorieUbalanceEntity]:
        """
        Update a calorie-balance entity.
        
        Args:
            entity_id: The ID of the entity to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            Updated UcalorieUbalanceEntity if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a calorie-balance entity.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UcalorieUbalanceEntity]:
        """
        List all calorie-balance entities with optional pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of UcalorieUbalanceEntity objects
        """
        pass


class IUcalorieUbalanceDomainService(ABC):
    """
    Abstract interface for UcalorieUbalance domain service operations.
    
    This interface defines domain-specific business logic operations
    that don't naturally fit within the entity itself.
    """
    
    @abstractmethod
    async def validate_calorie_balance_data(self, entity_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate calorie-balance data according to business rules.
        
        Args:
            entity_data: The data to validate
            
        Returns:
            Dictionary with validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def calculate_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate metrics for user's calorie-balance data.
        
        Args:
            user_id: The user ID to calculate metrics for
            
        Returns:
            Dictionary containing calculated metrics
        """
        pass
    
    @abstractmethod
    async def generate_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate insights based on user's calorie-balance data.
        
        Args:
            user_id: The user ID to generate insights for
            
        Returns:
            List of insight dictionaries
        """
        pass


class IEventPublisher(ABC):
    """
    Abstract interface for publishing domain events.
    
    This interface allows the domain layer to publish events
    without knowing about the specific event system implementation.
    """
    
    @abstractmethod
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish a domain event.
        
        Args:
            event_type: Type of the event
            event_data: Event payload data
        """
        pass
    
    @abstractmethod
    async def publish_calorie_balance_created(self, entity: UcalorieUbalanceEntity) -> None:
        """
        Publish event when a calorie-balance entity is created.
        
        Args:
            entity: The created entity
        """
        pass
    
    @abstractmethod
    async def publish_calorie_balance_updated(self, entity: UcalorieUbalanceEntity) -> None:
        """
        Publish event when a calorie-balance entity is updated.
        
        Args:
            entity: The updated entity
        """
        pass
    
    @abstractmethod
    async def publish_calorie_balance_deleted(self, entity_id: str, user_id: str) -> None:
        """
        Publish event when a calorie-balance entity is deleted.
        
        Args:
            entity_id: The ID of the deleted entity
            user_id: The ID of the user who owned the entity
        """
        pass


class ICacheService(ABC):
    """
    Abstract interface for caching operations.
    
    This interface allows the application layer to cache data
    without knowing about the specific caching implementation.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists, None otherwise
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
        """
        pass
    
    @abstractmethod
    async def clear_user_cache(self, user_id: str) -> None:
        """
        Clear all cache entries for a specific user.
        
        Args:
            user_id: The user ID
        """
        pass
