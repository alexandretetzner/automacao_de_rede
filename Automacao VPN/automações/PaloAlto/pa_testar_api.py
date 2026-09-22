import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PALOALTO_IP = "192.168.71.11"
API_KEY = os.getenv("PALOALTO_API_KEY")

if not API_KEY:
    print("[ERRO] Variável PALOALTO_API_KEY não encontrada.")
    exit()

url = f"https://{PALOALTO_IP}/api/"

parametros = {
    "type": "op",
    "cmd": "<show><system><info></info></system></show>",
    "key": API_KEY
}

print("Consultando informações do Palo Alto...")

response = requests.get(
    url,
    params=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)
print(response.text)