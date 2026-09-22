import requests
import urllib3
import os
import json
from pathlib import Path
import ipaddress
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
# CARREGAR CONFIGURAÇÕES
# ============================================================

CAMINHO_CONFIG = Path(__file__).parent / "config.json"

try:
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

except FileNotFoundError:
    print(f"[ERRO] Arquivo config.json não encontrado: {CAMINHO_CONFIG}")
    exit()

except json.JSONDecodeError as erro:
    print("[ERRO] O arquivo config.json possui formato inválido.")
    print(f"Detalhes: linha {erro.lineno}, coluna {erro.colno}.")
    exit()


paloalto = config["paloalto"]
vpn = config["vpn"]


# ============================================================
# PARÂMETROS DO PALO ALTO
# ============================================================

PALOALTO_IP = paloalto["management_ip"]
VSYS = paloalto["vsys"]

WAN_INTERFACE = paloalto["wan_interface"]
LAN_INTERFACE = paloalto["lan_interface"]

VIRTUAL_ROUTER = paloalto["virtual_router"]

INTERNAL_ZONE = paloalto["internal_zone"]
EXTERNAL_ZONE = paloalto["external_zone"]
VPN_ZONE = paloalto["vpn_zone"]

TUNNEL_INTERFACE = paloalto["tunnel_interface"]
TUNNEL_ADDRESS_OBJECT = paloalto["tunnel_address_object"]

PHASE1_PROPOSAL = vpn["phase1_proposal"]
PHASE2_PROPOSAL = vpn["phase2_proposal"]

STATIC_ROUTE_NAME = paloalto["static_route_name"]

POLICY_LAN_TO_VPN = paloalto["policy_lan_to_vpn"]
POLICY_VPN_TO_LAN = paloalto["policy_vpn_to_lan"]



# ============================================================
# PARÂMETROS DA VPN
# ============================================================

IKE_PROFILE = vpn["paloalto_ike_profile"]
IKE_GATEWAY = vpn["paloalto_ike_gateway"]

IPSEC_PROFILE = vpn["paloalto_ipsec_profile"]
IPSEC_TUNNEL = vpn["paloalto_ipsec_tunnel"]

PROXY_ID = vpn["paloalto_proxy_id"]

LOCAL_WAN_IP = vpn["paloalto_wan_ip"]
PEER_IP = vpn["fortigate_wan_ip"]

LOCAL_NETWORK = vpn["paloalto_network"]
LOCAL_MASK = vpn["paloalto_mask"]
LOCAL_PREFIX = ipaddress.IPv4Network(
    f"0.0.0.0/{LOCAL_MASK}"
).prefixlen

REMOTE_NETWORK = vpn["fortigate_network"]
REMOTE_MASK = vpn["fortigate_mask"]
REMOTE_PREFIX = ipaddress.IPv4Network(
    f"0.0.0.0/{REMOTE_MASK}"
).prefixlen

TUNNEL_LOCAL_IP = vpn["paloalto_tunnel_ip"]
TUNNEL_MASK = vpn["tunnel_mask"]
TUNNEL_REMOTE_IP = vpn["fortigate_tunnel_ip"]
TUNNEL_PREFIX = ipaddress.IPv4Network(
    f"0.0.0.0/{TUNNEL_MASK}"
).prefixlen

PHASE1_ENCRYPTION, PHASE1_HASH = PHASE1_PROPOSAL.split("-")
PHASE2_ENCRYPTION, PHASE2_HASH = PHASE2_PROPOSAL.split("-")

PHASE1_LIFETIME = vpn["phase1_lifetime"]
PHASE2_LIFETIME = vpn["phase2_lifetime"]

DH_GROUP = vpn["dh_group"]


# ============================================================
# CREDENCIAIS
# ============================================================

API_KEY = os.getenv("PALOALTO_API_KEY")
PSK = os.getenv("PALOALTO_PSK")

if not API_KEY:
    print("[ERRO] Variável PALOALTO_API_KEY não encontrada.")
    exit()

if not PSK:
    print("[ERRO] Variável PALOALTO_PSK não encontrada.")
    exit()

PSK_XML = escape(PSK)


# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

BASE_URL = f"https://{PALOALTO_IP}/api/"

# Controle de alterações realizadas pela automação
ALTERACOES_REALIZADAS = False

# ============================================================
# TESTE DE COMUNICAÇÃO
# ============================================================

