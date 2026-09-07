import hashlib
import sqlite3
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- BANCO DE DADOS ---
def conectar_db():
    return sqlite3.connect("database.db")


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

    # Tabela de Devocionais Personalizados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devocionais (
            data TEXT PRIMARY KEY,
            referencia TEXT,
            versiculo TEXT,
            fortalecimento TEXT
        )
    """)

    # Tabela de Reflexões
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

    # Garante a existência do Administrador Padrão
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ?", ("admin@vidanapalavra.com",)
    )
    if not cursor.fetchone():
        senha_hash = hashlib.sha256("123456".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (email, senha, tipo) VALUES (?, ?, ?)",
            ("admin@vidanapalavra.com", senha_hash, "admin"),
        )

    conn.commit()
    conn.close()


criar_tabelas()


# --- BASE DE DEVOCIONAIS AUTOMÁTICOS PARA TODO O ANO ---
def obter_devocional_padrao(data_obj):
    dia_do_ano = data_obj.timetuple().tm_yday
    base_devocionais = [
        (
            "Salmos 23:1",
            "O Senhor é o meu pastor; nada me faltará.",
            "Deus cuida de cada detalhe da sua vida. Descanse no cuidado e na provisão do Pai neste dia.",
        ),
        (
            "Filipenses 4:13",
            "Tudo posso naquele que me fortalece.",
            "Sua força não vem de suas próprias capacidades, mas da graça renovadora de Cristo em você.",
        ),
        (
            "Isaías 41:10",
            (
                "Não temas, porque eu sou contigo; não te assombres, porque eu"
                " sou o teu Deus; eu te fortaleço, e te ajudo, e te sustento"
                " com a destra da minha justiça."
            ),
            "A presença de Deus afasta todo o medo. Ele segura a sua mão em cada desafio hoje.",
        ),
        (
            "Provérbios 3:5-6",
            (
                "Confie no Senhor de todo o seu coração e não se apoie em seu"
                " próprio entendimento; reconheça o Senhor em todos os seus"
                " caminhos, e ele endireitará as suas veredas."
            ),
            "Entregue o controle das suas decisões ao Senhor. Ele guiará os seus passos com sabedoria.",
        ),
        (
            "Jeremias 29:11",
            (
                "Porque sou eu que conheço os planos que tenho para vocês’,"
                " diz o Senhor, ‘planos de fazê-los prosperar e não de causar"
                " dano, planos de dar a vocês esperança e um futuro’."
            ),
            "Deus já desenhou o seu futuro com paz e esperança. Permaneça firme na promessa Dele.",
        ),
        (
            "Mateus 11:28",
            (
                "Venham a mim, todos vocês que estão cansados e sobrecarregados,"
                " e eu lhes darei descanso."
            ),
            "Deposite suas preocupações nos pés de Jesus hoje. Nele você encontra a verdadeira paz.",
        ),
        (
            "Romanos 8:31",
            "Se Deus é por nós, quem será contra nós?",
            "Nenhuma adversidade pode prevalecer contra o propósito de Deus para a sua vida.",
        ),
        (
            "Salmos 46:1",
            (
                "Deus é o nosso refúgio e a nossa força, socorro bem presente"
                " na angústia."
            ),
            "Em momentos de tempestade, corra para o abraço do Pai. Ele é a sua fortaleza inabalável.",
        ),
        (
            "João 14:27",
            (
                "Deixo-lhes a paz; a minha paz lhes dou. Não a dou como o mundo"
                " a dá. Não se perturbe o seu coração, nem tenham medo."
            ),
            "A paz de Cristo excede todo o entendimento humano. Guarde seu coração nessa certeza.",
        ),
        (
            "Josué 1:9",
            (
                "Não fui eu que lhe ordenei? Seja forte e corajoso! Não fique"
                " desanimado nem apavore, porque o Senhor, o seu Deus, estará"
                " com você por onde você andar."
            ),
            "Avance com coragem. O Senhor dos Exércitos caminha à sua frente abrindo os caminhos.",
        ),
    ]

    indice = (dia_do_ano - 1) % len(base_devocionais)
    return base_devocionais[indice]


# --- FUNÇÕES DE SEGURANÇA E AUXILIARES ---
def normalizar_email(email):
    return email.strip().lower() if email else ""


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def verificar_login(email, senha):
    email_limpo = normalizar_email(email)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tipo FROM usuarios WHERE email = ? AND senha = ?",
        (email_limpo, hash_senha(senha)),
    )
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None


def criar_usuario(email, senha, tipo="usuario"):
    email_limpo = normalizar_email(email)
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (email, senha, tipo) VALUES (?, ?, ?)",
            (email_limpo, hash_senha(senha), tipo),
        )
        conn.commit()
        conn.close()
        return True, f"Usuário {email_limpo} cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Este e-mail já está cadastrado no sistema."


# --- CONTROLE DE SESSÃO E SEGURANÇA ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = ""


# --- TELA 0: LOGIN (BLOQUEIO PARA NÃO AUTORIZADOS) ---
if not st.session_state.logado:
    st.title("📖 Vida Na Palavra")
    st.subheader("🔒 Acesso Restrito aos Assinantes")
    st.write(
        "Por favor, insira suas credenciais cadastradas para acessar o"
        " aplicativo."
    )

    with st.form("form_login"):
        email_input = st.text_input("E-mail:")
        senha_input = st.text_input("Senha:", type="password")
        btn_login = st.form_submit_button("Entrar no Aplicativo")

        if btn_login:
            tipo = verificar_login(email_input, senha_input)
            if tipo:
                st.session_state.logado = True
                st.session_state.usuario_email = normalizar_email(email_input)
                st.session_state.tipo_usuario = tipo
                st.rerun()
            else:
                st.error(
                    "Acesso negado. E-mail ou senha incorretos. Verifique se o"
                    " seu cadastro foi liberado."
                )

# --- APLICAÇÃO PRINCIPAL (EXCLUSIVA PARA LOGADOS) ---
else:
    # Menu Lateral
    st.sidebar.title("📖 Vida Na Palavra")
    st.sidebar.write(f"👤 **{st.session_state.tipo_usuario.capitalize()}**")
    st.sidebar.caption(f"🔑 {st.session_state.usuario_email}")
    st.sidebar.divider()

    opcoes_menu = ["Devocional Diário", "Meu Diário", "Favoritos"]
    if st.session_state.tipo_usuario == "admin":
        opcoes_menu.append("Painel Admin")

    menu = st.sidebar.radio("Navegação", opcoes_menu)

    if st.sidebar.button("🚪 Sair (Logout)"):
        st.session_state.logado = False
        st.session_state.usuario_email = ""
        st.session_state.tipo_usuario = ""
        st.rerun()

    # --- TELA 1: DEVOCIONAL DIÁRIO ---
    if menu == "Devocional Diário":
        st.title("📖 Devocional Diário")

        # Data em Formato Brasileiro (DD/MM/AAAA)
        data_selecionada = st.date_input(
            "Selecione a Data do Devocional:",
            datetime.today(),
            format="DD/MM/YYYY",
        )
        data_str = data_selecionada.strftime("%Y-%m-%d")
        data_ptbr = data_selecionada.strftime("%d/%m/%Y")

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT referencia, versiculo, fortalecimento FROM devocionais"
            " WHERE data = ?",
            (data_str,),
        )
        devocional_db = cursor.fetchone()

        if devocional_db:
            ref, ver, fort = devocional_db
        else:
            ref, ver, fort = obter_devocional_padrao(data_selecionada)

        st.subheader(f"📅 Devocional para {data_ptbr}")
        st.info(f"📖 **{ref}**\n\n\"{ver}\"")
        st.success(f"💡 **Fortalecimento Espiritual:**\n\n{fort}")

        st.divider()
        st.subheader("✍️ Sua Reflexão Pessoal")

        cursor.execute(
            "SELECT reflexao FROM reflexoes WHERE usuario_email = ? AND data ="
            " ?",
            (st.session_state.usuario_email, data_str),
        )
        reflexao_salva = cursor.fetchone()
        texto_inicial = reflexao_salva[0] if reflexao_salva else ""

        nova_reflexao = st.text_area(
            "O que Deus falou ao seu coração hoje?",
            value=texto_inicial,
            height=150,
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Salvar Reflexão"):
                cursor.execute(
                    """
                    INSERT INTO reflexoes (usuario_email, data, reflexao)
                    VALUES (?, ?, ?)
                    ON CONFLICT(usuario_email, data) DO UPDATE SET reflexao = excluded.reflexao
                """,
                    (st.session_state.usuario_email, data_str, nova_reflexao),
                )
                conn.commit()
                st.success("Reflexão salva com sucesso!")

        # Botão de Impressão / PDF
        components.html(
            """
            <button onclick="window.parent.print()" style="
                background-color: #2E7D32;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;">
                🖨️ Imprimir / Salvar em PDF
            </button>
            """,
            height=60,
        )
        conn.close()

    # --- TELA 2: MEU DIÁRIO ---
    elif menu == "Meu Diário":
        st.title("📔 Meu Diário Espiritual")

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT data, reflexao FROM reflexoes 
            WHERE usuario_email = ? AND reflexao != '' 
            ORDER BY data DESC
        """,
            (st.session_state.usuario_email,),
        )
        historico = cursor.fetchall()
        conn.close()

        if historico:
            for item in historico:
                data_formatada = datetime.strptime(
                    item[0], "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
                with st.expander(f"📅 Registro de {data_formatada}"):
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

        # Cadastro de Usuários
        st.subheader("👥 Liberar Acesso a Novo Cliente")
        with st.form("form_novo_usuario", clear_on_submit=True):
            novo_email = st.text_input("E-mail do comprador:")
            nova_senha = st.text_input("Senha provisória:", type="password")
            btn_cadastrar = st.form_submit_button("Liberar Acesso")

            if btn_cadastrar:
                if novo_email and nova_senha:
                    sucesso, msg = criar_usuario(
                        novo_email, nova_senha, "usuario"
                    )
                    if sucesso:
                        st.success(msg)
                    else:
                        st.warning(msg)
                else:
                    st.error("Preencha todos os campos!")

        st.divider()

        # Cadastro Personalizado de Devocionais
        st.subheader("📖 Personalizar Devocional Específico")
        data_admin = st.date_input(
            "Selecione a Data:", datetime.today(), format="DD/MM/YYYY"
        )
        data_admin_str = data_admin.strftime("%Y-%m-%d")

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT referencia, versiculo, fortalecimento FROM devocionais"
            " WHERE data = ?",
            (data_admin_str,),
        )
        existente = cursor.fetchone()

        ref_val = existente[0] if existente else ""
        ver_val = existente[1] if existente else ""
        fort_val = existente[2] if existente else ""

        with st.form("form_devocional"):
            ref_input = st.text_input(
                "Referência Bíblica (ex: Salmos 23:1):", value=ref_val
            )
            ver_input = st.text_area(
                "Texto do Versículo:", value=ver_val, height=100
            )
            fort_input = st.text_area(
                "Mensagem de Fortalecimento:", value=fort_val, height=100
            )
            btn_salvar_dev = st.form_submit_button(
                "Salvar Devocional Personalizado"
            )

            if btn_salvar_dev:
                cursor.execute(
                    """
                    INSERT INTO devocionais (data, referencia, versiculo, fortalecimento)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(data) DO UPDATE SET
                        referencia = excluded.referencia,
                        versiculo = excluded.versiculo,
                        fortalecimento = excluded.fortalecimento
                """,
                    (data_admin_str, ref_input, ver_input, fort_input),
                )
                conn.commit()
                st.success("Devocional personalizado salvo com sucesso!")
        conn.close()

    else:
        st.warning("Selecione uma opção no menu lateral.")
