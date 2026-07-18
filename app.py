import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Controle Financeiro - Sorria Sil",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÃO DA API ---
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1mbT5DJ9re6i6RR8v2rdpUbW3-J00NXx-e1hbe-j4M1M/edit?usp=sharing"

# --- CLASSE DE CONEXÃO ---
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
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            creds_dict = dict(st.secrets["connections"]["gsheets"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', SCOPE)
        return ConexaoManualSheets(gspread.authorize(creds))
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

conn = get_connection()

# --- CSS E VARIÁVEIS ---
st.markdown("""
    <style>
    h1 { font-size: 48px !important; }
    @media (max-width: 600px) {
        .stMainBlockContainer { padding-top: 1.5rem !important; }
        h1 { font-size: 14vw !important; text-align: center; }
    }
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 10px #00e6ff; color: #ffffff; }
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid; }
    .metric-title { font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

def carregar_dados_mes(aba):
    if not conn: return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])
    try:
        df = conn.read(spreadsheet=URL_PLANILHA, sheet=aba)
        df = df.dropna(how='all')
        if not df.empty and 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.date
            return df.dropna(subset=['Data'])
    except: pass
    return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# --- INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month
if 'editando_mes' not in st.session_state: st.session_state['editando_mes'] = False

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

# Lógica de seleção de mês
if st.button("Trocar Mês"): st.session_state['editando_mes'] = not st.session_state['editando_mes']
if st.session_state['editando_mes']:
    novo_mes = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x])
    if st.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.session_state['editando_mes'] = False
        st.rerun()

df_mes = carregar_dados_mes(MESES_PT[st.session_state['mes_atual_num']])

# Cálculo de totais
if not df_mes.empty:
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            df_mes[col] = pd.to_numeric(df_mes[col].replace(r'[R$\s.]', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0)
    totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum()
else:
    totais = pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# Exibição de Métricas
cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
for i, (titulo, col) in enumerate(metricas):
    with cols[i]:
        st.markdown(f'''<div class="metric-box" style="border-left-color: #007bff;"><div class="metric-title">{titulo}</div><div class="metric-value">R$ {totais[col]:,.2f}</div></div>''', unsafe_allow_html=True)

st.markdown("---")

# ABAS
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data_input = st.date_input("Data")
        total_input = st.number_input("Total (R$)", step=10.0)
        dinheiro_input = st.number_input("Dinheiro (R$)", step=10.0)
        pix_input = st.number_input("Pix (R$)", step=10.0)
        uber_input = st.number_input("Uber (R$)", step=5.0)
        if st.form_submit_button("SALVAR"):
            if conn:
                nova_linha = [data_input.strftime('%d/%m/%Y'), total_input, dinheiro_input, pix_input, 0.0, uber_input]
                conn.write(URL_PLANILHA, MESES_PT[st.session_state['mes_atual_num']], nova_linha)
                st.success("Dados salvos!")
                st.rerun()

with tab2:
    st.dataframe(df_mes, use_container_width=True, hide_index=True)

with tab3:
    if not df_mes.empty:
        fig = px.pie(values=[totais['Dinheiro'], totais['Pix'], totais['Uber']], names=['Dinheiro', 'Pix', 'Uber'], title="Distribuição do Total")
        st.plotly_chart(fig, use_container_width=True)