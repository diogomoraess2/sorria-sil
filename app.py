import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import base64
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO PWA ---
manifest_json = """
{
  "name": "EasyCash",
  "short_name": "EasyCash",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#9b34eb",
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
    page_title="Controle Financeiro - EasyCash",
    page_icon="https://raw.githubusercontent.com/diogomoraess2/sorria-sil/main/static/icon.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INJEÇÃO DE CSS ---
st.markdown("""
    <style>
    /* Oculta o menu superior (hambúrguer), o cabeçalho e o rodapé do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer { display: none !important; }
    
    /* Fundo branco com símbolos financeiros mais escuros e marcantes */
    .stApp {
        background-color: #ffffff;
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%231a4f91' fill-opacity='0.28' font-family='sans-serif' font-weight='bold'%3E%3Ctext x='15' y='30' font-size='16'%3E$%3C/text%3E%3Ctext x='65' y='75' font-size='14'%3E%25%3C/text%3E%3Ctext x='40' y='50' font-size='12'%3ER%24%3C/text%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* Puxa todo o conteúdo para cima */
    .block-container { margin-top: -60px !important; padding-top: 0rem !important; }
    
    /* Reduz o espaço logo abaixo do título principal */
    h1 { font-family: 'Segoe UI', sans-serif !important; margin-bottom: -10px !important; }
    
    /* Remove o ícone de link do cabeçalho */
    h1 a { display: none !important; }
    
    .mes-clean { font-weight: 600; font-size: 28px !important; color: #333 !important; margin-bottom: 15px; display: block; }
    
    /* Cards */
    .metric-card { 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 5px; border-radius: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; 
        border: 1px solid #e0e0e0;
        border-left: 6px solid; 
        display: flex; flex-direction: column; align-items: center;
        margin-bottom: 10px;
    }
    
    /* MEDIA QUERY PARA CELULAR */
    @media (max-width: 640px) {
        .metric-card {
            margin-bottom: 20px !important;
        }
    }

    .metric-title { font-size: 13px !important; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; color: #555 !important; }
    .metric-value { font-size: 20px !important; font-weight: 700; color: #222 !important; }
    
    /* Força a cor do Selectbox */
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d0e8d0 !important;
        color: #222222 !important;
    }
    [data-baseweb="select"] span {
        color: #222222 !important;
    }

    /* Adiciona espaço visual acima das abas */
    .stTabs {
        margin-top: 30px !important;
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

# --- Mapeamento Unificado de Cores ---
cores_map = {
    'Total': '#4a90e2', 
    'Dinheiro': '#7ed321', 
    'Pix': '#f5a623', 
    'Dinheiro + Pix': '#20b2aa', 
    'Próximo mês': '#9013fe', 
    'Uber': '#d0021b'
}

# --- LÓGICA E INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown("""
    <h1 style="text-align: center; width: 100%; display: block;">
        <span style="color: #9b34eb;"> Easy</span><span style="color: #eb34c3;">Cash</span>
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

# --- Exibição dos Cards ---
cols = st.columns(6)
metricas = [
    ("Total", "Total"), 
    ("Dinheiro", "Dinheiro"), 
    ("Pix", "Pix"), 
    ("Dinheiro + Pix", "Dinheiro_Pix"), 
    ("A Receber", "Próximo mês"), 
    ("Uber", "Uber")
]

for i, (titulo, col) in enumerate(metricas):
    with cols[i]:
        if col == "Dinheiro_Pix":
            valor_soma = totais.get('Dinheiro', 0) + totais.get('Pix', 0)
            valor_formatado = f"R$ {valor_soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cor_hex = cores_map.get('Dinheiro + Pix', '#20b2aa')
        else:
            valor_formatado = f"R$ {totais[col]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cor_hex = cores_map.get(col, '#4a90e2')
            
        st.markdown(f'''<div class="metric-card" style="border-left-color: {cor_hex};">
            <div class="metric-title">{titulo}</div>
            <div class="metric-value">{valor_formatado}</div>
            </div>''', unsafe_allow_html=True)




# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançar", "📋 Dados", "📈 Gráficos"])

with tab1:
    with st.form("form_registro", clear_on_submit=True):
        data = st.date_input("Data", format="DD/MM/YYYY")
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
            data_formatada = data.strftime("%d/%m/%Y") 
            conn.write(URL_PLANILHA, MESES_PT[st.session_state['mes_atual_num']], 
                       [data_formatada, t, d, p, valor_a_receber, (st.session_state.get("uber_input") or 0)])
            st.success("Dados salvos!")

with tab2:
    st.dataframe(df_mes, use_container_width=True)

with tab3:
    if not df_mes.empty:
        colunas_grafico = ['Dinheiro', 'Pix', 'Uber', 'Próximo mês']
        valores_grafico = totais[colunas_grafico]
        
        fig = px.pie(values=valores_grafico, names=colunas_grafico, title="Distribuição de Receitas",
                     color=colunas_grafico, color_discrete_map=cores_map)
        
        fig.update_traces(
            textinfo='label+value+percent', 
            texttemplate='%{label}<br>R$ %{value:,.2f}<br>(%{percent:.1%})',
            insidetextorientation='radial',
            insidetextfont=dict(size=11)
        )
        
        fig.update_layout(
            template="plotly_white", 
            margin=dict(t=50, b=50, l=20, r=20),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir.")