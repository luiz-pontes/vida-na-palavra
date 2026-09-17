import streamlit as st
import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide"
)

# --- BASE DE DADOS DOS DEVOCIONAIS (DINÂMICA POR DATA) ---
DEVOCIONAIS_BD = {
    "17/09/2026": {
        "titulo": "A Renovação Diária da Fé",
        "versiculo": "Lamentações 3:22-23",
        "texto": "As misericórdias do Senhor são a causa de não sermos consumidos; elas se renovam a cada manhã. Grande é a tua fidelidade.",
        "fortalecimento": "Deus renova as suas forças a cada amanhecer. Não carregue o peso de ontem no dia de hoje."
    },
    "18/09/2026": {
        "titulo": "O Poder da Oração Persistente",
        "versiculo": "Filipenses 4:6-7",
        "texto": "Não andeis ansiosos por coisa alguma; antes, as vossas petições sejam em tudo conhecidas diante de Deus, pela oração e súplicas, com ação de graças.",
        "fortalecimento": "A paz de Deus, que excede todo o entendimento, guardará o seu coração no dia de hoje."
    },
    "16/09/2026": {
        "titulo": "A Força na Fraqueza",
        "versiculo": "2 Coríntios 12:9",
        "texto": "A minha graça te basta, porque o meu poder se aperfeiçoa na fraqueza.",
        "fortalecimento": "Quando você se sente fraco, é aí que a força de Cristo se manifesta em sua vida."
    }
}

# --- CONEXÃO SUPABASE ---
supabase: Client = None
try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    pass

# --- GERENCIAMENTO DE AUTENTICAÇÃO E LOGOUT ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = True

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = "flsp1986@hotmail.com"

# TELA DE LOGOUT / LOGIN
if not st.session_state["autenticado"]:
    st.title("📖 Vida Na Palavra")
    st.subheader("Login de Acesso")
    email_input = st.text_input("E-mail:")
    senha_input = st.text_input("Senha:", type="password")
    
    if st.button("Entrar"):
        if email_input:
            st.session_state["autenticado"] = True
            st.session_state["usuario_logado"] = email_input
            st.rerun()
        else:
            st.error("Informe seu e-mail.")
    st.stop() # INTERROMPE O APP AQUI SE NÃO ESTIVER LOGADO

# --- INICIALIZAÇÃO DE ESTADOS ---
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []

if "anotacoes" not in st.session_state:
    st.session_state["anotacoes"] = {}

if "data_selecionada" not in st.session_state:
    st.session_state["data_selecionada"] = datetime.date.today()

user_email = st.session_state["usuario_logado"]

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("📖 Vida Na Palavra")
st.sidebar.text(f"Usuário: {user_email}")

# CORREÇÃO DO BOTÃO DE LOGOUT
if st.sidebar.button("Sair / Logout"):
    st.session_state["autenticado"] = False
    st.session_state["usuario_logado"] = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Navegação")

menu = st.sidebar.radio(
    "Seleção de Tela",
    ["Devocional Diário", "Meus Favoritos", "Painel Admin"],
    label_visibility="collapsed"
)

# --- ROTA 1: DEVOCIONAL DIÁRIO ---
if menu == "Devocional Diário":
    st.title("📖 Devocional Diário")
    
    # NAVEGAÇÃO DE DATAS
    col_anterior, col_data, col_proximo = st.columns([1, 2, 1])
    
    with col_anterior:
        if st.button("⬅️ Dia Anterior"):
            st.session_state["data_selecionada"] -= datetime.timedelta(days=1)
            st.rerun()
            
    with col_data:
        nova_data = st.date_input(
            "Data do Devocional",
            value=st.session_state["data_selecionada"],
            format="DD/MM/YYYY",
            label_visibility="collapsed"
        )
        if nova_data != st.session_state["data_selecionada"]:
            st.session_state["data_selecionada"] = nova_data
            st.rerun()
            
    with col_proximo:
        if st.button("Próximo Dia ➡️"):
            st.session_state["data_selecionada"] += datetime.timedelta(days=1)
            st.rerun()

    data_formatada = st.session_state["data_selecionada"].strftime("%d/%m/%Y")
    devocional_id = f"Devocional_{data_formatada}"

    # CARREGA CONTEÚDO DINÂMICO
    conteudo = DEVOCIONAIS_BD.get(data_formatada, {
        "titulo": "Meditação na Palavra",
        "versiculo": "Salmos 119:105",
        "texto": "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho.",
        "fortalecimento": "A Palavra de Deus é o alicerce seguro para todas as suas decisões de hoje."
    })

    st.markdown("---")
    st.header(conteudo["titulo"])
    st.subheader(f"📖 {conteudo['versiculo']}")
    st.write(conteudo["texto"])

    # CONSULTA FAVORITO NO SUPABASE/SESSÃO
    e_favorito = devocional_id in st.session_state["favoritos"]
    if supabase:
        try:
            res_fav = supabase.table("favoritos").select("*").eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
            if res_fav.data:
                e_favorito = True
        except Exception:
            pass
    
    btn_fav_text = "⭐ Removido dos Favoritos" if e_favorito else "⭐ Adicionar aos Favoritos"
    if st.button(btn_fav_text):
        if e_favorito:
            if devocional_id in st.session_state["favoritos"]:
                st.session_state["favoritos"].remove(devocional_id)
            if supabase:
                try:
                    supabase.table("favoritos").delete().eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
                except Exception:
                    pass
            st.success("Removido dos favoritos!")
        else:
            st.session_state["favoritos"].append(devocional_id)
            if supabase:
                try:
                    supabase.table("favoritos").insert({"user_email": user_email, "devocional_id": devocional_id}).execute()
                except Exception:
                    pass
            st.success("Adicionado aos favoritos!")
        st.rerun()

    st.markdown("---")
    st.subheader("💡 Fortalecimento Espiritual do Dia")
    st.info(conteudo["fortalecimento"])

    st.markdown("---")
    st.subheader("📝 Minhas Anotações e Reflexão Pessoal")
    
    nota_existente = st.session_state["anotacoes"].get(devocional_id, "")
    if supabase:
        try:
            res_nota = supabase.table("anotacoes").select("anotacao").eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
            if res_nota.data:
                nota_existente = res_nota.data[0]["anotacao"]
        except Exception:
            pass
    
    texto_reflexao = st.text_area(
        f"Escreva o que Deus falou ao seu coração em {data_formatada}:",
        value=nota_existente,
        placeholder="Digite aqui sua oração, insight ou reflexão espiritual...",
        height=150,
        key=f"text_{devocional_id}"
    )
    
    if st.button("💾 Salvar Anotação"):
        if texto_reflexao.strip():
            st.session_state["anotacoes"][devocional_id] = texto_reflexao
            if supabase:
                try:
                    dados_payload = {
                        "user_email": user_email,
                        "devocional_id": devocional_id,
                        "anotacao": texto_reflexao
                    }
                    supabase.table("anotacoes").upsert(dados_payload).execute()
                except Exception:
                    pass
            st.success("Sua reflexão foi gravada com sucesso! Acesse 'Meus Favoritos' para visualizar ou imprimir.")
        else:
            st.warning("Escreva uma reflexão antes de salvar.")


