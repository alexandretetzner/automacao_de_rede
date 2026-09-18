import customtkinter as ctk
from tkinter import filedialog

import logonsw
import levantamento_vlan
import backup_sw


# ==================================================
# FUNÇÕES
# ==================================================

def testar_conectividade():

    ip_sw = campo_ip.get().strip()

    if not ip_sw:
        status.configure(text="Digite o IP do Switch")
        return

    status.configure(text="Testando conectividade...")
    app.update()

    resultado = logonsw.conectar_switch(ip_sw)

    if resultado:
        status.configure(
            text=f"Conectado ao Switch {ip_sw}"
        )
    else:
        status.configure(
            text=f"Falha na conexão com {ip_sw}"
        )


# ==================================================
# BUSCAR VLANS
# ==================================================

def buscar_vlans():

    ip_sw = campo_ip.get().strip()

    if not ip_sw:
        status.configure(text="Digite o IP do Switch")
        return

    status.configure(text="Buscando VLANs...")
    app.update()

    vlans = levantamento_vlan.buscar_vlans(ip_sw)

    # Limpa a lista
    lista_vlans.delete("1.0", "end")

    if not vlans:

        lista_vlans.insert(
            "end",
            "Nenhuma VLAN encontrada."
        )

        status.configure(
            text="Não foi possível obter as VLANs"
        )

        return

    # Exibe as VLANs encontradas
    for vlan in vlans:

        vlan_id = vlan.get("vlan_id")
        nome = vlan.get("name")
        vlan_status = vlan.get("status")

        lista_vlans.insert(
            "end",
            f"VLAN {vlan_id} | {nome} | {vlan_status}\n"
        )

    status.configure(
        text=f"{len(vlans)} VLAN(s) encontrada(s)"
    )


# ==================================================
# BACKUP
# ==================================================

def abrir_backup():

    ip_sw = campo_ip.get().strip()

    if not ip_sw:

        status.configure(
            text="Digite o IP do Switch"
        )

        return

    # Cria janela de backup
    janela_backup = ctk.CTkToplevel(app)

    janela_backup.title(
        "Backup do Switch"
    )

    janela_backup.geometry(
        "400x280"
    )

    janela_backup.grab_set()


    # --------------------------------------------------
    # TÍTULO
    # --------------------------------------------------

    titulo_backup = ctk.CTkLabel(
        janela_backup,
        text="Realizar Backup",
        font=("Arial", 18, "bold")
    )

    titulo_backup.pack(
        pady=25
    )


    # --------------------------------------------------
    # BACKUP LOCAL
    # --------------------------------------------------

    def backup_local():

        caminho = filedialog.askdirectory(
            title="Escolha onde salvar o backup"
        )

        # Usuário cancelou
        if not caminho:
            return

        status_backup.configure(
            text="Obtendo configuração..."
        )

        janela_backup.update()

        resultado = backup_sw.obter_backup(
            ip_sw
        )

        if not resultado["sucesso"]:

            status_backup.configure(
                text="Erro ao obter configuração"
            )

            return

        salvamento = backup_sw.salvar_local(
            resultado,
            caminho
        )

        if salvamento["sucesso"]:

            status_backup.configure(
                text="Backup realizado com sucesso!"
            )

        else:

            status_backup.configure(
                text="Erro ao salvar backup"
            )


    # --------------------------------------------------
    # BACKUP SFTP
    # --------------------------------------------------

    def backup_sftp():

        status_backup.configure(
            text="Configuração SFTP será aberta..."
        )

        # Será desenvolvido na próxima etapa


    # --------------------------------------------------
    # BOTÃO BACKUP LOCAL
    # --------------------------------------------------

    botao_local = ctk.CTkButton(
        janela_backup,
        text="Salvar Localmente",
        command=backup_local
    )

    botao_local.pack(
        pady=10
    )


    # --------------------------------------------------
    # BOTÃO BACKUP SFTP
    # --------------------------------------------------

    botao_sftp = ctk.CTkButton(
        janela_backup,
        text="Enviar para SFTP",
        command=backup_sftp
    )

    botao_sftp.pack(
        pady=10
    )


    # --------------------------------------------------
    # STATUS BACKUP
    # --------------------------------------------------

    status_backup = ctk.CTkLabel(
        janela_backup,
        text=""
    )

    status_backup.pack(
        pady=10
    )


# ==================================================
# CONFIGURAÇÃO CUSTOMTKINTER
# ==================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ==================================================
# JANELA PRINCIPAL
# ==================================================

app = ctk.CTk()

app.title("Cisco Network Automation")
app.geometry("850x550")


# ==================================================
# TÍTULO
# ==================================================

titulo = ctk.CTkLabel(
    app,
    text="Cisco Network Automation",
    font=("Arial", 24, "bold")
)

titulo.pack(
    pady=(20, 10)
)


# ==================================================
# ABAS
# ==================================================

abas = ctk.CTkTabview(
    app,
    width=800,
    height=450
)

abas.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)


# Criação das abas
aba_tools = abas.add("Tools")
aba_config = abas.add("Configuração")


# ==================================================
# ABA TOOLS
# ==================================================

titulo_tools = ctk.CTkLabel(
    aba_tools,
    text="Ferramentas do Switch",
    font=("Arial", 18, "bold")
)

titulo_tools.pack(
    pady=(20, 10)
)


# ==================================================
# FRAME CONEXÃO
# ==================================================

frame_conexao = ctk.CTkFrame(
    aba_tools
)

frame_conexao.pack(
    padx=20,
    pady=10
)


# ==================================================
# IP DO SWITCH
# ==================================================

campo_ip = ctk.CTkEntry(
    frame_conexao,
    width=180,
    placeholder_text="IP do Switch"
)

campo_ip.grid(
    row=0,
    column=0,
    padx=10,
    pady=15
)


# ==================================================
# BOTÃO TESTAR CONECTIVIDADE
# ==================================================

botao_testar = ctk.CTkButton(
    frame_conexao,
    text="Testar Conectividade",
    command=testar_conectividade
)

botao_testar.grid(
    row=0,
    column=1,
    padx=10,
    pady=15
)


# ==================================================
# BOTÃO BUSCAR VLANS
# ==================================================

botao_vlan = ctk.CTkButton(
    frame_conexao,
    text="Buscar VLANs",
    command=buscar_vlans
)

botao_vlan.grid(
    row=0,
    column=2,
    padx=10,
    pady=15
)


# ==================================================
# BOTÃO REALIZAR BACKUP
# ==================================================

botao_backup = ctk.CTkButton(
    frame_conexao,
    text="Realizar Backup",
    command=abrir_backup
)

botao_backup.grid(
    row=0,
    column=3,
    padx=10,
    pady=15
)


# ==================================================
# STATUS
# ==================================================

status = ctk.CTkLabel(
    aba_tools,
    text="Aguardando..."
)

status.pack(
    pady=10
)


# ==================================================
# LISTA DE VLANS
# ==================================================

lista_vlans = ctk.CTkTextbox(
    aba_tools,
    width=700,
    height=220
)

lista_vlans.pack(
    padx=20,
    pady=10
)


# ==================================================
# ABA CONFIGURAÇÃO
# ==================================================

titulo_config = ctk.CTkLabel(
    aba_config,
    text="Configuração do Switch",
    font=("Arial", 18, "bold")
)

titulo_config.pack(
    pady=(30, 10)
)


texto_config = ctk.CTkLabel(
    aba_config,
    text="Área destinada à configuração do Switch."
)

texto_config.pack(
    pady=10
)


# ==================================================
# EXECUTA A INTERFACE
# ==================================================

app.mainloop()