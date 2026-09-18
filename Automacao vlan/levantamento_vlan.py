from netmiko import ConnectHandler


def buscar_vlans(ip_sw):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios"
    }

    try:
        net_connect = ConnectHandler(**Network_Device)

        # Executa o comando no switch
        resultado = net_connect.send_command("show vlan brief")

        net_connect.disconnect()

        vlans = []

        # Analisa cada linha retornada pelo switch
        for linha in resultado.splitlines():

            partes = linha.split()

            # Verifica se a primeira coluna é o ID da VLAN
            if partes and partes[0].isdigit():

                vlan_id = partes[0]

                # Segunda coluna é o nome da VLAN
                vlan_nome = partes[1] if len(partes) > 1 else ""

                # Terceira coluna é o status
                vlan_status = partes[2] if len(partes) > 2 else ""

                vlans.append({
                    "vlan_id": vlan_id,
                    "name": vlan_nome,
                    "status": vlan_status
                })

        return vlans

    except Exception as erro:

        print(f"Erro ao consultar VLANs: {erro}")

        return []

# Executa somente quando rodar levantamento_vlan.py diretamente
if __name__ == "__main__":

    ip_sw = input("Digite o IP do switch: ")

    resultado = buscar_vlans(ip_sw)

    print(resultado)