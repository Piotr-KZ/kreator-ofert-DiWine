"""
Base model with common fields
All models inherit from this base
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from fasthub_core.db.session import Base


class BaseModel(Base):
    """
    Base model with common fields:
    - id: UUID primary key
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    """

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower() + "s"

    def dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
