import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="centered"
)

# CSS Customizado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    .stTextArea textarea { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# BASE DE DADOS FIXA E PERMANENTE DE USUÁRIOS
# -------------------------------------------------------------------
usuarios_padrao = {
    "admin@vidanapalavra.com": {"senha": "admin", "role": "admin"},
    "anabiabarros6@gmail.com": {"senha": "CRISTO", "role": "user"},
    "hemmely01@gmail.com": {"senha": "MARIA", "role": "user"},
    "cristine_barros@hotmail.com": {"senha": "AMOR", "role": "user"},
    "flsp1986@hotmail.com": {"senha": "VET", "role": "admin"},
    "juarezpontesneto@gmail.com": {"senha": "MESSI", "role": "user"},
    "lulumaia06luana@gmail.com": {"senha": "EVANGELHO", "role": "user"},
    "lima.beneditalima@gmail.com": {"senha": "IGREJA", "role": "user"},
    "alcineide0172@gmail.com": {"senha": "DIACONISA", "role": "user"},
    "contato.drartursoares@gmail.com": {"senha": "COLUNA", "role": "user"},
    "carlos.colares@hotmail.com": {"senha": "CANINDE", "role": "user"},
    "lidiapcolares@hotmail.com": {"senha": "FORTAL", "role": "user"},
    "gorete.bbarros@gmail.com": {"senha": "NETO", "role": "user"},
    "concinhabc@gmail.com": {"senha": "BOLO", "role": "user"},
    "layanaperez@gmail.com": {"senha": "FRUTA", "role": "user"}
}

ARQUIVO_USUARIOS = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        try:
            with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                dados.update(usuarios_padrao)
                return dados
        except Exception:
            return usuarios_padrao.copy()
    return usuarios_padrao.copy()

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

# -------------------------------------------------------------------
# ACERVO ROTATIVO DINÂMICO DE DEVOCIONAIS
# -------------------------------------------------------------------
ACERVO_ROTATIVO = [
    {
        "titulo": "A Renovação Diária da Fé",
        "versiculo": "Lamentações 3:22-23",
        "texto": "As misericórdias do Senhor são a causa de não sermos consumidos; elas se renovam a cada manhã. Grande é a tua fidelidade.",
        "fortalecimento": "Deus renova as suas forças a cada amanhecer. Não carregue o peso de ontem no dia de hoje."
    },
    {
        "titulo": "O Senhor é o Meu Pastor",
        "versiculo": "Salmos 23:1",
        "texto": "O Senhor é o meu pastor; nada me faltará. Ele me faz repousar em verdes pastos e me guia a águas tranquilas.",
        "fortalecimento": "Ainda que o cenário pareça incerto, a provisão e o cuidado de Deus são garantidos para a sua vida."
    },
    {
        "titulo": "Coragem e Bom Ânimo",
        "versiculo": "Josué 1:9",
        "texto": "Não fui eu que lhe ordenei? Seja forte e corajoso! Não se apavore nem desanime, pois o Senhor, o seu Deus, estará com você por onde você andar.",
        "fortalecimento": "A presença divina vai adiante dos seus passos. Avance com confiança!"
    },
    {
        "titulo": "Paz Que Excede todo o Entendimento",
        "versiculo": "Filipenses 4:6-7",
        "texto": "Não andem ansiosos por coisa alguma, mas em tudo, pela oração e suplicação, com ação de graças, apresentem seus pedidos a Deus.",
        "fortalecimento": "Entregue suas preocupações no altar através da oração e descanse no cuidado do Pai."
    },
    {
        "titulo": "Luz Para o Meu Caminho",
        "versiculo": "Salmos 119:105",
        "texto": "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho.",
        "fortalecimento": "Quando a Palavra de Deus guia seus passos, você nunca caminhará na escuridão."
    }
]

def obter_devocional_do_dia(data):
    # Seleciona a mensagem com base no dia do ano para variar diariamente
    indice = data.timetuple().tm_yday % len(ACERVO_ROTATIVO)
    return ACERVO_ROTATIVO[indice]

# -------------------------------------------------------------------
# SISTEMA DE SESSÃO
# -------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "user"
if "data_selecionada" not in st.session_state:
    st.session_state.data_selecionada = datetime.now()
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []
if "comentarios" not in st.session_state:
    st.session_state.comentarios = {}

