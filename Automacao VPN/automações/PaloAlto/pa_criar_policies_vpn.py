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
    "/vsys/entry[@name='vsys1']"
    "/rulebase/security/rules"
)

element = """
<entry name="INTERNA-TO-VPN">
    <from>
        <member>INTERNA</member>
    </from>
    <to>
        <member>VPN</member>
    </to>
    <source>
        <member>192.168.20.0/24</member>
    </source>
    <destination>
        <member>192.168.10.0/24</member>
    </destination>
    <source-user>
        <member>any</member>
    </source-user>
    <category>
        <member>any</member>
    </category>
    <application>
        <member>any</member>
    </application>
    <service>
        <member>application-default</member>
    </service>
    <hip-profiles>
        <member>any</member>
    </hip-profiles>
    <action>allow</action>
</entry>

<entry name="VPN-TO-INTERNA">
    <from>
        <member>VPN</member>
    </from>
    <to>
        <member>INTERNA</member>
    </to>
    <source>
        <member>192.168.10.0/24</member>
    </source>
    <destination>
        <member>192.168.20.0/24</member>
    </destination>
    <source-user>
        <member>any</member>
    </source-user>
    <category>
        <member>any</member>
    </category>
    <application>
        <member>any</member>
    </application>
    <service>
        <member>application-default</member>
    </service>
    <hip-profiles>
        <member>any</member>
    </hip-profiles>
    <action>allow</action>
</entry>
"""

parametros = {
    "type": "config",
    "action": "set",
    "xpath": xpath,
    "element": element,
    "key": API_KEY
}

print("Criando Security Policies...")
print()
print("INTERNA-TO-VPN")
print("INTERNA -> VPN")
print("192.168.20.0/24 -> 192.168.10.0/24")
print()
print("VPN-TO-INTERNA")
print("VPN -> INTERNA")
print("192.168.10.0/24 -> 192.168.20.0/24")

response = requests.post(
    url,
    data=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code == 200 and 'status="success"' in response.text:
    print("[OK] Security Policies criadas com sucesso.")
else:
    print("[ERRO] Não foi possível criar as Security Policies.")
    print(response.text)