import streamlit as st  
import pandas as pd  
from datetime import datetime  
import plotly.express as px  
from google.oauth2.service_account import Credentials
import gspread

# Configuração da página
st.set_page_config(page_title="Controle Financeiro - Sorria Sil", page_icon="🦷", layout="wide")

# Estilização CSS atualizada
st.markdown("""  
    <style>  
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid #007bff; text-align: center; margin-bottom: 10px; }  
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; text-transform: uppercase; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }  
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; color: #ffffff; }  
    </style>  
""", unsafe_allow_html=True)  

# --- [MANTENHA A SUA LÓGICA DE CONEXÃO E CARREGAMENTO AQUI] ---

# --- INTERFACE CORRIGIDA ---
st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)

# Mês separado e Neon
st.write("### Mês:")
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)
st.write("") # Espaçamento extra

# Popover de seleção (simplificado)
with st.popover("Trocar Mês"):
    novo_mes = st.selectbox("Escolha:", list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x])
    if st.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.rerun()

df_mes = carregar_dados_mes(nome_aba)

# CORREÇÃO DO CÁLCULO (Evitar valores astronômicos)
if not df_mes.empty:
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            # Converte para string, remove R$, pontos de milhar, substitui vírgula por ponto
            limpo = df_mes[col].replace(r'[R$\s]', '', regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_mes[col] = pd.to_numeric(limpo, errors='coerce').fillna(0)
    
    totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum()
else:
    totais = pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# --- [RESTANTE DO SEU CÓDIGO DE EXIBIÇÃO (Colunas e Tabs)] ---