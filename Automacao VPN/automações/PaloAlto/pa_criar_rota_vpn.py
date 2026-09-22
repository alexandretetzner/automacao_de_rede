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
    "/network/virtual-router/entry[@name='default']"
    "/routing-table/ip/static-route"
)

element = """
<entry name="ROTA-FORTIGATE">
    <interface>tunnel.1</interface>
    <metric>10</metric>
    <destination>192.168.10.0/24</destination>
    <route-table>
        <unicast/>
    </route-table>
</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando rota estática...")
print("Nome: ROTA-FORTIGATE")
print("Destino: 192.168.10.0/24")
print("Interface: tunnel.1")
print("Metric: 10")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] Rota estática criada com sucesso.")
else:
    print("[ERRO] Não foi possível criar a rota estática.")
    print(response.text)