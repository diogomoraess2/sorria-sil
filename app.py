import streamlit as st  
import pandas as pd  
from datetime import datetime  
import plotly.express as px  
from streamlit_gsheets import GSheetsConnection  

# Configuração da página do Streamlit otimizada para Celular
st.set_page_config(  
    page_title="Controle Financeiro - Sorria Sil",  
    page_icon="🦷",  
    layout="wide",  
    initial_sidebar_state="collapsed"  
)  
  
# Estilização personalizada via CSS focada em Mobile
st.markdown("""  
    <style>  
    .main { background-color: #f8f9fa; }  
    .stButton>button {  
        background-color: #007bff;  
        color: white;  
        border-radius: 12px;  
        font-weight: bold;  
        width: 100%;  
        height: 50px;  
        font-size: 16px;  
        box-shadow: 0 4px 6px rgba(0,123,255,0.15);  
    }  
    .stButton>button:hover {  
        background-color: #0056b3;  
        color: white;  
    }  
    .metric-box {  
        background-color: white;  
        padding: 15px;  
        border-radius: 12px;  
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);  
        border-left: 6px solid #007bff;  
        text-align: center;  
        margin-bottom: 10px;  
    }  
    .metric-title {  
        font-size: 11px;  
        color: #6c757d;  
        font-weight: bold;  
        text-transform: uppercase;  
        letter-spacing: 0.5px;  
    }  
    .metric-value {  
        font-size: 20px;  
        color: #212529;  
        font-weight: bold;  
        margin-top: 3px;  
    }  
    .stNumberInput div[data-baseweb="input"] {  
        border-radius: 10px !important;  
    }  
    </style>  
""", unsafe_allow_html=True)  

# --- TRATAMENTO ROBUSTO DE CREDENCIAIS ---
# Reconstrói o dicionário de conexões limpando e corrigindo quebras de linha na chave PEM
conexao_configurada = False
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        # Criamos uma cópia das credenciais em formato dicionário comum do Python
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # Limpa eventuais problemas de formatação na chave privada
        chave_crua = creds_dict.get("private_key", "")
        
        # Corrige quebras de linha literais escritas como string '\\n' ou convertidas incorretamente
        chave_corrigida = chave_crua.replace("\\n", "\n").replace("\n", "\n")
        
        # Garante que as bordas da chave estão limpas
        creds_dict["private_key"] = chave_corrigida.strip()
        
        # Instancia a conexão passando nosso dicionário corrigido manualmente
        conn = st.connection("gsheets", type=GSheetsConnection, **creds_dict)
        conexao_configurada = True
except Exception as e:
    st.error(f"Erro ao estruturar credenciais: {e}")

# Caso a montagem manual falhe por alguma razão, tentamos o fallback padrão
if not conexao_configurada:
    # --- TRATAMENTO ROBUSTO DE CREDENCIAIS ---
conexao_configurada = False
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        # Criamos um dicionário com as credenciais cadastradas nos Secrets
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # Puxamos a chave privada e limpamos espaços invisíveis ou quebras de linha corrompidas
        chave_crua = creds_dict.get("private_key", "")
        
        # Garante a formatação exata que a biblioteca de criptografia do Google exige
        chave_corrigida = chave_crua.replace("\\n", "\n").strip()
        creds_dict["private_key"] = chave_corrigida
        
        # Iniciamos a conexão passando os parâmetros limpos manualmente
        conn = st.connection("gsheets", type=GSheetsConnection, **creds_dict)
        conexao_configurada = True
except Exception as e:
    st.sidebar.warning(f"Aviso na preparação das credenciais: {e}")

# Caso o tratamento manual acima falhe, tenta o método padrão como plano B
if not conexao_configurada:
    conn = st.connection("gsheets", type=GSheetsConnection)
# ----------------------------------------
  
# URL oficial de compartilhamento da sua planilha do Google Sheets
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1mbT5DJ9re6i6RR8v2rdpUbW3-J00NXx-e1hbe-j4M1M/edit?usp=sharing"  
  
# Dicionário de tradução dos meses  
MESES_PT = {  
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',   
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',   
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'  
}  
  
def obter_nome_aba(data):  
    return MESES_PT[data.month]  
  
