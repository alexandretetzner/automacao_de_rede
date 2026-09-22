import requests
import urllib3
import os
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PALOALTO_IP = "192.168.71.11"
API_KEY = os.getenv("PALOALTO_API_KEY")

if not API_KEY:
    print("[ERRO] Variável PALOALTO_API_KEY não encontrada.")
    exit()

url = f"https://{PALOALTO_IP}/api/"

parametros = {
    "type": "commit",
    "cmd": "<commit></commit>",
    "key": API_KEY
}

print("Enviando Commit para o Palo Alto...")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code != 200 or 'status="success"' not in response.text:
    print("[ERRO] Não foi possível iniciar o Commit.")
    print(response.text)
    exit()

root = ET.fromstring(response.text)
job = root.find(".//job")

if job is not None:
    print("[OK] Commit iniciado.")
    print("Job ID:", job.text)
else:
    print("[AVISO] O Palo Alto aceitou a solicitação, mas não retornou Job ID.")
    print(response.text)