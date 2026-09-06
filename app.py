import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE
# ==========================================
st.set_page_config(
    page_title="Vida Na Palavra - Devocional",
    page_icon="📖",
    layout="centered"
)

# Estilização CSS (Cores da marca + Ocultar menus de desenvolvimento)
st.markdown("""
    <style>
        .stApp {
            background-color: #FAFAFA;
        }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        .versiculo-card {
            background-color: #F0F4F8;
            border-left: 5px solid #1E3A8A;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .versiculo-ref {
            color: #1E3A8A;
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 8px;
        }
        .versiculo-texto {
            font-size: 1.05rem;
            color: #333333;
            font-style: italic;
        }
        .mensagem-card {
            background-color: #FFFBEB;
            border: 1px solid #F59E0B;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .mensagem-titulo {
            color: #B45309;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Trava de idioma para evitar tradução automática incorreta
st.markdown('<html lang="pt-BR">', unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS E SEGURANÇA
# ==========================================
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    
    # Tabela de Usuários (com coluna 'is_admin')
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT 1,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Adiciona a coluna is_admin se a tabela já existia antes
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    # Tabela de Devocionais
    c.execute("""
        CREATE TABLE IF NOT EXISTS devocionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT UNIQUE NOT NULL,
            referencia TEXT NOT NULL,
            versiculo TEXT NOT NULL,
            mensagem TEXT NOT NULL
        )
    """)

    # Tabela do Diário Pessoal
    c.execute("""
        CREATE TABLE IF NOT EXISTS diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            data TEXT NOT NULL,
            reflexao TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def gerar_hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def validar_login(email: str, senha: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    senha_hash = gerar_hash_senha(senha)
    
    c.execute("""
        SELECT id, nome, email, ativo, is_admin 
        FROM usuarios 
        WHERE email = ? AND senha_hash = ?
    """, (email.lower().strip(), senha_hash))
    
    user = c.fetchone()
    conn.close()
    return user

def popular_dados_iniciais():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    
    # Usuário Cliente Padrão
    try:
        email_teste = "cliente@vidanapalavra.com"
        senha_hash = gerar_hash_senha("123456")
        c.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, ativo, is_admin) 
            VALUES (?, ?, ?, ?, ?)
        """, ("Irmão(ã) em Cristo", email_teste, senha_hash, 1, 0))
    except sqlite3.IntegrityError:
        pass

    # Usuário Administrador
    try:
        email_admin = "admin@vidanapalavra.com"
        senha_admin_hash = gerar_hash_senha("admin123")
        c.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, ativo, is_admin) 
            VALUES (?, ?, ?, ?, ?)
        """, ("Administrador", email_admin, senha_admin_hash, 1, 1))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

