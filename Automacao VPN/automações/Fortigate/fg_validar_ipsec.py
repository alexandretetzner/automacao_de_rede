import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.66"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/monitor/vpn/ipsec"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

parametros = {
    "vdom": "root"
}

print("Validando VPN IPSec...")

response = requests.get(
    url,
    headers=headers,
    params=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code != 200:
    print("[ERRO] Não foi possível consultar a VPN IPSec.")
    exit()

dados = response.json()

vpn = None

for item in dados.get("results", []):
    if item.get("name") == "VPN-PALOALTO":
        vpn = item
        break

if vpn is None:
    print("[ERRO] VPN-PALOALTO não encontrada.")
    exit()

print("VPN:", vpn.get("name"))
print("Peer:", vpn.get("rgwy"))
print("Conexões:", vpn.get("connection_count"))
print("RX:", vpn.get("incoming_bytes"), "bytes")
print("TX:", vpn.get("outgoing_bytes"), "bytes")

proxyids = vpn.get("proxyid", [])

if not proxyids:
    print("[ERRO] Nenhuma Phase 2 encontrada.")
    exit()

phase2 = None

for item in proxyids:
    if item.get("p2name") == "VPN-PALOALTO-P2":
        phase2 = item
        break

if phase2 is None:
    print("[ERRO] Phase 2 VPN-PALOALTO-P2 não encontrada.")
    exit()

print("\nPhase 2:", phase2.get("p2name"))
print("Status:", phase2.get("status"))
print("RX:", phase2.get("incoming_bytes"), "bytes")
print("TX:", phase2.get("outgoing_bytes"), "bytes")

if phase2.get("status") == "up":
    print("\n[OK] VPN IPSec está operacional.")
else:
    print("\n[ERRO] VPN IPSec não está operacional.")