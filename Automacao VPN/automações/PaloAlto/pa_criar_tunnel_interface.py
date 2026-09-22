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
    "/network/interface/tunnel"
)

element = """
<units>
    <entry name="tunnel.1">
        <ip>
            <entry name="TUNNEL1"/>
        </ip>
    </entry>
</units>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando Tunnel Interface...")
print("Interface: tunnel.1")
print("IPv4: TUNNEL1 (169.255.1.2/30)")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] Interface tunnel.1 criada com sucesso.")
else:
    print("[ERRO] Não foi possível criar a interface tunnel.1.")
    print(response.text)