import streamlit as st  
import pandas as pd  
import plotly.express as px
from datetime import datetime  
from google.oauth2.service_account import Credentials
import gspread

# Configuração da página
st.set_page_config(  
    page_title="Controle Financeiro - Sorria Sil",  
    page_icon="🦷",  
    layout="wide",  
    initial_sidebar_state="collapsed"  
)  

# Estilização CSS e Script de Tela Cheia
st.markdown("""  
    <style>  
    /* Esconder elementos padrão para visual de App */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ajuste para desktop */
    h1 { font-size: 48px !important; }

    /* Ajuste para mobile */
    @media (max-width: 600px) {
        h1 { 
            font-size: 14vw !important; 
            width: 100% !important; 
            text-align: center !important;
            display: block !important;
            white-space: nowrap !important;
            margin: 0 !important;
            padding: 15px 0 !important; 
            box-sizing: border-box !important; 
        }
        .mes-neon { font-size: 24px !important; }
    }
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px; border-left: 6px solid; }  
    .metric-title { font-size: 11px; font-weight: bold; text-transform: uppercase; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }  
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; color: #ffffff; }  
    </style>  

    <script>
    function openFullscreen() {
        var elem = document.documentElement;
        if (elem.requestFullscreen) { elem.requestFullscreen(); }
    }
    </script>
""", unsafe_allow_html=True)  

# --- BOTÃO DE TELA CHEIA E SAIR ---
col_fs, col_sair = st.columns(2)
with col_fs:
    st.markdown('<button onclick="openFullscreen()" style="width:100%; padding:10px;">Tela Cheia 📱</button>', unsafe_allow_html=True)
with col_sair:
    if st.button("❌ Sair do App"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://www.google.com">', unsafe_allow_html=True)

# --- CONEXÃO ---
class ConexaoManualSheets:
    def __init__(self, client):
        self.client = client
    def read(self, spreadsheet, sheet):
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        return pd.DataFrame(worksheet.get_all_records())

try:
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.stop()
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    escopos = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciais_google = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    cliente_gspread = gspread.authorize(credenciais_google)
    conn = ConexaoManualSheets(cliente_gspread)
except Exception:
    st.stop()

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1mbT5DJ9re6i6RR8v2rdpUbW3-J00NXx-e1hbe-j4M1M/edit?usp=sharing"  
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}  

# ... (Função carregar_dados_mes e lógica de interface permanecem as mesmas)
# [Recomendo manter o restante do código que você já validou]