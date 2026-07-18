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

# --- INJEÇÃO DE CSS (ESTILO EASYNOTES + BACKGROUND QUADRICULADO) ---
st.markdown("""
    <style>
    /* Aplica a imagem de fundo quadriculada */
    .stApp {
        background-image: url('https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/quadro-verde.jpg');
        background-size: cover;
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"], footer, #MainMenu, .stAppDeployButton, .viewerBadge_container__1QSob {
        display: none !important;
    }
    .block-container { padding-top: 0.5rem !important; }
    
    /* Título sóbrio */
    h1 { font-family: 'Segoe UI', sans-serif !important; margin-bottom: 20px !important; }

    /* Estilo de texto do mês */
    .mes-clean { 
        font-weight: 600; font-size: 28px !important; 
        color: #333 !important; margin-bottom: 15px; display: block;
    }
    
    /* Cards estilo EasyNotes com transparência */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.85) !important; 
        padding: 15px; border-radius: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; 
        border: 1px solid #d0e8d0;
        border-left: 6px solid; 
        display: flex; flex-direction: column; align-items: center;
    }
    .metric-title { 
        font-size: 13px !important; font-weight: 700; text-transform: uppercase; 
        margin-bottom: 5px; color: #555 !important; 
    }
    .metric-value { font-size: 22px !important; font-weight: 700; color: #222 !important; }
    
    /* Ajuste de labels e textos */
    .stSelectbox label, .stDateInput label, .stNumberInput label, .stMarkdown p {
        color: #222222 !important; font-weight: 500;
    }

    /* Ajuste de fundo da caixa de seleção do mês */
    div[data-baseweb="select"] > div {
        background-color: #f7fdf3 !important;
        border: 1px solid #d0e8d0 !important;
    }

/* Cor dos títulos das abas */
    button[data-baseweb="tab"] {
        color: #4a90e2 !important; /* Cor do texto quando inativo */
        font-weight: 600 !important;
    }

    /* Cor do título da aba quando selecionada */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f5a623 !important; /* Cor do texto quando a aba está ativa */
    }

    /* Cor da linha de destaque abaixo da aba ativa */
    div[data-baseweb="tab-highlight"] {
        background-color: #f5a623 !important;
    }

    </style>
""", unsafe_allow_html=True)

st.markdown(f'<link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">', unsafe_allow_html=True)
st.markdown('<link rel="shortcut icon" href="https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/icon.png">', unsafe_allow_html=True)

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
    except:
        return None

conn = get_connection()
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

# --- LÓGICA E INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown("""
    <h1 style="text-align: center; width: 100%; display: block;">
        <span style="color: #4a90e2;">Dent</span><span style="color: #f5a623;">Board</span>
    </h1>
""", unsafe_allow_html=True)

st.session_state['mes_atual_num'] = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num']-1)
st.markdown(f'<span class="mes-clean">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

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

# Métricas com Cores Estilo EasyNotes
cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
cores = {
    'Total': '#4a90e2', 
    'Dinheiro': '#7ed321', 
    'Pix': '#f5a623', 
    'Próximo mês': '#9013fe', 
    'Uber': '#d0021b'
}

for i, (titulo, col) in enumerate(metricas):
    with cols[i]:
        valor_formatado = f"R$ {totais[col]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        cor_hex = cores.get(col, '#4a90e2')
        st.markdown(f'''<div class="metric-card" style="border-left-color: {cor_hex};">
            <div class="metric-title">{titulo}</div>
            <div class="metric-value">{valor_formatado}</div>
            </div>''', unsafe_allow_html=True)

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data = st.date_input("Data")
        total = st.number_input("Total Diária (R$)", step=10.0, value=None, key="total_input")
        dinheiro = st.number_input("Dinheiro (R$)", step=10.0, value=None, key="dinheiro_input")
        pix = st.number_input("Pix (R$)", step=10.0, value=None, key="pix_input")
        uber = st.number_input("Uber (R$)", step=5.0, value=None, key="uber_input")
        t = st.session_state.get("total_input") or 0
        d = st.session_state.get("dinheiro_input") or 0
        p = st.session_state.get("pix_input") or 0
        valor_a_receber = max(0.0, t - (d + p))
        st.markdown(f"**Valor a Receber:** R$ {valor_a_receber:,.2f}")
        if st.form_submit_button("SALVAR"):
            conn.write(URL_PLANILHA, MESES_PT[st.session_state['mes_atual_num']], 
                       [str(data), t, d, p, valor_a_receber, (st.session_state.get("uber_input") or 0)])
            st.success("Dados salvos!")

with tab2:
    st.dataframe(df_mes, use_container_width=True)

with tab3:
    if not df_mes.empty:
        colunas_grafico = ['Dinheiro', 'Pix', 'Uber', 'Próximo mês']
        valores_grafico = totais[colunas_grafico]
        cores_map = {'Dinheiro': '#7ed321', 'Pix': '#f5a623', 'Uber': '#d0021b', 'Próximo mês': '#9013fe'}
        
        fig = px.pie(values=valores_grafico, names=colunas_grafico, title="Distribuição de Receitas",
                     color=colunas_grafico, color_discrete_map=cores_map)
        
        # Gráfico com tema claro e limpo
        fig.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir.")