# -------------------------------------------------------------------
# TELA DE LOGIN
# -------------------------------------------------------------------
if not st.session_state.logged_in:
    st.title("📖 Vida Na Palavra")
    st.subheader("Acesse seu Devocional Diário")

    with st.form("form_login"):
        email = st.text_input("E-mail:").strip().lower()
        senha = st.text_input("Senha:", type="password").strip()
        btn_entrar = st.form_submit_button("Entrar")

        if btn_entrar:
            usuarios = carregar_usuarios()
            if email in usuarios and usuarios[email]["senha"] == senha:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_role = usuarios[email].get("role", "user")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

else:
    # -------------------------------------------------------------------
    # ÁREA LOGADA
    # -------------------------------------------------------------------
    st.sidebar.title("📖 Vida Na Palavra")
    st.sidebar.write(f"Usuário: **{st.session_state.user_email}**")
    
    if st.sidebar.button("Sair / Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.divider()
    
    menu = ["Devocional Diário", "Meus Favoritos"]
    if st.session_state.user_role == "admin":
        menu.append("Painel Admin")
    
    opcao = st.sidebar.radio("Navegação", menu)

    # ABA 1: DEVOCIONAL DIÁRIO
    if opcao == "Devocional Diário":
        st.title("📖 Devocional Diário")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Dia Anterior"):
                st.session_state.data_selecionada -= timedelta(days=1)
                st.rerun()
        
        with col2:
            data_formatada = st.session_state.data_selecionada.strftime("%d/%m/%Y")
            st.markdown(f"<h3 style='text-align: center;'>{data_formatada}</h3>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Próximo Dia ➡️"):
                st.session_state.data_selecionada += timedelta(days=1)
                st.rerun()

        st.divider()

        # Busca o devocional variado da data selecionada
        devocional_hoje = obter_devocional_do_dia(st.session_state.data_selecionada)

        st.header(devocional_hoje["titulo"])
        st.subheader(f"📖 {devocional_hoje['versiculo']}")
        st.write(devocional_hoje["texto"])

        st.markdown("---")
        
        # BLANCO DE FORTALECIMENTO / EXPERIÊNCIA ESPIRITUAL
        st.subheader("💡 Fortalecimento Espiritual do Dia")
        st.info(devocional_hoje["fortalecimento"])

        st.markdown("---")

        # CAIXA DE COMENTÁRIOS E REFLEXÃO DO USUÁRIO
        st.subheader("✍️ Minhas Anotações e Reflexão Pessoal")
        chave_comentario = f"{st.session_state.user_email}_{data_formatada}"
        
        comentario_salvo = st.session_state.comentarios.get(chave_comentario, "")
        novo_comentario = st.text_area(
            "Escreva o que Deus falou ao seu coração hoje:", 
            value=comentario_salvo, 
            height=120,
            placeholder="Digite aqui sua oração, insight ou reflexão espiritual..."
        )

        if st.button("Salvar Anotação"):
            st.session_state.comentarios[chave_comentario] = novo_comentario
            st.success("Reflexão salva com sucesso!")

        st.divider()

        # FAVORITAR
        item_fav = f"{data_formatada} - {devocional_hoje['titulo']} ({devocional_hoje['versiculo']})"
        if item_fav in st.session_state.favoritos:
            st.info("⭐ Este devocional está salvo nos seus favoritos.")
        else:
            if st.button("⭐ Favoritar este Devocional"):
                st.session_state.favoritos.append(item_fav)
                st.success("Salvo nos favoritos!")
                st.rerun()

    # ABA 2: MEUS FAVORITOS
    elif opcao == "Meus Favoritos":
        st.title("⭐ Meus Favoritos")
        if not st.session_state.favoritos:
            st.info("Você ainda não salvou nenhum devocional nos favoritos.")
        else:
            for idx, fav in enumerate(st.session_state.favoritos):
                st.write(f"**{idx + 1}.** {fav}")

    # ABA 3: PAINEL ADMIN
    elif opcao == "Painel Admin" and st.session_state.user_role == "admin":
        st.title("⚙️ Painel do Administrador")
        st.subheader("Cadastrar Novo Usuário Temporário")

        with st.form("form_novo_user"):
            novo_email = st.text_input("E-mail do Usuário:").strip().lower()
            nova_senha = st.text_input("Senha de Acesso:").strip()
            role = st.selectbox("Perfil:", ["user", "admin"])
            btn_cadastrar = st.form_submit_button("Cadastrar Usuário")

            if btn_cadastrar:
                if novo_email and nova_senha:
                    usuarios = carregar_usuarios()
                    usuarios[novo_email] = {"senha": nova_senha, "role": role}
                    salvar_usuarios(usuarios)
                    st.success(f"Usuário {novo_email} cadastrado com sucesso!")
                else:
                    st.warning("Preencha todos os campos.")
