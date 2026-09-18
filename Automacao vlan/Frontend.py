import customtkinter as ctk
from tkinter import filedialog, messagebox

import logonsw
import levantamento_vlan
import backup_sw
import configurar_vlan
import configurar_hostname
import conexao_switch


# ==================================================
# VARIÁVEIS
# ==================================================

vlans_configuracao = {}


# ==================================================
# FUNÇÕES - TOOLS
# ==================================================

def testar_conectividade():

    ip_sw = campo_ip.get().strip()

    # ==================================================
    # VALIDAÇÃO DO IP
    # ==================================================

    if not ip_sw:

        messagebox.showwarning(
            "IP não informado",
            "Digite o IP do Switch."
        )

        status.configure(
            text="Digite o IP do Switch"
        )

        return


    # ==================================================
    # INICIANDO TESTE
    # ==================================================

    status.configure(
        text="Testando conectividade..."
    )

    app.update()


    # ==================================================
    # CONECTANDO AO SWITCH
    # ==================================================

    resultado = conexao_switch.conectar_switch(ip_sw)


    # ==================================================
    # ERRO DE CONEXÃO
    # ==================================================

    if not resultado["sucesso"]:

        messagebox.showerror(
            resultado["titulo"],
            resultado["mensagem"]
        )

        status.configure(
            text=resultado["titulo"]
        )

        return


    # ==================================================
    # CONEXÃO REALIZADA
    # ==================================================

    net_connect = resultado["conexao"]

    hostname = (
        net_connect.find_prompt()
        .replace("#", "")
        .replace(">", "")
        .strip()
    )

    net_connect.disconnect()


    # ==================================================
    # SUCESSO
    # ==================================================

    messagebox.showinfo(
        "Conexão realizada",
        f"Conexão realizada com sucesso!\n\n"
        f"IP: {ip_sw}\n"
        f"Hostname: {hostname}"
    )

    status.configure(
        text=f"Conectado ao Switch {ip_sw}"
    )


# ==================================================
# BUSCAR VLANS
# ==================================================

def buscar_vlans():

    ip_sw = campo_ip.get().strip()


    # ==================================================
    # VALIDAÇÃO
    # ==================================================

    if not ip_sw:

        messagebox.showwarning(
            "IP não informado",
            "Digite o IP do Switch."
        )

        status.configure(
            text="Digite o IP do Switch"
        )

        return


    # ==================================================
    # BUSCANDO VLANS
    # ==================================================

    status.configure(
        text="Buscando VLANs..."
    )

    app.update()

    resultado = levantamento_vlan.buscar_vlans(ip_sw)


    # ==================================================
    # ERRO
    # ==================================================

    if not resultado["sucesso"]:

        messagebox.showerror(
            resultado["titulo"],
            resultado["mensagem"]
        )

        status.configure(
            text=resultado["titulo"]
        )

        return


    # ==================================================
    # SUCESSO
    # ==================================================

    vlans = resultado["vlans"]

    lista_vlans.delete(
        "1.0",
        "end"
    )


    if not vlans:

        messagebox.showwarning(
            "VLANs",
            "Nenhuma VLAN encontrada."
        )

        status.configure(
            text="Nenhuma VLAN encontrada"
        )

        return


    # ==================================================
    # EXIBIR VLANS
    # ==================================================

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
# BACKUP - TOOLS
# ==================================================

