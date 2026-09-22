import requests
import urllib3
import os
import json
from pathlib import Path
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
# CARREGAR CONFIGURAÇÕES
# ============================================================

CAMINHO_CONFIG = Path(__file__).parent / "config.json"

try:
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

except FileNotFoundError:
    print(
        f"[ERRO] Arquivo config.json não encontrado: "
        f"{CAMINHO_CONFIG}"
    )
    exit()

except json.JSONDecodeError as erro:
    print("[ERRO] O arquivo config.json possui formato inválido.")
    print(
        f"Detalhes: linha {erro.lineno}, "
        f"coluna {erro.colno}."
    )
    exit()


# ============================================================
# PARÂMETROS DO FORTIGATE
# ============================================================

fortigate = config["fortigate"]
vpn = config["vpn"]

paloalto = config["paloalto"]

FORTIGATE_IP = fortigate["management_ip"]
VDOM = fortigate["vdom"]

VPN_NAME = vpn["fortigate_phase1_name"]
PHASE2_NAME = vpn["fortigate_phase2_name"]


# ============================================================
# CREDENCIAIS FORTIGATE
# ============================================================

TOKEN = os.getenv("FORTIGATE_TOKEN")

if not TOKEN:
    print(
        "[ERRO] Variável FORTIGATE_TOKEN "
        "não encontrada."
    )
    exit()

# ============================================================
# PARÂMETROS DO PALO ALTO
# ============================================================

paloalto = config["paloalto"]

PALOALTO_IP = paloalto["management_ip"]

IKE_GATEWAY = vpn["paloalto_ike_gateway"]
IPSEC_TUNNEL = vpn["paloalto_ipsec_tunnel"]
PROXY_ID = vpn["paloalto_proxy_id"]

# ============================================================
# CREDENCIAIS PALO ALTO
# ============================================================

PALOALTO_API_KEY = os.getenv("PALOALTO_API_KEY")

if not PALOALTO_API_KEY:
    print(
        "[ERRO] Variável PALOALTO_API_KEY "
        "não encontrada."
    )
    exit()

# ============================================================
# VALIDAR VPN NO FORTIGATE
# ============================================================

def validar_vpn_fortigate():

    print("\nValidando VPN no FortiGate...")

    url = (
        f"https://{FORTIGATE_IP}"
        f"/api/v2/monitor/vpn/ipsec"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    parametros = {
        "vdom": VDOM
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=parametros,
            verify=False,
            timeout=10
        )

        # ----------------------------------------------------
        # VALIDAR RESPOSTA HTTP
        # ----------------------------------------------------

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar VPN "
                f"no FortiGate. "
                f"HTTP {response.status_code}."
            )
            return False

        dados = response.json()

        # ----------------------------------------------------
        # VALIDAR RESPOSTA DA API
        # ----------------------------------------------------

        if dados.get("status") != "success":
            print(
                "[ERRO] FortiGate não retornou "
                "uma consulta válida."
            )
            return False

        # ----------------------------------------------------
        # LOCALIZAR PHASE 1
        # ----------------------------------------------------

        vpns = dados.get("results", [])

        vpn_encontrada = None

        for vpn_resultado in vpns:

            if vpn_resultado.get("name") == VPN_NAME:
                vpn_encontrada = vpn_resultado
                break

        if not vpn_encontrada:
            print(
                f"[ERRO] VPN {VPN_NAME} "
                f"não encontrada no FortiGate."
            )
            return False

        print(
            f"[OK] VPN {VPN_NAME} encontrada."
        )

        # ----------------------------------------------------
        # LOCALIZAR PHASE 2
        # ----------------------------------------------------

        phase2_encontrada = None

        for phase2 in vpn_encontrada.get("proxyid", []):

            if phase2.get("p2name") == PHASE2_NAME:
                phase2_encontrada = phase2
                break

        if not phase2_encontrada:
            print(
                f"[ERRO] Phase 2 {PHASE2_NAME} "
                f"não encontrada."
            )
            return False

        print(
            f"[OK] Phase 2 {PHASE2_NAME} encontrada."
        )

        # ----------------------------------------------------
        # VALIDAR STATUS DA PHASE 2
        # ----------------------------------------------------

        status_phase2 = phase2_encontrada.get("status")

        if status_phase2 == "up":

            print(
                "[OK] VPN operacional no FortiGate. "
                "Phase 2 está UP."
            )

            return True

        print(
            "[ALERTA] VPN não está operacional "
            "no FortiGate. "
            f"Phase 2 está {status_phase2}."
        )

        return False

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação "
            "com o FortiGate."
        )

        print(erro)

        return False

    except ValueError:

        print(
            "[ERRO] O FortiGate retornou "
            "uma resposta inválida."
        )

        return False

# ============================================================
# VALIDAR VPN NO PALO ALTO
# ============================================================

