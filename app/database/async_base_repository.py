from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, and_, select, func, update, delete
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

T = TypeVar("T")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class AsyncBaseRepository(Generic[T, CreateSchemaType, UpdateSchemaType]):
    """Async base repository with common CRUD operations for FastAPI endpoints."""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def create(self, obj_in: CreateSchemaType) -> T:
        """Create a new record."""
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def get(self, id: UUID) -> Optional[T]:
        """Get record by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get multiple records with optional filtering."""
        query = select(self.model)
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    attr = getattr(self.model, key)
                    if isinstance(value, list):
                        filter_conditions.append(attr.in_(value))
                    else:
                        filter_conditions.append(attr == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, db_obj: T, obj_in: UpdateSchemaType) -> T:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        query = select(func.count(self.model.id))
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    attr = getattr(self.model, key)
                    if isinstance(value, list):
                        filter_conditions.append(attr.in_(value))
                    else:
                        filter_conditions.append(attr == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(self, id: UUID) -> bool:
        """Check if record exists."""
        result = await self.session.execute(
            select(func.count(self.model.id)).where(self.model.id == id)
        )
        return result.scalar() > 0
    
    async def get_latest(self, n: int = 1) -> List[T]:
        """Get latest N records."""
        query = (
            select(self.model)
            .order_by(desc(self.model.created_at))
            .limit(n)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def bulk_create(self, obj_list: List[CreateSchemaType]) -> List[T]:
        """Create multiple records in a single transaction."""
        db_objects = []
        for obj_in in obj_list:
            obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
            db_obj = self.model(**obj_data)
            db_objects.append(db_obj)
        
        self.session.add_all(db_objects)
        await self.session.commit()
        
        # Refresh all objects
        for db_obj in db_objects:
            await self.session.refresh(db_obj)
        
        return db_objects
    
    async def bulk_update(self, updates: Dict[UUID, UpdateSchemaType]) -> int:
        """Update multiple records. Returns count of updated records."""
        updated_count = 0
        
        for obj_id, obj_in in updates.items():
            obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
            
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == obj_id)
                .values(**obj_data)
            )
            updated_count += result.rowcount
        
        await self.session.commit()
        return updated_count