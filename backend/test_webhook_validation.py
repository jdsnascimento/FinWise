import urllib.request
import json
import urllib.error

url = 'http://localhost:8000/api/whatsapp/webhook'

def send_payload(text):
    payload = {
        "event": "messages.upsert",
        "instance": "finwise_1",
        "data": {
            "key": {
                "remoteJid": "5565992849548@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST_MESSAGE_ID"
            },
            "message": {
                "conversation": text
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        response = urllib.request.urlopen(req)
        print(f"SUCCESS for '{text}': Status: {response.status}, Body: {response.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"HTTP ERROR for '{text}': Code: {e.code}, Body: {e.read().decode()}")
    except Exception as e:
        print(f"ERROR for '{text}': {e}")

print("Testing expense within limit...")
send_payload("Paguei 50 mercado no Nubank")

print("\nTesting expense exceeding limit (limit available: R$ 2334.00, test amount: R$ 2500.00)...")
send_payload("Paguei 2500 mercado no Nubank")
