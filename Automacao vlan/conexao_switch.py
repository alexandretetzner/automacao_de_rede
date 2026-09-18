from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException
)


def conectar_switch(ip_sw, session_log=None):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios"
    }

    if session_log:
        Network_Device["session_log"] = session_log

    try:

        net_connect = ConnectHandler(**Network_Device)

        return {
            "sucesso": True,
            "conexao": net_connect
        }


    # ==================================================
    # ERRO DE AUTENTICAÇÃO
    # ==================================================

    except NetmikoAuthenticationException:

        return {
            "sucesso": False,
            "tipo": "autenticacao",
            "titulo": "Erro de autenticação",
            "mensagem": (
                "Não foi possível autenticar no switch.\n\n"
                "Verifique o usuário e a senha."
            )
        }


    # ==================================================
    # TIMEOUT
    # ==================================================

    except NetmikoTimeoutException:

        return {
            "sucesso": False,
            "tipo": "timeout",
            "titulo": "Erro de conexão",
            "mensagem": (
                f"Não foi possível conectar ao switch {ip_sw}.\n\n"
                "A conexão excedeu o tempo limite.\n\n"
                "Verifique:\n"
                "• IP do equipamento\n"
                "• Conectividade de rede\n"
                "• Serviço SSH\n"
                "• Porta SSH"
            )
        }


    # ==================================================
    # OUTROS ERROS
    # ==================================================

    except Exception as erro:

        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro inesperado",
            "mensagem": (
                "Ocorreu um erro ao conectar ao switch.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }