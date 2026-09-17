import streamlit as st
import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide"
)

# --- CONFIGURAÇÃO E CONEXÃO SUPABASE ---
# O Streamlit busca as chaves cadastradas nos Secrets ou você pode colar diretamente abaixo
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "SUA_URL_SUPABASE_AQUI")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "SUA_CHAVE_SUPABASE_AQUI")

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = get_supabase_client()
except Exception as e:
    st.error("Erro ao conectar ao Supabase. Verifique suas credenciais de acesso.")

# --- INICIALIZAÇÃO DE SESSÃO LOCAL ---
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = "flsp1986@hotmail.com"

user_email = st.session_state["usuario_logado"]

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("📖 Vida Na Palavra")
st.sidebar.text(f"Usuário: {user_email}")

if st.sidebar.button("Sair / Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Navegação")

menu = st.sidebar.radio(
    "Seleção de Tela",
    ["Devocional Diário", "Meus Favoritos", "Painel Admin"],
    label_visibility="collapsed"
)

data_hoje = datetime.date.today().strftime("%d/%m/%Y")
devocional_id = f"Devocional_{data_hoje}"


# --- ROTA 1: DEVOCIONAL DIÁRIO ---
if menu == "Devocional Diário":
    st.title("📖 Devocional Diário")
    
    # Navegação de Datas
    col_anterior, col_data, col_proximo = st.columns([1, 2, 1])
    with col_anterior:
        st.button("⬅️ Dia Anterior")
    with col_data:
        st.markdown(f"<h3 style='text-align: center;'>{data_hoje}</h3>", unsafe_allow_html=True)
    with col_proximo:
        st.button("Próximo Dia ➡️")

    st.markdown("---")
    
    st.header("A Renovação Diária da Fé")
    st.subheader("📖 Lamentações 3:22-23")
    st.write("As misericórdias do Senhor são a causa de não sermos consumidos; elas se renovam a cada manhã. Grande é a tua fidelidade.")

    # CONSULTA FAVORITOS NO SUPABASE
    res_fav = supabase.table("favoritos").select("*").eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
    e_favorito = len(res_fav.data) > 0
    
    btn_fav_text = "⭐ Removido dos Favoritos" if e_favorito else "⭐ Adicionar aos Favoritos"
    if st.button(btn_fav_text):
        if e_favorito:
            supabase.table("favoritos").delete().eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
            st.success("Removido dos favoritos no banco de dados!")
        else:
            supabase.table("favoritos").insert({"user_email": user_email, "devocional_id": devocional_id}).execute()
            st.success("Guardado nos favoritos no Supabase!")
        st.rerun()

    st.markdown("---")
    st.subheader("💡 Fortalecimento Espiritual do Dia")
    st.info("Deus renova as suas forças a cada amanhecer. Não carregue o peso de ontem no dia de hoje.")

    st.markdown("---")
    st.subheader("📝 Minhas Anotações e Reflexão Pessoal")
    
    # BUSCA ANOTAÇÃO EXISTENTE NO SUPABASE
    res_nota = supabase.table("anotacoes").select("anotacao").eq("user_email", user_email).eq("devocional_id", devocional_id).execute()
    nota_existente = res_nota.data[0]["anotacao"] if res_nota.data else ""
    
    texto_reflexao = st.text_area(
        "Escreva o que Deus falou ao seu coração hoje:",
        value=nota_existente,
        placeholder="Digite aqui sua oração, insight ou reflexão espiritual...",
        height=150
    )
    
    if st.button("💾 Salvar Anotação no Supabase"):
        if texto_reflexao.strip():
            # Grava ou Atualiza no Supabase (Upsert)
            dados_payload = {
                "user_email": user_email,
                "devocional_id": devocional_id,
                "anotacao": texto_reflexao
            }
            supabase.table("anotacoes").upsert(dados_payload).execute()
            st.success("Sua reflexão foi gravada com segurança no banco de dados!")
        else:
            st.warning("Escreva uma reflexão antes de salvar.")


# --- ROTA 2: MEUS FAVORITOS E REFLEXÕES (IMPRESSÃO) ---
elif menu == "Meus Favoritos":
    st.title("⭐ Meus Favoritos e Minhas Reflexões")
    
    tab_fav, tab_notas = st.tabs(["📌 Devocionais Favoritos", "📝 Minhas Anotações e Reflexões"])
    
    # --- ABA 1: FAVORITOS SALVOS NO SUPABASE ---
    with tab_fav:
        res_favs = supabase.table("favoritos").select("*").eq("user_email", user_email).execute()
        if res_favs.data:
            st.subheader("Seus Devocionais Guardados:")
            for item in res_favs.data:
                st.success(f"⭐ {item['devocional_id']} - Guardado em sua lista pessoal.")
        else:
            st.info("Você não possui devocionais favoritados no momento.")

    # --- ABA 2: ANOTAÇÕES / REFLEXÕES PARA IMPRIMIR ---
    with tab_notas:
        res_notas = supabase.table("anotacoes").select("*").eq("user_email", user_email).execute()
        
        if res_notas.data:
            st.subheader("Histórico de Reflexões Salvas no Supabase:")
            
            texto_para_download = "=== MINHAS REFLEXÕES - DEVOCIONAL VIDA NA PALAVRA ===\n\n"
            
            for item in res_notas.data:
                dev_id = item.get("devocional_id", "Devocional")
                texto_item = item.get("anotacao", "")
                
                if texto_item.strip():
                    st.markdown(f"**Data / Registro:** `{dev_id}`")
                    st.info(texto_item)
                    texto_para_download += f"Registro: {dev_id}\nReflexão: {texto_item}\n" + "-"*50 + "\n\n"
            
            st.markdown("---")
            st.download_button(
                label="🖨️ Baixar / Imprimir Todas as Minhas Anotações (TXT)",
                data=texto_para_download,
                file_name=f"Reflexoes_Devocional_{user_email}.txt",
                mime="text/plain"
            )
        else:
            st.warning("Nenhuma anotação foi encontrada na sua conta.")


# --- ROTA 3: PAINEL ADMIN ---
elif menu == "Painel Admin":
    st.title("⚙️ Painel de Administração")
    st.write("Módulo de controle do sistema.")
