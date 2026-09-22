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
    policies = dados.get("results", [])

    print("\nConsulta de Firewall Policies: OK")

    if len(policies) == 0:
        print("\nNenhuma Firewall Policy configurada.")

    else:
        print("\nFirewall Policies encontradas:")

        for policy in policies:
            print("\nID:", policy.get("policyid"))
            print("Nome:", policy.get("name"))
            print("Origem:", policy.get("srcintf"))
            print("Destino:", policy.get("dstintf"))
            print("Source Address:", policy.get("srcaddr"))
            print("Destination Address:", policy.get("dstaddr"))
            print("Action:", policy.get("action"))
            print("NAT:", policy.get("nat"))
            print("Status:", policy.get("status"))

else:
    print("\n[ERRO] Não foi possível consultar as Firewall Policies.")
    print(response.text)