from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from pydantic import BaseModel

T = TypeVar("T")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[T, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
    
    def create(self, obj_in: CreateSchemaType) -> T:
        """Create a new record."""
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def get(self, id: UUID) -> Optional[T]:
        """Get record by ID."""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get multiple records with optional filtering."""
        query = self.session.query(self.model)
        
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
                query = query.filter(and_(*filter_conditions))
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, db_obj: T, obj_in: UpdateSchemaType) -> T:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        obj = self.session.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        query = self.session.query(self.model)
        
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
                query = query.filter(and_(*filter_conditions))
        
        return query.count()
    
    def exists(self, id: UUID) -> bool:
        """Check if record exists."""
        return self.session.query(
            self.session.query(self.model).filter(self.model.id == id).exists()
        ).scalar()
    
    def get_latest(self, n: int = 1) -> List[T]:
        """Get latest N records."""
        return (
            self.session.query(self.model)
            .order_by(desc(self.model.created_at))
            .limit(n)
            .all()
        )