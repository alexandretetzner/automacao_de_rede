import customtkinter as ctk

import logonsw
import levantamento_vlan


# ==================================================
# FUNÇÕES DOS BOTÕES
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


def buscar_vlans():

    ip_sw = campo_ip.get().strip()

    if not ip_sw:
        status.configure(text="Digite o IP do Switch")
        return

    status.configure(text="Buscando VLANs...")
    app.update()

    vlans = levantamento_vlan.buscar_vlans(ip_sw)

    # Limpa a lista antes de apresentar novo resultado
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

    # Exibe as VLANs
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
# CONFIGURAÇÃO DO CUSTOMTKINTER
# ==================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ==================================================
# JANELA
# ==================================================

app = ctk.CTk()

app.title("Cisco Network Automation")
app.geometry("700x500")


# ==================================================
# TÍTULO
# ==================================================

titulo = ctk.CTkLabel(
    app,
    text="Cisco Network Automation",
    font=("Arial", 22, "bold")
)

titulo.pack(pady=25)


# ==================================================
# FRAME CONEXÃO
# ==================================================

frame_conexao = ctk.CTkFrame(app)

frame_conexao.pack(
    padx=20,
    pady=10
)


# ==================================================
# CAMPO IP
# ==================================================

campo_ip = ctk.CTkEntry(
    frame_conexao,
    width=200,
    placeholder_text="IP do Switch"
)

campo_ip.grid(
    row=0,
    column=0,
    padx=10,
    pady=15
)


# ==================================================
# BOTÃO TESTAR
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
# BOTÃO BUSCAR VLAN
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
# STATUS
# ==================================================

status = ctk.CTkLabel(
    app,
    text="Aguardando..."
)

status.pack(pady=10)


# ==================================================
# LISTA DE VLANS
# ==================================================

lista_vlans = ctk.CTkTextbox(
    app,
    width=600,
    height=250
)

lista_vlans.pack(
    padx=20,
    pady=15
)


# ==================================================
# INICIAR INTERFACE
# ==================================================

app.mainloop()