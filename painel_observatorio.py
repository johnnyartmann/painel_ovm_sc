import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
# Usar o modo 'wide' para aproveitar melhor o espaço da tela
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- FUNÇÕES PARA GERAR DADOS DE EXEMPLO ---
# ATENÇÃO: Substitua o carregamento destes dados pelos seus arquivos reais.
# Exemplo: df_geral = pd.read_csv('sua_base_1.csv')
@st.cache_data
def carregar_dados_gerais():
    """
    Cria um DataFrame de exemplo simulando a Base 1 (dados gerais).
    """
    municipios = [
        "Florianópolis", "Joinville", "Blumenau", "São José", "Criciúma",
        "Chapecó", "Itajaí", "Lages", "Jaraguá do Sul", "Palhoça"
    ]
    fatos = [
        "Ameaça", "Lesão Corporal Dolosa", "Estupro", "Vias de fato",
        "Injúria", "Difamação"
    ]
    
    # Criando uma base de dados sintética
    num_registros = 5000
    np.random.seed(42)
    datas = pd.to_datetime(pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 365*5, num_registros), 'd'))
    
    df = pd.DataFrame({
        'data_fato': datas,
        'municipio': np.random.choice(municipios, num_registros),
        'fato_comunicado': np.random.choice(fatos, num_registros, p=[0.4, 0.2, 0.05, 0.15, 0.1, 0.1]),
        'idade_vitima': np.random.randint(14, 75, num_registros)
    })
    df['ano'] = df['data_fato'].dt.year
    df['mes'] = df['data_fato'].dt.month_name()
    return df

