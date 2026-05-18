from sqlalchemy import func
from decimal import Decimal
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.user import User
from ..models.whatsapp_instance import WhatsAppInstance, ConnectionStatus
from ..models.category import Category
from ..models.credit_card import CreditCard
from ..models.bill import Bill, BillStatus
from ..services.whatsapp_service import whatsapp_service
from ..services.bill_service import BillService
from ..services.income_service import IncomeService
from ..schemas.bill import BillCreate, PaymentTypeEnum
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
    
    # Usar nome fixo para o usuário (evita criar múltiplas instâncias)
    stable_name = f"finwise_{current_user.id}"
    
    # Verificar se já existe instância no banco
    existing = db.query(WhatsAppInstance).filter(
        WhatsAppInstance.user_id == current_user.id
    ).first()
    
    # Criar instância na Evolution API (sempre usa o nome estável)
    result = await whatsapp_service.create_instance(
        stable_name,
        data.phone_number
    )
    
    if existing:
        # Atualizar instância existente
        existing.instance_name = stable_name
        existing.phone_number = data.phone_number
        existing.connection_status = ConnectionStatus.CONNECTING
        db.commit()
    else:
        # Salvar no banco
        instance = WhatsAppInstance(
            user_id=current_user.id,
            instance_name=stable_name,
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
        return {"status": "disconnected", "connection_status": "disconnected", "message": "Nenhuma instância configurada"}
    
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


def get_pending_bills_summary(db: Session, user_id: int) -> str:
    """Gera resumo de contas pendentes para enviar via WhatsApp"""
    pending_bills = db.query(Bill).filter(
        Bill.user_id == user_id,
        Bill.status == BillStatus.PENDING
    ).order_by(Bill.due_date.asc()).limit(10).all()
    
    if not pending_bills:
        return "✅ Você não tem contas pendentes! 🎉"
    
    total = sum(b.total_amount for b in pending_bills)
    
    msg = f"📋 *Contas Pendentes* ({len(pending_bills)})\n\n"
    
    for i, bill in enumerate(pending_bills, 1):
        due_str = bill.due_date.strftime("%d/%m/%Y") if bill.due_date else "Sem data"
        cat_name = bill.category.name if bill.category else ""
        msg += f"{i}. {bill.description}\n"
        msg += f"   💰 R$ {bill.total_amount:,.2f}"
        if cat_name:
            msg += f" | 📂 {cat_name}"
        msg += f"\n   📅 Vence: {due_str}\n\n"
    
    msg += f"💵 *Total Pendente: R$ {total:,.2f}*"
    
    return msg


@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook que recebe mensagens do WhatsApp via Evolution API.
    Aceita mensagens próprias (fromMe) para o usuário conversar consigo mesmo.
    """
    try:
        data = await request.json()
        
        print(f"[WEBHOOK] Evento recebido: {data.get('event', 'unknown')}")
        
        # Verificar se é evento de mensagem (suporta v1 e v2)
        event = data.get("event", "")
        if event not in ["MESSAGES_UPSERT", "messages.upsert"]:
            return {"status": "ignored", "reason": f"event: {event}"}
        
        data_obj = data.get("data", {})
        key = data_obj.get("key", {})
        message_data = data_obj.get("message", {})
        
        # Extrair texto da mensagem (suporta vários formatos do WhatsApp)
        text = ""
        
        # Formato 1: conversation (mensagem normal)
        if message_data.get("conversation"):
            text = message_data["conversation"]
        # Formato 2: extendedTextMessage (mensagem com link preview, etc)
        elif message_data.get("extendedTextMessage", {}).get("text"):
            text = message_data["extendedTextMessage"]["text"]
        # Formato 3: messageContextInfo (resposta a mensagem)
        elif message_data.get("extendedTextMessage", {}).get("contextInfo", {}).get("quotedMessage", {}).get("conversation"):
            text = message_data["extendedTextMessage"]["text"]
            
        if not text:
            print(f"[WEBHOOK] Mensagem sem texto. messageType: {data_obj.get('messageType', 'unknown')}")
            return {"status": "ignored", "reason": "no text found"}
        
        print(f"[WEBHOOK] Texto: {text} | fromMe: {key.get('fromMe', False)}")
        
        sender = key.get("remoteJid", "").split("@")[0]
        is_from_me = key.get("fromMe", False)
        
        # Buscar instância pelo nome
        instance_name = data.get("instance", "")
        instance = db.query(WhatsAppInstance).filter(
            WhatsAppInstance.instance_name == instance_name
        ).first()
        
        if not instance:
            print(f"[WEBHOOK] Instância não encontrada: {instance_name}")
            return {"status": "error", "message": "Instância não encontrada"}
        
        # Se é fromMe, o sender é o próprio usuário, usar o número da instância
        reply_to = sender if not is_from_me else instance.phone_number
        
        # ===== COMANDOS DE CONSULTA =====
        text_lower = text.lower().strip()
        
        # Comando: consultar pendentes
        consulta_keywords = ['pendentes', 'pendente', 'contas', 'resumo', 'saldo', 'devo', 'quanto devo', 'status']
        if any(text_lower == kw or text_lower.startswith(kw) for kw in consulta_keywords):
            summary = get_pending_bills_summary(db, instance.user_id)
            await whatsapp_service.send_message(instance_name, reply_to, summary)
            return {"status": "processed", "action": "query_pending"}
        
        # Comando: ajuda
        ajuda_keywords = ['ajuda', 'help', 'comandos', 'como usar', 'menu']
        if any(text_lower == kw for kw in ajuda_keywords):
            help_msg = (
                "📱 *FinWise - Comandos*\n\n"
                "💸 *Registrar Despesa:*\n"
                "• _Paguei 150 mercado no Nubank 3x_\n"
                "• _Gastei 89.90 uber_\n"
                "• _pix 150 jantar_\n\n"
                "💰 *Registrar Receita:*\n"
                "• _Recebi 5000 salário_\n\n"
                "📋 *Consultar:*\n"
                "• _pendentes_ - Ver contas pendentes\n"
                "• _resumo_ - Ver resumo financeiro\n\n"
                "❓ _ajuda_ - Ver este menu"
            )
            await whatsapp_service.send_message(instance_name, reply_to, help_msg)
            return {"status": "processed", "action": "help"}
        
        # ===== PARSE DE MENSAGEM FINANCEIRA =====
        parsed = whatsapp_service.parse_financial_message(text)
        
        if parsed['amount'] and parsed['confidence'] > 30:
            # Buscar categoria do usuário
            category = None
            target_type = 'income' if parsed['type'] == 'income' else 'expense'
            
            if parsed.get('category_hint'):
                category = db.query(Category).filter(
                    Category.user_id == instance.user_id,
                    Category.type == target_type,
                    Category.name.ilike(f"%{parsed['category_hint']}%"),
                    Category.active == True
                ).first()
                
            if not category:
                category = db.query(Category).filter(
                    Category.user_id == instance.user_id,
                    Category.type == target_type,
                    Category.active == True
                ).first()
                
            if not category:
                # Se não tiver categorias, cria as padrão
                from ..routes.categories import create_default_categories
                cats = create_default_categories(db, instance.user_id)
                for c in cats:
                    if c.type == target_type:
                        category = c
                        break
            
            if not category:
                await whatsapp_service.send_message(
                    instance_name, reply_to,
                    "❌ Erro: nenhuma categoria encontrada. Acesse o FinWise e configure suas categorias."
                )
                return {"status": "error", "message": "Nenhuma categoria encontrada"}

            # Salvar no banco
            if parsed['type'] == 'income':
                # Criar receita
                income_data = IncomeCreate(
                    description=parsed['description'] or 'Receita via WhatsApp',
                    amount=Decimal(str(parsed['amount'])),
                    expected_date=date.today(),
                    category_id=category.id,
                    notes=f"Mensagem original: {text}"
                )
                IncomeService.create_income(db, instance.user_id, income_data)
                
                await whatsapp_service.send_message(
                    instance_name, reply_to,
                    f"✅ *Receita registrada!*\n"
                    f"📝 {parsed['description'] or 'Receita'}\n"
                    f"💰 R$ {parsed['amount']:,.2f}\n"
                    f"📂 {category.name}"
                )
            else:
                # Mapear payment_method para PaymentTypeEnum
                payment_map = {
                    'credit_card': PaymentTypeEnum.CREDIT_CARD,
                    'debito': PaymentTypeEnum.DEBIT_CARD,
                    'debit_card': PaymentTypeEnum.DEBIT_CARD,
                    'dinheiro': PaymentTypeEnum.CASH,
                    'cash': PaymentTypeEnum.CASH,
                    'pix': PaymentTypeEnum.PIX,
                    'boleto': PaymentTypeEnum.BOLETO,
                    'transfer': PaymentTypeEnum.TRANSFER
                }
                payment_type = payment_map.get(parsed.get('payment_method'), PaymentTypeEnum.CASH)
                
                card_id = None
                card_name = None
                if payment_type == PaymentTypeEnum.CREDIT_CARD:
                    card = None
                    if parsed.get('card_hint'):
                        card = db.query(CreditCard).filter(
                            CreditCard.user_id == instance.user_id,
                            CreditCard.active == True,
                            CreditCard.name.ilike(f"%{parsed['card_hint']}%")
                        ).first()
                    
                    if not card:
                        card = db.query(CreditCard).filter(
                            CreditCard.user_id == instance.user_id,
                            CreditCard.active == True
                        ).first()
                        
                    if card:
                        card_id = card.id
                        card_name = card.name
                    else:
                        # Se não tem cartão cadastrado, muda para PIX
                        payment_type = PaymentTypeEnum.PIX

                # Criar despesa
                bill_data = BillCreate(
                    description=parsed['description'] or 'Gasto via WhatsApp',
                    amount=Decimal(str(parsed['amount'])),
                    installments=parsed['installments'],
                    purchase_date=date.today(),
                    category_id=category.id,
                    card_id=card_id,
                    payment_type=payment_type,
                    notes=f"Mensagem original: {text}"
                )
                BillService.create_bill(db, instance.user_id, bill_data)
                
                # Montar mensagem de confirmação
                confirm_msg = (
                    f"✅ *Despesa registrada!*\n"
                    f"📝 {parsed['description'] or 'Gasto'}\n"
                    f"💰 R$ {parsed['amount']:,.2f}\n"
                    f"📂 {category.name}"
                )
                if parsed['installments'] > 1:
                    confirm_msg += f"\n🔄 {parsed['installments']}x de R$ {parsed['amount']:,.2f}"
                if card_name:
                    confirm_msg += f"\n💳 {card_name}"
                    
                payment_labels = {
                    PaymentTypeEnum.PIX: "PIX",
                    PaymentTypeEnum.CASH: "Dinheiro",
                    PaymentTypeEnum.DEBIT_CARD: "Débito",
                    PaymentTypeEnum.BOLETO: "Boleto",
                    PaymentTypeEnum.CREDIT_CARD: "Crédito"
                }
                confirm_msg += f"\n💱 {payment_labels.get(payment_type, 'Outro')}"
                
                await whatsapp_service.send_message(instance_name, reply_to, confirm_msg)
            
            return {"status": "processed", "parsed": parsed}
        else:
            # Mensagem não reconhecida como financeira
            if is_from_me:
                # Só responde se a confiança é > 0 (tentou mas não conseguiu parsear)
                if parsed.get('amount'):
                    await whatsapp_service.send_message(
                        instance_name, reply_to,
                        f"⚠️ Não consegui identificar bem a mensagem.\n"
                        f"Tente algo como:\n"
                        f"• _Paguei 150 mercado_\n"
                        f"• _Gastei 50 uber_\n"
                        f"• _pendentes_ para ver contas\n"
                        f"• _ajuda_ para ver comandos"
                    )
            return {"status": "low_confidence", "parsed": parsed}
        
    except Exception as e:
        import traceback
        print(f"[WEBHOOK] Erro: {e}")
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}

@router.post("/test-message")
async def test_parse_message(request: Request):
    """Testa o parser de mensagem"""
    data = await request.json()
    message = data.get("message", "")
    return whatsapp_service.parse_financial_message(message)