def abrir_backup():

    ip_sw = campo_ip.get().strip()

    if not ip_sw:
        status.configure(
            text="Digite o IP do Switch"
        )
        return

    janela_backup = ctk.CTkToplevel(app)

    janela_backup.title(
        "Backup do Switch"
    )

    janela_backup.geometry(
        "400x280"
    )

    janela_backup.grab_set()

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

            messagebox.showerror(
                resultado["titulo"],
                resultado["mensagem"]
            )

            status_backup.configure(
                text=resultado["titulo"]
            )

            return

        salvamento = backup_sw.salvar_local(
            resultado,
            caminho
        )

        if salvamento["sucesso"]:

            messagebox.showinfo(
                "Backup concluído",
                f"Backup realizado com sucesso!\n\n"
                f"Hostname: {resultado['hostname']}\n"
                f"Arquivo: {resultado['nome_arquivo']}"
            )

            status_backup.configure(
                text="Backup realizado com sucesso!"
            )

        else:

            messagebox.showerror(
                salvamento["titulo"],
                salvamento["mensagem"]
            )

            status_backup.configure(
                text=salvamento["titulo"]
            )

    # --------------------------------------------------
    # BACKUP SFTP - TOOLS
    # --------------------------------------------------

    def backup_sftp():

        janela_sftp = ctk.CTkToplevel(janela_backup)
        janela_sftp.title("Backup SFTP")
        janela_sftp.geometry("520x430")
        janela_sftp.grab_set()

        titulo_sftp = ctk.CTkLabel(
            janela_sftp,
            text="Enviar Backup para SFTP",
            font=("Arial", 18, "bold")
        )
        titulo_sftp.pack(pady=(20, 15))

        campo_servidor = ctk.CTkEntry(
            janela_sftp,
            width=380,
            placeholder_text="Servidor SFTP"
        )
        campo_servidor.pack(pady=6)

        campo_porta = ctk.CTkEntry(
            janela_sftp,
            width=380,
            placeholder_text="Porta"
        )
        campo_porta.insert(0, "22")
        campo_porta.pack(pady=6)

        campo_usuario = ctk.CTkEntry(
            janela_sftp,
            width=380,
            placeholder_text="Usuário"
        )
        campo_usuario.pack(pady=6)

        campo_senha = ctk.CTkEntry(
            janela_sftp,
            width=380,
            placeholder_text="Senha",
            show="*"
        )
        campo_senha.pack(pady=6)

        campo_diretorio = ctk.CTkEntry(
            janela_sftp,
            width=380,
            placeholder_text="Diretório remoto"
        )
        campo_diretorio.pack(pady=6)

        status_sftp = ctk.CTkLabel(
            janela_sftp,
            text=""
        )
        status_sftp.pack(pady=8)

        def enviar_backup_sftp():

            servidor = campo_servidor.get().strip()
            porta = campo_porta.get().strip()
            usuario = campo_usuario.get().strip()
            senha = campo_senha.get().strip()
            diretorio = campo_diretorio.get().strip()

            if not servidor:
                status_sftp.configure(text="Digite o servidor SFTP")
                return

            if not porta:
                status_sftp.configure(text="Digite a porta SFTP")
                return

            if not porta.isdigit():
                status_sftp.configure(text="A porta SFTP deve ser numérica")
                return

            if not usuario:
                status_sftp.configure(text="Digite o usuário SFTP")
                return

            if not senha:
                status_sftp.configure(text="Digite a senha SFTP")
                return

            status_sftp.configure(text="Obtendo configuração do switch...")
            status_backup.configure(text="Obtendo configuração...")
            janela_sftp.update()

            resultado = backup_sw.obter_backup(ip_sw)

            if not resultado["sucesso"]:
                messagebox.showerror(
                    resultado["titulo"],
                    resultado["mensagem"]
                )
                status_sftp.configure(text=resultado["titulo"])
                status_backup.configure(text=resultado["titulo"])
                return

            status_sftp.configure(text="Enviando backup para o SFTP...")
            status_backup.configure(text="Enviando backup para o SFTP...")
            janela_sftp.update()

            salvamento = backup_sw.salvar_sftp(
                resultado_backup=resultado,
                servidor=servidor,
                porta=porta,
                usuario=usuario,
                senha=senha,
                diretorio=diretorio
            )

            if salvamento["sucesso"]:
                messagebox.showinfo(
                    "Backup SFTP concluído",
                    f"Backup enviado com sucesso!\n\n"
                    f"Hostname: {resultado['hostname']}\n"
                    f"Arquivo: {resultado['nome_arquivo']}\n"
                    f"Destino: {salvamento['arquivo']}"
                )
                status_sftp.configure(text="Backup SFTP realizado com sucesso!")
                status_backup.configure(text="Backup SFTP realizado com sucesso!")

            else:
                messagebox.showerror(
                    salvamento["titulo"],
                    salvamento["mensagem"]
                )
                status_sftp.configure(text=salvamento["titulo"])
                status_backup.configure(text=salvamento["titulo"])

        botao_enviar_sftp = ctk.CTkButton(
            janela_sftp,
            text="Enviar Backup",
            command=enviar_backup_sftp
        )
        botao_enviar_sftp.pack(pady=10)

    botao_local = ctk.CTkButton(
        janela_backup,
        text="Salvar Localmente",
        command=backup_local
    )

    botao_local.pack(
        pady=10
    )

    botao_sftp = ctk.CTkButton(
        janela_backup,
        text="Enviar para SFTP",
        command=backup_sftp
    )

    botao_sftp.pack(
        pady=10
    )

    status_backup = ctk.CTkLabel(
        janela_backup,
        text=""
    )

    status_backup.pack(
        pady=10
    )


# ==================================================
# FUNÇÕES - CONFIGURAÇÃO
# ==================================================

def adicionar_vlan():

    vlan_id = campo_vlan_id.get().strip()
    vlan_nome = campo_vlan_nome.get().strip()

    if not vlan_id:

        status_config.configure(
            text="Digite o ID da VLAN"
        )

        return

    if not vlan_id.isdigit():

        status_config.configure(
            text="O ID da VLAN deve ser numérico"
        )

        return

    if not vlan_nome:

        status_config.configure(
            text="Digite o nome da VLAN"
        )

        return

    vlans_configuracao[int(vlan_id)] = vlan_nome

    atualizar_lista_configuracao()

    campo_vlan_id.delete(
        0,
        "end"
    )

    campo_vlan_nome.delete(
        0,
        "end"
    )

    status_config.configure(
        text=f"VLAN {vlan_id} adicionada à lista"
    )


# ==================================================
# ATUALIZAR LISTA DE VLANS
# ==================================================