# --- ROTA 2: MEUS FAVORITOS E REFLEXÕES (EXPORTAÇÃO ELEGANTE) ---
elif menu == "Meus Favoritos":
    st.title("⭐ Meus Favoritos e Minhas Reflexões")
    
    tab_fav, tab_notas = st.tabs(["📌 Devocionais Favoritos", "📝 Minhas Anotações e Reflexões"])
    
    with tab_fav:
        favs = list(st.session_state["favoritos"])
        if supabase:
            try:
                res_favs = supabase.table("favoritos").select("*").eq("user_email", user_email).execute()
                if res_favs.data:
                    favs = [item['devocional_id'] for item in res_favs.data]
            except Exception:
                pass
                
        if favs:
            st.subheader("Seus Devocionais Guardados:")
            for item in set(favs):
                st.success(f"⭐ {item}")
        else:
            st.info("Você não possui devocionais favoritados no momento.")

    with tab_notas:
        notas_dict = dict(st.session_state["anotacoes"])
        if supabase:
            try:
                res_notas = supabase.table("anotacoes").select("*").eq("user_email", user_email).execute()
                if res_notas.data:
                    for item in res_notas.data:
                        notas_dict[item.get("devocional_id", "Devocional")] = item.get("anotacao", "")
            except Exception:
                pass
        
        if notas_dict and any(t.strip() for t in notas_dict.values()):
            st.subheader("Histórico de Reflexões Salvas:")
            
            html_impressao = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Caderno de Reflexões - Vida Na Palavra</title>
                <style>
                    body {{ font-family: 'Georgia', serif; margin: 40px; color: #2c3e50; line-height: 1.6; }}
                    .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 15px; margin-bottom: 30px; }}
                    .card {{ background: #fdfdfd; border-left: 4px solid #3498db; padding: 15px 20px; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                    .card-title {{ font-weight: bold; font-size: 16px; color: #2980b9; margin-bottom: 8px; }}
                    .card-body {{ font-size: 15px; white-space: pre-wrap; color: #34495e; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📖 Caderno de Anotações e Reflexões Pessoais</h1>
                    <p>Aplicativo Vida Na Palavra | Usuário: {user_email}</p>
                </div>
            """
            
            for dev_id, texto_item in notas_dict.items():
                if texto_item.strip():
                    st.markdown(f"**Data / Registro:** `{dev_id}`")
                    st.info(texto_item)
                    html_impressao += f"""
                    <div class="card">
                        <div class="card-title">📌 Registro: {dev_id.replace('_', ' ')}</div>
                        <div class="card-body">{texto_item}</div>
                    </div>
                    """
            
            html_impressao += "</body></html>"
            
            st.markdown("---")
            st.download_button(
                label="📄 Baixar Documento Formatado para Impressão",
                data=html_impressao,
                file_name=f"Reflexoes_Elegantes_{user_email}.html",
                mime="text/html"
            )
        else:
            st.warning("Nenhuma anotação foi encontrada na sua conta.")


# --- ROTA 3: PAINEL ADMIN ---
elif menu == "Painel Admin":
    st.title("⚙️ Painel de Administração")
    st.write("Módulo de controle do sistema.")
