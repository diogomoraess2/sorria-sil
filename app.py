# --- 1. CONFIGURAÇÃO DO SELETOR E TÍTULO ---
if 'mes_atual_num' not in st.session_state:
    st.session_state['mes_atual_num'] = datetime.today().month

# --- 2. CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        display: inline-block !important;
    }
    .container-titulo { display: flex; flex-direction: column; margin-bottom: 15px; }
    .linha-superior { display: flex; align-items: baseline; }
    .titulo-principal { font-size: 42px; font-weight: bold; margin: 0; }
    .emoji-dente { font-size: 2.5em; margin-left: -8px; margin-right: 10px; line-height: 1; }
    .mes-neon { 
        font-weight: 500; 
        font-size: 1.2em; 
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDERIZAÇÃO ---
st.markdown("""
    <div class="container-titulo">
        <div class="linha-superior">
            <span class="emoji-dente">🦷</span>
            <h1 class="titulo-principal">Sorria Sil</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. BOTÃO/POPOVER ---
nome_aba_trabalho = MESES_PT[st.session_state['mes_atual_num']]
if st.button(f"Mês: <span class='mes-neon'>{nome_aba_trabalho}</span>", key="btn_mes"):
    pass

with st.popover("Trocar Mês", use_container_width=False):
    novo_mes_num = st.selectbox("Selecione o mês:", list(MESES_PT.keys()), 
                                 format_func=lambda x: MESES_PT[x],
                                 index=st.session_state['mes_atual_num'] - 1)
    if st.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes_num
        st.rerun()

# Atualiza a variável para o resto do app
nome_aba_trabalho = MESES_PT[st.session_state['mes_atual_num']]