def atualizar_lista_configuracao():

    lista_config.delete(
        "1.0",
        "end"
    )

    for vlan_id, vlan_nome in vlans_configuracao.items():

        lista_config.insert(
            "end",
            f"VLAN {vlan_id} | {vlan_nome}\n"
        )


# ==================================================
# LIMPAR LISTA DE VLANS
# ==================================================

def limpar_vlans():

    vlans_configuracao.clear()

    lista_config.delete(
        "1.0",
        "end"
    )

    status_config.configure(
        text="Lista de VLANs limpa"
    )


# ==================================================
# BACKUP LOCAL - CONFIGURAÇÃO
# ==================================================

def atualizar_opcao_backup_local():

    if backup_local_var.get():

        caminho = filedialog.askdirectory(
            title="Escolha onde salvar o backup"
        )

        if caminho:

            caminho_backup_local.set(
                caminho
            )

        else:

            backup_local_var.set(False)
            caminho_backup_local.set("")

    else:

        caminho_backup_local.set("")


# ==================================================
# MOSTRAR / ESCONDER SFTP
# ==================================================

def atualizar_opcao_sftp():

    if backup_sftp_var.get():

        frame_sftp.pack(
            padx=20,
            pady=(0, 10),
            fill="x",
            after=frame_backup_config
        )

    else:

        frame_sftp.pack_forget()


# ==================================================
# CONFIGURAR SWITCH
# ==================================================

