import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

INTERFACE_VPN = "VPN-PALOALTO"

url = (
    f"https://{FORTIGATE_IP}"
    f"/api/v2/cmdb/system/interface/{INTERFACE_VPN}"
)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

configuracao = {
    "ip": "169.255.1.1 255.255.255.255",
    "remote-ip": "169.255.1.2 255.255.255.252"
}

print("Configurando endereçamento da interface do túnel...")
print(f"Interface: {INTERFACE_VPN}")
print("IP local: 169.255.1.1")
print("IP remoto: 169.255.1.2/30")

response = requests.put(
    url,
    headers=headers,
    json=configuracao,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200:
    print("\n[OK] Endereçamento do túnel configurado com sucesso.")
else:
    print("\n[ERRO] Não foi possível configurar o túnel.")
    print(response.text)