import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/vpn.ipsec/phase2-interface"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

phase2 = {
    "name": "VPN-PALOALTO-P2",
    "phase1name": "VPN-PALOALTO",
    "proposal": "des-sha256",
    "pfs": "enable",
    "dhgrp": "20",
    "keylifeseconds": 3600,
    "src-subnet": "192.168.10.0 255.255.255.0",
    "dst-subnet": "192.168.20.0 255.255.255.0"
}

print("Criando Phase 2 da VPN...")
print("Phase 1: VPN-PALOALTO")
print("Rede local: 192.168.10.0/24")
print("Rede remota: 192.168.20.0/24")

response = requests.post(
    url,
    headers=headers,
    json=phase2,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code in [200, 201]:
    print("\n[OK] Phase 2 criada com sucesso.")
    print("Nome: VPN-PALOALTO-P2")

else:
    print("\n[ERRO] Não foi possível criar a Phase 2.")
    print(response.text)