def configurar_switch():

    ip_sw = campo_ip_config.get().strip()
    hostname = campo_hostname.get().strip()

    backup_local = backup_local_var.get()
    backup_sftp = backup_sftp_var.get()

    caminho_local = caminho_backup_local.get()

    # ==================================================
    # VALIDAÇÕES
    # ==================================================

    if not ip_sw:
        status_config.configure(text="Digite o IP do Switch")
        return

    if not vlans_configuracao and not hostname:
        status_config.configure(
            text="Informe um Hostname ou adicione pelo menos uma VLAN"
        )
        return

    if backup_local and not caminho_local:
        status_config.configure(
            text="Selecione o caminho do Backup Local"
        )
        return

    # ==================================================
    # VALIDAÇÃO SFTP
    # ==================================================

    if backup_sftp:
        servidor_sftp = campo_sftp_servidor.get().strip()
        porta_sftp = campo_sftp_porta.get().strip()
        usuario_sftp = campo_sftp_usuario.get().strip()
        senha_sftp = campo_sftp_senha.get().strip()
        diretorio_sftp = campo_sftp_diretorio.get().strip()

        if not servidor_sftp:
            status_config.configure(text="Digite o servidor SFTP")
            return

        if not porta_sftp:
            status_config.configure(text="Digite a porta SFTP")
            return

        if not usuario_sftp:
            status_config.configure(text="Digite o usuário SFTP")
            return

        if not senha_sftp:
            status_config.configure(text="Digite a senha SFTP")
            return

    # ==================================================
    # LIMPA RESULTADO
    # ==================================================

    lista_resultado.delete("1.0", "end")

    net_connect = None

    try:
        # ==================================================
        # CONEXÃO ÚNICA COM O SWITCH
        # ==================================================

        status_config.configure(text="Conectando ao switch...")
        app.update()

        resultado_conexao = conexao_switch.conectar_switch(
            ip_sw,
            "configuracao_switch_output.txt"
        )

        if not resultado_conexao["sucesso"]:
            messagebox.showerror(
                resultado_conexao["titulo"],
                resultado_conexao["mensagem"]
            )
            lista_resultado.insert(
                "end",
                resultado_conexao["mensagem"] + "\n"
            )
            status_config.configure(
                text=resultado_conexao["titulo"]
            )
            return

        net_connect = resultado_conexao["conexao"]

        lista_resultado.insert(
            "end",
            "Conexão SSH realizada com sucesso.\n"
        )

        # ==================================================
        # ETAPAS 1 E 2 - BACKUP LOCAL / SFTP
        # ==================================================

        resultado_backup = None

        # Obtém o running-config apenas uma vez caso algum
        # dos dois tipos de backup tenha sido solicitado.
        if backup_local or backup_sftp:

            status_config.configure(text="Obtendo configuração para backup...")
            app.update()

            resultado_backup = backup_sw.obter_backup(
                net_connect=net_connect
            )

            if not resultado_backup["sucesso"]:
                messagebox.showerror(
                    resultado_backup["titulo"],
                    resultado_backup["mensagem"]
                )
                lista_resultado.insert(
                    "end",
                    resultado_backup["mensagem"] + "\n"
                )
                status_config.configure(
                    text=resultado_backup["titulo"]
                )
                return

        # ==================================================
        # ETAPA 1 - BACKUP LOCAL
        # ==================================================

        if backup_local:

            status_config.configure(text="Salvando backup local...")
            app.update()

            salvamento = backup_sw.salvar_local(
                resultado_backup,
                caminho_local
            )

            if salvamento["sucesso"]:
                lista_resultado.insert(
                    "end",
                    "Backup local realizado com sucesso.\n"
                )
                lista_resultado.insert(
                    "end",
                    f"Arquivo: {salvamento['arquivo']}\n"
                )
            else:
                messagebox.showerror(
                    salvamento["titulo"],
                    salvamento["mensagem"]
                )
                lista_resultado.insert(
                    "end",
                    salvamento["mensagem"] + "\n"
                )
                status_config.configure(
                    text=salvamento["titulo"]
                )
                return

        else:
            lista_resultado.insert(
                "end",
                "Backup Local: não solicitado.\n"
            )

        # ==================================================
        # ETAPA 2 - BACKUP SFTP
        # ==================================================

        if backup_sftp:

            status_config.configure(text="Enviando backup para o SFTP...")
            app.update()

            salvamento_sftp = backup_sw.salvar_sftp(
                resultado_backup=resultado_backup,
                servidor=servidor_sftp,
                porta=porta_sftp,
                usuario=usuario_sftp,
                senha=senha_sftp,
                diretorio=diretorio_sftp
            )

            if salvamento_sftp["sucesso"]:
                lista_resultado.insert(
                    "end",
                    "Backup SFTP realizado com sucesso.\n"
                )
                lista_resultado.insert(
                    "end",
                    f"Arquivo remoto: {salvamento_sftp['arquivo']}\n"
                )
            else:
                messagebox.showerror(
                    salvamento_sftp["titulo"],
                    salvamento_sftp["mensagem"]
                )
                lista_resultado.insert(
                    "end",
                    salvamento_sftp["mensagem"] + "\n"
                )
                status_config.configure(
                    text=salvamento_sftp["titulo"]
                )
                return

        else:
            lista_resultado.insert(
                "end",
                "Backup SFTP: não solicitado.\n"
            )

        # ==================================================
        # ETAPA 3 - HOSTNAME
        # ==================================================

        if hostname:
            status_config.configure(text="Verificando hostname...")
            app.update()

            resultado_consulta = configurar_hostname.consultar_hostname(
                net_connect=net_connect
            )

            if not resultado_consulta["sucesso"]:
                mensagem_erro = resultado_consulta.get(
                    "mensagem",
                    resultado_consulta.get("erro", "Erro desconhecido")
                )
                messagebox.showerror(
                    resultado_consulta.get("titulo", "Erro ao consultar hostname"),
                    mensagem_erro
                )
                lista_resultado.insert(
                    "end",
                    "Erro ao consultar hostname:\n"
                )
                lista_resultado.insert(
                    "end",
                    mensagem_erro + "\n"
                )
                status_config.configure(
                    text="Erro ao consultar hostname"
                )
                return

            hostname_atual = resultado_consulta["hostname"]

            if hostname_atual == hostname:
                lista_resultado.insert(
                    "end",
                    f"Hostname já está correto: {hostname}\n"
                )
            else:
                resposta = messagebox.askyesno(
                    "Alteração de Hostname",
                    f"O hostname atual do switch é:\n\n"
                    f"{hostname_atual}\n\n"
                    f"O hostname solicitado é:\n\n"
                    f"{hostname}\n\n"
                    f"Deseja realizar a alteração?"
                )

                if resposta:
                    status_config.configure(text="Configurando hostname...")
                    app.update()

                    resultado_hostname = configurar_hostname.alterar_hostname(
                        novo_hostname=hostname,
                        net_connect=net_connect
                    )

                    if resultado_hostname["sucesso"]:
                        lista_resultado.insert(
                            "end",
                            resultado_hostname["mensagem"] + "\n"
                        )
                    else:
                        mensagem_erro = resultado_hostname.get(
                            "mensagem",
                            resultado_hostname.get("erro", "Erro desconhecido")
                        )
                        messagebox.showerror(
                            resultado_hostname.get("titulo", "Erro ao configurar hostname"),
                            mensagem_erro
                        )
                        lista_resultado.insert(
                            "end",
                            "Erro ao configurar hostname:\n"
                        )
                        lista_resultado.insert(
                            "end",
                            mensagem_erro + "\n"
                        )
                        status_config.configure(
                            text="Erro na configuração do hostname"
                        )
                        return
                else:
                    lista_resultado.insert(
                        "end",
                        f"Hostname atual: {hostname_atual}\n"
                    )
                    lista_resultado.insert(
                        "end",
                        f"Hostname solicitado: {hostname}\n"
                    )
                    lista_resultado.insert(
                        "end",
                        "Alteração de hostname não autorizada pelo usuário.\n"
                    )
        else:
            lista_resultado.insert(
                "end",
                "Hostname: nenhuma alteração solicitada.\n"
            )

        # ==================================================
        # ETAPA 4 - CONFIGURAÇÃO DAS VLANS
        # ==================================================

        if vlans_configuracao:
            status_config.configure(text="Verificando VLANs...")
            app.update()

            for vlan_id, vlan_nome in vlans_configuracao.items():

                resultado_vlan = configurar_vlan.consultar_vlan(
                    vlan_id=vlan_id,
                    net_connect=net_connect
                )

                if not resultado_vlan["sucesso"]:
                    mensagem_erro = resultado_vlan.get(
                        "mensagem",
                        resultado_vlan.get("erro", "Erro desconhecido")
                    )
                    messagebox.showerror(
                        resultado_vlan.get("titulo", f"Erro ao consultar VLAN {vlan_id}"),
                        mensagem_erro
                    )
                    lista_resultado.insert(
                        "end",
                        f"Erro ao consultar VLAN {vlan_id}:\n"
                    )
                    lista_resultado.insert(
                        "end",
                        mensagem_erro + "\n"
                    )
                    status_config.configure(
                        text=f"Erro ao consultar VLAN {vlan_id}"
                    )
                    return

                if not resultado_vlan["existe"]:
                    status_config.configure(
                        text=f"Criando VLAN {vlan_id}..."
                    )
                    app.update()

                    resultado_criacao = configurar_vlan.criar_vlan(
                        vlan_id=vlan_id,
                        vlan_nome=vlan_nome,
                        net_connect=net_connect
                    )

                    if resultado_criacao["sucesso"]:
                        lista_resultado.insert(
                            "end",
                            resultado_criacao["mensagem"] + "\n"
                        )
                    else:
                        mensagem_erro = resultado_criacao.get(
                            "mensagem",
                            resultado_criacao.get("erro", "Erro desconhecido")
                        )
                        messagebox.showerror(
                            resultado_criacao.get("titulo", f"Erro ao criar VLAN {vlan_id}"),
                            mensagem_erro
                        )
                        lista_resultado.insert(
                            "end",
                            f"Erro ao criar VLAN {vlan_id}:\n"
                        )
                        lista_resultado.insert(
                            "end",
                            mensagem_erro + "\n"
                        )
                        status_config.configure(
                            text=f"Erro ao criar VLAN {vlan_id}"
                        )
                        return

                else:
                    nome_atual = resultado_vlan["nome"]

                    if nome_atual == vlan_nome:
                        lista_resultado.insert(
                            "end",
                            f"VLAN {vlan_id} - {vlan_nome} "
                            f"já existe e está correta.\n"
                        )
                    else:
                        resposta = messagebox.askyesno(
                            "Alteração de VLAN",
                            f"A VLAN {vlan_id} já existe "
                            f"com outro nome.\n\n"
                            f"Nome atual:\n"
                            f"{nome_atual}\n\n"
                            f"Nome solicitado:\n"
                            f"{vlan_nome}\n\n"
                            f"Deseja alterar o nome da VLAN?"
                        )

                        if resposta:
                            status_config.configure(
                                text=f"Alterando VLAN {vlan_id}..."
                            )
                            app.update()

                            resultado_alteracao = configurar_vlan.alterar_vlan(
                                vlan_id=vlan_id,
                                vlan_nome=vlan_nome,
                                net_connect=net_connect
                            )

                            if resultado_alteracao["sucesso"]:
                                lista_resultado.insert(
                                    "end",
                                    resultado_alteracao["mensagem"] + "\n"
                                )
                            else:
                                mensagem_erro = resultado_alteracao.get(
                                    "mensagem",
                                    resultado_alteracao.get("erro", "Erro desconhecido")
                                )
                                messagebox.showerror(
                                    resultado_alteracao.get("titulo", f"Erro ao alterar VLAN {vlan_id}"),
                                    mensagem_erro
                                )
                                lista_resultado.insert(
                                    "end",
                                    f"Erro ao alterar VLAN {vlan_id}:\n"
                                )
                                lista_resultado.insert(
                                    "end",
                                    mensagem_erro + "\n"
                                )
                                status_config.configure(
                                    text=f"Erro ao alterar VLAN {vlan_id}"
                                )
                                return
                        else:
                            lista_resultado.insert(
                                "end",
                                f"VLAN {vlan_id} - "
                                f"Nome atual: {nome_atual} | "
                                f"Nome solicitado: {vlan_nome}\n"
                            )
                            lista_resultado.insert(
                                "end",
                                f"Alteração da VLAN {vlan_id} "
                                f"não autorizada pelo usuário.\n"
                            )
        else:
            lista_resultado.insert(
                "end",
                "VLANs: nenhuma alteração solicitada.\n"
            )

        # ==================================================
        # ETAPA 5 - VALIDAÇÃO FINAL
        # ==================================================

        status_config.configure(text="Realizando validação final...")
        app.update()

        lista_resultado.insert(
            "end",
            "\n\n========== VALIDAÇÃO FINAL ==========\n"
        )

        divergencias = []

        # --------------------------------------------------
        # VALIDAR HOSTNAME
        # --------------------------------------------------

        if hostname:

            resultado_validacao_hostname = configurar_hostname.consultar_hostname(
                net_connect=net_connect
            )

            if not resultado_validacao_hostname["sucesso"]:

                mensagem_erro = resultado_validacao_hostname.get(
                    "mensagem",
                    resultado_validacao_hostname.get(
                        "erro",
                        "Erro desconhecido"
                    )
                )

                divergencias.append(
                    f"Não foi possível validar o hostname: {mensagem_erro}"
                )

                lista_resultado.insert(
                    "end",
                    "Hostname: ERRO NA VALIDAÇÃO\n"
                )

            else:

                hostname_encontrado = resultado_validacao_hostname["hostname"]

                if hostname_encontrado == hostname:

                    lista_resultado.insert(
                        "end",
                        f"Hostname: {hostname} [OK]\n"
                    )

                else:

                    divergencias.append(
                        f"Hostname - Desejado: {hostname} | "
                        f"Encontrado: {hostname_encontrado}"
                    )

                    lista_resultado.insert(
                        "end",
                        "Hostname: [DIVERGÊNCIA]\n"
                    )

                    lista_resultado.insert(
                        "end",
                        f"  Desejado: {hostname}\n"
                    )

                    lista_resultado.insert(
                        "end",
                        f"  Encontrado: {hostname_encontrado}\n"
                    )

        else:

            lista_resultado.insert(
                "end",
                "Hostname: não solicitado.\n"
            )

        # --------------------------------------------------
        # VALIDAR VLANS
        # --------------------------------------------------

        if vlans_configuracao:

            for vlan_id, vlan_nome in vlans_configuracao.items():

                resultado_validacao_vlan = configurar_vlan.consultar_vlan(
                    vlan_id=vlan_id,
                    net_connect=net_connect
                )

                if not resultado_validacao_vlan["sucesso"]:

                    mensagem_erro = resultado_validacao_vlan.get(
                        "mensagem",
                        resultado_validacao_vlan.get(
                            "erro",
                            "Erro desconhecido"
                        )
                    )

                    divergencias.append(
                        f"VLAN {vlan_id} - erro na validação: {mensagem_erro}"
                    )

                    lista_resultado.insert(
                        "end",
                        f"VLAN {vlan_id}: ERRO NA VALIDAÇÃO\n"
                    )

                    continue

                if not resultado_validacao_vlan["existe"]:

                    divergencias.append(
                        f"VLAN {vlan_id} - Desejada: {vlan_nome} | "
                        f"Encontrada: VLAN inexistente"
                    )

                    lista_resultado.insert(
                        "end",
                        f"VLAN {vlan_id}: [DIVERGÊNCIA]\n"
                    )

                    lista_resultado.insert(
                        "end",
                        f"  Desejado: {vlan_nome}\n"
                    )

                    lista_resultado.insert(
                        "end",
                        "  Encontrado: VLAN inexistente\n"
                    )

                    continue

                nome_encontrado = resultado_validacao_vlan["nome"]

                if nome_encontrado == vlan_nome:

                    lista_resultado.insert(
                        "end",
                        f"VLAN {vlan_id} - {vlan_nome} [OK]\n"
                    )

                else:

                    divergencias.append(
                        f"VLAN {vlan_id} - Desejado: {vlan_nome} | "
                        f"Encontrado: {nome_encontrado}"
                    )

                    lista_resultado.insert(
                        "end",
                        f"VLAN {vlan_id}: [DIVERGÊNCIA]\n"
                    )

                    lista_resultado.insert(
                        "end",
                        f"  Desejado: {vlan_nome}\n"
                    )

                    lista_resultado.insert(
                        "end",
                        f"  Encontrado: {nome_encontrado}\n"
                    )

        else:

            lista_resultado.insert(
                "end",
                "VLANs: nenhuma VLAN solicitada.\n"
            )

        # ==================================================
        # RESULTADO DA VALIDAÇÃO
        # ==================================================

        if divergencias:

            lista_resultado.insert(
                "end",
                "\nATENÇÃO: foram encontradas divergências.\n"
            )

            lista_resultado.insert(
                "end",
                "Estado desejado != Estado encontrado.\n"
            )

            status_config.configure(
                text="Configuração concluída com divergências!"
            )

            messagebox.showerror(
                "Erro na Validação",
                "A configuração foi executada, mas foram encontradas "
                "divergências durante a validação final.\n\n"
                "Status: ERRO\n\n"
                "Consulte o log de resultados para verificar os detalhes."
            )

        else:

            lista_resultado.insert(
                "end",
                "\nEstado desejado = Estado encontrado.\n"
            )

            lista_resultado.insert(
                "end",
                "Validação concluída com sucesso.\n"
            )

            status_config.configure(
                text="Configuração e validação concluídas com sucesso!"
            )

            messagebox.showinfo(
                "Implementação e Validação",
                "Configuração implementada e validada com sucesso!\n\n"
                "Todos os parâmetros solicitados foram conferidos no switch.\n\n"
                "Status: OK"
            )

        lista_resultado.insert(
            "end",
            "\nProcesso finalizado."
        )

    except Exception as erro:
        messagebox.showerror(
            "Erro inesperado",
            f"Ocorreu um erro durante a configuração do switch.\n\n"
            f"Detalhes técnicos:\n{erro}"
        )
        lista_resultado.insert(
            "end",
            f"\nErro inesperado: {erro}\n"
        )
        status_config.configure(
            text="Erro durante a configuração"
        )

    finally:
        # ==================================================
        # ENCERRA A ÚNICA SESSÃO SSH
        # ==================================================

        if net_connect:
            try:
                net_connect.disconnect()
            except:
                pass

