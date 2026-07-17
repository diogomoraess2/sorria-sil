# Documentação do Dashboard "Sorria Sil"

## 1. Visão Geral
O "Sorria Sil" é uma ferramenta de controle financeiro automatizada, desenvolvida em Python com o framework Streamlit, integrada ao Google Sheets para armazenamento de dados. O objetivo é oferecer uma visualização intuitiva e rápida do faturamento diário e mensal.

## 2. Tecnologias Utilizadas
* Interface: Streamlit (responsiva com CSS customizado).
* Processamento de Dados: Pandas (manipulação de planilhas).
* Integração: `gspread` e `google-auth` para conexão direta com o Google Sheets.
* Visualização: Plotly Express (gráficos interativos).

## 3. Mini-Manual para o Usuário
* **Acesso**: O aplicativo abre na tela inicial mostrando o mês vigente automaticamente.
* **Trocar o Mês**: Clique no botão "Trocar Mês", selecione o mês desejado e clique em "Confirmar" para atualizar os valores.
* **Consultar Totais**: O topo da tela mostra o resumo financeiro (Total, Dinheiro, Pix, A Receber e Uber), com cores de borda para identificação visual.
* **Fazer um Lançamento**:
    1. Acesse a aba "📝 Lançar".
    2. Preencha a data e os valores correspondentes.
    3. Clique em "SALVAR".
* **Visualizar Gráficos**: Na aba "📈 Gráficos", você pode ver a distribuição do faturamento e a evolução dos ganhos.

## 4. Guia de Preenchimento da Planilha
Para garantir o funcionamento, a planilha Google Sheets deve seguir este padrão:
* **Estrutura de Colunas**: `Data`, `Total`, `Dinheiro`, `Pix`, `Próximo mês` e `Uber`.
* **Formato de Data**: DD/MM/AAAA (ex: 17/07/2026).
* **Valores Numéricos**: Insira apenas números, sem símbolos de moeda (R$).
* **Organização**: Evite deixar linhas totalmente em branco entre os registros.

## 5. Guia de Resolução de Problemas (FAQ)
* **O app não abre ou não atualiza**: Verifique a conexão com a internet e recarregue a página (F5).
* **Valor total zerado**: Verifique se o nome da aba na planilha corresponde exatamente ao mês selecionado.
* **Erro de Autenticação**: Verifique se as credenciais no `secrets.toml` ainda estão válidas no console do Google Cloud.
* **Visualização do texto**: O app possui modo adaptativo. Caso a leitura no modo claro não seja ideal, o uso do **modo escuro** no celular é a configuração recomendada para o efeito neon.

## 6. Configuração Técnica
* **Segurança**: O app utiliza `st.secrets` para autenticação.
* **Customização**: Estilos CSS e margens responsivas estão centralizados no bloco `st.markdown` dentro do arquivo `app.py`.
