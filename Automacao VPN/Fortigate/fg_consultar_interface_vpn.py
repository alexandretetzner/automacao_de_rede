import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/system/interface"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

response = requests.get(
    url,
    headers=headers,
    verify=False,
    timeout=10
)

print("Status HTTP:", response.status_code)

if response.status_code == 200:

    dados = response.json()
    interfaces = dados.get("results", [])

    vpn = next(
        (interface for interface in interfaces
         if interface.get("name") == "VPN-PALOALTO"),
        None
    )

    if vpn:
        print("\n[OK] Interface VPN-PALOALTO encontrada.")
        print("Nome:", vpn.get("name"))
        print("Tipo:", vpn.get("type"))
        print("IP:", vpn.get("ip"))
        print("Remote IP:", vpn.get("remote-ip"))
        print("Interface física:", vpn.get("interface"))
        print("Status:", vpn.get("status"))
    else:
        print("\n[ERRO] Interface VPN-PALOALTO não encontrada.")

else:
    print("\n[ERRO] Falha ao consultar interfaces.")
    print(response.text)