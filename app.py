import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
        return ConexaoManualSheets(gspread.authorize(creds))
    except Exception as e:
        st.error(f"Erro ao autenticar: {e}")
        return None

conn = get_connection()

# --- CSS ---
st.markdown("""
    <style>
    /* Oculta o cabeçalho superior (menu, deploy, etc) */
    [data-testid="stHeader"] {
        display: none;
    }
    
    /* Ajuste da margem superior do container principal */
    .block-container { 
        padding-top: 0.3rem !important; /* Diminuí de 1rem para 0.3rem */
    }
    
    h1 { font-size: 48px !important; }
    
    .mes-neon { 
        font-weight: 700; 
        font-size: 28px; 
        text-shadow: 0 0 10px #00e6ff; 
        color: #ffffff; 
    }
    
    .metric-box { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        text-align: center; 
        margin: 2px 5px; 
        border-left: 6px solid; 
    }
    
    .metric-title { font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
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
            
            # Limpeza robusta: garante que colunas financeiras sejam números
            for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
                if col in df.columns:
                    # Remove R$, espaços, pontos de milhar e substitui vírgula por ponto
                    df[col] = df[col].replace(r'[R$\s.]', '', regex=True).str.replace(',', '.')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df.dropna(subset=['Data'])
    except: pass
    return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# --- INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month
if 'editando_mes' not in st.session_state: st.session_state['editando_mes'] = False

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

if st.button("Trocar Mês"): st.session_state['editando_mes'] = not st.session_state['editando_mes']
if st.session_state['editando_mes']:
    novo_mes = st.selectbox("Selecione o mês:", options=list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x])
    if st.button("Confirmar"):
        st.session_state['mes_atual_num'] = novo_mes
        st.session_state['editando_mes'] = False
        st.rerun()

df_mes = carregar_dados_mes(MESES_PT[st.session_state['mes_atual_num']])
colunas_financeiras = ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']
totais = df_mes[colunas_financeiras].sum() if not df_mes.empty else pd.Series(0, index=colunas_financeiras)

# --- EXIBIÇÃO DE MÉTRICAS ---
cores = {'Total': '#007bff', 'Dinheiro': '#25D366', 'Pix': '#FBBC05', 'Próximo mês': '#636EFA', 'Uber': '#EA4335'}
cols = st.columns(5)
metricas = [("Total", "Total"), ("Dinheiro", "Dinheiro"), ("Pix", "Pix"), ("A Receber", "Próximo mês"), ("Uber", "Uber")]

for i, (titulo, col) in enumerate(metricas):
    cor = cores.get(col, '#007bff')
    with cols[i]:
        st.markdown(f'''
            <div class="metric-box" style="border-left-color: {cor};">
                <div class="metric-title" style="color: {cor};">{titulo}</div>
                <div class="metric-value">R$ {totais[col]:,.2f}</div>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data_input = st.date_input("Data", value=datetime.today())
        total_input = st.number_input("Total (R$)", value=None, step=10.0, placeholder="0.00")
        dinheiro_input = st.number_input("Dinheiro (R$)", value=None, step=10.0, placeholder="0.00")
        pix_input = st.number_input("Pix (R$)", value=None, step=10.0, placeholder="0.00")
        uber_input = st.number_input("Uber (R$)", step=5.0, value=None, placeholder="0.00")
        
        if st.form_submit_button("SALVAR"):
            if total_input is not None:
                # Cálculo automático do "Próximo mês" (A Receber)
                valor_dinheiro = dinheiro_input or 0
                valor_pix = pix_input or 0
                valor_receber = total_input - valor_dinheiro - valor_pix
                
                if conn:
                    nova_linha = [
                        data_input.strftime('%d/%m/%Y'), 
                        total_input, 
                        valor_dinheiro, 
                        valor_pix, 
                        valor_receber, # Agora calcula o que falta
                        uber_input or 0
                    ]
                    conn.write(URL_PLANILHA, MESES_PT[st.session_state['mes_atual_num']], nova_linha)
                    st.success("Dados salvos!")
                    st.rerun()
            else:
                st.warning("Por favor, preencha pelo menos o campo Total.")

with tab2:
    if not df_mes.empty:
        df_exibicao = df_mes.copy()
        for col in colunas_financeiras:
            df_exibicao[col] = df_exibicao[col].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado lançado.")

with tab3:
    if not df_mes.empty:
        fig = px.pie(values=[totais['Dinheiro'], totais['Pix'], totais['Uber']], names=['Dinheiro', 'Pix', 'Uber'], title="Distribuição de Receitas")
        st.plotly_chart(fig, use_container_width=True)