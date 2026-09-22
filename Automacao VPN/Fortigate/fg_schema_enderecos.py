import requests
import urllib3
import os
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

url = (
    f"https://{FORTIGATE_IP}"
    f"/api/v2/cmdb/firewall/address"
    f"?action=schema"
)

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

    print("\nSchema de firewall/address recebido com sucesso.")

    campos_schema = dados.get("results", {}).get("children", {})

    campos = [
        "name",
        "type",
        "subnet"
    ]

    for campo in campos:

        if campo in campos_schema:
            print(f"\n===== {campo} =====")
            print(json.dumps(campos_schema[campo], indent=4))

        else:
            print(f"\n[AVISO] Campo '{campo}' não encontrado.")

else:
    print("\n[ERRO] Não foi possível consultar o schema.")
    print(response.text)