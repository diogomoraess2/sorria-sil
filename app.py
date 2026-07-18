import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import base64

# --- CONFIGURAÇÃO PWA ---
manifest_json = """
{
  "name": "DentBoard",
  "short_name": "DentBoard",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4a90e2",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/icon.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""
b64_manifest = base64.b64encode(manifest_json.encode()).decode()

st.set_page_config(
    page_title="Controle Financeiro - DentBoard",
    page_icon="https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/icon.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS REVISADO (FOCO EM PRESERVAR CARDS E ESTILIZAR INPUTS) ---
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/quadro-verde.jpg');
        background-size: cover;
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"], footer, #MainMenu, .stAppDeployButton, .viewerBadge_container__1QSob {
        display: none !important;
    }
    
    /* DEFINIÇÃO DO CARD (garantindo visibilidade) */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.9) !important; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        text-align: center; 
        border-left: 6px solid #4a90e2;
        margin-bottom: 10px;
    }
    
    /* INPUTS (Fundo branco, borda suave) */
    div[data-baseweb="base-input"], div[data-baseweb="input"], input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #c8e6c9 !important;
        border-radius: 8px !important;
    }
    
    /* REMOVE BOTÕES +/- */
    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none !important;
        margin: 0 !important;
    }
    
    /* BOTÃO SALVAR SUAVE */
    div.stButton > button {
        background-color: #a8e0a8 !important; 
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO ---
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown('<h1 style="text-align: center;"><span style="color: #4a90e2;">Dent</span><span style="color: #f5a623;">Board</span></h1>', unsafe_allow_html=True)
st.session_state['mes_atual_num'] = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num']-1)

# --- LÓGICA DOS CARDS ---
cols = st.columns(5)
metricas = [("Total", "R$ 0,00"), ("Dinheiro", "R$ 0,00"), ("Pix", "R$ 0,00"), ("A Receber", "R$ 0,00"), ("Uber", "R$ 0,00")]

for i, (titulo, valor) in enumerate(metricas):
    with cols[i]:
        st.markdown(f'''<div class="metric-card">
            <div style="font-size: 13px; font-weight: 700; color: #555;">{titulo}</div>
            <div style="font-size: 22px; font-weight: 700; color: #222;">{valor}</div>
            </div>''', unsafe_allow_html=True)

# --- ABAS E INPUTS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])
with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data = st.date_input("Data")
        total = st.number_input("Total Diária (R$)", step=10.0, value=None)
        dinheiro = st.number_input("Dinheiro (R$)", step=10.0, value=None)
        pix = st.number_input("Pix (R$)", step=10.0, value=None)
        uber = st.number_input("Uber (R$)", step=5.0, value=None)
        if st.form_submit_button("SALVAR"):
            st.success("Dados salvos!")