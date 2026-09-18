from netmiko import ConnectHandler
from datetime import datetime
import os


def obter_backup(ip_sw):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios"
    }

    try:
        net_connect = ConnectHandler(**Network_Device)

        # Descobre o hostname
        prompt = net_connect.find_prompt()

        hostname = prompt.replace("#", "").replace(">", "").strip()

        # Pega a configuração atual
        configuracao = net_connect.send_command(
            "show running-config"
        )

        net_connect.disconnect()

        # Data e hora para o nome do arquivo
        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        nome_arquivo = (
            f"{hostname}_{data_hora}.cfg"
        )

        return {
            "sucesso": True,
            "hostname": hostname,
            "nome_arquivo": nome_arquivo,
            "configuracao": configuracao
        }

    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }


def salvar_local(resultado_backup, caminho):

    try:

        arquivo = os.path.join(
            caminho,
            resultado_backup["nome_arquivo"]
        )

        with open(
            arquivo,
            "w",
            encoding="utf-8"
        ) as backup:

            backup.write(
                resultado_backup["configuracao"]
            )

        return {
            "sucesso": True,
            "arquivo": arquivo
        }

    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }