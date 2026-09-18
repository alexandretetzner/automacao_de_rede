import customtkinter as ctk
import logon_sw_new

# Função botão Testar Conectividade
def testar_conectividade():
    ip_sw = campo_ip.get()

    if ip_sw == "":
        status.configure(text="Digite o IP do Switch")
        return

    status.configure(text="Testando conectividade...")
    app.update()

    resultado = logon_sw_new.conectar_switch(ip_sw)

    if resultado:
        status.configure(text=f"Conectado ao Switch {ip_sw}")
    else:
        status.configure(text=f"Falha na conexão com {ip_sw}")


# Configuração da interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Janela principal
app = ctk.CTk()
app.title("Automação de Switch Cisco")
app.geometry("550x250")


# Título
titulo = ctk.CTkLabel(
    app,
    text="Cisco Network Automation",
    font=("Arial", 22, "bold")
)
titulo.pack(pady=25)


# Frame para IP + botão
frame_conexao = ctk.CTkFrame(app)
frame_conexao.pack(padx=20, pady=10)


# Campo IP
campo_ip = ctk.CTkEntry(
    frame_conexao,
    width=220,
    placeholder_text="IP do Switch"
)
campo_ip.grid(row=0, column=0, padx=10, pady=15)


# Botão testar
botao_testar = ctk.CTkButton(
    frame_conexao,
    text="Testar Conectividade",
    command=testar_conectividade
)
botao_testar.grid(row=0, column=1, padx=10, pady=15)


# Status da conexão
status = ctk.CTkLabel(
    app,
    text="Aguardando teste..."
)
status.pack(pady=10)


# Inicia interface
app.mainloop()