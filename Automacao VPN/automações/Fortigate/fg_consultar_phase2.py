import requests
import urllib3
import os

# Desabilita o aviso de certificado HTTPS não confiável do laboratório
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORTIGATE_IP = "192.168.68.64"

# Token armazenado em variável de ambiente
TOKEN = os.getenv("FORTIGATE_TOKEN")

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/vpn.ipsec/phase2-interface"

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

    print("\nConsulta de VPN IPSec Phase 2: OK")

    vpns = dados.get("results", [])

    if len(vpns) == 0:
        print("\nNenhuma Phase 2 configurada.")
    else:
        print("\nPhase 2 encontradas:")

        for vpn in vpns:
            print(f"\nNome: {vpn.get('name')}")
            print(f"Phase 1: {vpn.get('phase1name')}")
            print(f"Proposal: {vpn.get('proposal')}")
            print(f"PFS: {vpn.get('pfs')}")
            print(f"DH Group: {vpn.get('dhgrp')}")
            print(f"Lifetime: {vpn.get('keylifeseconds')}")

else:
    print("\nErro ao consultar as configurações de Phase 2:")
    print(response.text)