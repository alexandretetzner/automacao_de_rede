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

JOB_ID = input("Informe o Job ID: ")

url = f"https://{PALOALTO_IP}/api/"

parametros = {
    "type": "op",
    "cmd": f"<show><jobs><id>{JOB_ID}</id></jobs></show>",
    "key": API_KEY
}

print(f"\nConsultando Job {JOB_ID}...")

response = requests.get(
    url,
    params=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code != 200 or 'status="success"' not in response.text:
    print("[ERRO] Não foi possível consultar o Job.")
    print(response.text)
    exit()

root = ET.fromstring(response.text)

status = root.findtext(".//job/status")
resultado = root.findtext(".//job/result")
progresso = root.findtext(".//job/progress")
detalhes = root.findtext(".//job/details/line")

print("Status:", status)
print("Resultado:", resultado)
print("Progresso:", progresso)
print("Detalhes:", detalhes)

if status == "FIN" and resultado == "OK":
    print("[OK] Commit concluído com sucesso.")
elif status == "FIN":
    print("[ERRO] O Commit terminou, mas apresentou falha.")
    print(response.text)
else:
    print("[AVISO] O Commit ainda está em processamento.")