# ==================================================
# CONFIGURAÇÃO CUSTOMTKINTER
# ==================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ==================================================
# JANELA PRINCIPAL
# ==================================================

app = ctk.CTk()

app.title(
    "Cisco Network Automation"
)

app.geometry(
    "950x750"
)


# ==================================================
# TÍTULO PRINCIPAL
# ==================================================

titulo = ctk.CTkLabel(
    app,
    text="Cisco Network Automation",
    font=("Arial", 24, "bold")
)

titulo.pack(
    pady=(15, 5)
)


# ==================================================
# ABAS
# ==================================================

abas = ctk.CTkTabview(
    app,
    width=900,
    height=650
)

abas.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)

aba_config = abas.add(
    "Configuração"
)

aba_tools = abas.add(
    "Tools"
)



# ==================================================
# ÁREA ROLÁVEL - ABA CONFIGURAÇÃO
# ==================================================

scroll_config = ctk.CTkScrollableFrame(
    aba_config,
    fg_color="transparent"
)

scroll_config.pack(
    fill="both",
    expand=True,
    padx=5,
    pady=5
)


# ==================================================
# ==================================================
# ABA TOOLS
# ==================================================
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
# TESTAR CONECTIVIDADE
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
# BUSCAR VLANS
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
# REALIZAR BACKUP
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
# STATUS TOOLS
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
    width=750,
    height=350
)

