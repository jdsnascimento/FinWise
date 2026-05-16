from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from ..utils.auth import verify_password, get_password_hash, create_access_token
from ..utils.dependencies import get_current_user
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra novo usuário"""
    
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Gerar token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Realiza login do usuário"""
    
    # Buscar usuário
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Gerar token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza dados do usuário logado"""
    
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    if user_data.whatsapp_connected is not None:
        current_user.whatsapp_connected = user_data.whatsapp_connected
    
    db.commit()
    db.refresh(current_user)
    
    return current_user