from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class CategoryType(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    icon = Column(String(50), default="receipt")
    color = Column(String(7), default="#10b981")
    type = Column(Enum(CategoryType), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="categories")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'type', name='uk_user_category'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"