def validar_vpn_paloalto():

    print("\nValidando VPN no Palo Alto...")

    base_url = f"https://{PALOALTO_IP}/api/"

    # --------------------------------------------------------
    # VALIDAR IKE SA
    # --------------------------------------------------------

    comando_ike = (
        "<show>"
        "<vpn>"
        "<ike-sa></ike-sa>"
        "</vpn>"
        "</show>"
    )

    parametros_ike = {
        "type": "op",
        "cmd": comando_ike,
        "key": PALOALTO_API_KEY
    }

    try:
        response_ike = requests.get(
            base_url,
            params=parametros_ike,
            verify=False,
            timeout=10
        )

        if response_ike.status_code != 200:
            print(
                "[ERRO] Falha ao consultar IKE SA "
                f"no Palo Alto. HTTP "
                f"{response_ike.status_code}."
            )
            return False

        if 'status="success"' not in response_ike.text:
            print(
                "[ERRO] Palo Alto retornou uma falha "
                "ao consultar IKE SA."
            )
            return False

        root_ike = ET.fromstring(response_ike.text)

        ike_encontrada = False

        for entry in root_ike.findall(".//entry"):

            nome = entry.findtext("name")

            if nome == IKE_GATEWAY:
                ike_encontrada = True
                break

        if not ike_encontrada:
            print(
                f"[ALERTA] IKE SA do gateway "
                f"{IKE_GATEWAY} não está ativa."
            )
            return False

        print(
            f"[OK] IKE SA do gateway "
            f"{IKE_GATEWAY} está ativa."
        )

        # ----------------------------------------------------
        # VALIDAR IPSEC SA
        # ----------------------------------------------------

        comando_ipsec = (
            "<show>"
            "<vpn>"
            "<ipsec-sa></ipsec-sa>"
            "</vpn>"
            "</show>"
        )

        parametros_ipsec = {
            "type": "op",
            "cmd": comando_ipsec,
            "key": PALOALTO_API_KEY
        }

        response_ipsec = requests.get(
            base_url,
            params=parametros_ipsec,
            verify=False,
            timeout=10
        )

        if response_ipsec.status_code != 200:
            print(
                "[ERRO] Falha ao consultar IPSec SA "
                f"no Palo Alto. HTTP "
                f"{response_ipsec.status_code}."
            )
            return False

        if 'status="success"' not in response_ipsec.text:
            print(
                "[ERRO] Palo Alto retornou uma falha "
                "ao consultar IPSec SA."
            )
            return False

        root_ipsec = ET.fromstring(response_ipsec.text)

        nome_sa_esperado = (
            f"{IPSEC_TUNNEL}:{PROXY_ID}"
        )

        ipsec_encontrada = None

        for entry in root_ipsec.findall(".//entry"):

            nome = entry.findtext("name")

            if nome == nome_sa_esperado:
                ipsec_encontrada = entry
                break

        if ipsec_encontrada is None:
            print(
                f"[ALERTA] IPSec SA "
                f"{nome_sa_esperado} não está ativa."
            )
            return False

        # ----------------------------------------------------
        # VALIDAR GATEWAY E SPIs
        # ----------------------------------------------------

        gateway = ipsec_encontrada.findtext("gateway")
        i_spi = ipsec_encontrada.findtext("i_spi")
        o_spi = ipsec_encontrada.findtext("o_spi")

        if gateway != IKE_GATEWAY:
            print(
                "[ALERTA] IPSec SA encontrada, mas "
                "está associada a um gateway diferente."
            )
            return False

        if not i_spi or not o_spi:
            print(
                "[ALERTA] IPSec SA encontrada, mas "
                "os SPIs não foram identificados."
            )
            return False

        print(
            f"[OK] IPSec SA {nome_sa_esperado} "
            "está ativa."
        )

        print(
            "[OK] VPN operacional no Palo Alto."
        )

        return True

    except requests.exceptions.RequestException as erro:

        print(
            "[ERRO] Falha de comunicação "
            "com o Palo Alto."
        )

        print(erro)

        return False

    except ET.ParseError:

        print(
            "[ERRO] Não foi possível interpretar "
            "a resposta XML do Palo Alto."
        )

        return False


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print(" VALIDAÇÃO VPN IPSEC")
    print("========================================")

    resultado_fortigate = validar_vpn_fortigate()
    resultado_paloalto = validar_vpn_paloalto()

    print("\n========================================")
    print(" RESUMO DA VALIDAÇÃO")
    print("========================================")

    if resultado_fortigate:
        print("FortiGate : VPN UP")
    else:
        print("FortiGate : VPN DOWN")

    if resultado_paloalto:
        print("Palo Alto : VPN UP")
    else:
        print("Palo Alto : VPN DOWN")

    print("========================================")

    if resultado_fortigate and resultado_paloalto:
        print(
            "[OK] VPN IPSec operacional "
            "nos dois firewalls."
        )
    else:
        print(
            "[ALERTA] A VPN IPSec não está "
            "operacional nos dois firewalls."
        )

    print("========================================")