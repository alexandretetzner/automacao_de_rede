import requests
import urllib3
import os

# Desabilita o aviso de certificado HTTPS não confiável do laboratório
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"

# Token armazenado em variável de ambiente
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

    print("\nConexão com o FortiGate: OK")
    print("\nInterfaces encontradas:")

    for interface in dados["results"]:
        nome = interface.get("name")

        if nome in ["port2", "port3"]:
            ip = interface.get("ip")
            status = interface.get("status")

            print(f"\nInterface: {nome}")
            print(f"IP: {ip}")
            print(f"Status: {status}")

else:
    print("\nErro ao consultar o FortiGate:")
    print(response.text)