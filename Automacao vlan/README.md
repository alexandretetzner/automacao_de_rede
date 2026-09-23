# Automação de Switch Cisco

Este projeto foi desenvolvido para automatizar configurações em um switch Cisco utilizando Python e Netmiko.

A automação possui uma interface gráfica desenvolvida com CustomTkinter, permitindo realizar configurações, validações e consultas no equipamento através de SSH.

O projeto foi desenvolvido como parte de um desafio técnico de automação de redes.

## Funcionalidades

A aplicação permite:

- Conectar ao switch através de SSH.
- Consultar as VLANs existentes.
- Criar e alterar VLANs.
- Consultar e alterar o hostname do switch.
- Validar as configurações realizadas.
- Salvar a configuração do equipamento.
- Realizar backup da configuração localmente.
- Enviar o backup para um servidor SFTP.

## Interface

A interface da aplicação foi dividida em duas abas principais: **Configuração** e **Tools**.

### Configuração

A aba **Configuração** concentra as funções utilizadas para realizar as alterações no switch.

Através dela é possível:

- Informar o endereço IP do switch.
- Configurar o hostname do switch se necessário.
- Informar o ID e o nome das VLANs que serão configuradas.
- Salvar a configuração atual antes das alterações.
- Aplicar as configurações.
- Validar novamente o equipamento após as alterações.

### Tools

A aba **Tools** foi adicionada como uma funcionalidade complementar da aplicação, reunindo ferramentas de consulta e manutenção do equipamento.

Através desta aba é possível:

- Realizar teste de conxão com o Switch 
- Consultar as VLANs existentes no switch.
- Realizar backup da configuração (Localmente ou via SFTP).

## Validação das Configurações

Antes de realizar as alterações, a automação consulta a configuração atual do switch para verificar as VLANs e o hostname existentes.

Caso seja encontrada alguma diferença entre a configuração atual e a configuração informada pelo usuário, a aplicação apresenta a divergência encontrada e pergunta se quer realizar a alteração.

Após a aplicação das configurações, uma nova validação é realizada para verificar se as alterações foram aplicadas corretamente.

## Salvamento da Configuração

Após realizar alterações no equipamento, a automação salva a configuração do switch aplicando na NVRAM.

## Backup

A aplicação permite realizar o backup da configuração atual do switch.

O backup pode ser:

- Salvo localmente no computador.
- Enviado para um servidor SFTP.

O nome do arquivo de backup é gerado utilizando o hostname do equipamento e a data e horário da execução, facilitando a identificação dos arquivos.

## Estrutura do Projeto

Os principais arquivos da automação são:

- `Frontend.py` - Interface gráfica da aplicação.
- `conexao_switch.py` - Responsável pela conexão SSH com o switch utilizando Netmiko.
- `levantamento_vlan.py` - Consulta as VLANs existentes no equipamento.
- `configurar_vlan.py` - Realiza a consulta, criação e alteração das VLANs.
- `configurar_hostname.py` - Realiza a consulta e alteração do hostname.
- `backup_sw.py` - Responsável pela obtenção da configuração e pelos backups local e SFTP.

## Ambiente de Laboratório

A automação foi desenvolvida e testada utilizando:

- Python 3.13.15.
- Switch Cisco em ambiente EVE-NG.
- Acesso SSH ao equipamento.

A utilização em outros ambientes pode exigir ajustes nos parâmetros de conexão e nas configurações do equipamento.

## Dependências

As principais bibliotecas utilizadas são:

- Netmiko
- CustomTkinter
- Paramiko

As dependências podem ser instaladas através do pip:

    pip install netmiko
    pip install customtkinter
    pip install paramiko

## Execução

Para iniciar a aplicação, acesse a pasta do projeto e execute:

    python Frontend.py

Após a execução será aberta a interface gráfica da automação.

## Utilização

1. Informe o endereço IP do switch..
2. Na aba **Configuração**, informe as VLANs e o hostname desejados.
3. Execute a validação da configuração atual.
4. Aplique as alterações necessárias.
5. Verifique o resultado da validação realizada após a configuração.
6. Utilize a aba **Tools** quando necessário para consultar VLANs ou realizar o backup do equipamento.

## Observações

O ambiente utilizado nos testes possui certificado e credenciais próprias de laboratório.

Os endereços e parâmetros de acesso ao equipamento devem ser ajustados de acordo com o ambiente onde a automação será utilizada.

## Scripts de desenvolvimento

A pasta `Desenvolvimento e testes` contém scripts utilizados nas etapas iniciais do projeto para testar a conexão e a automação das configurações do switch.

Após os testes iniciais, as funcionalidades foram separadas em módulos e integradas à interface gráfica da aplicação.