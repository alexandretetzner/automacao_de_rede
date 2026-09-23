# Scripts de Automação da VPN

Esta pasta contém os scripts desenvolvidos durante a implementação e os testes da automação da VPN IPSec entre o FortiGate e o Palo Alto.

Os scripts principais da automação são:

- `fortigate_vpn.py` - realiza a configuração da VPN no FortiGate através da REST API.
- `paloalto_vpn.py` - realiza a configuração da VPN no Palo Alto através da XML API.
- `validar_vpn.py` - consulta os dois equipamentos para validar o estado da VPN após a configuração.
- `config.json` - contém os parâmetros utilizados pelos scripts no ambiente de laboratório.

## Scripts de desenvolvimento e testes

As pastas `Fortigate` e `PaloAlto` possuem scripts utilizados durante o desenvolvimento da automação.

Esses scripts foram criados para testar individualmente as APIs, consultar configurações, verificar schemas e realizar a criação dos objetos necessários para a VPN de forma separada.

Após a validação de cada etapa, as funcionalidades foram consolidadas nos scripts principais da automação.

> Os scripts das pastas de testes representam diferentes etapas do desenvolvimento e podem conter parâmetros utilizados durante os testes iniciais do laboratório.