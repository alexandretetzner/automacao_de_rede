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
    "/network/ike/crypto-profiles/ipsec-crypto-profiles"
)

element = """
<entry name="IPSEC-FORTIGATE">
    <esp>
        <encryption>
            <member>des</member>
        </encryption>
        <authentication>
            <member>sha256</member>
        </authentication>
    </esp>
    <dh-group>group20</dh-group>
    <lifetime>
        <hours>1</hours>
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

print("Criando IPSec Crypto Profile...")
print("Nome: IPSEC-FORTIGATE")
print("Encryption: DES")
print("Authentication: SHA256")
print("DH Group: group20")
print("Lifetime: 1 hora")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] IPSec Crypto Profile criado com sucesso.")
else:
    print("[ERRO] Não foi possível criar o IPSec Crypto Profile.")
    print(response.text)