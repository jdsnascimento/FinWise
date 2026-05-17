from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class CategoryTypeEnum(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    icon: str = Field(default="receipt", max_length=50)
    color: str = Field(default="#10b981", max_length=7)
    type: CategoryTypeEnum

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    active: bool
    
    class Config:
        from_attributes = True