@st.cache_data
def carregar_dados_feminicidio():
    """
    Cria um DataFrame de exemplo simulando a Base 2 (feminicídios).
    """
    relacao = [
        "Companheiro(a)", "Ex-companheiro(a)", "Cônjuge", "Ex-cônjuge",
        "Namorado(a)", "Pai/Mãe", "Outro Parente"
    ]
    meio = [
        "Arma de Fogo", "Arma Branca", "Agressão Física",
        "Asfixia/Esganadura", "Outro"
    ]
    
    # Criando base sintética
    num_registros = 250
    np.random.seed(0)
    datas = pd.to_datetime(pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 365*5, num_registros), 'd'))
    
    df = pd.DataFrame({
        'data_fato': datas,
        'relacao_autor': np.random.choice(relacao, num_registros),
        'meio_crime': np.random.choice(meio, num_registros, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
        'idade_vitima': np.random.randint(18, 65, num_registros),
        'idade_autor': np.random.randint(20, 70, num_registros),
        'autor_preso': np.random.choice(["SIM", "NÃO", "SUICÍDIO"], num_registros, p=[0.7, 0.2, 0.1])
    })
    df['ano'] = df['data_fato'].dt.year
    return df

# Carregar os dados
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()


# --- BARRA LATERAL (SIDEBAR) PARA FILTROS ---
st.sidebar.image("https://i.imgur.com/805nJ3j.png", width=80)
st.sidebar.title("Observatório da Violência Contra a Mulher")
st.sidebar.header("Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df_geral['ano'].unique())
ano_selecionado = st.sidebar.multiselect(
    "Selecione o Ano",
    options=anos_disponiveis,
    default=anos_disponiveis  # Por padrão, todos os anos são selecionados
)

# Filtro de Tipo de Crime
fatos_disponiveis = sorted(df_geral['fato_comunicado'].unique())
fato_selecionado = st.sidebar.multiselect(
    "Selecione o Tipo de Crime",
    options=fatos_disponiveis,
    default=fatos_disponiveis
)

# Aplicar filtros aos dataframes
df_geral_filtrado = df_geral[
    (df_geral['ano'].isin(ano_selecionado)) &
    (df_geral['fato_comunicado'].isin(fato_selecionado))
]

df_feminicidio_filtrado = df_feminicidio[
    df_feminicidio['ano'].isin(ano_selecionado)
]


# --- ESTRUTURA COM ABAS (TABS) ---
tab_geral, tab_feminicidio, tab_glossario = st.tabs([
    "📊 Análise Geral da Violência", 
    "🚨 Análise de Feminicídios",
    "📖 Metodologia e Glossário"
])


# --- ABA 1: ANÁLISE GERAL ---
with tab_geral:
    st.header("Violência Contra a Mulher em Santa Catarina")
    st.markdown("Visão geral dos registros de ocorrências.")

    # KPIs (Indicadores Chave de Performance)
    total_registros = df_geral_filtrado.shape[0]
    media_idade_vitima = df_geral_filtrado['idade_vitima'].mean()
    
    # Organizar KPIs em colunas
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Registros de Crime", value=f"{total_registros:,}".replace(",", "."))
    with col2:
        st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
    
    st.markdown("---")

    # Gráficos em duas colunas
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # Gráfico 1: Quantidade de registros por ano
        st.subheader("Registros de Ocorrências por Ano")
        registros_por_ano = df_geral_filtrado['ano'].value_counts().sort_index()
        fig_ano = px.bar(
            registros_por_ano,
            x=registros_por_ano.index,
            y=registros_por_ano.values,
            labels={'x': 'Ano', 'y': 'Quantidade de Registros'},
            template='plotly_white',
            text=registros_por_ano.values
        )
        fig_ano.update_traces(marker_color='#8A2BE2', textposition='outside')
        st.plotly_chart(fig_ano, use_container_width=True)

    with col_graf2:
        # Gráfico 2: Quantidade de registros por tipo de crime
        st.subheader("Tipos de Crimes Mais Frequentes")
        registros_por_fato = df_geral_filtrado['fato_comunicado'].value_counts()
        fig_fato = px.bar(
            registros_por_fato,
            x=registros_por_fato.values,
            y=registros_por_fato.index,
            orientation='h',
            labels={'x': 'Quantidade de Registros', 'y': 'Tipo de Crime'},
            template='plotly_white',
            text=registros_por_fato.values
        )
        fig_fato.update_traces(marker_color='#9370DB', textposition='auto')
        fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_fato, use_container_width=True)


# --- ABA 2: ANÁLISE DE FEMINICÍDIOS ---
with tab_feminicidio:
    st.header("Análise de Feminicídios Consumados")
    st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")
    
    # KPIs
    total_feminicidios = df_feminicidio_filtrado.shape[0]
    idade_media_vitima_fem = df_feminicidio_filtrado['idade_vitima'].mean()
    idade_media_autor_fem = df_feminicidio_filtrado['idade_autor'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total de Feminicídios", value=total_feminicidios)
    with col2:
        st.metric(label="Idade Média da Vítima", value=f"{idade_media_vitima_fem:.1f} anos")
    with col3:
        st.metric(label="Idade Média do Autor", value=f"{idade_media_autor_fem:.1f} anos")
        
    st.markdown("---")
    
    # Gráficos em duas colunas
    col_graf_fem1, col_graf_fem2 = st.columns(2)
    
    with col_graf_fem1:
        # Gráfico 3: Vínculo entre vítima e autor
        st.subheader("Vínculo entre a Vítima e o Autor")
        vinculo_autor = df_feminicidio_filtrado['relacao_autor'].value_counts()
        fig_vinculo = px.pie(
            values=vinculo_autor.values,
            names=vinculo_autor.index,
            hole=.4, # Para criar um gráfico de rosca (donut)
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        st.plotly_chart(fig_vinculo, use_container_width=True)
        
    with col_graf_fem2:
        # Gráfico 4: Meio utilizado no crime
        st.subheader("Meio Utilizado para o Crime")
        meio_crime = df_feminicidio_filtrado['meio_crime'].value_counts()
        fig_meio = px.bar(
            meio_crime,
            x=meio_crime.index,
            y=meio_crime.values,
            labels={'x': 'Meio Utilizado', 'y': 'Quantidade'},
            template='plotly_white',
            text=meio_crime.values
        )
        fig_meio.update_traces(marker_color='#8A2BE2', textposition='outside')
        st.plotly_chart(fig_meio, use_container_width=True)

# --- ABA 3: GLOSSÁRIO ---
with tab_glossario:
    st.header("Metodologia e Glossário")
    
    st.subheader("Metodologia")
    st.markdown("""
    Os dados que constam neste painel foram fornecidos pela Gerência de Estatística e Análise Criminal da Secretaria de Estado da Segurança Pública - GEAC | DINE | SSP | SC.
    
    Eles foram organizados e processados para possibilitar clareza no entendimento das informações e permitir a interação dos usuários.
    
    A elaboração do painel é uma parceria entre o Observatório da Violência Contra a Mulher (OVM/SC) e o Ministério Público de Contas de Santa Catarina (MPC/SC).
    """)
    
    st.subheader("Glossário de Tipos de Crimes")
    st.markdown("""
    - **Ameaça:** Ameaçar alguém, por palavra, escrito ou gesto, ou qualquer outro meio simbólico, de causar-lhe mal injusto e grave.
    - **Lesão Corporal Dolosa:** A lesão corporal caracteriza-se por ofender a integridade corporal ou a saúde de outrem. O crime doloso ocorre quando o agente quis o resultado ou assumiu o risco de produzi-lo.
    - **Estupro:** Constranger alguém, mediante violência ou grave ameaça, a ter conjunção carnal ou a praticar ou permitir que com ele se pratique outro ato libidinoso.
    - **Feminicídio:** Homicídio contra a mulher por razões da condição de sexo feminino. Considera-se que há razões de condição de sexo feminino quando o crime envolve: violência doméstica e familiar ou menosprezo ou discriminação à condição de mulher.
    - **Vias de fato:** São atos agressivos praticados contra alguém, que não cheguem a causar lesão corporal. Exemplos: empurrar, sacudir, puxar cabelo, etc.
    """)
    st.markdown("---")
    st.info("Fonte: Código Penal Brasileiro, Lei do Feminicídio (Lei nº 13.104/2015), Lei Maria da Penha (Lei nº 11.340/2.006).")