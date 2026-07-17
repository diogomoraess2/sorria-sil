import streamlit as st  
import pandas as pd  
from datetime import datetime  
import plotly.express as px  
from google.oauth2.service_account import Credentials
import gspread

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

# --- CONEXÃO ROBUSTA E DIRETA COM GOOGLE SHEETS ---
class ConexaoManualSheets:
    """Classe simulada para manter a compatibilidade com o restante do código (.read e .update)"""
    def __init__(self, client):
        self.client = client

    def read(self, spreadsheet, sheet, ttl=None):
        # Abre a planilha pela URL e lê todos os registros como DataFrame
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        dados = worksheet.get_all_records()
        return pd.DataFrame(dados)

    def update(self, spreadsheet, sheet, data):
        # Abre a planilha pela URL e substitui os dados da aba selecionada
        sh = self.client.open_by_url(spreadsheet)
        worksheet = sh.worksheet(sheet)
        worksheet.clear()
        # Envia o cabeçalho e as linhas atualizadas
        worksheet.update([data.columns.values.tolist()] + data.values.tolist())

# --- TRATAMENTO ROBUSTO DE CREDENCIAIS (LIMPEZA PROFUNDA) ---
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        if "private_key" in creds_dict:
            # 1. Remove qualquer caractere que não seja imprimível ou que cause erro de codificação
            chave = creds_dict["private_key"]
            
            # 2. Garante que as bordas da chave estão presentes e corretas
            if "-----BEGIN PRIVATE KEY-----" not in chave:
                chave = "-----BEGIN PRIVATE KEY-----\n" + chave
            if "-----END PRIVATE KEY-----" not in chave:
                chave = chave + "\n-----END PRIVATE KEY-----"
            
            # 3. Força a formatação de linha correta, removendo \r ou espaços duplos
            creds_dict["private_key"] = chave.replace("\\n", "\n").replace("\r", "").strip()
        
        escopos = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Gera o objeto de credenciais oficial do Google
        credenciais_google = Credentials.from_service_account_info(creds_dict, scopes=escopos)
        
        # Inicializa o cliente do gspread
        cliente_gspread = gspread.authorize(credenciais_google)
        
        # Cria o objeto de conexão compatível com o seu código existente
        conn = ConexaoManualSheets(cliente_gspread)
    else:
        st.error("Configurações não encontradas nos Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")
    st.info("Por favor, verifique se as credenciais na aba 'Secrets' do Streamlit Cloud estão salvas corretamente.")
    st.stop()
# --------------------------------------------------
  
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
            # Forçamos o Python a ler a data no formato brasileiro Dia/Mês/Ano (dayfirst=True)
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.date  
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
  
# --- TÍTULO RESPONSIVO EM LINHA ÚNICA (DESKTOP E MOBILE ULTRA CALIBRADO) ---
st.markdown(
    f"""
    <style>
    /* Estilo padrão para Computador (Desktop) */
    .titulo-responsivo {{
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 15px;
        white-space: nowrap; /* Impede a quebra de linha de qualquer forma */
        overflow: hidden;
    }}
    .emoji-dente {{
        font-size: 0.9em;
    }}
    
    /* Ajuste responsivo ultra calibrado para Celulares */
    @media (max-width: 600px) {{
        .titulo-responsivo {{
            /* Encolhe o texto sutilmente e ganha espaço nas laterais */
            font-size: 5.8vw; 
            margin-bottom: 10px;
            margin-left: -12px; /* Empurra o título para a esquerda para ganhar espaço útil */
            text-align: left;
        }}
        .emoji-dente {{
            font-size: 5vw; /* Reduz o dente no celular para sobrar mais tela para as letras */
            margin-right: 2px;
        }}
    }}
    </style>
    
    <h1 class="titulo-responsivo">
        <span class="emoji-dente">🦷</span>Sorria Sil <span style="color: #6c757d; font-weight: 300;">|</span> {nome_aba_trabalho}
    </h1>
    """, 
    unsafe_allow_html=True
)
# ---------------------------------------------------------------------------  
  
df_mes = carregar_dados_mes(nome_aba_trabalho)  
  
if not df_mes.empty:  
    for col in ['Total', 'Dinheiro', 'Pix', 'Próximo mês', 'Uber']:
        if col in df_mes.columns:
            # 1. Garante que os dados sejam tratados como texto para podermos limpá-los[cite: 1]
            valores_limpos = df_mes[col].astype(str)
            
            # 2. Remove "R$", espaços, pontos de milhar e troca a vírgula decimal por ponto[cite: 1]
            valores_limpos = (
                valores_limpos.str.replace("R$", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(".", "", regex=False)  # Remove ponto de milhar (ex: 1.000 -> 1000)[cite: 1]
                .str.replace(",", ".", regex=False)  # Troca vírgula por ponto (ex: 150,50 -> 150.50)[cite: 1]
            )
            
            # 3. Converte com segurança para numérico[cite: 1]
            df_mes[col] = pd.to_numeric(valores_limpos, errors='coerce').fillna(0.0)
    
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