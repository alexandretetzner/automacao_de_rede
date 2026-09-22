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

xpath = (
    "/config/devices/entry[@name='localhost.localdomain']"
    "/vsys/entry[@name='vsys1']/address"
)

element = """
<entry name="TUNNEL1">
    <ip-netmask>169.255.1.2/30</ip-netmask>
</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando Address Object...")
print("Nome: TUNNEL1")
print("IP: 169.255.1.2/30")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] Address Object TUNNEL1 criado com sucesso.")
else:
    print("[ERRO] Não foi possível criar o Address Object.")
    print(response.text)