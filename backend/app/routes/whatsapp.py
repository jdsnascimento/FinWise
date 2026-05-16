from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from ..services.evolution_service import evolution_service

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

class InstanceCreate(BaseModel):
    instance_name: str
    phone_number: str

class TestMessage(BaseModel):
    instance_name: str
    phone: str
    message: str

@router.post("/instance/create")
async def create_instance(data: InstanceCreate):
    """Cria nova instância WhatsApp"""
    try:
        result = await evolution_service.create_instance(
            data.instance_name,
            data.phone_number
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/instance/qrcode/{instance_name}")
async def get_qrcode(instance_name: str):
    """Obtém QR Code da instância"""
    try:
        result = await evolution_service.get_qrcode(instance_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/instance/status/{instance_name}")
async def get_status(instance_name: str):
    """Verifica status da conexão"""
    try:
        result = await evolution_service.get_instance_status(instance_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/send-message")
async def send_message(data: TestMessage):
    """Envia mensagem de teste"""
    try:
        result = await evolution_service.send_message(
            data.instance_name,
            data.phone,
            data.message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))