# --- 1. AJUSTES DE CSS PARA O BOTÃO INVISÍVEL E EFEITO NEON ---
st.markdown("""
    <style>
    /* Transforma o botão do Streamlit em um elemento invisível */
    div[data-testid="stButton"] button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-block !important;
    }
    .container-titulo { display: flex; flex-direction: column; margin-bottom: 15px; }
    .linha-superior { display: flex; align-items: baseline; }
    .titulo-principal { font-size: 42px; font-weight: bold; margin: 0; }
    .emoji-dente { font-size: 2.5em; margin-left: -8px; margin-right: 10px; line-height: 1; }
    .linha-mes { font-size: 1.2em; font-weight: 300; color: #ffffff; margin-top: 5px; }
    .mes-neon { font-weight: 500; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; }
    
    @media (max-width: 600px) {
        .linha-superior { font-size: 5.6vw; }
        .emoji-dente { font-size: 2.2em; margin-left: -5px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE ESTADO PARA O MÊS ---
if 'mes_atual_num' not in st.session_state:
    st.session_state['mes_atual_num'] = datetime.today().month

# --- 3. RENDERIZAÇÃO DO TÍTULO ---
st.markdown(f"""
    <div class="container-titulo">
        <div class="linha-superior">
            <span class="emoji-dente">🦷</span>
            <h1 class="titulo-principal">Sorria Sil</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. SELETOR DISPARADO PELO TEXTO NEON ---
# O botão invisível que exibe seu texto com brilho
with st.container():
    nome_aba_trabalho = MESES_PT[st.session_state['mes_atual_num']]
    
    # Botão que, ao ser clicado, abre o popover
    if st.button(f"Mês: <span class='mes-neon'>{nome_aba_trabalho}</span>", type="primary"):
        pass # O botão serve apenas como âncora
    
    # O Popover contendo o seletor de mês
    with st.popover("Trocar Mês", use_container_width=True):
        novo_mes_num = st.selectbox("Selecione o mês:", list(MESES_PT.keys()), 
                                     format_func=lambda x: MESES_PT[x],
                                     index=st.session_state['mes_atual_num'] - 1)
        if st.button("Confirmar Alteração"):
            st.session_state['mes_atual_num'] = novo_mes_num
            st.rerun()

# Atualiza a variável para o resto do seu código
nome_aba_trabalho = MESES_PT[st.session_state['mes_atual_num']]