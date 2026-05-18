import urllib.request
import json
import urllib.error
import time

url = 'http://localhost:8080/instance/create'
data = {
    "instanceName": "test_qr_check10",
    "token": "your-api-key-here",
    "qrcode": False,  # NÃO esperar o QR code na criação para evitar timeout!
    "number": "5511999999999",
    "integration": "WHATSAPP-BAILEYS"
}
req = urllib.request.Request(
    url,
    data=json.dumps(data).encode(),
    headers={'apikey': 'your-api-key-here', 'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    create_data = json.loads(res.read().decode())
    print("CREATE SUCCESS")
    print("CREATE KEYS:", list(create_data.keys()))
except urllib.error.HTTPError as e:
    print("CREATE HTTP ERROR:", e.code)
    print(e.read().decode(errors='replace')[:500])
except Exception as e:
    print("CREATE OTHER ERROR:", e)

print("Aguardando 8 seconds para o Baileys inicializar e gerar o QR Code em background...")
time.sleep(8)

def check_url(url):
    req = urllib.request.Request(url, headers={'apikey': 'your-api-key-here'})
    try:
        res = urllib.request.urlopen(req)
        print(f"URL: {url} -> SUCCESS")
        print(res.read().decode()[:500])
    except urllib.error.HTTPError as e:
        print(f"URL: {url} -> HTTP ERROR {e.code}")
        print(e.read().decode(errors='replace')[:500])
    except Exception as e:
        print(f"URL: {url} -> OTHER ERROR {e}")

check_url('http://localhost:8080/instance/connectionState/test_qr_check10')
check_url('http://localhost:8080/instance/connect/test_qr_check10')
