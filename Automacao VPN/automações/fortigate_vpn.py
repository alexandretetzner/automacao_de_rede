import requests
import urllib3
import os
import json
from pathlib import Path

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

fortigate = config["fortigate"]
vpn = config["vpn"]


# ============================================================
# PARÂMETROS DO FORTIGATE
# ============================================================

FORTIGATE_IP = fortigate["management_ip"]
VDOM = fortigate["vdom"]
WAN_INTERFACE = fortigate["wan_interface"]
LAN_INTERFACE = fortigate["lan_interface"]

LOCAL_ADDRESS = fortigate["local_address_object"]
REMOTE_ADDRESS = fortigate["remote_address_object"]


# ============================================================
# PARÂMETROS DA VPN
# ============================================================

PHASE1_NAME = vpn["fortigate_phase1_name"]
PHASE2_NAME = vpn["fortigate_phase2_name"]

PEER_IP = vpn["paloalto_wan_ip"]

LOCAL_NETWORK = vpn["fortigate_network"]
LOCAL_MASK = vpn["fortigate_mask"]

REMOTE_NETWORK = vpn["paloalto_network"]
REMOTE_MASK = vpn["paloalto_mask"]

TUNNEL_LOCAL_IP = vpn["fortigate_tunnel_ip"]
TUNNEL_REMOTE_IP = vpn["paloalto_tunnel_ip"]
TUNNEL_MASK = vpn["tunnel_mask"]

PHASE1_PROPOSAL = vpn["phase1_proposal"]
PHASE2_PROPOSAL = vpn["phase2_proposal"]

DH_GROUP = vpn["dh_group"]

PHASE1_LIFETIME = vpn["phase1_lifetime"]
PHASE2_LIFETIME = vpn["phase2_lifetime"]


# ============================================================
# CREDENCIAIS
# ============================================================

TOKEN = os.getenv("FORTIGATE_TOKEN")
PSK = os.getenv("FORTIGATE_PSK")

if not TOKEN:
    print("[ERRO] Variável FORTIGATE_TOKEN não encontrada.")
    exit()

if not PSK:
    print("[ERRO] Variável FORTIGATE_PSK não encontrada.")
    exit()


# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

BASE_URL = f"https://{FORTIGATE_IP}/api/v2"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}


# ============================================================
# TESTE DE COMUNICAÇÃO
# ============================================================

def testar_conexao():

    url = f"{BASE_URL}/cmdb/system/interface"

    parametros = {
        "vdom": VDOM
    }

    print("Testando comunicação com o FortiGate...")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            print(f"[OK] Comunicação estabelecida com {FORTIGATE_IP}.")
            return True

        print(f"[ERRO] FortiGate retornou HTTP {response.status_code}.")
        return False

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha na comunicação com o FortiGate.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR PHASE 1
# ============================================================

