from netmiko import ConnectHandler
from getpass import getpass

#Variaveis
change = "TESTE"
switch_ip = "192.168.71.10"


# Conectando
Network_Device= {"host": switch_ip, 
                 "username": "admin",
                 "password": "admin",
                 "device_type": "cisco_ios",
                 "session_log": change + "_output.txt"
                 }
net_connect =ConnectHandler(**Network_Device)

print()
print(f'Connected to {Network_Device["host"]}')
print()
show_clock()
print('Fazendo um backup da configuração')
output_show_runn = net_connect.send_command ('show running-config')
print()

#configuração da Vlan
Vlans_padrao = {10:"VLAN_DADOS",20: "VLAN_VOZ",50:"VLAN_SEGURANCA"}
for Vlan_ID, Vlan_Name in Vlans_padrao.items():
   Command_vlan = net_connect.send_command('show vlan id ' + str(Vlan_ID),use_textfsm=True)
   if Command_vlan == 'VLAN id ' + str(Vlan_ID) +' not found in current VLAN database':
      print('Não existe a Vlan criada')
      config_commands_1 = ['vlan ' + str(Vlan_ID) ,'name '+ str(Vlan_Name)]
      output = net_connect.send_config_set(config_commands_1)
      output += net_connect.save_config()
      print(f'Vlan criada com sucesso')
      #print(output)
   else:
      Vlan_criada = [item['name'] for item in Command_vlan if item['vlan_id'] == str(Vlan_ID)]
      if [item['vlan_id'] for item in Command_vlan if item['name'] == str(Vlan_Name)]:
         print('Vlan já estava criada e com o IP e nome correto')
      else:
         print("A Vlan com ID " +str(Vlan_ID) +" está configurada com o nome " + str(Vlan_criada)+" e está fora do padrã")

#Verificações
print('###### VALIDANDO CONFIGURAÇÕES ######')
output_show_vlan_brief = net_connect.send_command ('show vlan brief')
print(output_show_vlan_brief)
#print(output_Interface_ap)
show_clock()
net_connect.disconnect()
print('Closing Connection')