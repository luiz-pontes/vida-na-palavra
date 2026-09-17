import streamlit as st
import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide"
)

# --- CONEXÃO SUPABASE ---
supabase: Client = None
try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    pass

# --- ESTADO DA SESSÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = "flsp1986@hotmail.com"

if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []

if "anotacoes" not in st.session_state:
    st.session_state["anotacoes"] = {}

# Controle dinâmico da data selecionada
if "data_selecionada" not in st.session_state:
    st.session_state["data_selecionada"] = datetime.date.today()

user_email = st.session_state["usuario_logado"]

# --- BARRA LATERAL ---
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

# --- ROTA 1: DEVOCIONAL DIÁRIO ---
if menu == "Devocional Diário":
    st.title("📖 Devocional Diário")
    
    # Navegação Dinâmica de Datas
    col_anterior, col_data, col_proximo = st.columns([1, 2, 1])
    
    with col_anterior:
        if st.button("⬅️ Dia Anterior"):
            st.session_state["data_selecionada"] -= datetime.timedelta(days=1)
            st.rerun()
            
    with col_data:
        # Seletor interativo de data
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

    st.markdown("---")
    
    st.header("A Renovação Diária da Fé")
    st.subheader("📖 Lamentações 3:22-23")
    st.write("As misericórdias do Senhor são a causa de não sermos consumidos; elas se renovam a cada manhã. Grande é a tua fidelidade.")

    # CONSULTA FAVORITO
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
    st.info("Deus renova as suas forças a cada amanhecer. Não carregue o peso de ontem no dia de hoje.")

    st.markdown("---")
    st.subheader("📝 Minhas Anotações e Reflexão Pessoal")
    
    # CONSULTA ANOTAÇÃO POR DATA
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


# --- ROTA 2: MEUS FAVORITOS E REFLEXÕES ---
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
                st.success(f"⭐ {item} - A Renovação Diária da Fé")
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
            texto_para_download = "=== MINHAS REFLEXÕES - DEVOCIONAL VIDA NA PALAVRA ===\n\n"
            
            for dev_id, texto_item in notas_dict.items():
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
