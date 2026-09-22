import requests
import urllib3
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PALOALTO_IP = "192.168.71.11"

usuario = input("Usuário do Palo Alto: ")
senha = getpass.getpass("Senha: ")

url = f"https://{PALOALTO_IP}/api/"

dados = {
    "type": "keygen",
    "user": usuario,
    "password": senha
}

print("\nSolicitando API Key ao Palo Alto...")

response = requests.post(
    url,
    data=dados,
    verify=False,
    timeout=10
)

print("Status HTTP:", response.status_code)
print(response.text)