def carregar_dados_mes(aba):  
    try:  
        df = conn.read(spreadsheet=URL_PLANILHA, sheet=aba, ttl="0")  
        df = df.dropna(how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        if not df.empty and 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.date  
            df = df.dropna(subset=['Data'])
            return df  
    except Exception as e:  
        st.sidebar.error(f"Erro ao carregar a aba '{aba}': {e}")
        pass  
    return pd.DataFrame(columns=['Data', 'Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber'])  
  
def salvar_dados_sheets(df_novo_registro, aba):
    try:
        df_existente = carregar_dados_mes(aba)
        df_atualizado = pd.concat([df_existente, df_novo_registro], ignore_index=True)
        conn.update(spreadsheet=URL_PLANILHA, sheet=aba, data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")
        return False

# Interface Principal  
st.sidebar.image("https://img.icons8.com/cotton/128/dentist-chair.png", width=60)  
st.sidebar.title("Sorria Sil 🦷")  
st.sidebar.write("### Painel Administrativo")  
  
hoje = datetime.today()  
mes_selecionado_num = st.sidebar.selectbox("Mês de Visualização", list(MESES_PT.keys()), index=hoje.month - 1)  
nome_aba_trabalho = MESES_PT[mes_selecionado_num]  
  
st.markdown(
    f"""
    <h1 style="
        font-size: clamp(30px, 5.5vw, 50px); 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis;
        margin-bottom: 15px;
    ">
        🦷 Sorria Sil <span style="color: #6c757d; font-weight: 300;">|</span> {nome_aba_trabalho}
    </h1>
    """, 
    unsafe_allow_html=True
)  
  
df_mes = carregar_dados_mes(nome_aba_trabalho)  
  
if not df_mes.empty:  
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            df_mes[col] = pd.to_numeric(df_mes[col], errors='coerce').fillna(0.0)
    
    total_geral = df_mes['Total'].sum() if 'Total' in df_mes.columns else 0.0
    total_dinheiro = df_mes['Dinheiro'].sum() if 'Dinheiro' in df_mes.columns else 0.0
    total_pix = df_mes['Pix'].sum() if 'Pix' in df_mes.columns else 0.0
    total_proximo_mes = df_mes['Próximo mês'].sum() if 'Próximo mês' in df_mes.columns else 0.0
    total_uber = df_mes['Uber'].sum() if 'Uber' in df_mes.columns else 0.0
else:  
    total_geral = total_dinheiro = total_pix = total_proximo_mes = total_uber = 0.0  
  
# Indicadores financeiros
col1, col2, col3, col4, col5 = st.columns(5)  
with col1:  
    st.markdown(f'<div class="metric-box"><div class="metric-title">Faturamento Total</div><div class="metric-value">R$ {total_geral:,.2f}</div></div>', unsafe_allow_html=True)  
with col2:  
    st.markdown(f'<div class="metric-box" style="border-left-color: #28a745;"><div class="metric-title">Total Dinheiro</div><div class="metric-value" style="color: #28a745;">R$ {total_dinheiro:,.2f}</div></div>', unsafe_allow_html=True)  
with col3:  
    st.markdown(f'<div class="metric-box" style="border-left-color: #17a2b8;"><div class="metric-title">Total Pix</div><div class="metric-value" style="color: #17a2b8;">R$ {total_pix:,.2f}</div></div>', unsafe_allow_html=True)  
with col4:  
    st.markdown(f'<div class="metric-box" style="border-left-color: #ffc107;"><div class="metric-title">A Receber Próx. Mês</div><div class="metric-value" style="color: #ffc107;">R$ {total_proximo_mes:,.2f}</div></div>', unsafe_allow_html=True)  
with col5:  
    st.markdown(f'<div class="metric-box" style="border-left-color: #dc3545;"><div class="metric-title">Gastos Uber</div><div class="metric-value" style="color: #dc3545;">R$ {total_uber:,.2f}</div></div>', unsafe_allow_html=True)  
  
st.markdown("---")  
  
# Abas de navegação principal  
tab_novo, tab_dados, tab_graficos = st.tabs(["📝 Lançar", "📅 Planilha", "📈 Gráficos"])  
  
with tab_novo:  
    st.subheader("Registrar Diária")  
    with st.form("form_registro", clear_on_submit=True):  
          
        data_lancamento = st.date_input("Data do Lançamento", hoje.date())  
        dia_semana = data_lancamento.weekday()  
        dias_nome = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]  
          
        if dia_semana == 6:  
            st.error("⚠️ Atenção: Lançamentos não são permitidos aos domingos!")  
            validacao_domingo = False  
        else:  
            st.info(f"📅 Selecionado: {dias_nome[dia_semana]}")  
            validacao_domingo = True  
          
        st.markdown("---")
          
        val_total_dia = st.number_input("Valor Total do Dia (R$)", min_value=0.0, value=0.0, step=10.0, format="%.2f")  
        val_dinheiro = st.number_input("Valor Recebido em Dinheiro (R$)", min_value=0.0, value=0.0, step=10.0, format="%.2f")  
        val_pix = st.number_input("Valor Recebido em Pix (R$)", min_value=0.0, value=0.0, step=10.0, format="%.2f")  
        val_uber = st.number_input("Valor Gasto no Uber (R$)", min_value=0.0, value=0.0, step=5.0, format="%.2f")  
                
        val_proximo_mes = max(0.0, val_total_dia - (val_dinheiro + val_pix))  
          
        st.markdown("""<div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin-top: 15px;">
            <p style="margin: 0; color: #856404; font-weight: bold; font-size: 14px;">Resumo do Lançamento:</p>
            <p style="margin: 5px 0 0 0; font-size: 13px; color: #333;">
                • Total do Dia: <b>R$ {:,.2f}</b><br>
                • Pago Hoje: R$ {:,.2f}<br>
                • <b>Pendente p/ Próximo Mês: <span style="color:#b58100;">R$ {:,.2f}</span></b><br>
                • Gasto Uber: R$ {:,.2f}
            </p>
        </div>""".format(val_total_dia, (val_dinheiro + val_pix), val_proximo_mes, val_uber), unsafe_allow_html=True)
          
        st.write("") 
            
        btn_salvar = st.form_submit_button("SALVAR REGISTRO", disabled=not validacao_domingo)  
        
        if btn_salvar and validacao_domingo:  
            novo_df = pd.DataFrame([{
                'Data': data_lancamento.strftime('%Y-%m-%d'), 
                'Total': val_total_dia,
                'Dinheiro': val_dinheiro,
                'Pix': val_pix,
                'Próximo mês': val_proximo_mes,
                'Uber': val_uber
            }])
            
            aba_destino = obter_nome_aba(data_lancamento)
            
            with st.spinner("Enviando dados de forma segura para o Google Sheets..."):
                sucesso = salvar_dados_sheets(novo_df, aba_destino)
                
            if sucesso:
                st.success(f"🎉 Registro de R$ {val_total_dia:.2f} adicionado com sucesso em '{aba_destino}'!")
                st.rerun()
            else:
                st.error("❌ Ocorreu um problema ao tentar registrar o dado. Verifique as credenciais.")
  
with tab_dados:  
    st.subheader("📋 Planilha Mensal")  
    if not df_mes.empty:  
        df_exibir = df_mes.copy()  
        if 'Data' in df_exibir.columns:
            df_exibir['Data'] = pd.to_datetime(df_exibir['Data']).dt.strftime('%d/%m')  
          
        df_exibir = df_exibir.rename(columns={  
            'Total': 'Total (R$)',   
            'Dinheiro': 'Din (R$)',   
            'Pix': 'Pix (R$)',   
            'Próximo mês': 'Próx (R$)',  
            'Uber': 'Uber (R$)'  
        })  
        st.dataframe(df_exibir, use_container_width=True, hide_index=True)  
    else:  
        st.info("Nenhum lançamento registrado para este mês.")  
  
with tab_graficos:  
    st.subheader("📈 Gráficos de Desempenho")  
    if not df_mes.empty:  
        st.markdown("#### Faturamento Diário")  
        df_mes_ordenado = df_mes.sort_values(by='Data')  
        fig_linha = px.line(  
            df_mes_ordenado,   
            x='Data',   
            y='Total',   
            markers=True,  
            labels={'Total': 'Faturamento (R$)', 'Data': 'Dia'}  
        )  
        fig_linha.update_layout(height=280, margin=dict(l=20, r=20, t=10, b=10))  
        st.plotly_chart(fig_linha, use_container_width=True)  
          
        st.markdown("#### Divisão de Recebimentos")  
        valores = [total_dinheiro, total_pix, total_proximo_mes]  
        categorias = ['Dinheiro', 'Pix', 'Próximo Mês']  
          
        df_pizza = pd.DataFrame({'Meio': categorias, 'Valor': valores})  
        df_pizza = df_pizza[df_pizza['Valor'] > 0]  
          
        if not df_pizza.empty:  
            fig_pizza = px.pie(  
                df_pizza,   
                values='Valor',   
                names='Meio',   
                color_discrete_sequence=['#28a745', '#17a2b8', '#ffc107']  
            )  
            fig_pizza.update_layout(height=280, margin=dict(l=20, r=20, t=10, b=10))  
            st.plotly_chart(fig_pizza, use_container_width=True)  
        else:  
            st.info("Adicione lançamentos para gerar o gráfico de divisão.")  
    else:  
        st.info("Sem dados suficientes para gerar gráficos.")