def configurar_phase1():

    url = f"{BASE_URL}/cmdb/vpn.ipsec/phase1-interface"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando Phase 1...")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(f"[ERRO] Falha ao consultar Phase 1. HTTP {response.status_code}.")
            return False

        dados = response.json()

        phase1_atual = None

        for item in dados.get("results", []):
            if item.get("name") == PHASE1_NAME:
                phase1_atual = item
                break

        # ----------------------------------------------------
        # PHASE 1 NÃO EXISTE
        # ----------------------------------------------------

        if phase1_atual is None:

            print(f"[INFO] Phase 1 {PHASE1_NAME} não encontrada.")
            print("[INFO] Criando Phase 1...")

            nova_phase1 = {
                "name": PHASE1_NAME,
                "type": "static",
                "interface": WAN_INTERFACE,
                "ike-version": "2",
                "remote-gw": PEER_IP,
                "authmethod": "psk",
                "psksecret": PSK,
                "proposal": PHASE1_PROPOSAL,
                "dhgrp": DH_GROUP,
                "keylife": PHASE1_LIFETIME
            }

            response = requests.post(
                url,
                headers=HEADERS,
                params=parametros,
                json=nova_phase1,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                print(f"[OK] Phase 1 {PHASE1_NAME} criada com sucesso.")
                return True

            print(f"[ERRO] Falha ao criar Phase 1. HTTP {response.status_code}.")
            print(response.text)
            return False

        # ----------------------------------------------------
        # PHASE 1 JÁ EXISTE
        # ----------------------------------------------------

        print(f"[INFO] Phase 1 {PHASE1_NAME} já existe.")

        esperado = {
            "interface": WAN_INTERFACE,
            "ike-version": "2",
            "remote-gw": PEER_IP,
            "proposal": PHASE1_PROPOSAL,
            "dhgrp": DH_GROUP,
            "keylife": PHASE1_LIFETIME
        }

        divergencias = []

        for campo, valor_esperado in esperado.items():

            valor_atual = phase1_atual.get(campo)

            if str(valor_atual) != str(valor_esperado):
                divergencias.append(
                    f"{campo}: atual={valor_atual} / esperado={valor_esperado}"
                )

        if divergencias:
            print("[ALERTA] Foram encontradas divergências na Phase 1:")

            for divergencia in divergencias:
                print("  -", divergencia)

            return False

        print("[OK] Phase 1 já existe e está de acordo com o config.json.")
        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar Phase 1.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR PHASE 2
# ============================================================

def configurar_phase2():

    url = f"{BASE_URL}/cmdb/vpn.ipsec/phase2-interface"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando Phase 2...")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(f"[ERRO] Falha ao consultar Phase 2. HTTP {response.status_code}.")
            return False

        dados = response.json()

        phase2_atual = None

        for item in dados.get("results", []):
            if item.get("name") == PHASE2_NAME:
                phase2_atual = item
                break

        # ----------------------------------------------------
        # PHASE 2 NÃO EXISTE
        # ----------------------------------------------------

        if phase2_atual is None:

            print(f"[INFO] Phase 2 {PHASE2_NAME} não encontrada.")
            print("[INFO] Criando Phase 2...")

            nova_phase2 = {
                "name": PHASE2_NAME,
                "phase1name": PHASE1_NAME,
                "proposal": PHASE2_PROPOSAL,
                "pfs": "enable",
                "dhgrp": DH_GROUP,
                "keylifeseconds": PHASE2_LIFETIME,
                "src-subnet": f"{LOCAL_NETWORK} {LOCAL_MASK}",
                "dst-subnet": f"{REMOTE_NETWORK} {REMOTE_MASK}"
            }

            response = requests.post(
                url,
                headers=HEADERS,
                params=parametros,
                json=nova_phase2,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                print(f"[OK] Phase 2 {PHASE2_NAME} criada com sucesso.")
                return True

            print(f"[ERRO] Falha ao criar Phase 2. HTTP {response.status_code}.")
            print(response.text)
            return False

        # ----------------------------------------------------
        # PHASE 2 JÁ EXISTE
        # ----------------------------------------------------

        print(f"[INFO] Phase 2 {PHASE2_NAME} já existe.")

        esperado = {
            "phase1name": PHASE1_NAME,
            "proposal": PHASE2_PROPOSAL,
            "pfs": "enable",
            "dhgrp": DH_GROUP,
            "keylifeseconds": PHASE2_LIFETIME,
            "src-subnet": f"{LOCAL_NETWORK} {LOCAL_MASK}",
            "dst-subnet": f"{REMOTE_NETWORK} {REMOTE_MASK}"
        }

        divergencias = []

        for campo, valor_esperado in esperado.items():

            valor_atual = phase2_atual.get(campo)

            if str(valor_atual) != str(valor_esperado):
                divergencias.append(
                    f"{campo}: atual={valor_atual} / esperado={valor_esperado}"
                )

        if divergencias:
            print("[ALERTA] Foram encontradas divergências na Phase 2:")

            for divergencia in divergencias:
                print("  -", divergencia)

            return False

        print("[OK] Phase 2 já existe e está de acordo com o config.json.")
        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar Phase 2.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR INTERFACE TUNNEL
# ============================================================

def configurar_interface_tunnel():

    url = f"{BASE_URL}/cmdb/system/interface/{PHASE1_NAME}"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando interface do túnel...")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Não foi possível consultar a interface "
                f"{PHASE1_NAME}. HTTP {response.status_code}."
            )
            return False

        dados = response.json()
        resultados = dados.get("results", [])

        interface = None

        for item in resultados:
            if item.get("name") == PHASE1_NAME:
                interface = item
                break

        if interface is None:
            print(f"[ERRO] Interface {PHASE1_NAME} não encontrada.")
            return False

        ip_esperado = f"{TUNNEL_LOCAL_IP} 255.255.255.255"
        remote_ip_esperado = f"{TUNNEL_REMOTE_IP} {TUNNEL_MASK}"

        ip_atual = interface.get("ip")
        remote_ip_atual = interface.get("remote-ip")

        divergencias = []

        if str(ip_atual) != ip_esperado:
            divergencias.append(
                f"ip: atual={ip_atual} / esperado={ip_esperado}"
            )

        if str(remote_ip_atual) != remote_ip_esperado:
            divergencias.append(
                f"remote-ip: atual={remote_ip_atual} / "
                f"esperado={remote_ip_esperado}"
            )

        # Interface já está correta
        if not divergencias:
            print(f"[OK] Interface {PHASE1_NAME} já está configurada corretamente.")
            return True

        # Interface existe, mas precisa receber os IPs
        print("[INFO] Configurando endereçamento da interface do túnel...")

        configuracao = {
            "ip": ip_esperado,
            "remote-ip": remote_ip_esperado
        }

        response = requests.put(
            url,
            headers=HEADERS,
            params=parametros,
            json=configuracao,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao configurar interface do túnel. "
                f"HTTP {response.status_code}."
            )
            print(response.text)
            return False

        print(f"[OK] Interface {PHASE1_NAME} configurada com sucesso.")
        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar a interface do túnel.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR ADDRESS OBJECTS
# ============================================================

def configurar_address_objects():

    url = f"{BASE_URL}/cmdb/firewall/address"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando Address Objects...")

    enderecos = [
        {
            "name": LOCAL_ADDRESS,
            "type": "ipmask",
            "subnet": f"{LOCAL_NETWORK} {LOCAL_MASK}"
        },
        {
            "name": REMOTE_ADDRESS,
            "type": "ipmask",
            "subnet": f"{REMOTE_NETWORK} {REMOTE_MASK}"
        }
    ]

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar Address Objects. "
                f"HTTP {response.status_code}."
            )
            return False

        dados = response.json()
        objetos_existentes = dados.get("results", [])

        for endereco in enderecos:

            objeto_atual = None

            for item in objetos_existentes:
                if item.get("name") == endereco["name"]:
                    objeto_atual = item
                    break

            # Objeto não existe
            if objeto_atual is None:

                print(
                    f"[INFO] Address Object {endereco['name']} "
                    f"não encontrado."
                )

                response = requests.post(
                    url,
                    headers=HEADERS,
                    params=parametros,
                    json=endereco,
                    verify=False,
                    timeout=10
                )

                if response.status_code != 200:
                    print(
                        f"[ERRO] Falha ao criar {endereco['name']}. "
                        f"HTTP {response.status_code}."
                    )
                    print(response.text)
                    return False

                print(
                    f"[OK] Address Object {endereco['name']} "
                    f"criado com sucesso."
                )

                continue

            # Objeto já existe
            subnet_atual = objeto_atual.get("subnet")
            subnet_esperada = endereco["subnet"]

            if str(subnet_atual) != str(subnet_esperada):
                print(
                    f"[ALERTA] Divergência no Address Object "
                    f"{endereco['name']}."
                )
                print(f"  Atual:    {subnet_atual}")
                print(f"  Esperado: {subnet_esperada}")
                return False

            print(
                f"[OK] Address Object {endereco['name']} "
                f"já está configurado corretamente."
            )

        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar Address Objects.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR ROTA
