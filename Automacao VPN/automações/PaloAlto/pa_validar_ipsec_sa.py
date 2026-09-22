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

cmd = "<show><vpn><ipsec-sa></ipsec-sa></vpn></show>"

parametros = {
    "type": "op",
    "cmd": cmd,
    "key": API_KEY
}

print("Validando IPSec SA...")

response = requests.get(
    url,
    params=parametros,
    verify=False,
    timeout=10
)

print("\nStatus HTTP:", response.status_code)

if response.status_code != 200:
    print("[ERRO] Não foi possível consultar a IPSec SA.")
    exit()

root = ET.fromstring(response.text)

tunnel = root.find(".//entries/entry")

if tunnel is None:
    print("[ERRO] Nenhuma IPSec SA ativa encontrada.")
    exit()

nome = tunnel.findtext("name")
gateway = tunnel.findtext("gateway")
peer = tunnel.findtext("remote")
protocolo = tunnel.findtext("proto")
criptografia = tunnel.findtext("enc")
hash_algoritmo = tunnel.findtext("hash")
spi_in = tunnel.findtext("i_spi")
spi_out = tunnel.findtext("o_spi")

if peer:
    peer = peer.strip()

print("Tunnel:", nome)
print("Gateway:", gateway)
print("Peer:", peer)
print("Protocolo:", protocolo)
print("Criptografia:", criptografia)
print("Hash:", hash_algoritmo)
print("SPI IN:", spi_in)
print("SPI OUT:", spi_out)

if nome == "VPN-FORTIGATE:PROXY-FORTIGATE":
    print("[OK] IPSec SA do FortiGate está ativa.")
else:
    print("[ERRO] IPSec SA do FortiGate não encontrada.")