lista_vlans.pack(
    padx=20,
    pady=10
)


# ==================================================
# ==================================================
# ABA CONFIGURAÇÃO
# ==================================================
# ==================================================

titulo_config = ctk.CTkLabel(
    scroll_config,
    text="Configuração do Switch",
    font=("Arial", 18, "bold")
)

titulo_config.pack(
    pady=(10, 5)
)


# ==================================================
# DADOS DO SWITCH
# ==================================================

frame_switch_config = ctk.CTkFrame(
    scroll_config
)

frame_switch_config.pack(
    padx=20,
    pady=5,
    fill="x"
)

label_ip_config = ctk.CTkLabel(
    frame_switch_config,
    text="Informe o IP do Switch:",
    font=("Arial", 13, "bold"),
    width=190,
    anchor="w"
)

label_ip_config.grid(
    row=0,
    column=0,
    padx=(15, 10),
    pady=(15, 8),
    sticky="w"
)

campo_ip_config = ctk.CTkEntry(
    frame_switch_config,
    width=300,
    placeholder_text="Ex.: 192.168.1.10"
)

campo_ip_config.grid(
    row=0,
    column=1,
    padx=10,
    pady=(15, 8),
    sticky="w"
)

label_hostname_config = ctk.CTkLabel(
    frame_switch_config,
    text="Informe o Hostname:",
    font=("Arial", 13, "bold"),
    width=190,
    anchor="w"
)

