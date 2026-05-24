from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.category import Category
from ..schemas.category import (
    CategoryCreate, 
    CategoryUpdate, 
    CategoryResponse, 
    CategoryTypeEnum
)
from ..utils.dependencies import get_current_user
from fastapi import HTTPException, status

router = APIRouter(prefix="/api/categories", tags=["categories"])

# Categorias padrão
DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Alimentação", "icon": "restaurant", "color": "#ef4444", "type": "expense"},
    {"name": "Transporte", "icon": "car", "color": "#f97316", "type": "expense"},
    {"name": "Moradia", "icon": "home", "color": "#6366f1", "type": "expense"},
    {"name": "Saúde", "icon": "heart", "color": "#ec4899", "type": "expense"},
    {"name": "Educação", "icon": "book", "color": "#8b5cf6", "type": "expense"},
    {"name": "Lazer", "icon": "gamepad", "color": "#06b6d4", "type": "expense"},
    {"name": "Mercado", "icon": "cart", "color": "#84cc16", "type": "expense"},
    {"name": "Assinaturas", "icon": "credit-card", "color": "#64748b", "type": "expense"},
    {"name": "Pet", "icon": "credit-card", "color": "#2eba66", "type": "expense"},
]

DEFAULT_INCOME_CATEGORIES = [
    {"name": "Salário", "icon": "briefcase", "color": "#10b981", "type": "income"},
    {"name": "Freelance", "icon": "laptop", "color": "#3b82f6", "type": "income"},
    {"name": "Investimentos", "icon": "trending-up", "color": "#059669", "type": "income"},
    {"name": "Vendas", "icon": "tag", "color": "#eab308", "type": "income"},
    {"name": "Reembolso", "icon": "receipt", "color": "#a855f7", "type": "income"},
]

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    type: Optional[CategoryTypeEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista categorias do usuário"""
    query = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.active == True
    )
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.name).all()
    
    # Se não tem categorias, criar padrão
    if not categories:
        categories = create_default_categories(db, current_user.id)
        if type:
            categories = [c for c in categories if c.type == type]
    
    return categories

@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria nova categoria"""
    
    # Verificar se já existe (apenas categorias ativas)
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_data.name,
        Category.type == category_data.type,
        Category.active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria '{category_data.name}' já existe para este tipo"
        )

    # Reativar categoria desativada com o mesmo nome
    inactive = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_data.name,
        Category.type == category_data.type,
        Category.active == False
    ).first()

    if inactive:
        inactive.active = True
        inactive.icon = category_data.icon
        inactive.color = category_data.color
        db.commit()
        db.refresh(inactive)
        return inactive
    
    category = Category(
        user_id=current_user.id,
        name=category_data.name,
        icon=category_data.icon,
        color=category_data.color,
        type=category_data.type
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza categoria"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    update_data = category_data.dict(exclude_unset=True)

    if 'name' in update_data and update_data['name'] != category.name:
        duplicate = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.name == update_data['name'],
            Category.type == category.type,
            Category.active == True,
            Category.id != category_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoria '{update_data['name']}' já existe para este tipo"
            )

    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desativa categoria"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    category.active = False
    db.commit()
    
    return {"message": "Categoria desativada com sucesso"}


def create_default_categories(db: Session, user_id: int):
    """Cria categorias padrão para novo usuário"""
    categories = []
    
    for cat_data in DEFAULT_EXPENSE_CATEGORIES + DEFAULT_INCOME_CATEGORIES:
        category = Category(
            user_id=user_id,
            name=cat_data["name"],
            icon=cat_data["icon"],
            color=cat_data["color"],
            type=cat_data["type"]
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    return categories