def testar_conexao():

    print("Testando comunicação com o Palo Alto...")

    parametros = {
        "type": "op",
        "cmd": "<show><system><info></info></system></show>",
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Palo Alto retornou HTTP "
                f"{response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print("[ERRO] A API respondeu, mas retornou uma falha.")
            print(response.text)
            return False

        print(f"[OK] Comunicação estabelecida com {PALOALTO_IP}.")
        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha na comunicação com o Palo Alto.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR IKE CRYPTO PROFILE
# ============================================================

def configurar_ike_crypto_profile():

    global ALTERACOES_REALIZADAS

    print("\nVerificando IKE Crypto Profile...")

    xpath = (
        "/config/devices/entry[@name='localhost.localdomain']"
        "/network/ike/crypto-profiles/ike-crypto-profiles"
        f"/entry[@name='{IKE_PROFILE}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar IKE Crypto Profile. "
                f"HTTP {response.status_code}."
            )
            return False

        # ----------------------------------------------------
        # PROFILE NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(f"[INFO] IKE Crypto Profile {IKE_PROFILE} não encontrado.")
            print("[INFO] Criando IKE Crypto Profile...")

            elemento = f"""
                <entry name="{IKE_PROFILE}">
                    <encryption>
                        <member>{PHASE1_ENCRYPTION}</member>
                    </encryption>
                    <hash>
                        <member>{PHASE1_HASH}</member>
                    </hash>
                    <dh-group>
                        <member>group{DH_GROUP}</member>
                    </dh-group>
                    <lifetime>
                        <hours>{PHASE1_LIFETIME // 3600}</hours>
                    </lifetime>
                </entry>
                """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": (
                    "/config/devices/entry[@name='localhost.localdomain']"
                    "/network/ike/crypto-profiles/ike-crypto-profiles"
                ),
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] IKE Crypto Profile {IKE_PROFILE} "
                    f"criado com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar IKE Crypto Profile "
                f"{IKE_PROFILE}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # PROFILE JÁ EXISTE
        # ----------------------------------------------------

        print(f"[INFO] IKE Crypto Profile {IKE_PROFILE} já existe.")

        verificacoes = {
            f"<member>{PHASE1_ENCRYPTION}</member>": f"Encryption {PHASE1_ENCRYPTION}",
            f"<member>{PHASE1_HASH}</member>": f"Hash {PHASE1_HASH}",
            f"<member>group{DH_GROUP}</member>": f"DH Group {DH_GROUP}",
            f"<hours>{PHASE1_LIFETIME // 3600}</hours>": f"Lifetime {PHASE1_LIFETIME // 3600} hora(s)"
        }

        divergencias = []

        for valor_xml, descricao in verificacoes.items():
            if valor_xml not in response.text:
                divergencias.append(descricao)

        if divergencias:
            print(
                f"[ALERTA] Foram encontradas divergências "
                f"no IKE Crypto Profile {IKE_PROFILE}:"
            )

            for divergencia in divergencias:
                print(f"  - {divergencia}")

            return False

        print(
            f"[OK] IKE Crypto Profile {IKE_PROFILE} "
            f"já está configurado corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:
        print(
            "[ERRO] Falha de comunicação ao configurar "
            "IKE Crypto Profile."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR IKE GATEWAY
# ============================================================

# ============================================================
# CONFIGURAR IKE GATEWAY
# ============================================================

def configurar_ike_gateway():

    global ALTERACOES_REALIZADAS

    print("\nVerificando IKE Gateway...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        "/network/ike/gateway"
    )

    xpath_gateway = (
        f"{xpath_base}/entry[@name='{IKE_GATEWAY}']"
    )

    # --------------------------------------------------------
    # CONSULTAR IKE GATEWAY
    # --------------------------------------------------------

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_gateway,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar IKE Gateway. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print("[ERRO] A API retornou uma falha ao consultar o IKE Gateway.")
            return False

        # ----------------------------------------------------
        # IKE GATEWAY NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(f"[INFO] IKE Gateway {IKE_GATEWAY} não encontrado.")
            print("[INFO] Criando IKE Gateway...")

            elemento = f"""
            <entry name="{IKE_GATEWAY}">
                <authentication>
                    <pre-shared-key>
                        <key>{PSK_XML}</key>
                    </pre-shared-key>
                </authentication>

                <protocol>
                    <ikev2>
                        <dpd>
                            <enable>yes</enable>
                        </dpd>

                        <ike-crypto-profile>
                            {IKE_PROFILE}
                        </ike-crypto-profile>
                    </ikev2>

                    <version>ikev2</version>
                </protocol>

                <protocol-common>
                    <nat-traversal>
                        <enable>no</enable>
                    </nat-traversal>
                </protocol-common>

                <local-address>
                    <interface>{WAN_INTERFACE}</interface>
                </local-address>

                <peer-address>
                    <ip>{PEER_IP}</ip>
                </peer-address>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] IKE Gateway {IKE_GATEWAY} "
                    f"criado com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar IKE Gateway "
                f"{IKE_GATEWAY}."
            )

            print(response.text)
            return False

        # ----------------------------------------------------
        # IKE GATEWAY JÁ EXISTE
        # ----------------------------------------------------

        print(f"[INFO] IKE Gateway {IKE_GATEWAY} já existe.")

        verificacoes = {
            f"<interface>{WAN_INTERFACE}</interface>":
                f"Interface WAN {WAN_INTERFACE}",

            f"<ip>{PEER_IP}</ip>":
                f"Peer {PEER_IP}",

            "<version>ikev2</version>":
                "IKEv2",

            f"<ike-crypto-profile>{IKE_PROFILE}</ike-crypto-profile>":
                f"IKE Crypto Profile {IKE_PROFILE}"
        }

        divergencias = []

        for valor_xml, descricao in verificacoes.items():

            if valor_xml not in response.text:
                divergencias.append(descricao)

        # ----------------------------------------------------
        # VERIFICAR DIVERGÊNCIAS
        # ----------------------------------------------------

        if divergencias:

            print(
                f"[ALERTA] Foram encontradas divergências "
                f"no IKE Gateway {IKE_GATEWAY}:"
            )

            for divergencia in divergencias:
                print(f"  - {divergencia}")

            return False

        print(
            f"[OK] IKE Gateway {IKE_GATEWAY} "
            f"já está configurado corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "IKE Gateway."
        )

        print(erro)
        return False

# ============================================================
# CONFIGURAR IPSEC CRYPTO PROFILE
# ============================================================

def configurar_ipsec_crypto_profile():

    global ALTERACOES_REALIZADAS

    print("\nVerificando IPSec Crypto Profile...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        "/network/ike/crypto-profiles/ipsec-crypto-profiles"
    )

    xpath_profile = (
        f"{xpath_base}/entry[@name='{IPSEC_PROFILE}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_profile,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar IPSec Crypto Profile. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao consultar "
                "o IPSec Crypto Profile."
            )
            return False

        # ----------------------------------------------------
        # PROFILE NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] IPSec Crypto Profile "
                f"{IPSEC_PROFILE} não encontrado."
            )

            print("[INFO] Criando IPSec Crypto Profile...")

            elemento = f"""
            <entry name="{IPSEC_PROFILE}">
                <esp>
                    <encryption>
                        <member>{PHASE2_ENCRYPTION}</member>
                    </encryption>

                    <authentication>
                        <member>{PHASE2_HASH}</member>
                    </authentication>
                </esp>

                <dh-group>
                    group{DH_GROUP}
                </dh-group>

                <lifetime>
                    <hours>{PHASE2_LIFETIME // 3600}</hours>
                </lifetime>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] IPSec Crypto Profile "
                    f"{IPSEC_PROFILE} criado com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar IPSec Crypto Profile "
                f"{IPSEC_PROFILE}."
            )

            print(response.text)
            return False

        # ----------------------------------------------------
        # PROFILE JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] IPSec Crypto Profile "
            f"{IPSEC_PROFILE} já existe."
        )

        verificacoes = {
            f"<member>{PHASE2_ENCRYPTION}</member>":
                f"Encryption {PHASE2_ENCRYPTION}",

            f"<member>{PHASE2_HASH}</member>":
                f"Authentication {PHASE2_HASH}",

            f"<dh-group>group{DH_GROUP}</dh-group>":
                f"PFS DH Group {DH_GROUP}",

            f"<hours>{PHASE2_LIFETIME // 3600}</hours>":
                f"Lifetime {PHASE2_LIFETIME // 3600} hora(s)"
        }

        divergencias = []

        for valor_xml, descricao in verificacoes.items():

            if valor_xml not in response.text:
                divergencias.append(descricao)

        # ----------------------------------------------------
        # VERIFICAR DIVERGÊNCIAS
        # ----------------------------------------------------

        if divergencias:

            print(
                f"[ALERTA] Foram encontradas divergências "
                f"no IPSec Crypto Profile {IPSEC_PROFILE}:"
            )

            for divergencia in divergencias:
                print(f"  - {divergencia}")

            return False

        print(
            f"[OK] IPSec Crypto Profile {IPSEC_PROFILE} "
            f"já está configurado corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "IPSec Crypto Profile."
        )

        print(erro)
        return False