label_hostname_config.grid(
    row=1,
    column=0,
    padx=(15, 10),
    pady=(8, 15),
    sticky="w"
)

campo_hostname = ctk.CTkEntry(
    frame_switch_config,
    width=300,
    placeholder_text="Ex.: SWITCH_AUTOMACAO"
)

campo_hostname.grid(
    row=1,
    column=1,
    padx=10,
    pady=(8, 15),
    sticky="w"
)


# ==================================================
# CONFIGURAÇÃO DAS VLANS
# ==================================================

frame_vlan = ctk.CTkFrame(
    scroll_config
)

frame_vlan.pack(
    padx=20,
    pady=5,
    fill="x"
)

label_vlan = ctk.CTkLabel(
    frame_vlan,
    text="Informe a VLAN:",
    font=("Arial", 14, "bold")
)

label_vlan.grid(
    row=0,
    column=0,
    columnspan=3,
    padx=15,
    pady=(12, 5),
    sticky="w"
)

label_vlan_id = ctk.CTkLabel(
    frame_vlan,
    text="VLAN ID:"
)

label_vlan_id.grid(
    row=1,
    column=0,
    padx=(15, 5),
    pady=10,
    sticky="e"
)

campo_vlan_id = ctk.CTkEntry(
    frame_vlan,
    width=120,
    placeholder_text="Ex.: 10"
)

campo_vlan_id.grid(
    row=1,
    column=1,
    padx=5,
    pady=10
)

label_vlan_nome = ctk.CTkLabel(
    frame_vlan,
    text="Nome:"
)

label_vlan_nome.grid(
    row=1,
    column=2,
    padx=(15, 5),
    pady=10,
    sticky="e"
)

