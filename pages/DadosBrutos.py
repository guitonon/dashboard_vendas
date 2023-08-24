import streamlit as st 
import requests 
import pandas as pd
import plotly.express as px 
import time

# Criação de função para converter os dados para arquivo
# Opção para manter o arquivo no cache

@st.cache_data # Armazenar o data frame caso nao seja alterado

def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)

# Transforma-se a requisição para JSON -> DataFrame

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criação de filtro para decidir que colunas mostrar
# Expander: permite que seja ocultado ou não

    # Filtro de colunas 
    
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas desejadas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')

   # Filtro de nome do produto
   
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

   # Filtro de categoria do produto
   
with st.sidebar.expander('Categoria do produto'):
    categorias = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

   # Filtro de preço do produto
   
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))

   # Filtro de frete do produto
   
with st.sidebar.expander('Frete do produto'):
    frete = st.slider('Selecione o frete', int(dados['Frete'].min()), int(dados['Frete'].max()), (int(dados['Frete'].min()), int(dados['Frete'].max())))

   # Filtro de data da compra do produto
   
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data da compra', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

   # Filtro de vendedor do produto
   
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

   # Filtro de local da compra do produto
   
with st.sidebar.expander('Local da compra'):
    local = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

   # Filtro de avaliação da compra do produto
   
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra', int(dados['Avaliação da compra'].min()), int(dados['Avaliação da compra'].max()), (int(dados['Avaliação da compra'].min()), int(dados['Avaliação da compra'].max())))

   # Filtro de tipo de pagamento da compra do produto
   
with st.sidebar.expander('Tipo de pagamento da compra'):
    pagamento = st.multiselect('Selecione a forma de pagamento da compra', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
    
   # Filtro de quantidade de parcelas da compra do produto
   
with st.sidebar.expander('Quantidade de parcelas da compra'):
    parcelas = st.slider('Selecione a quantidade de parcelas da compra', int(dados['Quantidade de parcelas'].min()), int(dados['Quantidade de parcelas'].max()), (int(dados['Quantidade de parcelas'].min()), int(dados['Quantidade de parcelas'].max())))

# Colocando os filtros para funcionar

query = '''
Produto in @produtos and \
`Categoria do Produto` in @categorias and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local and \
@avaliacao[0] <= `Avaliação da compra`<= @avaliacao[1] and \
`Tipo de pagamento` in @pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]

'''

# Aplicação dos filtros

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Criação do dataframe filtrado

st.dataframe(dados_filtrados)

# Texto mostrando quantidade de linhas e colunas

st.markdown(f'Tabela com :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

# Download do arquivo

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
    
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
