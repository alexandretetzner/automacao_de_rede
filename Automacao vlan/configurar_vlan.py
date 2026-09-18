from netmiko import ConnectHandler


def configurar_vlans(ip_sw, vlans):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios",
        "session_log": "config_vlan_output.txt"
    }

    resultados = []

    try:

        # Conectando ao Switch
        net_connect = ConnectHandler(**Network_Device)

        # Percorre todas as VLANs recebidas do frontend
        for Vlan_ID, Vlan_Name in vlans.items():

            Command_vlan = net_connect.send_command(
                "show vlan id " + str(Vlan_ID),
                use_textfsm=True
            )

            # VLAN não existe
            if Command_vlan == "VLAN id " + str(Vlan_ID) + " not found in current VLAN database":

                config_commands = [
                    "vlan " + str(Vlan_ID),
                    "name " + str(Vlan_Name)
                ]

                net_connect.send_config_set(
                    config_commands
                )

                resultados.append(
                    f"VLAN {Vlan_ID} - {Vlan_Name} criada com sucesso."
                )

            else:

                Vlan_criada = [
                    item["vlan_name"]
                    for item in Command_vlan
                    if item["vlan_id"] == str(Vlan_ID)
                ]

                if [
                    item["vlan_id"]
                    for item in Command_vlan
                    if item["vlan_name"] == str(Vlan_Name)
                ]:

                    resultados.append(
                        f"VLAN {Vlan_ID} - {Vlan_Name} já existe e está correta."
                    )

                else:

                    resultados.append(
                        f"VLAN {Vlan_ID} existe com outro nome: {Vlan_criada}"
                    )

        # Salva configuração na NVRAM
        net_connect.save_config()

        # Validação final
        output_vlan = net_connect.send_command(
            "show vlan brief"
        )

        net_connect.disconnect()

        return {
            "sucesso": True,
            "resultados": resultados,
            "validacao": output_vlan
        }

    except Exception as erro:

        return {
            "sucesso": False,
            "erro": str(erro)
        }