campo_vlan_nome = ctk.CTkEntry(
    frame_vlan,
    width=220,
    placeholder_text="Ex.: VLAN_DADOS"
)

campo_vlan_nome.grid(
    row=1,
    column=3,
    padx=5,
    pady=10
)

botao_adicionar_vlan = ctk.CTkButton(
    frame_vlan,
    text="Adicionar VLAN",
    command=adicionar_vlan
)

botao_adicionar_vlan.grid(
    row=1,
    column=4,
    padx=15,
    pady=10
)


# ==================================================
# LISTA DE VLANS PARA CONFIGURAÇÃO
# ==================================================

lista_config = ctk.CTkTextbox(
    scroll_config,
    width=700,
    height=80
)

lista_config.pack(
    padx=20,
    pady=5
)


# ==================================================
# BACKUP ANTES DA CONFIGURAÇÃO
# ==================================================

frame_backup_config = ctk.CTkFrame(
    scroll_config
)

frame_backup_config.pack(
    padx=20,
    pady=5,
    fill="x"
)

label_backup = ctk.CTkLabel(
    frame_backup_config,
    text="Selecione o tipo de Backup:",
    font=("Arial", 14, "bold")
)

label_backup.grid(
    row=0,
    column=0,
    columnspan=3,
    padx=10,
    pady=(10, 5),
    sticky="w"
)


# ==================================================
# BACKUP LOCAL
# ==================================================

backup_local_var = ctk.BooleanVar(
    value=False
)

caminho_backup_local = ctk.StringVar(
    value=""
)

check_backup_local = ctk.CTkCheckBox(
    frame_backup_config,
    text="Backup Local",
    variable=backup_local_var,
    command=atualizar_opcao_backup_local
)

check_backup_local.grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

campo_caminho_backup = ctk.CTkEntry(
    frame_backup_config,
    width=550,
    textvariable=caminho_backup_local,
    placeholder_text="Caminho do backup local"
)

campo_caminho_backup.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)


# ==================================================
# BACKUP SFTP
# ==================================================

backup_sftp_var = ctk.BooleanVar(
    value=False
)

check_backup_sftp = ctk.CTkCheckBox(
    frame_backup_config,
    text="Backup SFTP",
    variable=backup_sftp_var,
    command=atualizar_opcao_sftp
)

check_backup_sftp.grid(
    row=2,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


# ==================================================
# CONFIGURAÇÃO SFTP
# ==================================================

frame_sftp = ctk.CTkFrame(
    scroll_config
)

label_sftp = ctk.CTkLabel(
    frame_sftp,
    text="Configuração do Servidor SFTP",
    font=("Arial", 14, "bold")
)

label_sftp.grid(
    row=0,
    column=0,
    columnspan=5,
    padx=10,
    pady=(10, 5)
)

campo_sftp_servidor = ctk.CTkEntry(
    frame_sftp,
    width=150,
    placeholder_text="Servidor SFTP"
)

campo_sftp_servidor.grid(
    row=1,
    column=0,
    padx=5,
    pady=10
)

campo_sftp_porta = ctk.CTkEntry(
    frame_sftp,
    width=70,
    placeholder_text="Porta"
)

campo_sftp_porta.insert(
    0,
    "22"
)

campo_sftp_porta.grid(
    row=1,
    column=1,
    padx=5,
    pady=10
)

campo_sftp_usuario = ctk.CTkEntry(
    frame_sftp,
    width=130,
    placeholder_text="Usuário"
)

campo_sftp_usuario.grid(
    row=1,
    column=2,
    padx=5,
    pady=10
)

campo_sftp_senha = ctk.CTkEntry(
    frame_sftp,
    width=130,
    placeholder_text="Senha",
    show="*"
)

campo_sftp_senha.grid(
    row=1,
    column=3,
    padx=5,
    pady=10
)

campo_sftp_diretorio = ctk.CTkEntry(
    frame_sftp,
    width=160,
    placeholder_text="Diretório remoto"
)

campo_sftp_diretorio.grid(
    row=1,
    column=4,
    padx=5,
    pady=10
)


# ==================================================
# BOTÕES
# ==================================================

frame_botoes_config = ctk.CTkFrame(
    scroll_config
)

frame_botoes_config.pack(
    pady=5
)


botao_configurar = ctk.CTkButton(
    frame_botoes_config,
    text="Configurar Switch",
    command=configurar_switch
)

botao_configurar.grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)


botao_limpar = ctk.CTkButton(
    frame_botoes_config,
    text="Limpar Lista",
    command=limpar_vlans
)

botao_limpar.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)


# ==================================================
# RESULTADO
# ==================================================

lista_resultado = ctk.CTkTextbox(
    scroll_config,
    width=700,
    height=100
)

lista_resultado.pack(
    padx=20,
    pady=5
)


# ==================================================
# STATUS
# ==================================================

status_config = ctk.CTkLabel(
    scroll_config,
    text="Aguardando configuração..."
)

status_config.pack(
    pady=5
)


# ==================================================
# EXECUTA INTERFACE
# ==================================================

app.mainloop()