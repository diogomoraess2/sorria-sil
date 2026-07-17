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

# Estilização CSS
st.markdown("""  
    <style>  
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px; border-left: 6px solid; }  
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; text-transform: uppercase; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }  
    .mes-neon { font-weight: 700; font-size: 28px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; color: #ffffff; }  
    </style>  
""", unsafe_allow_html=True)  

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
if 'editando_mes' not in st.session_state: st.session_state['editando_mes'] = False

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)

st.markdown("### Mês:")
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

# Lógica de seleção
if not st.session_state['editando_mes']:
    if st.button("Trocar Mês"):
        st.session_state['editando_mes'] = True
        st.rerun()
else:
    novo_mes = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=st.session_state['mes_atual_num'] - 1)
    col_a, col_b = st.columns(2)
    if col_a.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.session_state['editando_mes'] = False
        st.rerun()
    if col_b.button("Cancelar"):
        st.session_state['editando_mes'] = False
        st.rerun()

df_mes = carregar_dados_mes(MESES_PT[st.session_state['mes_atual_num']])

# Cálculo de totais
if not df_mes.empty:
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            limpo = df_mes[col].replace(r'[R$\s.]', '', regex=True).str.replace(',', '.', regex=False)
            df_mes[col] = pd.to_numeric(limpo, errors='coerce').fillna(0)
    totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum()
else:
    totais = pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# Mapeamento de cores
cores = {'Total': '#007bff', 'Dinheiro': '#636EFA', 'Pix': '#FBBC05', 'A Receber': '#25D366', 'Uber': '#EA4335'}

cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]
for i, (titulo, col) in enumerate(metricas):
    cor_lateral = cores.get(titulo, '#007bff')
    with cols[i]:
        st.markdown(f'''
            <div class="metric-box" style="border-left-color: {cor_lateral};">
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">R$ {totais[col]:,.2f}</div>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

# --- ABAS CORRIGIDAS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        st.date_input("Data")
        st.number_input("Total (R$)", step=10.0)
        st.number_input("Dinheiro (R$)", step=10.0)
        st.number_input("Pix (R$)", step=10.0)
        st.number_input("Uber (R$)", step=5.0)
        if st.form_submit_button("SALVAR"):
            st.success("Dados enviados!")

with tab2:
    st.dataframe(df_mes, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Análise Financeira")
    if not df_mes.empty:
        dados_pizza = {'Categoria': ['Dinheiro', 'Pix', 'Uber', 'A Receber'], 
                       'Valores': [totais['Dinheiro'], totais['Pix'], totais['Uber'], totais['Próximo mês']]}
        df_pizza = pd.DataFrame(dados_pizza)
        cores_pizza = {'Dinheiro': '#636EFA', 'Pix': '#FBBC05', 'Uber': '#EA4335', 'A Receber': '#25D366'}
        fig_pizza = px.pie(df_pizza, values='Valores', names='Categoria', title="Distribuição do Total", color='Categoria', color_discrete_map=cores_pizza)
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        df_plot = df_mes.sort_values(by='Data')
        fig_linha = px.line(df_plot, x='Data', y='Total', title='Evolução do Faturamento Total', markers=True)
        st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.info("Sem dados suficientes para gráficos.")