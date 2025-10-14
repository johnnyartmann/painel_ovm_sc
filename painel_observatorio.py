import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- FUNÇÕES PARA CARREGAR OS DADOS DOS ARQUIVOS EXCEL ---
# ATENÇÃO: A mudança está aqui! Trocamos pd.read_csv por pd.read_excel

@st.cache_data
def carregar_dados_gerais():
    """
    Carrega e trata os dados da base geral a partir do arquivo Excel.
    """
    try:
        df = pd.read_excel('data/base_geral.xlsx') # Certifique-se que o nome do arquivo está correto

        # Renomeia as colunas usando os nomes da imagem para os nomes padrão do código
        df.rename(columns={
            'Data do Fato': 'data_fato',
            'Município': 'municipio',
            'Mesoregião': 'mesoregiao',
            'Fato Comunicado': 'fato_comunicado',
            'Idade': 'idade_vitima'  # Renomeando 'Idade' para 'idade_vitima' para ser mais específico
        }, inplace=True)

        # --- Tratamento de Dados Essencial ---
        # Agora usamos a nova coluna 'data_fato' que acabamos de renomear
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['ano'] = df['data_fato'].dt.year
        df['mes'] = df['data_fato'].dt.month_name()
        
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' não encontrado na pasta 'data'. Verifique o nome do arquivo.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError): A coluna {e} não foi encontrada. "
                 "Isso pode acontecer se o cabeçalho no arquivo Excel mudou. "
                 "Verifique se as colunas 'Data do Fato', 'Município', etc., existem no arquivo.")
        return pd.DataFrame()
    
@st.cache_data
def carregar_dados_feminicidio():
    """
    Carrega e trata os dados da base de feminicídio a partir do arquivo Excel.
    """
    try:
        df = pd.read_excel('data/base_feminicidio.xlsx') # Certifique-se que o nome do arquivo está correto

        # Renomeia as colunas usando os nomes da imagem para os nomes padrão do código
        df.rename(columns={
            'DATA': 'data_fato',
            'MUNICÍPIO': 'municipio',
            'RELAÇÃO COM O AUTOR': 'relacao_autor',
            'IDADE AUTOR': 'idade_autor',
            'PRISÃO': 'autor_preso',
            'IDADE VITIMA': 'idade_vitima',
            'MEIO': 'meio_crime'
            # Adicione outras colunas que você for usar aqui, se necessário
        }, inplace=True)

        # --- Tratamento de Dados Essencial ---
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['ano'] = df['data_fato'].dt.year
        
        return df

    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'. Verifique o nome do arquivo.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) no arquivo de feminicídio: A coluna {e} não foi encontrada. "
                 "Verifique se o cabeçalho no arquivo Excel corresponde ao esperado.")
        return pd.DataFrame()

# Carregar os dados
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()


# --- BARRA LATERAL (SIDEBAR) E O RESTO DA APLICAÇÃO ---
# O restante do seu código continua exatamente o mesmo.
st.sidebar.image("https://i.imgur.com/805nJ3j.png", width=80)
st.sidebar.title("Observatório da Violência Contra a Mulher")

# Verificação para evitar erros se os arquivos não forem carregados
if not df_geral.empty and not df_feminicidio.empty:
    st.sidebar.header("Filtros")
    
    # Filtro de Ano
    anos_disponiveis = sorted(df_geral['ano'].unique())
    ano_selecionado = st.sidebar.multiselect(
        "Selecione o Ano",
        options=anos_disponiveis,
        default=anos_disponiveis
    )

    # Filtro de Tipo de Crime
    # Usar 'fato_comunicado' (o nome renomeado), e não 'Fato Comunicado'
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