def buscar_devocional_por_data(data_str: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT referencia, versiculo, mensagem FROM devocionais WHERE data = ?", (data_str,))
    resultado = c.fetchone()
    conn.close()
    return resultado

def salvar_ou_atualizar_devocional(data_str: str, referencia: str, versiculo: str, mensagem: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO devocionais (data, referencia, versiculo, mensagem)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(data) DO UPDATE SET
            referencia = excluded.referencia,
            versiculo = excluded.versiculo,
            mensagem = excluded.mensagem
    """, (data_str, referencia, versiculo, mensagem))
    conn.commit()
    conn.close()

def salvar_reflexao(user_email: str, data_str: str, texto: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO diario (user_email, data, reflexao)
        VALUES (?, ?, ?)
    """, (user_email, data_str, texto))
    conn.commit()
    conn.close()

def buscar_diario_usuario(user_email: str):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT data, reflexao FROM diario WHERE user_email = ? ORDER BY id DESC", (user_email,))
    registros = c.fetchall()
    conn.close()
    return registros

# Inicializa banco de dados
init_db()
popular_dados_iniciais()

# ==========================================
# 3. CONTROLE DE SESSÃO
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_nome" not in st.session_state:
    st.session_state["user_nome"] = ""
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "data_devocional" not in st.session_state:
    st.session_state["data_devocional"] = date.today()
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []

# ==========================================
# 4. TELA DE LOGIN
# ==========================================
if not st.session_state["logged_in"]:
    st.title("📖 Vida Na Palavra")
    st.subheader("Acesso Restrito ao Devocional")
    st.write("Por favor, informe seu e-mail de acesso e sua senha.")

    with st.form("form_login"):
        email = st.text_input("E-mail de Acesso")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar no Aplicativo", type="primary")

        if submit:
            if not email or not senha:
                st.warning("Por favor, preencha todos os campos.")
            else:
                user = validar_login(email, senha)
                if user:
                    user_id, nome, user_email, ativo, is_admin = user
                    if ativo:
                        st.session_state["logged_in"] = True
                        st.session_state["user_nome"] = nome
                        st.session_state["user_email"] = user_email
                        st.session_state["is_admin"] = bool(is_admin)
                        st.success(f"Bem-vindo(a), {nome}!")
                        st.rerun()
                    else:
                        st.error("Sua assinatura está inativa. Verifique seu acesso.")
                else:
                    st.error("E-mail ou senha incorretos. Tente novamente.")

# ==========================================
# 5. ÁREA RESTRITA (APÓS AUTENTICAÇÃO)
# ==========================================
else:
    with st.sidebar:
        st.title("Vida Na Palavra")
        st.write(f"👤 **{st.session_state['user_nome']}**")
        st.caption(st.session_state['user_email'])
        
        st.divider()
        
        # Opções de menu (Aba Admin visível apenas para administradores)
        opcoes_menu = ["Devocional Diário", "Meu Diário", "Favoritos"]
        if st.session_state["is_admin"]:
            opcoes_menu.append("Painel Admin")

        menu = st.radio("Navegação", opcoes_menu)
        
        st.divider()
        if st.button("Sair (Logout)"):
            st.session_state["logged_in"] = False
            st.session_state["user_nome"] = ""
            st.session_state["user_email"] = ""
            st.session_state["is_admin"] = False
            st.rerun()

    # --- TELA 1: DEVOCIONAL DIÁRIO ---
    if menu == "Devocional Diário":
        st.title("Devocional Diário")
        
        if "data_devocional" not in st.session_state:
            st.session_state["data_devocional"] = date.today()

        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Dia Anterior", use_container_width=True):
                st.session_state["data_devocional"] -= timedelta(days=1)
                st.rerun()
                
        with col3:
            if st.button("Próximo Dia ➡️", use_container_width=True):
                st.session_state["data_devocional"] += timedelta(days=1)
                st.rerun()

        with col2:
            nova_data = st.date_input(
                "Data:",
                value=st.session_state["data_devocional"],
                format="DD/MM/YYYY",
                label_visibility="collapsed"
            )
            if nova_data != st.session_state["data_devocional"]:
                st.session_state["data_devocional"] = nova_data
                st.rerun()

        data_str = st.session_state["data_devocional"].strftime("%Y-%m-%d")
        st.divider()

        devocional = buscar_devocional_por_data(data_str)

        if devocional:
            referencia, versiculo, mensagem = devocional

            st.markdown(f"""
                <div class="versiculo-card">
                    <div class="versiculo-ref">{referencia}</div>
                    <div class="versiculo-texto">"{versiculo}"</div>
                </div>
            """, unsafe_allow_html=True)

            # Botão de Favoritar
            if st.button("⭐ Salvar nos Favoritos"):
                novo_favorito = {
                    "data": st.session_state['data_devocional'].strftime('%d/%m/%Y'),
                    "referencia": referencia,
                    "versiculo": versiculo,
                    "mensagem": mensagem
                }
                if novo_favorito not in st.session_state["favoritos"]:
                    st.session_state["favoritos"].append(novo_favorito)
                    st.success("Versículo adicionado aos Favoritos com sucesso!")
                else:
                    st.warning("Este versículo já está na sua lista de favoritos.")

            st.markdown(f"""
                <div class="mensagem-card">
                    <div class="mensagem-titulo">💡 Fortalecimento Espiritual</div>
                    <p style="color: #4B5563; margin: 0;">{mensagem}</p>
                </div>
            """, unsafe_allow_html=True)

            st.subheader("✍️ Sua Reflexão Pessoal")
            reflexao = st.text_area(
                label=f"O que Deus falou com você em {st.session_state['data_devocional'].strftime('%d/%m/%Y')}?",
                placeholder="Escreva aqui suas orações ou reflexões...",
                height=130
            )

            if st.button("Salvar Reflexão", type="primary"):
                if reflexao.strip():
                    salvar_reflexao(st.session_state['user_email'], data_str, reflexao.strip())
                    st.success("Reflexão salva no seu diário com sucesso!")
                else:
                    st.warning("Escreva algo antes de salvar.")

        else:
            st.info(f"Nenhum devocional cadastrado para a data **{st.session_state['data_devocional'].strftime('%d/%m/%Y')}**.")

    # --- TELA 2: MEU DIÁRIO ---
    elif menu == "Meu Diário":
        st.title("📖 Meu Diário de Reflexões")
        st.write("Confira o seu histórico de anotações e reflexões diárias:")
        st.divider()

        registros = buscar_diario_usuario(st.session_state['user_email'])
        if registros:
            # Botão de Impressão / PDF
            if st.button("🖨️ Imprimir / Salvar Diário em PDF"):
                st.components.v1.html(
                    "<script>window.print();</script>",
                    height=0,
                    width=0
                )

            st.write("")  # Espaçamento

            for d_str, reftxt in registros:
                try:
                    data_fmt = datetime.strptime(d_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    data_fmt = d_str
                
                with st.expander(f"🗓️ Reflexão do dia {data_fmt}"):
                    st.write(reftxt)
        else:
            st.info("Você ainda não salvou nenhuma reflexão. Escreva uma anotação na aba Devocional Diário!")

    # --- TELA 3: FAVORITOS ---
    elif menu == "Favoritos":
        st.title("⭐ Versículos Favoritos")
        st.write("Sua coleção de versículos e mensagens marcados para rápida consulta:")
        st.divider()

        if not st.session_state["favoritos"]:
            st.info("Você ainda não guardou nenhum versículo. Clique no botão '⭐ Salvar nos Favoritos' enquanto lê o devocional diário!")
        else:
            for idx, item in enumerate(st.session_state["favoritos"]):
                with st.expander(f"📖 {item['referencia']} ({item['data']})"):
                    st.write(f"*\"{item['versiculo']}\"*")
                    st.caption(f"💡 {item['mensagem']}")
                    
                    if st.button("Remover dos Favoritos", key=f"rem_{idx}"):
                        st.session_state["favoritos"].pop(idx)
                        st.rerun()

    elif menu == "Favoritos":
    # (conteúdo da tela de favoritos)

elif menu == "Painel Admin":
    st.title("⚙️ Painel do Administrador")

    # --- CADASTRO DE USUÁRIOS ---
    st.subheader("👥 Cadastrar Novo Usuário")
    with st.form("form_novo_usuario", clear_on_submit=True):
        novo_email = st.text_input("E-mail do usuário:")
        nova_senha = st.text_input("Senha provisória:", type="password")
        btn_cadastrar = st.form_submit_button("Cadastrar Usuário")

        if btn_cadastrar:
            if novo_email and nova_senha:
                sucesso, msg = criar_usuario(
                    novo_email, nova_senha, "usuario"
                )
                if sucesso:
                    st.success(
                        f"Usuário {novo_email} cadastrado com sucesso!"
                    )
                else:
                    st.warning(msg)
            else:
                st.error("Preencha todos os campos!")

    st.divider()

    # --- GERENCIAMENTO DE DEVOCIONAIS ---
    st.subheader("📖 Gerenciamento de Devocionais Diários")
    # (mantenha a lógica de edição de devocionais aqui)

else:
    st.warning("Selecione uma opção no menu lateral.")
