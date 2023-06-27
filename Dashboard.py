## Bibliotecas

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
## Funcoes
def format_number(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor<1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

## Titulo
st.title('Dashboard do Mariano :nerd_face: ')

## Dados
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'região':regiao.lower(), 'ano':ano} # lower: colocamos maiuscula na lista pra ficar bonito, mas api só aceita minuscula

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    

## Tabelas
### Tabelas de receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas de quantidade de vendas
vendas_estado = pd.DataFrame(dados.groupby('Local da compra')['Preço'].agg(['count']))
vendas_estado = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on = 'Local da compra', right_index = True).sort_values('count', ascending=False)


vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Produto'].count().reset_index()
vendas_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

### Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

## Receitas

# Receita por estado
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon' : False},
                                  title = 'Receita por estado'
                                  )
# Receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y= (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal'
                             )
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Top 5 Estados
fig_receita_estados = px.bar( receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Vendas

# (mapa) Vendas por estado
fig_vendas_mapa = px.scatter_geo(vendas_estado,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'count',
                                  template = 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon' : False},
                                  title = 'Qtd Vendas por estado'
                                  )
# (linhas) Qtd vendas mensal
fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mes',
                             y = 'Produto',
                             markers = True,
                             range_y= (0, vendas_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Qtd Vendas mensal'
                             )
fig_vendas_mensal.update_layout(yaxis_title = 'Qtde')

# (barras) 5 estados com maior qtd vendas
fig_vendas_estados = px.bar( vendas_estado.head(),
                             x='Local da compra',
                             y='count',
                             text_auto=True,
                             title='Top estados (Qtd)')

# (barras) Qtde Vendas por Categoria
fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto=True,
                                title='Qtd Vendas por categoria')

fig_vendas_categorias.update_layout(yaxis_title = 'Qtde', showlegend=False)



# Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])


with aba1: #Receita
    coluna1, coluna2 = st.columns(2)
    # Receita Total
    with coluna1: 
        st.metric('Receita', format_number(dados['Preço'].sum(), 'R$'))
        st.plotly_chart (fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    # Qtd Vendas
    with coluna2:
        st.metric('Qtd Vendas', format_number(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2: #Qtd Vendas
    coluna1, coluna2 = st.columns(2)
    with coluna1: 
        st.metric('Receita', format_number(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_vendas_mapa)
        st.plotly_chart(fig_vendas_estados)

    with coluna2:
        st.metric('Qtd Vendas', format_number(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal)
        st.plotly_chart(fig_vendas_categorias)


with aba3: #Vendedores
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1: 
        st.metric('Receita', format_number(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y= vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)' )
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Qtd Vendas', format_number(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y= vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (Qtd Vendas)' )
        st.plotly_chart(fig_vendas_vendedores)
