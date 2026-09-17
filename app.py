import streamlit as st
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Vida Na Palavra",
    page_icon="📖",
    layout="wide"
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []

if "anotacoes" not in st.session_state:
    st.session_state["anotacoes"] = {}

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = "flsp1986@hotmail.com"

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("📖 Vida Na Palavra")
st.sidebar.text(f"Usuário: {st.session_state['usuario_logado']}")

if st.sidebar.button("Sair / Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Navegação")

# Menu de navegação por rádio
menu = st.sidebar.radio(
    "Seleção de Tela",
    ["Devocional Diário", "Meus Favoritos", "Painel Admin"],
    label_visibility="collapsed"
)

# DATA ATUAL DO DEVOCIONAL
data_hoje = datetime.date.today().strftime("%d/%m/%Y")


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
    
    # Conteúdo do Devocional
    st.header("A Renovação Diária da Fé")
    st.subheader("📖 Lamentações 3:22-23")
    st.write("As misericórdias do Senhor são a causa de não sermos consumidos; elas se renovam a cada manhã. Grande é a tua fidelidade.")

    # Controle de Favoritos
    devocional_id = f"Devocional_{data_hoje}"
    e_favorito = devocional_id in st.session_state["favoritos"]
    
    btn_fav_text = "⭐ Removido dos Favoritos" if e_favorito else "⭐ Adicionar aos Favoritos"
    if st.button(btn_fav_text):
        if e_favorito:
            st.session_state["favoritos"].remove(devocional_id)
            st.success("Removido dos favoritos!")
        else:
            st.session_state["favoritos"].append(devocional_id)
            st.success("Adicionado aos favoritos!")
        st.rerun()

    st.markdown("---")
    st.subheader("💡 Fortalecimento Espiritual do Dia")
    st.info("Deus renova as suas forças a cada amanhecer. Não carregue o peso de ontem no dia de hoje.")

    st.markdown("---")
    st.subheader("📝 Minhas Anotações e Reflexão Pessoal")
    
    # Recupera nota existente, se houver
    nota_salva = st.session_state["anotacoes"].get(devocional_id, "")
    
    texto_reflexao = st.text_area(
        "Escreva o que Deus falou ao seu coração hoje:",
        value=nota_salva,
        placeholder="Digite aqui sua oração, insight ou reflexão espiritual...",
        height=150
    )
    
    if st.button("💾 Salvar Anotação"):
        if texto_reflexao.strip():
            st.session_state["anotacoes"][devocional_id] = texto_reflexao
            st.success("Anotação salva com sucesso! Acesse 'Meus Favoritos' no menu para visualizar ou imprimir.")
        else:
            st.warning("Escreva algo antes de salvar.")


# --- ROTA 2: MEUS FAVORITOS E REFLEXÕES (TELA DE IMPRESSÃO) ---
elif menu == "Meus Favoritos":
    st.title("⭐ Meus Favoritos e Minhas Reflexões")
    
    # Criação das duas abas organizadas na tela central
    tab_fav, tab_notas = st.tabs(["📌 Devocionais Favoritos", "📝 Minhas Anotações e Reflexões"])
    
    # --- ABA 1: DEVOCIONAIS FAVORITOS ---
    with tab_fav:
        if st.session_state["favoritos"]:
            st.subheader("Devocionais Marcados como Favoritos:")
            for item in st.session_state["favoritos"]:
                st.success(f"⭐ {item} - A Renovação Diária da Fé (Lamentações 3:22-23)")
        else:
            st.info("Você ainda não favoritou nenhum devocional.")

    # --- ABA 2: MINHAS ANOTAÇÕES E REFLEXÕES ---
    with tab_notas:
        if st.session_state["anotacoes"] and any(t.strip() for t in st.session_state["anotacoes"].values()):
            st.subheader("Histórico de Reflexões Salvas:")
            
            texto_para_download = "=== MINHAS REFLEXÕES - DEVOCIONAL VIDA NA PALAVRA ===\n\n"
            
            # Percorre e exibe cada nota salva
            for id_dev, texto in st.session_state["anotacoes"].items():
                if texto.strip():
                    st.markdown(f"**Data / Devocional:** `{id_dev}`")
                    st.info(texto)
                    texto_para_download += f"Devocional: {id_dev}\nReflexão: {texto}\n" + "-"*50 + "\n\n"
            
            st.markdown("---")
            # Botão de Download para Impressão
            st.download_button(
                label="🖨️ Baixar / Imprimir Todas as Minhas Anotações (TXT)",
                data=texto_para_download,
                file_name="Minhas_Reflexoes_Vida_Na_Palavra.txt",
                mime="text/plain"
            )
        else:
            st.warning("Você ainda não salvou nenhuma anotação ou reflexão pessoal.")


# --- ROTA 3: PAINEL ADMIN ---
elif menu == "Painel Admin":
    st.title("⚙️ Painel de Administração")
    st.write("Gerenciamento de conteúdos e usuários do aplicativo.")
