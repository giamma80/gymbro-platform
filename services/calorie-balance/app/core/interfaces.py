from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Base repository interface for CRUD operations"""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        pass


class UnitOfWork(ABC):
    """Unit of Work pattern for managing transactions"""
    
    @abstractmethod
    async def __aenter__(self):
        """Enter async context"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction"""
        pass
