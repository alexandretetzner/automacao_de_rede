import conexao_switch


# ==================================================
# CONSULTAR HOSTNAME
# ==================================================

def consultar_hostname(ip_sw=None, net_connect=None):

    conexao_criada_aqui = False

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        if net_connect is None:

            resultado_conexao = conexao_switch.conectar_switch(
                ip_sw
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
        # CONSULTAR HOSTNAME
        # ==================================================

        prompt = net_connect.find_prompt()

        hostname_atual = (
            prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        return {
            "sucesso": True,
            "hostname": hostname_atual
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
            "titulo": "Erro ao consultar hostname",
            "mensagem": (
                "Ocorreu um erro ao consultar "
                "o hostname do switch.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }


# ==================================================
# ALTERAR HOSTNAME
# ==================================================

def alterar_hostname(
    novo_hostname,
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
                "config_hostname_output.txt"
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
        # HOSTNAME ATUAL
        # ==================================================

        prompt = net_connect.find_prompt()

        hostname_anterior = (
            prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )


        # ==================================================
        # ALTERAR HOSTNAME
        # ==================================================

        config_commands = [
            f"hostname {novo_hostname}"
        ]

        net_connect.send_config_set(
            config_commands,
            cmd_verify=False
        )


        # ==================================================
        # ATUALIZAR PROMPT DO NETMIKO
        # ==================================================

        net_connect.set_base_prompt()


        # ==================================================
        # SALVAR NA NVRAM
        # ==================================================

        net_connect.save_config()


        # ==================================================
        # VALIDAR ALTERAÇÃO
        # ==================================================

        novo_prompt = net_connect.find_prompt()

        hostname_configurado = (
            novo_prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        # ==================================================
        # RESULTADO
        # ==================================================

        if hostname_configurado == novo_hostname:

            return {
                "sucesso": True,
                "alterado": True,
                "hostname_anterior": hostname_anterior,
                "hostname_novo": hostname_configurado,
                "mensagem": (
                    f"Hostname alterado de {hostname_anterior} "
                    f"para {hostname_configurado}."
                )
            }

        else:

            return {
                "sucesso": False,
                "tipo": "validacao",
                "titulo": "Erro na validação do hostname",
                "mensagem": (
                    f"Hostname esperado: {novo_hostname}\n"
                    f"Hostname encontrado: {hostname_configurado}"
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
            "titulo": "Erro ao alterar hostname",
            "mensagem": (
                "Ocorreu um erro ao alterar "
                "o hostname do switch.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }