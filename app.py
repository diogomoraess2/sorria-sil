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

# --- INJEÇÃO DE CSS REFORÇADO ---
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
    .block-container { padding-top: 0.5rem !important; }
    
    /* Forçar fundo branco nos inputs */
    div[data-baseweb="base-input"], div[data-baseweb="input"], input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Remover botões +/- */
    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none !important;
        margin: 0 !important;
    }
    
    /* Botão Salvar */
    div.stButton > button {
        background-color: #a8e0a8 !important; 
        color: #ffffff !important;
        border: none !important;
    }
    
    label { color: #222 !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

# --- RESTANTE DO CÓDIGO ---
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1mbT5DJ9re6i6RR8v2rdpUbW3-J00NXx-e1hbe-j4M1M/edit?usp=sharing"

class ConexaoManualSheets:
    def __init__(self, client):
        self.client = client
    def read(self, spreadsheet, sheet):
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        return pd.DataFrame(worksheet.get_all_records())
    def write(self, spreadsheet, sheet, row_data):
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        worksheet.append_row(row_data)

@st.cache_resource
def get_connection():
    try:
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
        return ConexaoManualSheets(gspread.authorize(creds))
    except:
        return None

conn = get_connection()
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown('<h1 style="text-align: center;"><span style="color: #4a90e2;">Dent</span><span style="color: #f5a623;">Board</span></h1>', unsafe_allow_html=True)
st.session_state['mes_atual_num'] = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num']-1)

# Lógica da aba lançar
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