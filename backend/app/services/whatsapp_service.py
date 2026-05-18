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
    
    def _get_webhook_url(self) -> str:
        """Retorna a URL do webhook acessível pela Evolution API"""
        # Ambos containers estão na mesma rede Docker (finwise_network)
        # então http://backend:8000 funciona perfeitamente
        return settings.EVOLUTION_WEBHOOK_URL
    
    async def create_instance(self, instance_name: str, phone_number: str):
        """Cria uma nova instância WhatsApp e configura webhook"""
        async with httpx.AsyncClient(timeout=30) as client:
            # Primeiro, tentar deletar instância existente com mesmo nome
            try:
                await client.delete(
                    f"{self.base_url}/instance/delete/{instance_name}",
                    headers=self.headers
                )
                print(f"[WA] Instância anterior '{instance_name}' removida")
            except Exception:
                pass  # Ignora se não existir
            
            # Criar nova instância
            create_payload = {
                "instanceName": instance_name,
                "token": self.api_key,
                "qrcode": True,
                "number": phone_number,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            print(f"[WA] Criando instância: {instance_name}")
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json=create_payload
            )
            result = response.json()
            print(f"[WA] Resposta create: {result}")
            
            # Configurar webhook
            try:
                webhook_url = self._get_webhook_url()
                print(f"[WA] Configurando webhook: {webhook_url}")
                
                webhook_response = await client.post(
                    f"{self.base_url}/webhook/set/{instance_name}",
                    headers=self.headers,
                    json={
                        "webhook": {
                            "enabled": True,
                            "url": webhook_url,
                            "byEvents": False,
                            "base64": False,
                            "events": [
                                "MESSAGES_UPSERT"
                            ]
                        }
                    }
                )
                print(f"[WA] Webhook configurado: {webhook_response.status_code}")
            except Exception as e:
                print(f"[WA] Aviso: Falha ao configurar webhook: {e}")
                
            return result
    
    async def get_qrcode(self, instance_name: str) -> Optional[str]:
        """Obtém QR Code para conectar WhatsApp"""
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/instance/connect/{instance_name}",
                    headers=self.headers
                )
                data = response.json()
                # Na Evolution API v2 o base64 vem direto na raiz, na v1 vinha dentro de qrcode
                base64_qr = data.get("base64") or data.get("qrcode", {}).get("base64")
                return base64_qr
            except Exception as e:
                print(f"[WA] Erro ao obter qrcode: {e}")
                return None
    
    async def get_instance_status(self, instance_name: str) -> str:
        """Verifica status da instância"""
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{instance_name}",
                    headers=self.headers
                )
                data = response.json()
                state = data.get("instance", {}).get("state", "disconnected")
                return state
            except Exception:
                return "disconnected"
    
    async def send_message(self, instance_name: str, phone: str, message: str):
        """Envia mensagem WhatsApp"""
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{instance_name}",
                    headers=self.headers,
                    json={
                        "number": phone,
                        "text": message
                    }
                )
                result = response.json()
                print(f"[WA] Mensagem enviada para {phone}: {response.status_code}")
                return result
            except Exception as e:
                print(f"[WA] Erro ao enviar mensagem: {e}")
                return {"error": str(e)}
    
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
            'payment_method': 'cash',
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
        if 'pix' in message:
            result['payment_method'] = 'pix'
        elif any(k in message for k in ['crédito', 'credito', 'cartão', 'cartao']):
            result['payment_method'] = 'credit_card'
        elif any(k in message for k in ['débito', 'debito']):
            result['payment_method'] = 'debit_card'
        elif any(k in message for k in ['dinheiro', 'cash', 'nota']):
            result['payment_method'] = 'cash'
        elif any(k in message for k in ['boleto']):
            result['payment_method'] = 'boleto'
        
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
                if result['payment_method'] == 'cash':
                    result['payment_method'] = 'credit_card'
                break
        
        # Extrair descrição (palavras entre valor e cartão/parcelas)
        # Remove palavras-chave conhecidas
        stop_words = ['paguei', 'gastei', 'comprei', 'recebi', 'pix', 'no', 'na', 'com', 'o', 'a', 'em', 'de', 'do', 'da']
        
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
            'almoço': 'Alimentação',
            'almoco': 'Alimentação',
            'café': 'Alimentação',
            'cafe': 'Alimentação',
            'geladeira': 'Moradia',
            'eletrodoméstico': 'Moradia',
            'eletrodomestico': 'Moradia',
            'roupa': 'Lazer',
            'tênis': 'Lazer',
            'tenis': 'Lazer',
            'celular': 'Assinaturas',
            'iphone': 'Assinaturas',
            'salário': 'Salário',
            'salario': 'Salário',
            'freelance': 'Freelance',
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