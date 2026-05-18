import urllib.request
import json
import urllib.error

url2 = 'http://localhost:8080/webhook/set/test_inst_with_webhook3'
data2 = {
    "webhook": {
        "enabled": True,
        "url": "https://example.com/webhook",
        "byEvents": False,
        "base64": False,
        "events": ["MESSAGES_UPSERT"]
    }
}
req2 = urllib.request.Request(
    url2,
    data=json.dumps(data2).encode(),
    headers={'apikey': 'your-api-key-here', 'Content-Type': 'application/json'}
)

try:
    res2 = urllib.request.urlopen(req2)
    print("WEBHOOK SUCCESS")
except urllib.error.HTTPError as e:
    print("WEBHOOK HTTP ERROR:", e.code)
    print("WEBHOOK BODY:", e.read().decode(errors='replace'))
except Exception as e:
    print("WEBHOOK OTHER ERROR:", e)
