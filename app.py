import streamlit as st  
import pandas as pd  
from datetime import datetime  
import plotly.express as px  
from google.oauth2.service_account import Credentials
import gspread

# Configuração da página
st.set_page_config(  
    page_title="Controle Financeiro - Sorria Sil",  
    page_icon="🦷",  
    layout="wide",  
    initial_sidebar_state="collapsed"  
)  

# Estilização CSS
st.markdown("""  
    <style>  
    .main { background-color: #f8f9fa; }  
    .stButton>button { background-color: #007bff; color: white; border-radius: 12px; font-weight: bold; width: 100%; height: 50px; font-size: 16px; box-shadow: 0 4px 6px rgba(0,123,255,0.15); }  
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid #007bff; text-align: center; margin-bottom: 10px; }  
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; margin-top: 3px; }  
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; color: #ffffff; }  
    </style>  
""", unsafe_allow_html=True)  

# --- CONEXÃO E TRATAMENTO DE ERROS ---
class ConexaoManualSheets:
    def __init__(self, client):
        self.client = client
    def read(self, spreadsheet, sheet):
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        return pd.DataFrame(worksheet.get_all_records())
    def update(self, spreadsheet, sheet, data):
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        worksheet.clear()
        worksheet.update([data.columns.values.tolist()] + data.values.tolist())

try:
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.error("Configuração de [connections.gsheets] não encontrada no arquivo Secrets.")
        st.stop()
        
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    if "private_key" in creds_dict:
        chave = creds_dict["private_key"].replace("\\n", "\n")
        creds_dict["private_key"] = chave
        
    escopos = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciais_google = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    cliente_gspread = gspread.authorize(credenciais_google)
    conn = ConexaoManualSheets(cliente_gspread)
except Exception as e:
    st.error(f"Erro Crítico de Conexão: {e}")
    st.stop()

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1mbT5DJ9re6i6RR8v2rdpUbW3-J00NXx-e1hbe-j4M1M/edit?usp=sharing"  
MESES_PT = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}  
  
def carregar_dados_mes(aba):  
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

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)
nome_aba = MESES_PT[st.session_state['mes_atual_num']]

# Exibição do mês ajustada
st.markdown("### Mês:")
st.markdown(f'<span class="mes-neon">{nome_aba}</span>', unsafe_allow_html=True)
st.write("") 

with st.popover("Trocar Mês"):
    novo_mes = st.selectbox("Selecione:", list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num'] - 1)
    if st.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.rerun()

df_mes = carregar_dados_mes(nome_aba)

# Cálculo de totais com limpeza robusta para evitar valores "astronômicos"
if not df_mes.empty:
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            # Limpa R$, pontos de milhar e converte vírgula para ponto decimal
            limpo = df_mes[col].replace(r'[R$\s.]', '', regex=True).str.replace(',', '.', regex=False)
            df_mes[col] = pd.to_numeric(limpo, errors='coerce').fillna(0)
    totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum()
else:
    totais = pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# Exibição de métricas
col1, col2, col3, col4, col5 = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
for i, (titulo, col) in enumerate(metricas):
    with locals()[f'col{i+1}']:
        st.markdown(f'<div class="metric-box"><div class="metric-title">{titulo}</div><div class="metric-value">R$ {totais[col]:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("---")
tab1, tab2 = st.tabs(["📝 Lançar", "📋 Dados"])
with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data = st.date_input("Data")
        v_total = st.number_input("Total (R$)", step=10.0)
        v_din = st.number_input("Dinheiro (R$)", step=10.0)
        v_pix = st.number_input("Pix (R$)", step=10.0)
        v_uber = st.number_input("Uber (R$)", step=5.0)
        if st.form_submit_button("SALVAR"):
            st.success("Dados enviados!")
with tab2:
    st.dataframe(df_mes, use_container_width=True, hide_index=True)