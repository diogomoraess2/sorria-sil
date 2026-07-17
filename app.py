import streamlit as st  
import pandas as pd  
from datetime import datetime  
from google.oauth2.service_account import Credentials
import gspread

# Configuração da página
st.set_page_config(page_title="Controle Financeiro - Sorria Sil", layout="wide", initial_sidebar_state="collapsed")  

# Estilização CSS
st.markdown("""  
    <style>  
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid #007bff; text-align: center; margin-bottom: 10px; }  
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; text-transform: uppercase; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }  
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; color: #ffffff; }  
    </style>  
""", unsafe_allow_html=True)  

# --- CONEXÃO ---
# (Manter sua classe e try/except de conexão aqui)

MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}  

# --- INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month
if 'editando_mes' not in st.session_state: st.session_state['editando_mes'] = False

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)

# Título do Mês separado e Neon
st.markdown("### Mês:")
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)
st.write("") 

# --- LÓGICA DE SELEÇÃO SEM TECLADO ACIDENTAL ---
if not st.session_state['editando_mes']:
    if st.button("Trocar Mês"):
        st.session_state['editando_mes'] = True
        st.rerun()
else:
    novo_mes = st.selectbox(
        "Selecione o mês:", 
        options=list(MESES_PT.keys()), 
        format_func=lambda x: MESES_PT[x],
        index=st.session_state['mes_atual_num'] - 1
    )
    col_a, col_b = st.columns(2)
    if col_a.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.session_state['editando_mes'] = False
        st.rerun()
    if col_b.button("Cancelar"):
        st.session_state['editando_mes'] = False
        st.rerun()

# --- CÁLCULO E DEMAIS COMPONENTES ---
# (Continue com a sua lógica de carregar_dados_mes, colunas e tabs abaixo)