import conexao_switch

# ==================================================
# DADOS DE CONEXÃO
# ==================================================

def dados_switch(ip_sw):

    return {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios",
        "session_log": "config_vlan_output.txt"
    }


# ==================================================
# CONSULTAR VLAN
# ==================================================

def consultar_vlan(ip_sw, vlan_id):

    try:

        net_connect = conexao_switch.conectar_switch(ip_sw,"config_vlan_output.txt")

        resultado = net_connect.send_command(
            f"show vlan id {vlan_id}"
        )

        net_connect.disconnect()

        # VLAN NÃO EXISTE
        if "not found in current VLAN database" in resultado:

            return {
                "sucesso": True,
                "existe": False,
                "vlan_id": str(vlan_id),
                "nome": None
            }


        # VLAN EXISTE
        # Procura a linha que começa com o ID da VLAN

        for linha in resultado.splitlines():

            partes = linha.split()

            if partes and partes[0] == str(vlan_id):

                nome_vlan = partes[1]

                return {
                    "sucesso": True,
                    "existe": True,
                    "vlan_id": str(vlan_id),
                    "nome": nome_vlan
                }


        return {
            "sucesso": False,
            "erro": (
                f"Não foi possível identificar "
                f"a VLAN {vlan_id}."
            )
        }


    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }


# ==================================================
# CRIAR VLAN
# ==================================================

def criar_vlan(ip_sw, vlan_id, vlan_nome):

    try:

        net_connect = ConnectHandler(
            **dados_switch(ip_sw)
        )

        config_commands = [
            f"vlan {vlan_id}",
            f"name {vlan_nome}"
        ]

        net_connect.send_config_set(
            config_commands
        )

        # Salva na NVRAM
        net_connect.save_config()

        net_connect.disconnect()

        return {
            "sucesso": True,
            "mensagem": (
                f"VLAN {vlan_id} - {vlan_nome} "
                f"criada com sucesso."
            )
        }


    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }


# ==================================================
# ALTERAR NOME DA VLAN
# ==================================================

def alterar_vlan(ip_sw, vlan_id, vlan_nome):

    try:

        net_connect = ConnectHandler(
            **dados_switch(ip_sw)
        )

        config_commands = [
            f"vlan {vlan_id}",
            f"name {vlan_nome}"
        ]

        net_connect.send_config_set(
            config_commands
        )

        # Salva na NVRAM
        net_connect.save_config()

        net_connect.disconnect()

        return {
            "sucesso": True,
            "mensagem": (
                f"VLAN {vlan_id} alterada para "
                f"{vlan_nome} com sucesso."
            )
        }


    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }