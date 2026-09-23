from netmiko import ConnectHandler


def conectar_switch(ip_sw):
    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios",
        "session_log": "teste_output.txt"
    }

    try:
        net_connect = ConnectHandler(**Network_Device)

        print(f'Connected to {Network_Device["host"]}')

        net_connect.disconnect()

        return True

    except Exception as erro:
        print(f"Erro ao conectar: {erro}")
        return False