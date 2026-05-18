import httpx
import re
from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal
from ..config import settings

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_instance(self, instance_name: str, phone_number: str):
        """Cria uma nova instância WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json={
                    "instanceName": instance_name,
                    "token": self.api_key,
                    "qrcode": False,
                    "number": phone_number,
                    "integration": "WHATSAPP-BAILEYS"
                },
                timeout=30
            )
            result = response.json()
            
            try:
                # Setup do webhook separado (V2 exige URL com domínio válido)
                webhook_url = settings.EVOLUTION_WEBHOOK_URL
                if "http://backend:" in webhook_url:
                    webhook_url = webhook_url.replace("http://backend:", "http://host.docker.internal:")
                    
                await client.post(
                    f"{self.base_url}/webhook/set/{instance_name}",
                    headers=self.headers,
                    json={
                        "webhook": {
                            "enabled": True,
                            "url": webhook_url,
                            "byEvents": False,
                            "base64": False,
                            "events": ["MESSAGES_UPSERT"]
                        }
                    },
                    timeout=30
                )
            except Exception as e:
                print("Aviso: Falha ao configurar webhook, mas instância criada:", e)
                
            return result
    
    async def get_qrcode(self, instance_name: str) -> Optional[str]:
        """Obtém QR Code para conectar WhatsApp"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/instance/connect/{instance_name}",
                    headers=self.headers,
                    timeout=30
                )
                data = response.json()
                # Na Evolution API v2 o base64 vem direto na raiz, na v1 vinha dentro de qrcode
                base64_qr = data.get("base64") or data.get("qrcode", {}).get("base64")
                return base64_qr
            except Exception as e:
                print("Erro ao obter qrcode:", e)
                return None
    
    async def get_instance_status(self, instance_name: str) -> str:
        """Verifica status da instância"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{instance_name}",
                    headers=self.headers
                )
                data = response.json()
                return data.get("instance", {}).get("state", "disconnected")
            except:
                return "disconnected"
    
    async def send_message(self, instance_name: str, phone: str, message: str):
        """Envia mensagem WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendText/{instance_name}",
                headers=self.headers,
                json={
                    "number": phone,
                    "text": message
                }
            )
            return response.json()
    
    def parse_financial_message(self, message: str) -> Dict[str, Any]:
        """
        Parse de mensagem financeira via WhatsApp
        
        Formatos aceitos:
        1. "Paguei 150 mercado no Nubank 3x"
        2. "Gastei 89.90 uber"
        3. "Comprei 2500 geladeira no Inter 10x"
        4. "Recebi 5000 salário"
        5. "pix 150 jantar"
        """
        message = message.lower().strip()
        
        result = {
            'type': 'expense',  # expense ou income
            'amount': None,
            'description': None,
            'category_hint': None,
            'card_hint': None,
            'installments': 1,
            'payment_method': 'credit_card',
            'confidence': 0
        }
        
        # Detectar se é receita
        income_keywords = ['recebi', 'recebido', 'salário', 'salario', 'freelance', 'pagamento recebido']
        if any(keyword in message for keyword in income_keywords):
            result['type'] = 'income'
            result['payment_method'] = 'pix'
        
        # Extrair valor (padrão: R$ XXX,XX ou XXX.XX ou XXX,XX)
        value_patterns = [
            r'r\$\s*(\d+[\.,]?\d*)',  # R$ 150.00
            r'(\d+[\.,]\d{2})',        # 150.00
            r'(\d+)',                   # 150 (fallback)
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, message)
            if match:
                value_str = match.group(1).replace(',', '.')
                try:
                    result['amount'] = float(value_str)
                    # Remover o valor da mensagem para análise
                    message = message.replace(match.group(0), '')
                    break
                except:
                    continue
        
        # Detectar método de pagamento
        payment_methods = {
            'pix': ['pix'],
            'credito': ['crédito', 'credito', 'cartão', 'cartao', 'no ', 'com o '],
            'debito': ['débito', 'debito'],
            'dinheiro': ['dinheiro', 'cash', 'nota'],
            'boleto': ['boleto']
        }
        
        for method, keywords in payment_methods.items():
            if any(keyword in message for keyword in keywords):
                result['payment_method'] = 'credit_card' if method == 'credito' else method
                break
        
        # Extrair número de parcelas
        installments_match = re.search(r'(\d+)\s*x', message)
        if installments_match:
            result['installments'] = int(installments_match.group(1))
            result['payment_method'] = 'credit_card'
        
        # Detectar nome do cartão
        card_keywords = ['nubank', 'inter', 'bradesco', 'itau', 'itaú', 'santander', 'c6', 'will', 'picpay']
        for card in card_keywords:
            if card in message:
                result['card_hint'] = card.upper()
                break
        
        # Extrair descrição (palavras entre valor e cartão/parcelas)
        # Remove palavras-chave conhecidas
        stop_words = ['paguei', 'gastei', 'comprei', 'recebi', 'pix', 'no', 'na', 'com', 'o', 'a', 'em']
        
        words = message.split()
        description_words = [w for w in words if w not in stop_words and not w.isdigit() 
                           and w not in card_keywords and 'x' not in w]
        
        if description_words:
            result['description'] = ' '.join(description_words).title()
        
        # Sugerir categoria baseado em palavras-chave
        category_map = {
            'mercado': 'Mercado',
            'supermercado': 'Mercado',
            'comida': 'Alimentação',
            'restaurante': 'Alimentação',
            'lanche': 'Alimentação',
            'alimentação': 'Alimentação',
            'alimentacao': 'Alimentação',
            'uber': 'Transporte',
            'transporte': 'Transporte',
            'gasolina': 'Transporte',
            'combustível': 'Transporte',
            'combustivel': 'Transporte',
            'aluguel': 'Moradia',
            'aluguel': 'Moradia',
            'conta': 'Moradia',
            'luz': 'Moradia',
            'água': 'Moradia',
            'agua': 'Moradia',
            'internet': 'Assinaturas',
            'netflix': 'Assinaturas',
            'spotify': 'Assinaturas',
            'academia': 'Saúde',
            'saúde': 'Saúde',
            'saude': 'Saúde',
            'farmácia': 'Saúde',
            'farmacia': 'Saúde',
            'médico': 'Saúde',
            'medico': 'Saúde',
            'curso': 'Educação',
            'educação': 'Educação',
            'educacao': 'Educação',
            'livro': 'Educação',
            'cinema': 'Lazer',
            'lazer': 'Lazer',
            'viagem': 'Lazer',
            'shopping': 'Lazer',
            'jantar': 'Alimentação',
            'geladeira': 'Moradia',
            'eletrodoméstico': 'Moradia',
            'eletrodomestico': 'Moradia',
            'roupa': 'Lazer',
            'tênis': 'Lazer',
            'tenis': 'Lazer',
            'celular': 'Assinaturas',
            'iphone': 'Assinaturas'
        }
        
        for keyword, category in category_map.items():
            if keyword in message:
                result['category_hint'] = category
                break
        
        # Calcular confiança
        confidence_points = 0
        if result['amount']: confidence_points += 3
        if result['description']: confidence_points += 2
        if result['category_hint']: confidence_points += 2
        if result['card_hint']: confidence_points += 1
        if result['installments'] > 1: confidence_points += 1
        
        result['confidence'] = min(confidence_points / 9 * 100, 100)
        
        return result

whatsapp_service = WhatsAppService()