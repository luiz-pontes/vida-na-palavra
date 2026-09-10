import streamlit as st
import datetime
import json
import os

# Configuração da Página
st.set_page_config(page_title="Vida Na Palavra", page_icon="📖", layout="wide")

# Ocultar Menu Superior, Cabeçalho e Rodapé do Streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Arquivos de Armazenamento Persistente
USUARIOS_FILE = "usuarios.json"
DEVOCIONAIS_FILE = "devocionais.json"
FAVORITOS_FILE = "favoritos.json"
DIARIO_FILE = "diario.json"

def carregar_dados(filepath, default_data):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def salvar_dados(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Inicialização de Dados
usuarios_padrao = {
    "admin@vidanapalavra.com": {"senha": "admin", "role": "admin"}
}
usuarios = carregar_dados(USUARIOS_FILE, usuarios_padrao)
if "admin@vidanapalavra.com" not in usuarios:
    usuarios["admin@vidanapalavra.com"] = {"senha": "admin", "role": "admin"}
    salvar_dados(USUARIOS_FILE, usuarios)

devocionais_padrao = {
    "09/09/2026": {
        "referencia": "Filipenses 4:13",
        "versiculo": '"Tudo posso naquele que me fortalece."',
        "titulo_reflexao": "Fortalecimento Espiritual",
        "reflexao": "Sua força não vem de suas próprias capacidades, mas da graça renovadora de Cristo em você."
    }
}
devocionais = carregar_dados(DEVOCIONAIS_FILE, devocionais_padrao)
favoritos = carregar_dados(FAVORITOS_FILE, {})
diario = carregar_dados(DIARIO_FILE, {})

# Gerenciamento da Sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = None

# TELA DE LOGIN
if not st.session_state["logado"]:
    st.title("📖 Vida Na Palavra")
    st.subheader("Acesse seu Devocional Diário")
    
    with st.form("form_login"):
        email = st.text_input("E-mail:").strip().lower()
        senha = st.text_input("Senha:", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if email in usuarios and usuarios[email]["senha"] == senha:
                st.session_state["logado"] = True
                st.session_state["usuario_atual"] = email
                st.session_state["role"] = usuarios[email].get("role", "user")
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

# ÁREA LOGADA
else:
    usuario_email = st.session_state["usuario_atual"]
    role = st.session_state.get("role", "user")
    
    # Barra Lateral
    st.sidebar.title("📖 Vida Na Palavra")
    st.sidebar.write(f"👤 **{role.capitalize()}**")
    st.sidebar.caption(usuario_email)
    st.sidebar.divider()
    
    opcoes_nav = ["Devocional Diário", "Meu Diário", "Favoritos"]
    if role == "admin":
        opcoes_nav.append("Painel Admin")
        
    pagina = st.sidebar.radio("Navegação", opcoes_nav)
    
    if st.sidebar.button("🚪 Sair (Logout)"):
        st.session_state["logado"] = False
        st.session_state["usuario_atual"] = None
        st.rerun()

    # 1. DEVOCIONAL DIÁRIO
    if pagina == "Devocional Diário":
        st.title("📖 Devocional Diário")
        
        data_sel = st.date_input("Selecione a Data do Devocional:", datetime.date.today())
        data_str = data_sel.strftime("%d/%m/%Y")
        
        st.subheader(f"📅 Devocional para {data_str}")
        
        dev = devocionais.get(data_str, {
            "referencia": "Salmos 119:105",
            "versiculo": '"Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."',
            "titulo_reflexao": "Luz na Caminhada",
            "reflexao": "Busque a palavra diária para guiar cada uma das suas decisões hoje."
        })
        
        st.info(f"📖 **{dev['referencia']}**\n\n{dev['versiculo']}")
        st.success(f"💡 **{dev['titulo_reflexao']}:**\n\n{dev['reflexao']}")
        
        # Botão de Favoritar
        fav_user = favoritos.get(usuario_email, [])
        ja_favoritou = any(item.get("data") == data_str for item in fav_user)
        
        if ja_favoritou:
            st.warning("⭐ Este devocional já está nos seus Favoritos!")
        else:
            if st.button("⭐ Favoritar este Devocional"):
                fav_user.append({
                    "data": data_str,
                    "referencia": dev["referencia"],
                    "versiculo": dev["versiculo"],
                    "reflexao": dev["reflexao"]
                })
                favoritos[usuario_email] = fav_user
                salvar_dados(FAVORITOS_FILE, favoritos)
                st.success("Devocional adicionado aos Favoritos!")
                st.rerun()

        st.divider()
        st.subheader("✍️ Sua Reflexão Pessoal")
        
        chave_diario = f"{usuario_email}_{data_str}"
        texto_existente = diario.get(chave_diario, "")
        
        nova_reflexao = st.text_area("O que Deus falou ao seu coração hoje?", value=texto_existente, height=120)
        if st.button("Salvar Reflexão"):
            diario[chave_diario] = nova_reflexao
            salvar_dados(DIARIO_FILE, diario)
            st.success("Reflexão salva com sucesso no seu Diário!")

    # 2. MEU DIÁRIO
    elif pagina == "Meu Diário":
        st.title("📓 Meu Diário Espiritual")
        registros = {k.split("_")[1]: v for k, v in diario.items() if k.startswith(f"{usuario_email}_") and v.strip()}
        
        if registros:
            for d, texto in sorted(registros.items(), reverse=True):
                with st.expander(f"📅 Registro de {d}"):
                    st.write(texto)
        else:
            st.info("Você ainda não salvou nenhuma reflexão no seu diário.")

    # 3. FAVORITOS
    elif pagina == "Favoritos":
        st.title("⭐ Meus Devocionais Favoritos")
        fav_user = favoritos.get(usuario_email, [])
        
        if fav_user:
            for idx, fav in enumerate(fav_user):
                with st.expander(f"📅 {fav['data']} - {fav['referencia']}"):
                    st.write(f"**Versículo:** {fav['versiculo']}")
                    st.write(f"**Reflexão:** {fav['reflexao']}")
                    if st.button(f"Remover dos Favoritos", key=f"del_{idx}"):
                        fav_user.pop(idx)
                        favoritos[usuario_email] = fav_user
                        salvar_dados(FAVORITOS_FILE, favoritos)
                        st.success("Removido dos favoritos!")
                        st.rerun()
        else:
            st.info("Você ainda não favoritou nenhum devocional.")

    # 4. PAINEL ADMIN
    elif pagina == "Painel Admin" and role == "admin":
        st.title("⚙️ Painel do Administrador")
        
        st.subheader("👥 Liberar Acesso a Novo Cliente")
        with st.form("form_novo_cliente"):
            novo_email = st.text_input("E-mail do comprador:").strip().lower()
            nova_senha = st.text_input("Senha provisória (padrão: 123456):", value="123456")
            submit_cliente = st.form_submit_button("Liberar Acesso")
            
            if submit_cliente:
                if novo_email:
                    usuarios[novo_email] = {"senha": nova_senha, "role": "user"}
                    salvar_dados(USUARIOS_FILE, usuarios)
                    st.success(f"Acesso liberado permanentemente para {novo_email}!")
                else:
                    st.error("Informe um e-mail válido.")
                    
        st.divider()
        st.subheader("📖 Personalizar Devocional Específico")
        with st.form("form_devocional"):
            data_dev = st.date_input("Selecione a Data:", datetime.date.today())
            ref_dev = st.text_input("Referência Bíblica (ex: Salmos 23:1):")
            ver_dev = st.text_area("Texto do Versículo:")
            tit_dev = st.text_input("Título da Reflexão:")
            refle_dev = st.text_area("Texto da Reflexão:")
            submit_dev = st.form_submit_button("Salvar Devocional")
            
            if submit_dev:
                d_str = data_dev.strftime("%d/%m/%Y")
                devocionais[d_str] = {
                    "referencia": ref_dev,
                    "versiculo": ver_dev,
                    "titulo_reflexao": tit_dev,
                    "reflexao": refle_dev
                }
                salvar_dados(DEVOCIONAIS_FILE, devocionais)
                st.success(f"Devocional do dia {d_str} atualizado com sucesso!")
