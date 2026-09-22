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
    enderecos = dados.get("results", [])

    print("\nConsulta de Address Objects: OK")

    if len(enderecos) == 0:
        print("\nNenhum Address Object configurado.")

    else:
        print("\nAddress Objects encontrados:")

        for endereco in enderecos:
            print("\nNome:", endereco.get("name"))
            print("Tipo:", endereco.get("type"))
            print("Subnet:", endereco.get("subnet"))

else:
    print("\n[ERRO] Não foi possível consultar os Address Objects.")
    print(response.text)