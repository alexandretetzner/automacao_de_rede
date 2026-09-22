import requests
import urllib3
import os
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"
TOKEN = os.getenv("FORTIGATE_TOKEN")

url = (
    f"https://{FORTIGATE_IP}"
    f"/api/v2/cmdb/vpn.ipsec/phase1-interface"
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

    print("\nSchema da Phase 1 recebido com sucesso.\n")
    campos = [
    "name",
    "interface",
    "ike-version",
    "remote-gw",
    "proposal",
    "dhgrp",
    "keylife",
    "authmethod",
    "psksecret"
]

schema = dados.get("results", {})

for campo in campos:
    if campo in schema:
        print(f"\n===== {campo} =====")
        print(json.dumps(schema[campo], indent=4))

else:
    print("\nErro ao consultar o schema:")
    print(response.text)