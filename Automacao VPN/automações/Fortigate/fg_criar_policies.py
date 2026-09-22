import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/firewall/policy"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

policies = [
    {
        "name": "LAN-TO-VPN-PALOALTO",
        "srcintf": [
            {"name": "port3"}
        ],
        "dstintf": [
            {"name": "VPN-PALOALTO"}
        ],
        "srcaddr": [
            {"name": "LAN-FORTIGATE"}
        ],
        "dstaddr": [
            {"name": "LAN-PALOALTO"}
        ],
        "action": "accept",
        "schedule": "always",
        "service": [
            {"name": "ALL"}
        ],
        "nat": "disable",
        "status": "enable"
    },

    {
        "name": "VPN-PALOALTO-TO-LAN",
        "srcintf": [
            {"name": "VPN-PALOALTO"}
        ],
        "dstintf": [
            {"name": "port3"}
        ],
        "srcaddr": [
            {"name": "LAN-PALOALTO"}
        ],
        "dstaddr": [
            {"name": "LAN-FORTIGATE"}
        ],
        "action": "accept",
        "schedule": "always",
        "service": [
            {"name": "ALL"}
        ],
        "nat": "disable",
        "status": "enable"
    }
]

for policy in policies:

    print(f"\nCriando Firewall Policy: {policy['name']}")

    response = requests.post(
        url,
        headers=headers,
        json=policy,
        verify=False,
        timeout=10
    )

    print("Status HTTP:", response.status_code)

    if response.status_code in [200, 201]:
        print(f"[OK] Policy {policy['name']} criada com sucesso.")
    else:
        print(f"[ERRO] Não foi possível criar {policy['name']}.")
        print(response.text)