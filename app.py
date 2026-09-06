import streamlit as st
import sqlite3
import hashlib
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide"
)

# --- BANCO DE DADOS ---
def conectar_db():
    conn = sqlite3.connect("database.db")
    return conn

def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)
    
    # Tabela de Devocionais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devocionais (
            data TEXT PRIMARY KEY,
            referencia TEXT,
            versiculo TEXT,
            fortalecimento TEXT
        )
    """)
    
    # Tabela de Reflexões do Usuário
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflexoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_email TEXT,
            data TEXT,
            reflexao TEXT,
            UNIQUE(usuario_email, data)
        )
    """)
    
    # Tabela de Favoritos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_email TEXT,
            data TEXT,
            UNIQUE(usuario_email, data)
        )
    """)
    
    # Garante a existência do usuário Admin padrão
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("admin@vidanapalavra.com",))
    if not cursor.fetchone():
        senha_hash = hashlib.sha256("123456".encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (email, senha, tipo) VALUES (?, ?, ?)",
                       ("admin@vidanapalavra.com", senha_hash, "admin"))
        
    conn.commit()
    conn.close()

criar_tabelas()

# --- FUNÇÕES DE AUTENTICAÇÃO E NAVEGAÇÃO ---
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(email, senha):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM usuarios WHERE email = ? AND senha = ?", (email, hash_senha(senha)))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def criar_usuario(email, senha, tipo="usuario"):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (email, senha, tipo) VALUES (?, ?, ?)",
                       (email, hash_senha(senha), tipo))
        conn.commit()
        conn.close()
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Este e-mail já está cadastrado no sistema."

# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = ""

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("📖 Vida Na Palavra")
    st.subheader("Acesso ao Sistema")
    
    with st.form("form_login"):
        email_input = st.text_input("E-mail:")
        senha_input = st.text_input("Senha:", type="password")
        btn_login = st.form_submit_button("Entrar")
        
        if btn_login:
            tipo = verificar_login(email_input, senha_input)
            if tipo:
                st.session_state.logado = True
                st.session_state.usuario_email = email_input
                st.session_state.tipo_usuario = tipo
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

# --- APLICAÇÃO PRINCIPAL (LOGADO) ---
else:
    # Menu Lateral
    st.sidebar.title("Vida Na Palavra")
    st.sidebar.write(f"👤 **{st.session_state.tipo_usuario.capitalize()}**")
    st.sidebar.caption(st.session_state.usuario_email)
    st.sidebar.divider()
    
    opcoes_menu = ["Devocional Diário", "Meu Diário", "Favoritos"]
    if st.session_state.tipo_usuario == "admin":
        opcoes_menu.append("Painel Admin")
        
    menu = st.sidebar.radio("Navegação", opcoes_menu)
    
    if st.sidebar.button("Sair (Logout)"):
        st.session_state.logado = False
        st.session_state.usuario_email = ""
        st.session_state.tipo_usuario = ""
        st.rerun()

    # --- TELA 1: DEVOCIONAL DIÁRIO ---
    if menu == "Devocional Diário":
        st.title("📖 Devocional Diário")
        
        data_selecionada = st.date_input("Data do Devocional:", date.today())
        data_str = data_selecionada.strftime("%Y-%m-%d")
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT referencia, versiculo, fortalecimento FROM devocionais WHERE data = ?", (data_str,))
        devocional = cursor.fetchone()
        
        if devocional:
            st.info(f"**{devocional[0]}**\n\n\"{devocional[1]}\"")
            st.success(f"💡 **Fortalecimento Espiritual:**\n\n{devocional[2]}")
        else:
            st.warning("Nenhum devocional cadastrado para esta data.")
            
        st.divider()
        st.subheader("✍️ Sua Reflexão Pessoal")
        
        cursor.execute("SELECT reflexao FROM reflexoes WHERE usuario_email = ? AND data = ?",
                       (st.session_state.usuario_email, data_str))
        reflexao_salva = cursor.fetchone()
        texto_inicial = reflexao_salva[0] if reflexao_salva else ""
        
        nova_reflexao = st.text_area("O que Deus falou com você hoje?", value=texto_inicial, height=150)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Salvar Reflexão"):
                cursor.execute("""
                    INSERT INTO reflexoes (usuario_email, data, reflexao)
                    VALUES (?, ?, ?)
                    ON CONFLICT(usuario_email, data) DO UPDATE SET reflexao = excluded.reflexao
                """, (st.session_state.usuario_email, data_str, nova_reflexao))
                conn.commit()
                st.success("Reflexão salva!")
                
        # Botão de Impressão / PDF
        components.html(
            """
            <button onclick="window.parent.print()" style="
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 10px;">
                🖨️ Imprimir / Salvar PDF
            </button>
            """,
            height=60
        )
        conn.close()

    # --- TELA 2: MEU DIÁRIO ---
    elif menu == "Meu Diário":
        st.title("📔 Meu Diário Espiritual")
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data, reflexao FROM reflexoes 
            WHERE usuario_email = ? AND reflexao != '' 
            ORDER BY data DESC
        """, (st.session_state.usuario_email,))
        historico = cursor.fetchall()
        conn.close()
        
        if historico:
            for item in historico:
                with st.expander(f"📅 Registros de {item[0]}"):
                    st.write(item[1])
        else:
            st.info("Você ainda não salvou nenhuma reflexão.")

    # --- TELA 3: FAVORITOS ---
    elif menu == "Favoritos":
        st.title("⭐ Meus Devocionais Favoritos")
        st.info("Em breve você poderá consultar seus trechos favoritados aqui!")

    # --- TELA 4: PAINEL ADMIN ---
    elif menu == "Painel Admin":
        st.title("⚙️ Painel do Administrador")
        
        # Bloco de Cadastro de Usuários
        st.subheader("👥 Cadastrar Novo Usuário")
        with st.form("form_novo_usuario", clear_on_submit=True):
            novo_email = st.text_input("E-mail do usuário:")
            nova_senha = st.text_input("Senha provisória:", type="password")
            btn_cadastrar = st.form_submit_button("Cadastrar Usuário")
            
            if btn_cadastrar:
                if novo_email and nova_senha:
                    sucesso, msg = criar_usuario(novo_email, nova_senha, "usuario")
                    if sucesso:
                        st.success(f"Usuário {novo_email} cadastrado com sucesso!")
                    else:
                        st.warning(msg)
                else:
                    st.error("Preencha todos os campos!")
                    
        st.divider()
        
        # Bloco de Cadastro de Devocionais
        st.subheader("📖 Gerenciamento de Devocionais Diários")
        data_admin = st.date_input("Selecione a Data para o Devocional:", date.today(), key="admin_date")
        data_admin_str = data_admin.strftime("%Y-%m-%d")
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT referencia, versiculo, fortalecimento FROM devocionais WHERE data = ?", (data_admin_str,))
        existente = cursor.fetchone()
        
        ref_val = existente[0] if existente else ""
        ver_val = existente[1] if existente else ""
        fort_val = existente[2] if existente else ""
        
        with st.form("form_devocional"):
            ref_input = st.text_input("Referência Bíblica (ex: Salmos 23:1):", value=ref_val)
            ver_input = st.text_area("Texto do Versículo:", value=ver_val, height=100)
            fort_input = st.text_area("Mensagem de Fortalecimento:", value=fort_val, height=100)
            btn_salvar_dev = st.form_submit_button("Salvar Devocional")
            
            if btn_salvar_dev:
                cursor.execute("""
                    INSERT INTO devocionais (data, referencia, versiculo, fortalecimento)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(data) DO UPDATE SET
                        referencia = excluded.referencia,
                        versiculo = excluded.versiculo,
                        fortalecimento = excluded.fortalecimento
                """, (data_admin_str, ref_input, ver_input, fort_input))
                conn.commit()
                st.success("Devocional salvo no banco de dados!")
        conn.close()

    # --- FALLBACK DE SEGURANÇA ---
    else:
        st.warning("Selecione uma opção no menu lateral.")
