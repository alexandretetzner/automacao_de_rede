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

cmd = "<show><vpn><ike-sa></ike-sa></vpn></show>"

parametros = {
    "type": "op",
    "cmd": cmd,
    "key": API_KEY
}

print("Validando IKE SA...")

response = requests.get(
    url,
    params=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code != 200:
    print("[ERRO] Não foi possível consultar a IKE SA.")
    exit()

root = ET.fromstring(response.text)

gateway = root.find(".//entry")

if gateway is None:
    print("[ERRO] Nenhuma IKE SA ativa encontrada.")
    exit()

nome = gateway.findtext("name")
modo = gateway.findtext("mode")
algoritmo = gateway.findtext("algo")
criado = gateway.findtext("created")
expira = gateway.findtext("expires")

print("Gateway:", nome)
print("Modo:", modo)
print("Algoritmo:", algoritmo)
print("Criada em:", criado)
print("Expira em:", expira)

if nome == "IKE-GW-FORTIGATE":
    print("[OK] IKE SA do FortiGate está ativa.")
else:
    print("[ERRO] IKE SA do FortiGate não encontrada.")