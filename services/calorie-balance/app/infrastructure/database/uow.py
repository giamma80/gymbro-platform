from sqlalchemy.ext.asyncio import AsyncSession

from ...core.interfaces import UnitOfWork


class SqlUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work pattern"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
    
    async def __aenter__(self):
        """Enter async context"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if exc_type is not None:
            await self.rollback()
        elif not self._committed:
            await self.commit()
    
    async def commit(self) -> None:
        """Commit transaction"""
        if not self._committed:
            await self.session.commit()
            self._committed = True
    
    async def rollback(self) -> None:
        """Rollback transaction"""
        await self.session.rollback()
        self._committed = False
