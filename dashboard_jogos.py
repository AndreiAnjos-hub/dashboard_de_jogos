# Dashboard de Jogos

import pandas as pd
import streamlit as st  
import plotly.express as px

st.set_page_config(page_title="Dashboard de Jogos", layout="wide")
st.title("🎮 Dashboard de Vendas de Jogos")
st.markdown("---")

df = pd.read_csv('vgsales.csv')

for coluna_reais in ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]:
    df[coluna_reais] = df[coluna_reais].astype(float)

st.header("1. Métricas Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_jogos = df['Name'].nunique()
    st.metric("Total de Jogos Únicos", f"{total_jogos}")
with col2:
    ano_antigo = int(df['Year'].min())
    ano_recente = int(df['Year'].max())
    st.metric("Ano do Jogo Mais Antigo", f"{ano_antigo}")
    st.metric("Ano do Jogo Mais Recente", f"{ano_recente}")
with col3:
    media_vendas = df['Global_Sales'].mean()
    st.metric("Média Global de Vendas", f"{media_vendas:.2f} milhões")
with col4:
    editora_top = df['Publisher'].value_counts().idxmax()
    total_publicados = df['Publisher'].value_counts().max()
    st.metric("Editora com + Jogos", f"{editora_top} ({total_publicados})")

st.markdown("---")
st.header("Top Jogos por Vendas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    plataforma = st.selectbox("Selecione a Plataforma:", options=["Todas"] + sorted(df['Platform'].dropna().unique().tolist()))
with col2:
    genero = st.selectbox("Selecione o Gênero:", options=["Todos"] + sorted(df['Genre'].dropna().unique().tolist()))
with col3:
    editora = st.selectbox("Selecione a Editora:", options=["Todas"] + sorted(df['Publisher'].dropna().unique().tolist()))
with col4:
    vendas_opcao = st.selectbox("Tipo de Vendas:", options=["Global_Sales", "NA_Sales", "EU_Sales", "JP_Sales"])

df_filtrado = df.copy()

if plataforma != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Platform'] == plataforma]
if genero != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Genre'] == genero]
if editora != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Publisher'] == editora]

top_n = st.slider("Número de Jogos para Exibir:", min_value=5, max_value=20, value=10)
top_jogos = df_filtrado.sort_values(by=vendas_opcao, ascending=False).head(top_n)

fig = px.bar(
    top_jogos,
    x=vendas_opcao,
    y='Name',
    orientation='h',
    title=f"Top {top_n} Jogos - {vendas_opcao.replace('_', ' ')}",
    hover_data={'Platform': True, 'Year': True, 'Publisher': True},
    labels={vendas_opcao: 'Vendas (em milhões)', 'Name': 'Nome do Jogo'}
)

fig.update_layout(yaxis={'categoryorder':'total ascending'}) 
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("2. Distribuição de Vendas por Região")

df['Decada'] = (df['Year'] // 10) * 10

decadas_disponiveis = sorted(df['Decada'].dropna().unique())
decada_escolhida = st.selectbox('Filtrar por Década:', options=['Todas'] + [f"{int(d)}-{int(d)+9}" for d in decadas_disponiveis])

df_filtrado = df.copy()

if decada_escolhida != 'Todas':
    inicio_decada = int(decada_escolhida.split('-')[0])
    fim_decada = int(decada_escolhida.split('-')[1])
    df_filtrado = df_filtrado[(df_filtrado['Year'] >= inicio_decada) & (df_filtrado['Year'] <= fim_decada)]

vendas_por_regiao = {
    'Região': ['América do Norte', 'Europa', 'Japão', 'Outras Regiões'],
    'Vendas': [
        df_filtrado['NA_Sales'].sum(),
        df_filtrado['EU_Sales'].sum(),
        df_filtrado['JP_Sales'].sum(),
        df_filtrado['Other_Sales'].sum()
    ]
}

df_vendas = pd.DataFrame(vendas_por_regiao)
df_vendas['Percentual'] = (df_vendas['Vendas'] / df_vendas['Vendas'].sum()) * 100

tipo_grafico = st.radio("Tipo de Gráfico:", ["Pizza", "Treemap"])

if tipo_grafico == "Pizza":
    fig = px.pie(df_vendas, values='Vendas', names='Região',
                 title='Distribuição Percentual de Vendas por Região (Pizza)',
                 hover_data=['Percentual'],
                 labels={'Percentual': '%'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
else:
    fig = px.treemap(
        df_vendas,
        path=['Região'],
        values='Vendas',
        title='Distribuição Percentual de Vendas por Região (Treemap)',
        hover_data={'Percentual': ':.2f'}
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("3. Distribuição de Vendas por Gênero")

df_grouped = df.groupby(['Year', 'Genre'])[['Global_Sales']].sum().reset_index()

fig = px.bar(df_grouped, x='Year', y='Global_Sales', color='Genre', title='Vendas Globais por Gênero',
             labels={'Global_Sales': 'Vendas Globais', 'Year': 'Ano'}, 
             barmode='stack')
st.plotly_chart(fig)

st.markdown("---")
st.header("4. Análise de Vendas de Jogos")

ano_min = int(df['Year'].min())
ano_max = int(df['Year'].max())

intervalo_anos = st.slider('Selecione o intervalo de anos:', ano_min, ano_max, (ano_min, ano_max))
df_filtrado = df[(df['Year'] >= intervalo_anos[0]) & (df['Year'] <= intervalo_anos[1])]

tab_generos, tab_temporal = st.tabs(["📊 Popularidade de Gêneros", "📈 Tendências Temporais"])

with tab_generos:
    st.subheader(f"Popularidade de Gêneros por Região ({intervalo_anos[0]} - {intervalo_anos[1]})")

    df_genero_regiao = df_filtrado.groupby('Genre')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()

    df_genero_melt = df_genero_regiao.melt(id_vars='Genre', 
                                           value_vars=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
                                           var_name='Região',
                                           value_name='Vendas')

    df_genero_melt['Região'] = df_genero_melt['Região'].map({
        'NA_Sales': 'América do Norte',
        'EU_Sales': 'Europa',
        'JP_Sales': 'Japão',
        'Other_Sales': 'Outras regiões'
    })

    fig = px.bar(df_genero_melt, 
                 x='Genre', 
                 y='Vendas', 
                 color='Região',
                 labels={'Genre': 'Gênero', 'Vendas': 'Vendas (em milhões)'},
                 barmode='stack')

    fig.update_layout(xaxis_title="Gênero", yaxis_title="Vendas Totais", 
                      legend_title="Região", 
                      xaxis={'categoryorder':'total descending'})

    st.plotly_chart(fig, use_container_width=True)

with tab_temporal:
    st.subheader(f"Tendências Temporais de Vendas Globais ({intervalo_anos[0]} - {intervalo_anos[1]})")

    df_temporal = df_filtrado.groupby('Year')['Global_Sales'].sum().reset_index()

    fig = px.line(
        df_temporal,
        x='Year', 
        y='Global_Sales', 
        labels={'Global_Sales': 'Vendas Globais (milhões)', 'Year': 'Ano'},
        markers=True
    )

    fig.add_hline(y=df_temporal['Global_Sales'].mean(), line_dash="dash", line_color="green",
                  annotation_text="Média Global", annotation_position="bottom right")

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("5. Busca de Jogos")

nome_jogo = st.text_input("Digite o nome do jogo:")

if nome_jogo:
    df_exato = df[df['Name'].str.lower() == nome_jogo.lower()]

    if not df_exato.empty:
        st.success("Jogo encontrado com o nome exato!")

        st.dataframe(df_exato[['Name', 'Platform', 'Year', 'Genre', 'Publisher', 
                               'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']])

        jogo = df_exato.iloc[0]

        st.subheader(f"Análise de Vendas do {jogo['Name']}")

        tipo_grafico = st.radio("Tipo de gráfico:", ["Barras", "Pizza"])

        vendas = {
            'Região': ['América do Norte', 'Europa', 'Japão', 'Outros'],
            'Vendas': [jogo['NA_Sales'], jogo['EU_Sales'], jogo['JP_Sales'], jogo['Other_Sales']]
        }
        df_vendas = pd.DataFrame(vendas)

        if tipo_grafico == "Barras":
            fig = px.bar(df_vendas, x='Região', y='Vendas', 
                         title=f"Vendas por Região - {jogo['Name']}",
                         labels={'Vendas': 'Vendas (em milhões)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.pie(df_vendas, values='Vendas', names='Região',
                         title=f"Vendas por Região - {jogo['Name']}")
            st.plotly_chart(fig, use_container_width=True)

    else:
        df_resultado = df[df['Name'].str.contains(nome_jogo, case=False, na=False)]

        if not df_resultado.empty:
            st.success(f"{len(df_resultado)} jogo(s) parecido(s) encontrado(s):")
            st.dataframe(df_resultado[['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'NA_Sales',
                                       'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']])

            if len(df_resultado) == 1:
                jogo = df_resultado.iloc[0]

                st.subheader(f"Análise de Vendas - {jogo['Name']}")

                tipo_grafico = st.radio("Tipo de gráfico:", ["Barras", "Pizza"])

                vendas = {
                    'Região': ['América do Norte', 'Europa', 'Japão', 'Outros'],
                    'Vendas': [jogo['NA_Sales'], jogo['EU_Sales'], jogo['JP_Sales'], jogo['Other_Sales']]
                }
                df_vendas = pd.DataFrame(vendas)

                if tipo_grafico == "Barras":
                    fig = px.bar(df_vendas, x='Região', y='Vendas', 
                                 title=f"Vendas por Região - {jogo['Name']}",
                                 labels={'Vendas': 'Vendas (em milhões)'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = px.pie(df_vendas, values='Vendas', names='Região',
                                 title=f"Vendas por Região - {jogo['Name']}")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum jogo encontrado. Verifique o nome digitado.")
