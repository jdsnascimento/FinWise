from fastapi import APIRouter, Request, HTTPException
# pyrefly: ignore [missing-import]
from ..services.evolution_service import evolution_service
from ..database import get_db
import json

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Recebe mensagens do WhatsApp via Evolution API"""
    try:
        data = await request.json()
        
        # Extrair dados da mensagem
        event = data.get("event")
        
        if event == "MESSAGES_UPSERT":
            message_data = data.get("data", {}).get("message", {})
            
            # Verificar se é mensagem de texto
            if message_data.get("messageType") == "conversation":
                text = message_data.get("conversation", "")
                sender = data.get("data", {}).get("key", {}).get("remoteJid", "")
                
                # Parse da mensagem
                parsed = await evolution_service.parse_whatsapp_message(text)
                
                # TODO: Salvar no banco de dados (Conta a Pagar)
                # Aqui você integrará com o modelo Bill posteriormente
                
                return {
                    "status": "received",
                    "sender": sender,
                    "parsed": parsed
                }
        
        return {"status": "ignored"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))