# ============================================================

def configurar_rota():

    url = f"{BASE_URL}/cmdb/router/static"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando rota estática...")

    destino_esperado = f"{REMOTE_NETWORK} {REMOTE_MASK}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar rotas estáticas. "
                f"HTTP {response.status_code}."
            )
            return False

        dados = response.json()
        rotas = dados.get("results", [])

        rota_atual = None

        # Procura a rota pela rede de destino
        for item in rotas:
            if item.get("dst") == destino_esperado:
                rota_atual = item
                break

        # ----------------------------------------------------
        # ROTA NÃO EXISTE
        # ----------------------------------------------------

        if rota_atual is None:

            print(
                f"[INFO] Rota para {REMOTE_NETWORK}/{REMOTE_MASK} "
                f"não encontrada."
            )
            print("[INFO] Criando rota estática...")

            nova_rota = {
                "dst": destino_esperado,
                "device": PHASE1_NAME,
                "gateway": "0.0.0.0",
                "distance": 10,
                "status": "enable"
            }

            response = requests.post(
                url,
                headers=HEADERS,
                params=parametros,
                json=nova_rota,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                print("[OK] Rota estática criada com sucesso.")
                return True

            print(
                f"[ERRO] Falha ao criar rota estática. "
                f"HTTP {response.status_code}."
            )
            print(response.text)
            return False

        # ----------------------------------------------------
        # ROTA JÁ EXISTE
        # ----------------------------------------------------

        print(f"[INFO] Rota para {REMOTE_NETWORK} já existe.")

        divergencias = []

        if rota_atual.get("device") != PHASE1_NAME:
            divergencias.append(
                f"device: atual={rota_atual.get('device')} / "
                f"esperado={PHASE1_NAME}"
            )

        if rota_atual.get("status") != "enable":
            divergencias.append(
                f"status: atual={rota_atual.get('status')} / "
                f"esperado=enable"
            )

        if divergencias:

            print("[ALERTA] Foram encontradas divergências na rota:")

            for divergencia in divergencias:
                print("  -", divergencia)

            return False

        print(
            f"[OK] Rota para {REMOTE_NETWORK} "
            f"já está configurada corretamente."
        )

        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar a rota.")
        print(erro)
        return False

# ============================================================
# CONFIGURAR POLICIES
# ============================================================

def configurar_policies():

    url = f"{BASE_URL}/cmdb/firewall/policy"

    parametros = {
        "vdom": VDOM
    }

    print("\nVerificando Firewall Policies...")

    policies = [
        {
            "name": "LAN-TO-VPN-PALOALTO",
            "srcintf": [{"name": LAN_INTERFACE}],
            "dstintf": [{"name": PHASE1_NAME}],
            "srcaddr": [{"name": LOCAL_ADDRESS}],
            "dstaddr": [{"name": REMOTE_ADDRESS}],
            "action": "accept",
            "schedule": "always",
            "service": [{"name": "ALL"}],
            "nat": "disable",
            "status": "enable"
        },
        {
            "name": "VPN-PALOALTO-TO-LAN",
            "srcintf": [{"name": PHASE1_NAME}],
            "dstintf": [{"name": LAN_INTERFACE}],
            "srcaddr": [{"name": REMOTE_ADDRESS}],
            "dstaddr": [{"name": LOCAL_ADDRESS}],
            "action": "accept",
            "schedule": "always",
            "service": [{"name": "ALL"}],
            "nat": "disable",
            "status": "enable"
        }
    ]

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=parametros,
            verify=False,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"[ERRO] Falha ao consultar Firewall Policies. "
                f"HTTP {response.status_code}."
            )
            return False

        dados = response.json()
        policies_existentes = dados.get("results", [])

        for policy in policies:

            policy_atual = None

            for item in policies_existentes:
                if item.get("name") == policy["name"]:
                    policy_atual = item
                    break

            # -----------------------------------------------
            # POLICY NÃO EXISTE
            # -----------------------------------------------

            if policy_atual is None:

                print(
                    f"[INFO] Policy {policy['name']} "
                    f"não encontrada."
                )

                response = requests.post(
                    url,
                    headers=HEADERS,
                    params=parametros,
                    json=policy,
                    verify=False,
                    timeout=10
                )

                if response.status_code != 200:
                    print(
                        f"[ERRO] Falha ao criar Policy "
                        f"{policy['name']}. "
                        f"HTTP {response.status_code}."
                    )
                    print(response.text)
                    return False

                print(
                    f"[OK] Policy {policy['name']} "
                    f"criada com sucesso."
                )

                continue

            # -----------------------------------------------
            # POLICY JÁ EXISTE
            # -----------------------------------------------

            print(f"[INFO] Policy {policy['name']} já existe.")

            divergencias = []

            campos_simples = [
                "action",
                "schedule",
                "nat",
                "status"
            ]

            for campo in campos_simples:

                if policy_atual.get(campo) != policy.get(campo):
                    divergencias.append(
                        f"{campo}: atual={policy_atual.get(campo)} / "
                        f"esperado={policy.get(campo)}"
                    )

            # Interfaces
            srcintf_atual = [
                item.get("name")
                for item in policy_atual.get("srcintf", [])
            ]

            dstintf_atual = [
                item.get("name")
                for item in policy_atual.get("dstintf", [])
            ]

            if policy["srcintf"][0]["name"] not in srcintf_atual:
                divergencias.append(
                    f"srcintf: esperado={policy['srcintf'][0]['name']}"
                )

            if policy["dstintf"][0]["name"] not in dstintf_atual:
                divergencias.append(
                    f"dstintf: esperado={policy['dstintf'][0]['name']}"
                )

            # Address Objects
            srcaddr_atual = [
                item.get("name")
                for item in policy_atual.get("srcaddr", [])
            ]

            dstaddr_atual = [
                item.get("name")
                for item in policy_atual.get("dstaddr", [])
            ]

            if policy["srcaddr"][0]["name"] not in srcaddr_atual:
                divergencias.append(
                    f"srcaddr: esperado={policy['srcaddr'][0]['name']}"
                )

            if policy["dstaddr"][0]["name"] not in dstaddr_atual:
                divergencias.append(
                    f"dstaddr: esperado={policy['dstaddr'][0]['name']}"
                )

            # Serviços
            service_atual = [
                item.get("name")
                for item in policy_atual.get("service", [])
            ]

            if policy["service"][0]["name"] not in service_atual:
                divergencias.append(
                    f"service: esperado={policy['service'][0]['name']}"
                )

            if divergencias:

                print(
                    f"[ALERTA] Foram encontradas divergências "
                    f"na Policy {policy['name']}:"
                )

                for divergencia in divergencias:
                    print("  -", divergencia)

                return False

            print(
                f"[OK] Policy {policy['name']} "
                f"já está configurada corretamente."
            )

        return True

    except requests.exceptions.RequestException as erro:
        print("[ERRO] Falha de comunicação ao configurar Firewall Policies.")
        print(erro)
        return False

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print(" AUTOMAÇÃO VPN - FORTIGATE")
    print("========================================")
    print()

    if not testar_conexao():
        print("\n[ERRO] Automação interrompida.")
        exit()

    print("\n[OK] Parâmetros carregados com sucesso.")

    if not configurar_phase1():
        print("\n[ERRO] Falha na configuração da Phase 1.")
        exit()

    if not configurar_phase2():
        print("\n[ERRO] Falha na configuração da Phase 2.")
        exit()

    if not configurar_interface_tunnel():
        print("\n[ERRO] Falha na configuração da interface do túnel.")
        exit()

    if not configurar_address_objects():
        print("\n[ERRO] Falha na configuração dos Address Objects.")
        exit()

    if not configurar_rota():
        print("\n[ERRO] Falha na configuração da rota estática.")
        exit()

    if not configurar_policies():
        print("\n[ERRO] Falha na configuração das Firewall Policies.")
        exit()

print()
print("========================================")
print("[OK] CONFIGURAÇÃO DO FORTIGATE CONCLUÍDA")
print("========================================")