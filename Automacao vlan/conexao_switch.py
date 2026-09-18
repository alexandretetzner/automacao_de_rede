from netmiko import ConnectHandler

def conectar_switch(ip_sw, session_log=None):

    Network_Device = {
        "host": ip_sw,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_ios"
    }

    # Adiciona session_log somente quando solicitado
    if session_log:
        Network_Device["session_log"] = session_log

    net_connect = ConnectHandler(**Network_Device)

    return net_connect