# ============================================================
# CONFIGURAR OBJETO DE ENDEREÇO DO TÚNEL
# ============================================================

def configurar_tunnel_address_object():

    global ALTERACOES_REALIZADAS

    print("\nVerificando objeto de endereço do túnel...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        f"/vsys/entry[@name='{VSYS}']"
        "/address"
    )

    xpath_objeto = (
        f"{xpath_base}/entry[@name='{TUNNEL_ADDRESS_OBJECT}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_objeto,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar objeto "
                f"{TUNNEL_ADDRESS_OBJECT}. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao consultar "
                "o objeto de endereço do túnel."
            )
            return False

        endereco_esperado = (
            f"{TUNNEL_LOCAL_IP}/{TUNNEL_PREFIX}"
        )

        # ----------------------------------------------------
        # OBJETO NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] Objeto {TUNNEL_ADDRESS_OBJECT} "
                f"não encontrado."
            )

            print(
                "[INFO] Criando objeto de endereço do túnel..."
            )

            elemento = f"""
            <entry name="{TUNNEL_ADDRESS_OBJECT}">
                <ip-netmask>{endereco_esperado}</ip-netmask>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] Objeto {TUNNEL_ADDRESS_OBJECT} "
                    f"criado com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar objeto "
                f"{TUNNEL_ADDRESS_OBJECT}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # OBJETO JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] Objeto {TUNNEL_ADDRESS_OBJECT} "
            f"já existe."
        )

        if (
            f"<ip-netmask>{endereco_esperado}</ip-netmask>"
            not in response.text
        ):
            print(
                f"[ALERTA] Divergência no objeto "
                f"{TUNNEL_ADDRESS_OBJECT}."
            )
            print(f"  Esperado: {endereco_esperado}")
            return False

        print(
            f"[OK] Objeto {TUNNEL_ADDRESS_OBJECT} "
            f"já está configurado corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "o objeto de endereço do túnel."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR TUNNEL INTERFACE
# ============================================================

def configurar_tunnel_interface():

    global ALTERACOES_REALIZADAS

    print("\nVerificando Tunnel Interface...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        "/network/interface/tunnel/units"
    )

    xpath_tunnel = (
        f"{xpath_base}/entry[@name='{TUNNEL_INTERFACE}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_tunnel,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar Tunnel Interface. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao consultar "
                "a Tunnel Interface."
            )
            return False

        # ----------------------------------------------------
        # TUNNEL INTERFACE NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] Tunnel Interface "
                f"{TUNNEL_INTERFACE} não encontrada."
            )

            print("[INFO] Criando Tunnel Interface...")

            elemento = f"""
            <entry name="{TUNNEL_INTERFACE}">
                <ip>
                    <entry name="{TUNNEL_ADDRESS_OBJECT}"/>
                </ip>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] Tunnel Interface "
                    f"{TUNNEL_INTERFACE} criada com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar Tunnel Interface "
                f"{TUNNEL_INTERFACE}."
            )

            print(response.text)
            return False

        # ----------------------------------------------------
        # TUNNEL INTERFACE JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] Tunnel Interface "
            f"{TUNNEL_INTERFACE} já existe."
        )

        objeto_esperado = (
            f'name="{TUNNEL_ADDRESS_OBJECT}"'
        )

        if objeto_esperado not in response.text:

            print(
                f"[ALERTA] Divergência na Tunnel Interface "
                f"{TUNNEL_INTERFACE}."
            )

            print(
                f"  Objeto esperado: "
                f"{TUNNEL_ADDRESS_OBJECT}"
            )

            return False
        
        print(
            f"[OK] Tunnel Interface {TUNNEL_INTERFACE} "
            f"já está configurada corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "Tunnel Interface."
        )

        print(erro)
        return False

