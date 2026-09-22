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
    "/network/tunnel/ipsec"
)

element = """
<entry name="VPN-FORTIGATE">

    <auto-key>

        <ike-gateway>
            <entry name="IKE-GW-FORTIGATE"/>
        </ike-gateway>

        <proxy-id>
            <entry name="PROXY-FORTIGATE">
                <protocol>
                    <any/>
                </protocol>
                <local>192.168.20.0/24</local>
                <remote>192.168.10.0/24</remote>
            </entry>
        </proxy-id>

        <ipsec-crypto-profile>IPSEC-FORTIGATE</ipsec-crypto-profile>

    </auto-key>

    <tunnel-monitor>
        <enable>no</enable>
    </tunnel-monitor>

    <tunnel-interface>tunnel.1</tunnel-interface>

</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando IPSec Tunnel...")
print("Nome: VPN-FORTIGATE")
print("IKE Gateway: IKE-GW-FORTIGATE")
print("IPSec Crypto Profile: IPSEC-FORTIGATE")
print("Tunnel Interface: tunnel.1")
print("Proxy Local: 192.168.20.0/24")
print("Proxy Remote: 192.168.10.0/24")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] IPSec Tunnel criado com sucesso.")
else:
    print("[ERRO] Não foi possível criar o IPSec Tunnel.")
    print(response.text)