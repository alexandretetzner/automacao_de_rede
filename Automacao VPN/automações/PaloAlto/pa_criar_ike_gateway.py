import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PALOALTO_IP = "192.168.71.11"

API_KEY = os.getenv("PALOALTO_API_KEY")
PSK = os.getenv("PALOALTO_PSK")

if not API_KEY:
    print("[ERRO] Variável PALOALTO_API_KEY não encontrada.")
    exit()

if not PSK:
    print("[ERRO] Variável PALOALTO_PSK não encontrada.")
    exit()

url = f"https://{PALOALTO_IP}/api/"

xpath = (
    "/config/devices/entry[@name='localhost.localdomain']"
    "/network/ike/gateway"
)

element = f"""
<entry name="IKE-GW-FORTIGATE">
    <authentication>
        <pre-shared-key>
            <key>{PSK}</key>
        </pre-shared-key>
    </authentication>

    <protocol>
        <ikev2>
            <dpd>
                <enable>yes</enable>
            </dpd>
            <ike-crypto-profile>IKE-FORTIGATE</ike-crypto-profile>
        </ikev2>
        <version>ikev2</version>
    </protocol>

    <protocol-common>
        <nat-traversal>
            <enable>no</enable>
        </nat-traversal>
        <fragmentation>
            <enable>no</enable>
        </fragmentation>
    </protocol-common>

    <local-address>
        <interface>ethernet1/1</interface>
    </local-address>

    <peer-address>
        <ip>200.201.100.2</ip>
    </peer-address>
</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando IKE Gateway...")
print("Nome: IKE-GW-FORTIGATE")
print("Interface: ethernet1/1")
print("Peer: 200.201.100.2")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] IKE Gateway criado com sucesso.")
else:
    print("[ERRO] Não foi possível criar o IKE Gateway.")
    print(response.text)