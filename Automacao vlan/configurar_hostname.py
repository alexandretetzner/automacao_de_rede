from netmiko import ConnectHandler


# ==================================================
# CONSULTAR HOSTNAME
# ==================================================

def consultar_hostname(ip_sw):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios"
    }

    try:

        net_connect = ConnectHandler(**Network_Device)

        prompt = net_connect.find_prompt()

        hostname_atual = (
            prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )

        net_connect.disconnect()

        return {
            "sucesso": True,
            "hostname": hostname_atual
        }

    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }


# ==================================================
# ALTERAR HOSTNAME
# ==================================================

def alterar_hostname(ip_sw, novo_hostname):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios",
        "session_log": "config_hostname_output.txt"
    }

    try:

        net_connect = ConnectHandler(**Network_Device)

        # Descobre hostname atual
        prompt = net_connect.find_prompt()

        hostname_anterior = (
            prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )

        # Comando de alteração
        config_commands = [
            f"hostname {novo_hostname}"
        ]

        # Altera hostname
        net_connect.send_config_set(
            config_commands,
            cmd_verify=False
        )

        # Atualiza o prompt conhecido pelo Netmiko
        net_connect.set_base_prompt()

        # Salva na NVRAM
        net_connect.save_config()

        # ==================================================
        # VALIDAÇÃO
        # ==================================================

        novo_prompt = net_connect.find_prompt()

        hostname_configurado = (
            novo_prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )

        net_connect.disconnect()

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
                "erro": (
                    f"Hostname esperado: {novo_hostname} | "
                    f"Hostname encontrado: {hostname_configurado}"
                )
            }

    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }