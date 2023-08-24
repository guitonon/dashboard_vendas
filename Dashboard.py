# Criando o ambiente virtual: python -m venv venv
# Selecionar cmd no terminal

import streamlit as st 
import requests 
import pandas as pd
import plotly.express as px 

# Configuração do dashboard como visão wide

st.set_page_config(layout = 'wide', page_title = 'DashboardDeVendas', page_icon = 'random')

# Criação de função para formatar os números

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

 # Para adicionar um título, pode-se usar a estrutura abaixo. 
 # Emoji colocado entre ::
 # Para executar o código, basta ir no terminal e escrever o comando "streamlit run nome.py"
 
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Para fazer a leitura dos dados da API, usar o método get do módulo requests

url = 'https://labdados.com/produtos'

# Criação de filtro diretamente no carregamento dos dados

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params = query_string)

# Transforma-se a requisição para JSON -> DataFrame

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criação de filtro após o carregamento dos dados 

filtro_vendedores = st.sidebar.multiselect('Vendedor', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas

    # Receitas

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']] \
    .merge(receita_estados, left_on = 'Local da compra', right_index= True) \
    .sort_values('Preço', ascending= False)
    
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']] \
    .sum()  \
    .sort_values('Preço', ascending = False)
    
    # Quantidade de vendas
    
vendas_estados = dados.groupby('Local da compra')[['Produto']].count()
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']] \
    .merge(vendas_estados, left_on = 'Local da compra', right_index= True) \
    .sort_values('Produto', ascending= False) \
    .rename(columns = {'Produto': 'Quantidade'})

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Produto'] \
    .count() \
    .reset_index()\
    .rename(columns = {'Produto': 'Quantidade'})
    
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Produto']] \
    .count()  \
    .rename(columns = {'Produto' : 'Quantidade'}) \
    .sort_values('Quantidade', ascending = False)
    
    # Vendedores
    
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

    # Receita
    
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_data = {'lat': False, 'lon': False},
                                  hover_name = 'Local da compra',
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estado = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top 5 Estados com maior receita')

fig_receita_estado.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria') # Não precisa de x e y pois só há duas informações

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

    # Quantidade de vendas

fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Quantidade',
                                 template = 'seaborn',
                                 hover_data = {'lat': False, 'lon': False},
                                 hover_name = 'Local da compra',
                                 title = 'Vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mês',
                             y = 'Quantidade',
                             markers = True,
                             range_y = (0, vendas_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Vendas mensais')

fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade')

fig_vendas_estado = px.bar(vendas_estados.head(),
                            x = 'Local da compra',
                            y = 'Quantidade',
                            text_auto = True,
                            title = 'Top 5 Estados com maior venda')

fig_vendas_estado.update_layout(yaxis_title = 'Quantidade')

fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por categoria') # Não precisa de x e y pois só há duas informações

fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade')

# Algumas métricas podem ser feitas, como a receita total e a quantidade de vendas
# Delta permite mostrar se houve variação; help coloca texto explicativo. label_visibility define a visibilidade do rótulo
# Para construir mais de uma coluna, deve-se procurar a documentação de layouts e containers

## VISUALIZAÇÃO DO STREAMLIT

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estado, use_container_width = True)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estado, use_container_width = True)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False ).head(qtd_vendedores),
            x = 'sum',
            y = vendedores[['sum']].sort_values('sum', ascending = False ).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores em receita')
        st.plotly_chart(fig_receita_vendedores, use_container_width = True)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False ).head(qtd_vendedores),
            x = 'count',
            y = vendedores[['count']].sort_values('count', ascending = False ).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores em quantidade')
        st.plotly_chart(fig_vendas_vendedores, use_container_width = True)

# Mostra-se o DataFrame no aplicativo por meio do Magic ou pela documentação, na melhor forma de direcionar a visualização

# st.dataframe(dados)

# Criação de um gráfico de mapa, com a receita total para cada estado como uma bolha
# st.map apenas cria pontos em uma mapa, não consegue vincular mais informações