# ============================================================
# CONFIGURAR VIRTUAL ROUTER
# ============================================================

def configurar_virtual_router():

    global ALTERACOES_REALIZADAS

    print("\nVerificando associação ao Virtual Router...")

    xpath_vr = (
        "/config/devices/entry[@name='localhost.localdomain']"
        f"/network/virtual-router/entry[@name='{VIRTUAL_ROUTER}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_vr,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar Virtual Router. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao consultar "
                "o Virtual Router."
            )
            return False

        if "<entry" not in response.text:
            print(
                f"[ERRO] Virtual Router "
                f"{VIRTUAL_ROUTER} não encontrado."
            )
            return False

        print(
            f"[INFO] Virtual Router "
            f"{VIRTUAL_ROUTER} encontrado."
        )

        # Verifica se a Tunnel Interface já pertence ao VR
        interface_esperada = (
            f"<member>{TUNNEL_INTERFACE}</member>"
        )

        if interface_esperada in response.text:
            print(
                f"[OK] Interface {TUNNEL_INTERFACE} "
                f"já está associada ao Virtual Router "
                f"{VIRTUAL_ROUTER}."
            )
            return True

        # ----------------------------------------------------
        # INTERFACE NÃO ESTÁ ASSOCIADA AO VR
        # ----------------------------------------------------

        print(
            f"[INFO] Interface {TUNNEL_INTERFACE} "
            f"ainda não está associada ao Virtual Router."
        )

        print(
            f"[INFO] Adicionando {TUNNEL_INTERFACE} "
            f"ao Virtual Router {VIRTUAL_ROUTER}..."
        )

        xpath_interface = (
            f"{xpath_vr}/interface"
        )

        elemento = (
            f"<member>{TUNNEL_INTERFACE}</member>"
        )

        parametros = {
            "type": "config",
            "action": "set",
            "xpath": xpath_interface,
            "element": elemento,
            "key": API_KEY
        }

        response = requests.post(
            BASE_URL,
            data=parametros,
            verify=False,
            timeout=10
        )

        if (
            response.status_code == 200
            and 'status="success"' in response.text
        ):
            ALTERACOES_REALIZADAS = True
            print(
                f"[OK] Interface {TUNNEL_INTERFACE} "
                f"associada ao Virtual Router "
                f"{VIRTUAL_ROUTER} com sucesso."
            )
            return True

        print(
            f"[ERRO] Falha ao associar "
            f"{TUNNEL_INTERFACE} ao Virtual Router."
        )

        print(response.text)
        return False

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "o Virtual Router."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR ROTA ESTÁTICA
# ============================================================

