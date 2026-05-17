from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.credit_card import (
    CreditCardCreate, 
    CreditCardUpdate, 
    CreditCardResponse,
    CreditCardSummary
)
from ..services.credit_card_service import CreditCardService
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/credit-cards", tags=["credit-cards"])

@router.get("/", response_model=List[CreditCardResponse])
async def list_cards(
    active_only: bool = Query(False, description="Apenas cartões ativos"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos os cartões do usuário"""
    return CreditCardService.get_user_cards(db, current_user.id, active_only)

@router.get("/summary", response_model=List[CreditCardSummary])
async def list_cards_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista resumo dos cartões para dashboard"""
    cards = CreditCardService.get_user_cards(db, current_user.id, True)
    
    summaries = []
    for card in cards:
        summary = CreditCardService.get_card_summary(db, card.id, current_user.id)
        summaries.append(CreditCardSummary(
            id=card.id,
            name=card.name,
            bank=card.bank,
            flag=card.flag,
            limit_amount=card.limit_amount,
            available_limit=card.available_limit,
            usage_percentage=summary['usage_percentage'],
            color=card.color,
            current_bill_total=summary['current_bill_total']
        ))
    
    return summaries

@router.get("/{card_id}", response_model=CreditCardResponse)
async def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um cartão"""
    return CreditCardService.get_card_by_id(db, card_id, current_user.id)

@router.get("/{card_id}/details")
async def get_card_details(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes completos do cartão com resumo"""
    return CreditCardService.get_card_summary(db, card_id, current_user.id)

@router.post("/", response_model=CreditCardResponse, status_code=201)
async def create_card(
    card_data: CreditCardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo cartão de crédito"""
    return CreditCardService.create_card(db, current_user.id, card_data)

@router.put("/{card_id}", response_model=CreditCardResponse)
async def update_card(
    card_id: int,
    card_data: CreditCardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um cartão existente"""
    return CreditCardService.update_card(db, card_id, current_user.id, card_data)

@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desativa um cartão"""
    return CreditCardService.delete_card(db, card_id, current_user.id)