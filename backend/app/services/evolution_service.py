import httpx
# pyrefly: ignore [missing-import]
from ..config import settings

class EvolutionService:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_instance(self, instance_name: str, phone_number: str):
        """Cria uma nova instância do WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json={
                    "instanceName": instance_name,
                    "token": self.api_key,
                    "qrcode": True,
                    "number": phone_number,
                    "webhook": settings.EVOLUTION_WEBHOOK_URL,
                    "webhook_by_events": True,
                    "events": [
                        "MESSAGES_UPSERT",
                        "MESSAGES_UPDATE",
                        "SEND_MESSAGE"
                    ]
                }
            )
            return response.json()
    
    async def get_qrcode(self, instance_name: str):
        """Obtém QR Code para conectar WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/connect/{instance_name}",
                headers=self.headers
            )
            return response.json()
    
    async def send_message(self, instance_name: str, phone: str, message: str):
        """Envia mensagem WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendText/{instance_name}",
                headers=self.headers,
                json={
                    "number": phone,
                    "text": message,
                    "delay": 1200
                }
            )
            return response.json()
    
    async def get_instance_status(self, instance_name: str):
        """Verifica status da instância"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers=self.headers
            )
            return response.json()
    
    async def parse_whatsapp_message(self, message: str):
        """
        Parse mensagem WhatsApp para extrair dados financeiros
        Exemplo: "Paguei 150 mercado no Nubank 3x"
        """
        import re
        
        # Padrão para extrair informações
        patterns = {
            'value': r'(\d+[\.,]?\d*)',
            'category': r'(?:paguei|gastei|comprei)\s+\d+[\.,]?\d*\s+(?:em\s+)?(\w+)',
            'card': r'(?:no|com\s+o)\s+(\w+)',
            'installments': r'(\d+)x'
        }
        
        result = {
            'raw_message': message,
            'value': None,
            'category': None,
            'card': None,
            'installments': 1
        }
        
        # Extrair valor
        value_match = re.search(patterns['value'], message)
        if value_match:
            result['value'] = float(value_match.group(1).replace(',', '.'))
        
        # Extrair categoria
        category_match = re.search(patterns['category'], message.lower())
        if category_match:
            result['category'] = category_match.group(1)
        
        # Extrair cartão
        card_match = re.search(patterns['card'], message.lower())
        if card_match:
            result['card'] = card_match.group(1)
        
        # Extrair parcelas
        installments_match = re.search(patterns['installments'], message.lower())
        if installments_match:
            result['installments'] = int(installments_match.group(1))
        
        return result

evolution_service = EvolutionService()