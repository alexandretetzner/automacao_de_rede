import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/firewall/address"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

enderecos = [
    {
        "name": "LAN-FORTIGATE",
        "type": "ipmask",
        "subnet": "192.168.10.0 255.255.255.0"
    },
    {
        "name": "LAN-PALOALTO",
        "type": "ipmask",
        "subnet": "192.168.20.0 255.255.255.0"
    }
]

for endereco in enderecos:

    print(f"\nCriando Address Object: {endereco['name']}")
    print(f"Subnet: {endereco['subnet']}")

    response = requests.post(
        url,
        headers=headers,
        json=endereco,
        verify=False,
        timeout=10
    )

    print("Status HTTP:", response.status_code)

    if response.status_code in [200, 201]:
        print(f"[OK] {endereco['name']} criado com sucesso.")
    else:
        print(f"[ERRO] Não foi possível criar {endereco['name']}.")
        print(response.text)