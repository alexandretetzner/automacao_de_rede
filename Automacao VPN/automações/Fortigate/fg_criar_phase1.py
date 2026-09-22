import requests
import urllib3
import os

# Desabilita o aviso de certificado HTTPS do laboratório
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"

TOKEN = os.getenv("FORTIGATE_TOKEN")
PSK = os.getenv("FORTIGATE_PSK")

# Verifica se as variáveis de ambiente foram configuradas
if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

if not PSK:
    print("[ERRO] Variável FORTIGATE_PSK não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/vpn.ipsec/phase1-interface"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

phase1 = {
    "name": "VPN-PALOALTO",
    "type": "static",
    "interface": "port2",
    "ike-version": "2",
    "remote-gw": "200.201.186.2",
    "authmethod": "psk",
    "psksecret": PSK,
    "proposal": "des-sha256",
    "dhgrp": "20",
    "keylife": 28800
}

print("Criando Phase 1 da VPN...")
print("Peer: 200.201.186.2")
print("Interface: port2")

response = requests.post(
    url,
    headers=headers,
    json=phase1,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code in [200, 201]:
    print("\n[OK] Phase 1 criada com sucesso.")
    print("Nome: VPN-PALOALTO")

else:
    print("\n[ERRO] Não foi possível criar a Phase 1.")
    print(response.text)