import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import base64

# --- CONFIGURAÇÃO PWA E ESTILO ---
manifest_json = """
{
  "name": "Sorria Sil",
  "short_name": "Sorria Sil",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#00e6ff",
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
    page_title="Controle Financeiro - Sorria Sil",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injeção de CSS e Metatags com chaves dobradas para evitar NameError
st.markdown(f"""
    <link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">
    <style>
    /* Oculta elementos da interface Streamlit */
    [data-testid="stHeader"], footer, #MainMenu, .stAppDeployButton, .viewerBadge_container__1QSob {{
        display: none !important;
    }}
    .block-container {{ padding-top: 0.5rem !important; }}
    
    h1 {{ font-size: 32px !important; margin-bottom: 0px !important; }}
    
    .mes-neon {{ 
        font-weight: 700; font-size: 24px; 
        text-shadow: 0 0 10px #00e6ff; color: #ffffff; 
        margin-bottom: 15px; display: block;
    }}
    
    .metric-box {{ 
        background-color: #f8f9fa; padding: 10px; border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; 
        margin-bottom: 10px; border-left: 5px solid; 
    }}
    .metric-title {{ font-size: 10px; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 16px; color: #212529; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API ---
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
    except Exception as e:
        return None

conn = get_connection()
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

# --- LÓGICA E INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

def carregar_dados_mes(aba):
    if not conn: return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])
    try:
        df = conn.read(spreadsheet=URL_PLANILHA, sheet=aba)
        df = df.dropna(how='all')
        if not df.empty and 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.date
            for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
                if col in df.columns:
                    df[col] = df[col].replace(r'[R$\s.]', '', regex=True).str.replace(',', '.')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df.dropna(subset=['Data'])
    except: pass
    return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

df_mes = carregar_dados_mes(MESES_PT[st.session_state['mes_atual_num']])
colunas_financeiras = ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']
totais = df_mes[colunas_financeiras].sum() if not df_mes.empty else pd.Series(0, index=colunas_financeiras)

# Métricas
cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
cores = {'Total': '#007bff', 'Dinheiro': '#25D366', 'Pix': '#FBBC05', 'Próximo mês': '#636EFA', 'Uber': '#EA4335'}

for i, (titulo, col) in enumerate(metricas):
    with cols[i]:
        st.markdown(f'''<div class="metric-box" style="border-left-color: {cores.get(col, '#007bff')};">
            <div class="metric-title">{titulo}</div>
            <div class="metric-value">R$ {totais[col]:,.0f}</div>
        </div>''', unsafe_allow_html=True)

# Tabs e Formulário
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])
with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data_input = st.date_input("Data", value=datetime.today())
        total_input = st.number_input("Total (R$)", value=None, step=10.0, placeholder="0.00")
        dinheiro_input = st.number_input("Dinheiro (R$)", value=None, step=10.0, placeholder="0.00")
        pix_input = st.number_input("Pix (R$)", value=None, step=10.0, placeholder="0.00")
        uber_input = st.number_input("Uber (R$)", step=5.0, value=None, placeholder="0.00")
        
        if st.form_submit_button("SALVAR"):
            st.success("Dados processados!")