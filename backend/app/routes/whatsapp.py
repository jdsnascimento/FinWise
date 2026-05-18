from sqlalchemy import func
from pydantic import functional_serializers
from fastapi import param_functions
from fastapi import param_functions
from decimal import Decimal
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import param_functions
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.user import User
from ..models.whatsapp_instance import WhatsAppInstance, ConnectionStatus
from ..services.whatsapp_service import whatsapp_service
from ..services.bill_service import BillService
from ..services.income_service import IncomeService
from ..schemas.bill import BillCreate
from ..schemas.income import IncomeCreate
from ..utils.dependencies import get_current_user
from datetime import date

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

class CreateInstanceRequest(BaseModel):
    instance_name: str
    phone_number: str

@router.post("/instance/create")
async def create_instance(
    data: CreateInstanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria nova instância WhatsApp"""
    
    # Verificar se já existe instância
    existing = db.query(WhatsAppInstance).filter(
        WhatsAppInstance.user_id == current_user.id
    ).first()
    
    if existing:
        # Reativar instância existente
        result = await whatsapp_service.create_instance(
            data.instance_name,
            data.phone_number
        )
        existing.instance_name = data.instance_name
        existing.phone_number = data.phone_number
        existing.connection_status = ConnectionStatus.CONNECTING
        db.commit()
        return result
    
    # Criar no Evolution API
    result = await whatsapp_service.create_instance(
        data.instance_name,
        data.phone_number
    )
    
    # Salvar no banco
    instance = WhatsAppInstance(
        user_id=current_user.id,
        instance_name=data.instance_name,
        phone_number=data.phone_number,
        connection_status=ConnectionStatus.CONNECTING
    )
    db.add(instance)
    db.commit()
    
    return result

@router.get("/instance/qrcode")
async def get_qrcode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém QR Code para conectar WhatsApp"""
    instance = db.query(WhatsAppInstance).filter(
        WhatsAppInstance.user_id == current_user.id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Nenhuma instância encontrada")
    
    qrcode = await whatsapp_service.get_qrcode(instance.instance_name)
    
    if qrcode:
        instance.qrcode_base64 = qrcode
        db.commit()
    
    return {"qrcode": qrcode}

@router.get("/instance/status")
async def get_instance_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica status da conexão"""
    instance = db.query(WhatsAppInstance).filter(
        WhatsAppInstance.user_id == current_user.id
    ).first()
    
    if not instance:
        return {"status": "disconnected", "message": "Nenhuma instância configurada"}
    
    status = await whatsapp_service.get_instance_status(instance.instance_name)
    
    # Atualizar status
    status_map = {
        "open": ConnectionStatus.CONNECTED,
        "connecting": ConnectionStatus.CONNECTING,
        "close": ConnectionStatus.DISCONNECTED
    }
    
    new_status = status_map.get(status, ConnectionStatus.DISCONNECTED)
    instance.connection_status = new_status
    
    if new_status == ConnectionStatus.CONNECTED:
        instance.last_connected = func.now()
        # Atualizar usuário
        current_user.whatsapp_connected = True
    
    db.commit()
    
    return {"status": status, "connection_status": new_status}

@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook que recebe mensagens do WhatsApp via Evolution API
    """
    try:
        data = await request.json()
        
        # Verificar se é evento de mensagem
        if data.get("event") != "MESSAGES_UPSERT":
            return {"status": "ignored"}
        
        message_data = data.get("data", {}).get("message", {})
        
        # Verificar se é mensagem de texto
        if message_data.get("messageType") != "conversation":
            return {"status": "ignored"}
        
        text = message_data.get("conversation", "")
        sender = data.get("data", {}).get("key", {}).get("remoteJid", "").split("@")[0]
        
        # Buscar usuário pelo número
        instance_name = data.get("instance", "")
        instance = db.query(WhatsAppInstance).filter(
            WhatsAppInstance.instance_name == instance_name
        ).first()
        
        if not instance:
            return {"status": "error", "message": "Instância não encontrada"}
        
        # Parse da mensagem
        parsed = whatsapp_service.parse_financial_message(text)
        
        if parsed['amount'] and parsed['confidence'] > 30:
            # Salvar no banco
            if parsed['type'] == 'income':
                # Criar receita
                income_data = IncomeCreate(
                    description=parsed['description'] or 'Receita via WhatsApp',
                    amount=Decimal(str(parsed['amount'])),
                    expected_date=date.today(),
                    category_id=1,  # Categoria padrão
                    notes=f"Mensagem original: {text}"
                )
                IncomeService.create_income(db, instance.user_id, income_data)
            else:
                # Criar despesa
                bill_data = BillCreate(
                    description=parsed['description'] or 'Gasto via WhatsApp',
                    amount=Decimal(str(parsed['amount'])),
                    installments=parsed['installments'],
                    purchase_date=date.today(),
                    category_id=1,  # Categoria padrão
                    payment_type=parsed['payment_method'],
                    notes=f"Mensagem original: {text}"
                )
                BillService.create_bill(db, instance.user_id, bill_data)
            
            # Confirmar para o usuário
            await whatsapp_service.send_message(
                instance_name,
                sender,
                f"✅ Registrado! {parsed['description'] or 'Gasto'} - R$ {parsed['amount']:.2f}"
            )
        
        return {"status": "processed", "parsed": parsed}
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/test-message")
async def test_parse_message(request: Request):
    """Testa o parser de mensagem"""
    data = await request.json()
    message = data.get("message", "")
    return whatsapp_service.parse_financial_message(message)