def configurar_rota_estatica():

    global ALTERACOES_REALIZADAS

    print("\nVerificando rota estática...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        f"/network/virtual-router/entry[@name='{VIRTUAL_ROUTER}']"
        "/routing-table/ip/static-route"
    )

    xpath_rota = (
        f"{xpath_base}/entry[@name='{STATIC_ROUTE_NAME}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_rota,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar rota estática. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao "
                "consultar a rota estática."
            )
            return False

        destino_esperado = (
            f"{REMOTE_NETWORK}/{REMOTE_PREFIX}"
        )

        # ----------------------------------------------------
        # ROTA NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] Rota {STATIC_ROUTE_NAME} "
                f"não encontrada."
            )

            print("[INFO] Criando rota estática...")

            elemento = f"""
            <entry name="{STATIC_ROUTE_NAME}">
                <interface>{TUNNEL_INTERFACE}</interface>
                <metric>10</metric>
                <destination>{destino_esperado}</destination>
                <route-table>
                    <unicast/>
                </route-table>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] Rota {STATIC_ROUTE_NAME} "
                    f"criada com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar rota "
                f"{STATIC_ROUTE_NAME}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # ROTA JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] Rota {STATIC_ROUTE_NAME} já existe."
        )

        divergencias = []

        if (
            f"<destination>{destino_esperado}</destination>"
            not in response.text
        ):
            divergencias.append(
                f"Destino esperado: {destino_esperado}"
            )

        if (
            f"<interface>{TUNNEL_INTERFACE}</interface>"
            not in response.text
        ):
            divergencias.append(
                f"Interface esperada: {TUNNEL_INTERFACE}"
            )

        if "<metric>10</metric>" not in response.text:
            divergencias.append(
                "Métrica esperada: 10"
            )

        if divergencias:

            print(
                f"[ALERTA] Foram encontradas divergências "
                f"na rota {STATIC_ROUTE_NAME}:"
            )

            for divergencia in divergencias:
                print(f"  - {divergencia}")

            return False

        print(
            f"[OK] Rota {STATIC_ROUTE_NAME} "
            f"já está configurada corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "a rota estática."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR IPSEC TUNNEL
# ============================================================

def configurar_ipsec_tunnel():

    global ALTERACOES_REALIZADAS

    print("\nVerificando IPSec Tunnel...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        "/network/tunnel/ipsec"
    )

    xpath_tunnel = (
        f"{xpath_base}/entry[@name='{IPSEC_TUNNEL}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_tunnel,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar IPSec Tunnel. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha ao "
                "consultar o IPSec Tunnel."
            )
            return False

        local_esperado = (
            f"{LOCAL_NETWORK}/{LOCAL_PREFIX}"
        )

        remote_esperado = (
            f"{REMOTE_NETWORK}/{REMOTE_PREFIX}"
        )

        # ----------------------------------------------------
        # IPSEC TUNNEL NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] IPSec Tunnel {IPSEC_TUNNEL} "
                f"não encontrado."
            )

            print("[INFO] Criando IPSec Tunnel...")

            elemento = f"""
            <entry name="{IPSEC_TUNNEL}">
                <auto-key>
                    <ike-gateway>
                        <entry name="{IKE_GATEWAY}"/>
                    </ike-gateway>

                    <proxy-id>
                        <entry name="{PROXY_ID}">
                            <protocol>
                                <any/>
                            </protocol>
                            <local>{local_esperado}</local>
                            <remote>{remote_esperado}</remote>
                        </entry>
                    </proxy-id>

                    <ipsec-crypto-profile>
                        {IPSEC_PROFILE}
                    </ipsec-crypto-profile>
                </auto-key>

                <tunnel-monitor>
                    <enable>no</enable>
                </tunnel-monitor>

                <tunnel-interface>
                    {TUNNEL_INTERFACE}
                </tunnel-interface>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] IPSec Tunnel {IPSEC_TUNNEL} "
                    f"criado com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar IPSec Tunnel "
                f"{IPSEC_TUNNEL}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # IPSEC TUNNEL JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] IPSec Tunnel {IPSEC_TUNNEL} "
            f"já existe."
        )

        divergencias = []

        if (
            f'<entry name="{IKE_GATEWAY}"/>'
            not in response.text
        ):
            divergencias.append(
                f"IKE Gateway esperado: {IKE_GATEWAY}"
            )

        if (
            f"<ipsec-crypto-profile>{IPSEC_PROFILE}"
            f"</ipsec-crypto-profile>"
            not in response.text
        ):
            divergencias.append(
                f"IPSec Crypto Profile esperado: "
                f"{IPSEC_PROFILE}"
            )

        if (
            f"<tunnel-interface>{TUNNEL_INTERFACE}"
            f"</tunnel-interface>"
            not in response.text
        ):
            divergencias.append(
                f"Tunnel Interface esperada: "
                f"{TUNNEL_INTERFACE}"
            )

        if (
            f'<entry name="{PROXY_ID}">'
            not in response.text
        ):
            divergencias.append(
                f"Proxy-ID esperado: {PROXY_ID}"
            )

        if (
            f"<local>{local_esperado}</local>"
            not in response.text
        ):
            divergencias.append(
                f"Rede local esperada: {local_esperado}"
            )

        if (
            f"<remote>{remote_esperado}</remote>"
            not in response.text
        ):
            divergencias.append(
                f"Rede remota esperada: {remote_esperado}"
            )

        if divergencias:

            print(
                f"[ALERTA] Foram encontradas divergências "
                f"no IPSec Tunnel {IPSEC_TUNNEL}:"
            )

            for divergencia in divergencias:
                print(f"  - {divergencia}")

            return False

        print(
            f"[OK] IPSec Tunnel {IPSEC_TUNNEL} "
            f"já está configurado corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "o IPSec Tunnel."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR ZONA VPN
# ============================================================

def configurar_zona_vpn():

    global ALTERACOES_REALIZADAS

    print("\nVerificando zona VPN...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        f"/vsys/entry[@name='{VSYS}']"
        "/zone"
    )

    xpath_zona = (
        f"{xpath_base}/entry[@name='{VPN_ZONE}']"
    )

    parametros = {
        "type": "config",
        "action": "get",
        "xpath": xpath_zona,
        "key": API_KEY
    }

    try:
        response = requests.get(
            BASE_URL,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar zona VPN. "
                f"HTTP {response.status_code}."
            )
            return False

        if 'status="success"' not in response.text:
            print(
                "[ERRO] A API retornou uma falha "
                "ao consultar a zona VPN."
            )
            return False

        # ----------------------------------------------------
        # ZONA NÃO EXISTE
        # ----------------------------------------------------

        if "<entry" not in response.text:

            print(
                f"[INFO] Zona {VPN_ZONE} não encontrada."
            )

            print(
                f"[INFO] Criando zona {VPN_ZONE}..."
            )

            elemento = f"""
            <entry name="{VPN_ZONE}">
                <network>
                    <layer3>
                        <member>{TUNNEL_INTERFACE}</member>
                    </layer3>
                </network>
            </entry>
            """

            parametros = {
                "type": "config",
                "action": "set",
                "xpath": xpath_base,
                "element": elemento,
                "key": API_KEY
            }

            response = requests.post(
                BASE_URL,
                data=parametros,
                verify=False,
                timeout=10
            )

            if (
                response.status_code == 200
                and 'status="success"' in response.text
            ):
                ALTERACOES_REALIZADAS = True
                print(
                    f"[OK] Zona {VPN_ZONE} criada "
                    f"com sucesso."
                )
                return True

            print(
                f"[ERRO] Falha ao criar zona "
                f"{VPN_ZONE}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # ZONA JÁ EXISTE
        # ----------------------------------------------------

        print(
            f"[INFO] Zona {VPN_ZONE} já existe."
        )

        interface_esperada = (
            f"<member>{TUNNEL_INTERFACE}</member>"
        )

        if interface_esperada in response.text:

            print(
                f"[OK] Interface {TUNNEL_INTERFACE} "
                f"já está associada à zona {VPN_ZONE}."
            )
            return True

        # ----------------------------------------------------
        # ZONA EXISTE, MAS NÃO POSSUI A TUNNEL
        # ----------------------------------------------------

        print(
            f"[INFO] Interface {TUNNEL_INTERFACE} "
            f"não está associada à zona {VPN_ZONE}."
        )

        print(
            f"[INFO] Associando {TUNNEL_INTERFACE} "
            f"à zona {VPN_ZONE}..."
        )

        xpath_layer3 = (
            f"{xpath_zona}/network/layer3"
        )

        elemento = (
            f"<member>{TUNNEL_INTERFACE}</member>"
        )

        parametros = {
            "type": "config",
            "action": "set",
            "xpath": xpath_layer3,
            "element": elemento,
            "key": API_KEY
        }

        response = requests.post(
            BASE_URL,
            data=parametros,
            verify=False,
            timeout=10
        )

        if (
            response.status_code == 200
            and 'status="success"' in response.text
        ):
            ALTERACOES_REALIZADAS = True
            print(
                f"[OK] Interface {TUNNEL_INTERFACE} "
                f"associada à zona {VPN_ZONE} "
                f"com sucesso."
            )
            return True

        print(
            f"[ERRO] Falha ao associar "
            f"{TUNNEL_INTERFACE} à zona {VPN_ZONE}."
        )
        print(response.text)
        return False

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação "
            "ao configurar a zona VPN."
        )
        print(erro)
        return False

# ============================================================
# CONFIGURAR SECURITY POLICIES
# ============================================================

def configurar_security_policies():

    global ALTERACOES_REALIZADAS

    print("\nVerificando Security Policies...")

    xpath_base = (
        "/config/devices/entry[@name='localhost.localdomain']"
        f"/vsys/entry[@name='{VSYS}']"
        "/rulebase/security/rules"
    )

    local_network = (
        f"{LOCAL_NETWORK}/{LOCAL_PREFIX}"
    )

    remote_network = (
        f"{REMOTE_NETWORK}/{REMOTE_PREFIX}"
    )

    policies = [
        {
            "name": POLICY_LAN_TO_VPN,
            "from": INTERNAL_ZONE,
            "to": VPN_ZONE,
            "source": local_network,
            "destination": remote_network
        },
        {
            "name": POLICY_VPN_TO_LAN,
            "from": VPN_ZONE,
            "to": INTERNAL_ZONE,
            "source": remote_network,
            "destination": local_network
        }
    ]

    try:

        for policy in policies:

            nome = policy["name"]

            print(f"\nVerificando policy {nome}...")

            xpath_policy = (
                f"{xpath_base}/entry[@name='{nome}']"
            )

            parametros = {
                "type": "config",
                "action": "get",
                "xpath": xpath_policy,
                "key": API_KEY
            }

            response = requests.get(
                BASE_URL,
                params=parametros,
                verify=False,
                timeout=10
            )

            if response.status_code != 200:
                print(
                    f"[ERRO] Falha ao consultar policy "
                    f"{nome}. HTTP {response.status_code}."
                )
                return False

            if 'status="success"' not in response.text:
                print(
                    f"[ERRO] A API retornou uma falha "
                    f"ao consultar a policy {nome}."
                )
                return False

            # ------------------------------------------------
            # POLICY NÃO EXISTE
            # ------------------------------------------------

            if "<entry" not in response.text:

                print(
                    f"[INFO] Policy {nome} não encontrada."
                )

                print(
                    f"[INFO] Criando policy {nome}..."
                )

                elemento = f"""
                <entry name="{nome}">
                    <from>
                        <member>{policy["from"]}</member>
                    </from>
                    <to>
                        <member>{policy["to"]}</member>
                    </to>
                    <source>
                        <member>{policy["source"]}</member>
                    </source>
                    <destination>
                        <member>{policy["destination"]}</member>
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
                    "xpath": xpath_base,
                    "element": elemento,
                    "key": API_KEY
                }

                response = requests.post(
                    BASE_URL,
                    data=parametros,
                    verify=False,
                    timeout=10
                )

                if (
                    response.status_code == 200
                    and 'status="success"' in response.text
                ):
                    ALTERACOES_REALIZADAS = True

                    print(
                        f"[OK] Policy {nome} "
                        f"criada com sucesso."
                    )
                    continue

                print(
                    f"[ERRO] Falha ao criar policy {nome}."
                )
                print(response.text)
                return False

            # ------------------------------------------------
            # POLICY JÁ EXISTE
            # ------------------------------------------------

            print(
                f"[INFO] Policy {nome} já existe."
            )

            verificacoes = {
                (
                    f"<from>"
                    f"<member>{policy['from']}</member>"
                    f"</from>"
                ):
                    f"Zona de origem: {policy['from']}",

                (
                    f"<to>"
                    f"<member>{policy['to']}</member>"
                    f"</to>"
                ):
                    f"Zona de destino: {policy['to']}",

                (
                    f"<source>"
                    f"<member>{policy['source']}</member>"
                    f"</source>"
                ):
                    f"Origem: {policy['source']}",

                (
                    f"<destination>"
                    f"<member>{policy['destination']}</member>"
                    f"</destination>"
                ):
                    f"Destino: {policy['destination']}",

                (
                    "<application>"
                    "<member>any</member>"
                    "</application>"
                ):
                    "Application: any",

                (
                    "<service>"
                    "<member>application-default</member>"
                    "</service>"
                ):
                    "Service: application-default",

                "<action>allow</action>":
                    "Action: allow"
            }

            divergencias = []

            # Remove espaços e quebras de linha do XML
            xml = "".join(response.text.split())

            for esperado, descricao in verificacoes.items():

                esperado = "".join(esperado.split())

                if esperado not in xml:
                    divergencias.append(descricao)

            if divergencias:

                print(
                    f"[ALERTA] Foram encontradas "
                    f"divergências na policy {nome}:"
                )

                for divergencia in divergencias:
                    print(f"  - {divergencia}")

                return False

            print(
                f"[OK] Policy {nome} já está "
                f"configurada corretamente."
            )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação ao configurar "
            "as Security Policies."
        )
        print(erro)
        return False

# ============================================================
# COMMIT
# ============================================================

def realizar_commit():

    if not ALTERACOES_REALIZADAS:
        print(
            "\n[INFO] Nenhuma alteração realizada. "
            "Commit não necessário."
        )
        return "sem_alteracoes"

    print(
        "\n[INFO] A automação realizou alterações "
        "na candidate configuration do Palo Alto."
    )

    while True:
        resposta = input(
            "\nDeseja aplicar as alterações com commit? [S/N]: "
        ).strip().lower()

        if resposta in ["s", "sim"]:
            break

        if resposta in ["n", "nao", "não"]:
            print(
                "\n[INFO] Commit não realizado por opção do usuário."
            )
            print(
                "[INFO] As alterações permanecem na "
                "candidate configuration."
            )
            return "nao_aplicado"

        print(
            "[ALERTA] Opção inválida. "
            "Digite S para sim ou N para não."
        )

    print("\nIniciando commit...")

    parametros = {
        "type": "commit",
        "cmd": "<commit></commit>",
        "key": API_KEY
    }

    try:
        response = requests.post(
            BASE_URL,
            data=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao iniciar commit. "
                f"HTTP {response.status_code}."
            )
            return "erro"

        if 'status="success"' not in response.text:
            print("[ERRO] Palo Alto recusou o commit.")
            print(response.text)
            return "erro"

        root = ET.fromstring(response.text)
        job = root.findtext(".//job")

        if not job:
            print(
                "[ERRO] Não foi possível identificar "
                "o Job ID do commit."
            )
            return "erro"

        print(f"[INFO] Commit iniciado. Job ID: {job}")

        if acompanhar_commit(job):
            return "commit_ok"

        return "erro"

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação durante o commit.")
        print(erro)
        return "erro"

    except ET.ParseError as erro:
        print(
            "[ERRO] Não foi possível interpretar "
            "a resposta do commit."
        )
        print(erro)
        return "erro"


def acompanhar_commit(job):

    print("[INFO] Aguardando conclusão do commit...")

    comando = (
        "<show>"
        "<jobs>"
        f"<id>{job}</id>"
        "</jobs>"
        "</show>"
    )

    parametros = {
        "type": "op",
        "cmd": comando,
        "key": API_KEY
    }

    for tentativa in range(30):

        try:
            response = requests.get(
                BASE_URL,
                params=parametros,
                verify=False,
                timeout=10
            )

            if response.status_code != 200:
                print(
                    "[ERRO] Falha ao consultar "
                    "o status do commit."
                )
                return False

            if 'status="success"' not in response.text:
                print(
                    "[ERRO] A API retornou uma falha "
                    "ao consultar o Job."
                )
                return False

            root = ET.fromstring(response.text)

            status = root.findtext(".//job/status")
            resultado = root.findtext(".//job/result")

            if status == "FIN":
                    
                if resultado == "OK":
                    print(
                        f"[OK] Commit concluído "
                        f"com sucesso. Job {job}."
                    )
                    return True

                print(
                    f"[ERRO] Commit finalizado "
                    f"com resultado: {resultado}"
                )
                return False

            print(
                f"[INFO] Commit em andamento... "
                f"Status: {status}"
            )

            time.sleep(2)

        except requests.exceptions.RequestException as erro:
            print(
                "[ERRO] Falha de comunicação ao "
                "consultar o Job do commit."
            )
            print(erro)
            return False

        except ET.ParseError as erro:
            print(
                "[ERRO] Não foi possível interpretar "
                "o status do commit."
            )
            print(erro)
            return False

    print(
        "[ERRO] Tempo limite excedido "
        "aguardando o commit."
    )
    return False

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print(" AUTOMAÇÃO VPN - PALO ALTO")
    print("========================================")
    print()

    if not testar_conexao():
        print("\n[ERRO] Automação interrompida.")
        exit()

    print("\n[OK] Parâmetros carregados com sucesso.")

    if not configurar_ike_crypto_profile():
        print("\n[ERRO] Falha na configuração do IKE Crypto Profile.")
        exit()

    if not configurar_ike_gateway():
        print("\n[ERRO] Falha na configuração do IKE Gateway.")
        exit()

    if not configurar_ipsec_crypto_profile():
        print("\n[ERRO] Falha na configuração do IPSec Crypto Profile.")
        exit()

    if not configurar_tunnel_address_object():
        print("\n[ERRO] Falha na configuração do objeto de endereço do túnel.")
        exit()

    if not configurar_tunnel_interface():
        print("\n[ERRO] Falha na configuração da Tunnel Interface.")
        exit()

    if not configurar_virtual_router():
        print("\n[ERRO] Falha na configuração do Virtual Router.")
        exit()

    if not configurar_rota_estatica():
        print("\n[ERRO] Falha na configuração da rota estática.")
        exit()

    if not configurar_ipsec_tunnel():
        print("\n[ERRO] Falha na configuração do IPSec Tunnel.")
        exit()

    if not configurar_zona_vpn():
        print("\n[ERRO] Falha na configuração da zona VPN.")
        exit()

    if not configurar_security_policies():
        print("\n[ERRO] Falha na configuração das Security Policies.")
        exit()

    resultado_commit = realizar_commit()

    if resultado_commit == "erro":
        print(
            "\n[ERRO] A configuração foi preparada, "
            "mas houve falha no commit."
        )
        exit()

    if resultado_commit == "nao_aplicado":
        print(
            "\n[INFO] Configuração preparada, mas não aplicada."
        )
        print(
            "[INFO] As alterações permanecem na candidate configuration."
        )
    elif resultado_commit == "commit_ok":
        print(
            "\n[OK] Configuração do Palo Alto aplicada com sucesso."
        )
    else:
        print(
            "\n[OK] Configuração do Palo Alto validada com sucesso."
        )
