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

# --- INJEÇÃO DE CSS (Compactado conforme solicitado) ---
st.markdown("""
    <style>
    [data-testid="stHeader"], footer, #MainMenu, .stAppDeployButton, .viewerBadge_container__1QSob {
        display: none !important;
    }
    .block-container { padding-top: 0.5rem !important; }
    
    h1 { font-size: 50px !important; margin-bottom: 0px !important; }
    .mes-neon { 
        font-weight: 700; font-size: 35px !important; 
        text-shadow: 0 0 10px #00e6ff; color: #ffffff; 
        margin-bottom: 10px; display: block;
    }
    .metric-card { 
        background-color: #f8f9fa; padding: 5px; border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; 
        margin-bottom: 5px; border-left: 6px solid; 
        display: flex; flex-direction: column; align-items: center;
    }
    .metric-title { font-size: 12px !important; font-weight: 800; text-transform: uppercase; margin-bottom: 2px; color: #6c757d; }
    .metric-value { font-size: 18px !important; color: #212529; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">', unsafe_allow_html=True)

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

# --- LÓGICA E INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)
st.session_state['mes_atual_num'] = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num']-1)
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
            return df
    except: pass
    return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

df_mes = carregar_dados_mes(MESES_PT[st.session_state['mes_atual_num']])
totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum() if not df_mes.empty else pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
cores = {'Total': '#007bff', 'Dinheiro': '#25D366', 'Pix': '#FBBC05', 'Próximo mês': '#636EFA', 'Uber': '#EA4335'}

for i, (titulo, col) in enumerate(metricas):
    with cols[i]:
        valor_formatado = f"R$ {totais[col]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f'''<div class="metric-card" style="border-left-color: {cores.get(col, '#007bff')};">
            <div class="metric-title">{titulo}</div><div class="metric-value">{valor_formatado}</div></div>''', unsafe_allow_html=True)

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        st.date_input("Data")
        st.number_input("Total (R$)", step=10.0)
        st.form_submit_button("SALVAR")

with tab2:
    st.write("Registros do mês:")
    st.dataframe(df_mes, use_container_width=True)

with tab3:
    if not df_mes.empty:
        fig = px.pie(values=totais[['Dinheiro', 'Pix', 'Uber']], names=['Dinheiro', 'Pix', 'Uber'], title="Distribuição de Receitas")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir nos gráficos.")