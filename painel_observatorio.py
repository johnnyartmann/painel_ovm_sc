import pandas as pd
import streamlit as st
from data_loader import carregar_dados_processados
from tabs import (analise_feminicidios, analise_geral, analises_avancadas,
                  download, glossario)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    /* ... (seu CSS existente) ... */
</style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DOS DADOS ---
dfs, geojson_data = carregar_dados_processados()

if dfs is not None and geojson_data is not None:
    st.session_state.df_geral = dfs.get('geral', pd.DataFrame())
    st.session_state.df_feminicidio = dfs.get('feminicidio', pd.DataFrame())
    st.session_state.df_populacao = dfs.get('populacao', pd.DataFrame())
    st.session_state.df_regioes = dfs.get('regioes', pd.DataFrame())
    st.session_state.df_calendario = dfs.get('calendario', pd.DataFrame())
    st.session_state.geojson_sc = geojson_data
else:
    st.error("🚨 Falha no carregamento dos dados processados.")
    st.warning("Execute o script 'preprocess_data.py' para gerar os arquivos de dados necessários.")
    st.stop()

# --- SIDEBAR E FILTROS ---
st.sidebar.image("logo_ovm.jpeg", use_container_width=True)

tab_geral, tab_feminicidio, tab_analises_avancadas, tab_glossario, tab_download = st.tabs([
    "📊 Análise Geral",
    "🚨 Análise de Feminicídios",
    "🔬 Análises Avançadas",
    "📖 Metodologia e Glossário",
    "📥 Download de Dados"
])

if not st.session_state.df_geral.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")

        # --- VISUALIZAÇÃO / AGRUPAMENTO ---
        st.subheader("📊 VISUALIZAR POR")
        st.session_state.agrupamento_selecionado = st.selectbox(
            "Agrupar por",
            options=["Consolidado", "Município", "Mesorregião", "Associação"],
            index=0,
            help="Escolha como os dados devem ser agrupados nos gráficos e tabelas."
        )

        # --- PERÍODO ---
        st.subheader("📅 PERÍODO")
        min_date = st.session_state.df_geral['data_fato'].min().date()
        max_date = st.session_state.df_geral['data_fato'].max().date()

        st.session_state.data_inicial = st.date_input(
            "Data Inicial",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            help="Selecione a data de início do período."
        )

        st.session_state.data_final = st.date_input(
            "Data Final",
            value=max_date,
            min_value=st.session_state.data_inicial,
            max_value=max_date,
            help="Selecione a data de fim do período."
        )

        df_geral_filtrado_por_data = st.session_state.df_geral[
            (st.session_state.df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
            (st.session_state.df_geral['data_fato'].dt.date <= st.session_state.data_final)
        ]

        # --- LOCALIZAÇÃO ---
        st.subheader("📍 LOCALIZAÇÃO")
        municipios_disponiveis = sorted(df_geral_filtrado_por_data['municipio'].dropna().unique())
        todos_municipios = st.checkbox("Todos os municípios", value=True, help="Marque para selecionar todos")

        if todos_municipios:
            municipio_selecionado = municipios_disponiveis
        else:
            municipio_selecionado = st.multiselect(
                "Município(s) específico(s)",
                options=municipios_disponiveis,
                default=[]
            )
            if not municipio_selecionado:
                municipio_selecionado = municipios_disponiveis

        # --- TIPO DE CRIME ---
        st.subheader("🚨 TIPO DE CRIME")
        fatos_disponiveis = sorted(st.session_state.df_geral['fato_comunicado'].unique())
        todos_crimes = st.checkbox("Todos os tipos", value=True, help="Marque para incluir todos os crimes")

        if todos_crimes:
            fato_selecionado = fatos_disponiveis
        else:
            fato_selecionado = st.multiselect(
                "Tipo(s) de crime",
                options=fatos_disponiveis,
                default=[]
            )
            if not fato_selecionado:
                fato_selecionado = fatos_disponiveis

        # --- LÓGICA DE FILTRAGEM FINAL ---
        st.session_state.df_geral_filtrado = df_geral_filtrado_por_data[
            (df_geral_filtrado_por_data['municipio'].isin(municipio_selecionado)) &
            (df_geral_filtrado_por_data['fato_comunicado'].isin(fato_selecionado))
        ].copy()

        st.session_state.df_feminicidio_filtrado = st.session_state.df_feminicidio[
            (st.session_state.df_feminicidio['data_fato'].dt.date >= st.session_state.data_inicial) &
            (st.session_state.df_feminicidio['data_fato'].dt.date <= st.session_state.data_final) &
            (st.session_state.df_feminicidio['municipio'].isin(municipio_selecionado))
        ].copy()

    with tab_geral:
        analise_geral.render()
    with tab_feminicidio:
        analise_feminicidios.render()
    with tab_analises_avancadas:
        analises_avancadas.render()
    with tab_glossario:
        glossario.render()
    with tab_download:
        download.render()
else:
    st.error("🚨 Nenhum dado para exibir.")
    st.warning("Verifique se os filtros aplicados não resultaram em uma seleção vazia.")