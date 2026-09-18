import conexao_switch
from datetime import datetime
import os


# ==================================================
# OBTER BACKUP DO SWITCH
# ==================================================

def obter_backup(ip_sw=None, net_connect=None):

    conexao_criada_aqui = False

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        # Se não recebeu uma conexão aberta,
        # cria uma nova conexão.
        if net_connect is None:

            resultado_conexao = conexao_switch.conectar_switch(
                ip_sw,
                "backup_output.txt"
            )

            if not resultado_conexao["sucesso"]:

                return {
                    "sucesso": False,
                    "tipo": resultado_conexao["tipo"],
                    "titulo": resultado_conexao["titulo"],
                    "mensagem": resultado_conexao["mensagem"]
                }

            net_connect = resultado_conexao["conexao"]

            # Marca que esta função criou a conexão
            conexao_criada_aqui = True


        # ==================================================
        # IDENTIFICAR HOSTNAME
        # ==================================================

        prompt = net_connect.find_prompt()

        hostname = (
            prompt
            .replace("#", "")
            .replace(">", "")
            .strip()
        )


        # ==================================================
        # OBTER RUNNING-CONFIG
        # ==================================================

        configuracao = net_connect.send_command(
            "show running-config"
        )


        # ==================================================
        # DESCONECTAR SOMENTE SE CONECTOU AQUI
        # ==================================================

        if conexao_criada_aqui:

            net_connect.disconnect()


        # ==================================================
        # CRIAR NOME DO ARQUIVO
        # ==================================================

        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        nome_arquivo = (
            f"{hostname}_{data_hora}.cfg"
        )


        # ==================================================
        # RETORNO
        # ==================================================

        return {
            "sucesso": True,
            "hostname": hostname,
            "nome_arquivo": nome_arquivo,
            "configuracao": configuracao
        }


    # ==================================================
    # OUTROS ERROS
    # ==================================================

    except Exception as erro:

        # Se essa função abriu a conexão,
        # ela também é responsável por fechar.
        if conexao_criada_aqui and net_connect:

            try:
                net_connect.disconnect()
            except:
                pass


        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro ao realizar backup",
            "mensagem": (
                "Ocorreu um erro ao realizar "
                "o backup do switch.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }
# ==================================================
# SALVAR BACKUP LOCAL
# ==================================================

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
            "tipo": "arquivo",
            "titulo": "Erro ao salvar backup",
            "mensagem": (
                "Não foi possível salvar "
                "o arquivo de backup.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }