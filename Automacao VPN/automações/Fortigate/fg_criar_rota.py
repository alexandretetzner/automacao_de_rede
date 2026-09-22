import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/router/static"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

rota = {
    "dst": "192.168.20.0 255.255.255.0",
    "device": "VPN-PALOALTO",
    "gateway": "0.0.0.0",
    "distance": 10,
    "status": "enable"
}

print("Criando rota estática...")
print("Destino: 192.168.20.0/24")
print("Interface: VPN-PALOALTO")

response = requests.post(
    url,
    headers=headers,
    json=rota,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code in [200, 201]:
    print("\n[OK] Rota estática criada com sucesso.")
else:
    print("\n[ERRO] Não foi possível criar a rota estática.")
    print(response.text)