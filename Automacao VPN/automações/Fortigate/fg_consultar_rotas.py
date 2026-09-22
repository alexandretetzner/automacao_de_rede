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

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/router/static"

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
    rotas = dados.get("results", [])

    print("\nConsulta de rotas estáticas: OK")

    if len(rotas) == 0:
        print("\nNenhuma rota estática configurada.")

    else:
        print("\nRotas estáticas encontradas:")

        for rota in rotas:
            if rota.get("seq-num") == 2:
                print(json.dumps(rota, indent=4))

else:
    print("\n[ERRO] Não foi possível consultar as rotas.")
    print(response.text)