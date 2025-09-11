"""
Domain Repositories - {service-name} Service

Abstract repository interfaces for the {service-name} domain.
These define the contracts that infrastructure implementations must fulfill.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Import domain entities
from app.domain.entities import Example{ServiceName}Entity


class I{ServiceName}Repository(ABC):
    """
    Abstract repository interface for {service-name} operations.
    
    This interface defines the contract that infrastructure
    repositories must implement.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[Example{ServiceName}Entity]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Example{ServiceName}Entity]:
        """Get all entities."""
        pass
    
    @abstractmethod
    async def create(self, entity: Example{ServiceName}Entity) -> Example{ServiceName}Entity:
        """Create new entity."""
        pass
    
    @abstractmethod
    async def update(self, entity: Example{ServiceName}Entity) -> Optional[Example{ServiceName}Entity]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID."""
        pass


# Add more repository interfaces as needed
# class IAnotherRepository(ABC):
#     pass
