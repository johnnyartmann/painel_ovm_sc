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
    Carrega e trata os dados da base geral de forma robusta.
    """
    try:
        df = pd.read_excel('data/base_geral.xlsx')

        df.columns = (df.columns.str.strip()
                      .str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ú', 'u', regex=False))

        df.rename(columns={
            'data_do_fato': 'data_fato',
            'município': 'municipio',
            'mesoregião': 'mesoregiao',
            'fato_comunicado': 'fato_comunicado',
            'idade': 'idade_vitima'
        }, inplace=True)

        # --- Tratamento de Dados Essencial ---
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        
        # --- NOVA LINHA ADICIONADA AQUI ---
        # Força a coluna 'idade_vitima' a ser numérica, tratando erros.
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        
        df['ano'] = df['data_fato'].dt.year
        df['mes'] = df['data_fato'].dt.month_name()
        
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base geral: A coluna {e} não foi encontrada. Verifique o nome no arquivo Excel.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_feminicidio():
    """
    Carrega e trata os dados da base de feminicídio de forma robusta.
    """
    try:
        df = pd.read_excel('data/base_feminicidio.xlsx')

        # Etapa de limpeza automática de colunas
        df.columns = (df.columns.str.strip()
                      .str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False))

        # --- CORREÇÃO APLICADA AQUI ---
        # A chave agora corresponde exatamente ao nome da coluna após a limpeza.
        df.rename(columns={
            'relacao_com_o_autor': 'relacao_autor', # Chave corrigida (sem acentos)
            'município': 'municipio',
            'idade_autor': 'idade_autor',
            'prisão': 'autor_preso',
            'idade_vitima': 'idade_vitima',
            'meio': 'meio_crime'
        }, inplace=True)
        
        if 'data' in df.columns:
            df.rename(columns={'data':'data_fato'}, inplace=True)

        # Tratamento de Dados Essencial
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        df['idade_autor'] = pd.to_numeric(df['idade_autor'], errors='coerce')
        df['ano'] = df['data_fato'].dt.year
        
        return df

    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base de feminicídio: A coluna {e} não foi encontrada. Verifique o nome no arquivo Excel.")
        # Linha de depuração útil:
        st.write("Colunas encontradas após limpeza:", df.columns.tolist())
        return pd.DataFrame()

# Carregar os dados
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()


# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://i.imgur.com/805nJ3j.png", width=80)
st.sidebar.title("Observatório da Violência Contra a Mulher")

# --- ESTRUTURA COM ABAS (TABS) ---
tab_geral, tab_feminicidio, tab_glossario = st.tabs([
    "📊 Análise Geral da Violência",
    "🚨 Análise de Feminicídios",
    "📖 Metodologia e Glossário"
])

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
# A verificação agora engloba toda a lógica de filtros e exibição de dados.
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

    # --- ABA 1: ANÁLISE GERAL ---
    with tab_geral:
        st.header("Violência Contra a Mulher em Santa Catarina")
        st.markdown("Visão geral dos registros de ocorrências.")

        # KPIs (Indicadores Chave de Performance)
        total_registros = df_geral_filtrado.shape[0]
        
        # Calcula a média de idade apenas se houver registros
        media_idade_vitima = 0.0
        if not df_geral_filtrado.empty:
            media_idade_vitima = df_geral_filtrado['idade_vitima'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total de Registros de Crime", value=f"{total_registros:,}".replace(",", "."))
        with col2:
            st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
        
        st.markdown("---")

        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader("Registros de Ocorrências por Ano")
            registros_por_ano = df_geral_filtrado['ano'].value_counts().sort_index()
            fig_ano = px.bar(
                registros_por_ano, x=registros_por_ano.index, y=registros_por_ano.values,
                labels={'x': 'Ano', 'y': 'Quantidade de Registros'}, template='plotly_white',
                text=registros_por_ano.values
            )
            fig_ano.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_ano, use_container_width=True)

        with col_graf2:
            st.subheader("Tipos de Crimes Mais Frequentes")
            registros_por_fato = df_geral_filtrado['fato_comunicado'].value_counts()
            fig_fato = px.bar(
                registros_por_fato, x=registros_por_fato.values, y=registros_por_fato.index,
                orientation='h', labels={'x': 'Quantidade de Registros', 'y': 'Tipo de Crime'},
                template='plotly_white', text=registros_por_fato.values
            )
            fig_fato.update_traces(marker_color='#9370DB', textposition='auto')
            fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_fato, use_container_width=True)

    # --- ABA 2: ANÁLISE DE FEMINICÍDIOS ---
    with tab_feminicidio:
        st.header("Análise de Feminicídios Consumados")
        st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")
    
        total_feminicidios = df_feminicidio_filtrado.shape[0]
    
        # 1. Calcule as médias como antes
        idade_media_vitima_fem = df_feminicidio_filtrado['idade_vitima'].mean()
        idade_media_autor_fem = df_feminicidio_filtrado['idade_autor'].mean()

        # 2. Crie as variáveis de texto para exibição
        # Para a idade da vítima
        if pd.isna(idade_media_vitima_fem):
            texto_idade_vitima = "Dados Insuficientes"
        else:
            texto_idade_vitima = f"{idade_media_vitima_fem:.1f} anos"

        # Para a idade do autor
        if pd.isna(idade_media_autor_fem):
            texto_idade_autor = "Dados Insuficientes"
        else:
            texto_idade_autor = f"{idade_media_autor_fem:.1f} anos"

        # 3. Use as novas variáveis de texto nos KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total de Feminicídios", value=total_feminicidios)
        with col2:
            st.metric(label="Idade Média da Vítima", value=texto_idade_vitima)
        with col3:
            st.metric(label="Idade Média do Autor", value=texto_idade_autor)
        
        st.markdown("---")
        
        col_graf_fem1, col_graf_fem2 = st.columns(2)
        with col_graf_fem1:
            st.subheader("Vínculo entre a Vítima e o Autor")
            vinculo_autor = df_feminicidio_filtrado['relacao_autor'].value_counts()
            fig_vinculo = px.pie(
                values=vinculo_autor.values, names=vinculo_autor.index, hole=.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            st.plotly_chart(fig_vinculo, use_container_width=True)
            
        with col_graf_fem2:
            st.subheader("Meio Utilizado para o Crime")
            meio_crime = df_feminicidio_filtrado['meio_crime'].value_counts()
            fig_meio = px.bar(
                meio_crime, x=meio_crime.index, y=meio_crime.values,
                labels={'x': 'Meio Utilizado', 'y': 'Quantidade'}, template='plotly_white',
                text=meio_crime.values
            )
            fig_meio.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_meio, use_container_width=True)

else:
    # Mensagem de erro se os dados não puderem ser carregados
    with tab_geral:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data` e que os nomes das colunas estão corretos.")
    with tab_feminicidio:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data` e que os nomes das colunas estão corretos.")


# --- ABA 3: GLOSSÁRIO (Sempre visível) ---
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
