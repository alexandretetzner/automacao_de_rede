import conexao_switch


# ==================================================
# CONSULTAR VLAN
# ==================================================

def consultar_vlan(
    vlan_id,
    ip_sw=None,
    net_connect=None
):

    conexao_criada_aqui = False

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        if net_connect is None:

            resultado_conexao = conexao_switch.conectar_switch(
                ip_sw,
                "config_vlan_output.txt"
            )

            if not resultado_conexao["sucesso"]:

                return {
                    "sucesso": False,
                    "tipo": resultado_conexao["tipo"],
                    "titulo": resultado_conexao["titulo"],
                    "mensagem": resultado_conexao["mensagem"]
                }

            net_connect = resultado_conexao["conexao"]

            conexao_criada_aqui = True


        # ==================================================
        # CONSULTAR VLAN
        # ==================================================

        resultado = net_connect.send_command(
            f"show vlan id {vlan_id}"
        )


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        # ==================================================
        # VLAN NÃO EXISTE
        # ==================================================

        if "not found in current VLAN database" in resultado:

            return {
                "sucesso": True,
                "existe": False,
                "vlan_id": str(vlan_id),
                "nome": None
            }


        # ==================================================
        # VLAN EXISTE
        # ==================================================

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


        # ==================================================
        # NÃO FOI POSSÍVEL IDENTIFICAR
        # ==================================================

        return {
            "sucesso": False,
            "tipo": "validacao",
            "titulo": "Erro ao consultar VLAN",
            "mensagem": (
                f"Não foi possível identificar "
                f"a VLAN {vlan_id}."
            )
        }


    except Exception as erro:

        if conexao_criada_aqui and net_connect:

            try:
                net_connect.disconnect()
            except:
                pass

        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro ao consultar VLAN",
            "mensagem": (
                f"Ocorreu um erro ao consultar "
                f"a VLAN {vlan_id}.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }


# ==================================================
# CRIAR VLAN
# ==================================================

def criar_vlan(
    vlan_id,
    vlan_nome,
    ip_sw=None,
    net_connect=None
):

    conexao_criada_aqui = False

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        if net_connect is None:

            resultado_conexao = conexao_switch.conectar_switch(
                ip_sw,
                "config_vlan_output.txt"
            )

            if not resultado_conexao["sucesso"]:

                return {
                    "sucesso": False,
                    "tipo": resultado_conexao["tipo"],
                    "titulo": resultado_conexao["titulo"],
                    "mensagem": resultado_conexao["mensagem"]
                }

            net_connect = resultado_conexao["conexao"]

            conexao_criada_aqui = True


        # ==================================================
        # CRIAR VLAN
        # ==================================================

        config_commands = [
            f"vlan {vlan_id}",
            f"name {vlan_nome}"
        ]

        net_connect.send_config_set(
            config_commands
        )


        # ==================================================
        # SALVAR NA NVRAM
        # ==================================================

        net_connect.save_config()


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        return {
            "sucesso": True,
            "mensagem": (
                f"VLAN {vlan_id} - {vlan_nome} "
                f"criada com sucesso."
            )
        }


    except Exception as erro:

        if conexao_criada_aqui and net_connect:

            try:
                net_connect.disconnect()
            except:
                pass

        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro ao criar VLAN",
            "mensagem": (
                f"Ocorreu um erro ao criar "
                f"a VLAN {vlan_id}.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }


# ==================================================
# ALTERAR NOME DA VLAN
# ==================================================

def alterar_vlan(
    vlan_id,
    vlan_nome,
    ip_sw=None,
    net_connect=None
):

    conexao_criada_aqui = False

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        if net_connect is None:

            resultado_conexao = conexao_switch.conectar_switch(
                ip_sw,
                "config_vlan_output.txt"
            )

            if not resultado_conexao["sucesso"]:

                return {
                    "sucesso": False,
                    "tipo": resultado_conexao["tipo"],
                    "titulo": resultado_conexao["titulo"],
                    "mensagem": resultado_conexao["mensagem"]
                }

            net_connect = resultado_conexao["conexao"]

            conexao_criada_aqui = True


        # ==================================================
        # ALTERAR VLAN
        # ==================================================

        config_commands = [
            f"vlan {vlan_id}",
            f"name {vlan_nome}"
        ]

        net_connect.send_config_set(
            config_commands
        )


        # ==================================================
        # SALVAR NA NVRAM
        # ==================================================

        net_connect.save_config()


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        return {
            "sucesso": True,
            "mensagem": (
                f"VLAN {vlan_id} alterada para "
                f"{vlan_nome} com sucesso."
            )
        }


    except Exception as erro:

        if conexao_criada_aqui and net_connect:

            try:
                net_connect.disconnect()
            except:
                pass

        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro ao alterar VLAN",
            "mensagem": (
                f"Ocorreu um erro ao alterar "
                f"a VLAN {vlan_id}.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }