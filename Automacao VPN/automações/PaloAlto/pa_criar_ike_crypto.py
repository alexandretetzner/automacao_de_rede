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
    "/network/ike/crypto-profiles/ike-crypto-profiles"
)

element = """
<entry name="IKE-FORTIGATE">
    <encryption>
        <member>des</member>
    </encryption>
    <hash>
        <member>sha256</member>
    </hash>
    <dh-group>
        <member>group20</member>
    </dh-group>
    <lifetime>
        <hours>8</hours>
    </lifetime>
</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando IKE Crypto Profile...")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)
print(response.text)