import streamlit as st  
import pandas as pd  
from datetime import datetime  
import plotly.express as px  
from google.oauth2.service_account import Credentials
import gspread

# Configuração da página
st.set_page_config(page_title="Controle Financeiro - Sorria Sil", layout="wide")

# CSS para o Mês Neon e Ajustes
st.markdown("""  
    <style>  
    .metric-box { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid #007bff; text-align: center; margin-bottom: 10px; }  
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; text-transform: uppercase; }  
    .metric-value { font-size: 20px; color: #212529; font-weight: bold; }  
    .mes-neon { 
        font-weight: 700; font-size: 24px; 
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00e6ff, 0 0 30px #00e6ff; 
        color: #ffffff; margin-bottom: 20px; display: block;
    }
    </style>  
""", unsafe_allow_html=True)  

# --- LÓGICA DE LIMPEZA E CÁLCULO ---
def limpar_valor(valor):
    """Converte valores vindos da planilha para float limpo."""
    try:
        if isinstance(valor, (int, float)): return float(valor)
        # Remove tudo que não for dígito, ponto ou vírgula
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- INTERFACE ---
if 'mes_atual_num' not in st.session_state: st.session_state['mes_atual_num'] = datetime.today().month

st.markdown("<h1>🦷 Sorria Sil</h1>", unsafe_allow_html=True)

# Exibição do Mês separado e Neon
st.write("### Mês:")
st.markdown(f'<span class="mes-neon">{MESES_PT[st.session_state["mes_atual_num"]]}</span>', unsafe_allow_html=True)

# Lógica de popover para trocar mês...
# (Mantenha sua lógica de popover anterior aqui)

# --- CORREÇÃO DO CÁLCULO ---
# Ao invés de processar o df inteiro com replace global, processamos coluna por coluna individualmente
if not df_mes.empty:
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            # Aplica a função de limpeza individualmente em cada linha da coluna
            df_mes[col] = df_mes[col].apply(limpar_valor)
    
    totais = df_mes[['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']].sum()
else:
    totais = pd.Series(0, index=['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])

# Exibição das métricas
col1, col2, col3, col4, col5 = st.columns(5)
# ... (restante do código de exibição das colunas)