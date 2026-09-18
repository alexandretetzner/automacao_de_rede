import conexao_switch


# ==================================================
# BUSCAR VLANS
# ==================================================

def buscar_vlans(ip_sw):

    try:

        # ==================================================
        # CONECTAR AO SWITCH
        # ==================================================

        resultado_conexao = conexao_switch.conectar_switch(ip_sw)

        # Verifica se ocorreu algum erro na conexão
        if not resultado_conexao["sucesso"]:

            return {
                "sucesso": False,
                "tipo": resultado_conexao["tipo"],
                "titulo": resultado_conexao["titulo"],
                "mensagem": resultado_conexao["mensagem"]
            }


        # Recupera a conexão Netmiko
        net_connect = resultado_conexao["conexao"]


        # ==================================================
        # EXECUTAR SHOW VLAN
        # ==================================================

        resultado = net_connect.send_command(
            "show vlan brief"
        )

        net_connect.disconnect()


        # ==================================================
        # TRATAR RESULTADO
        # ==================================================

        vlans = []

        for linha in resultado.splitlines():

            partes = linha.split()

            # Verifica se a primeira coluna é o ID da VLAN
            if partes and partes[0].isdigit():

                vlan_id = partes[0]

                # Segunda coluna é o nome da VLAN
                vlan_nome = (
                    partes[1]
                    if len(partes) > 1
                    else ""
                )

                # Terceira coluna é o status
                vlan_status = (
                    partes[2]
                    if len(partes) > 2
                    else ""
                )

                vlans.append({
                    "vlan_id": vlan_id,
                    "name": vlan_nome,
                    "status": vlan_status
                })


        # ==================================================
        # RETORNO DE SUCESSO
        # ==================================================

        return {
            "sucesso": True,
            "vlans": vlans
        }


    # ==================================================
    # OUTROS ERROS
    # ==================================================

    except Exception as erro:

        return {
            "sucesso": False,
            "tipo": "desconhecido",
            "titulo": "Erro ao buscar VLANs",
            "mensagem": (
                "Ocorreu um erro ao consultar as VLANs.\n\n"
                f"Detalhes técnicos:\n{erro}"
            )
        }


# ==================================================
# TESTE DIRETO DO ARQUIVO
# ==================================================

if __name__ == "__main__":

    ip_sw = input(
        "Digite o IP do switch: "
    )

    resultado = buscar_vlans(ip_sw)

    if resultado["sucesso"]:

        print("\nVLANs encontradas:\n")

        for vlan in resultado["vlans"]:

            print(
                f'VLAN {vlan["vlan_id"]} | '
                f'{vlan["name"]} | '
                f'{vlan["status"]}'
            )

    else:

        print("\nERRO:")
        print(resultado["titulo"])
        print(resultado["mensagem"])