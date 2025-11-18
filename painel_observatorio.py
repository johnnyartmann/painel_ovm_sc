import pandas as pd
import streamlit as st

from data_loader import (carregar_dados_calendario, carregar_dados_feminicidio, carregar_dados_gerais,
                         carregar_dados_populacao, carregar_dados_regioes, carregar_geojson_sc)
from tabs import analise_feminicidios, analise_geral, analises_avancadas, download, glossario

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    /* Importar fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Configurações globais */
    * {
        font_family: 'Inter', sans-serif;
    }
    
    /* Fundo principal */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Sidebar customizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4a148c 0%, #6a1b9a 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Corrigir a cor da fonte nos campos de data */
    [data-testid="stSidebar"] [data-baseweb="base-input"] input {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    /* Headers principais */
    h1 {
        color: #4a148c;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 4px solid #8e24aa;
    }
    
    h2 {
        color: #6a1b9a;
        font-weight: 600;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #7b1fa2;
        font-weight: 600;
        font-size: 1.4rem;
        margin-top: 1.5rem;
    }
    
    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4a148c;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #6a1b9a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 5px solid #8e24aa;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.12);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        color: #6a1b9a;
        font-weight: 600;
        font-size: 1rem;
        padding: 0 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f3e5f5;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8e24aa 0%, #ab47bc 100%);
        color: white !important;
        box-shadow: 0 4px 8px rgba(142, 36, 170, 0.3);
    }
    
    /* Divisores */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #8e24aa, transparent);
    }
    
    /* Containers de gráficos */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        background: white;
        padding: 1rem;
        box-sizing: border-box;
        width: 100% !important;
    }
    
    /* Tabelas */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    [data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, #6a1b9a 0%, #8e24aa 100%);
        color: white !important;
        font-weight: 600;
        padding: 1rem;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stDataFrame"] td {
        padding: 0.8rem;
        border-bottom: 1px solid #f0f0f0;
    }
    
    [data-testid="stDataFrame"] tr:hover {
        background-color: #f8f4fb;
    }
    
    /* Alertas e mensagens */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
        padding: 1rem 1.5rem;
    }
    
    [data-baseweb="notification"][kind="error"] {
        border-left-color: #d32f2f;
    }
    
    [data-baseweb="notification"][kind="warning"] {
        border-left-color: #f57c00;
    }
    
    [data-baseweb="notification"][kind="info"] {
        border-left-color: #0288d1;
    }
    
    /* Expander na sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px;
        font-weight: 600;
        color: white !important;
        padding: 0.8rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        color: white !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader svg {
        fill: white !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.15);
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-top: none;
    }
    
    /* Checkbox na sidebar */
    [data-testid="stSidebar"] .stCheckbox {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    /* Info boxes na sidebar */
    [data-testid="stSidebar"] [data-testid="stNotification"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-left: 3px solid #fff !important;
        padding: 0.5rem !important;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    [data-testid="stSidebar"] [data-testid="stNotification"] p {
        color: white !important;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* Caption na sidebar */
    [data-testid="stSidebar"] .stCaptionContainer {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #8e24aa 0%, #ab47bc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(142, 36, 170, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(142, 36, 170, 0.4);
    }
    
    /* Select boxes e inputs na sidebar */
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="base-input"] {
        background-color: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
    [data-testid="stSidebar"] [data-baseweb="base-input"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    /* Marca d'água de rodapé */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #4a148c 0%, #6a1b9a 100%);
        color: white;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.85rem;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* Títulos das seções com ícones */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid #8e24aa;
    }
    
    .section-header h2 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    /* Animação de entrada */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem;
        }
        
        h2 {
            font-size: 1.4rem;
        }
        
        h3 {
            font-size: 1.2rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
        }

        /* Faz as colunas empilharem */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }

        /* Ajusta o espaçamento das abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            padding: 0.3rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0 1rem;
            height: 40px;
            font-size: 0.9rem;
        }

        /* Reduz o padding dos gráficos */
        .js-plotly-plot {
            padding: 0.5rem;
        }

        /* Rodapé fixo pode atrapalhar em telas menores */
        .footer {
            position: relative;
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DOS DADOS ---
st.session_state.geojson_sc = carregar_geojson_sc()
st.session_state.df_geral = carregar_dados_gerais()
st.session_state.df_feminicidio = carregar_dados_feminicidio()
st.session_state.df_populacao = carregar_dados_populacao()
st.session_state.df_regioes = carregar_dados_regioes()
st.session_state.df_calendario = carregar_dados_calendario()

# --- SIDEBAR E FILTROS ---
st.sidebar.image("logo_ovm.jpeg", use_container_width=True)

tab_geral, tab_feminicidio, tab_analises_avancadas, tab_glossario, tab_download = st.tabs([
    "📊 Análise Geral",
    "🚨 Análise de Feminicídios",
    "🔬 Análises Avançadas",
    "📖 Metodologia e Glossário",
    "📥 Download de Dados"
])

if not st.session_state.df_geral.empty and not st.session_state.df_feminicidio.empty and st.session_state.geojson_sc is not None and not st.session_state.df_populacao.empty and not st.session_state.df_calendario.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")

        # --- VISUALIZAÇÃO / AGRUPAMENTO (MOVIMENTEI PARA CIMA) ---
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
            st.info(f"✓ 295 municípios selecionados")
        else:
            municipio_selecionado = st.multiselect(
                "Município(s) específico(s)",
                options=municipios_disponiveis,
                default=[],
                help="Digite para buscar. Deixe vazio para todos"
            )
            if not municipio_selecionado:
                municipio_selecionado = municipios_disponiveis

        mesoregioes_disponiveis = sorted(
            [m for m in st.session_state.df_geral['mesoregiao'].unique() if m != 'Não informado'])
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)",
            options=mesoregioes_disponiveis,
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina"
        )

        associacoes_disponiveis = sorted(
            [a for a in st.session_state.df_geral['associacao'].dropna().unique() if a != 'Não informado'])
        associacao_selecionado = st.multiselect(
            "Associação(ões)",
            options=associacoes_disponiveis,
            default=associacoes_disponiveis,
            help="Filtre por associação de municípios"
        )

        # --- TIPO DE CRIME ---
        st.subheader("🚨 TIPO DE CRIME")
        fatos_disponiveis = sorted(st.session_state.df_geral['fato_comunicado'].unique())

        todos_crimes = st.checkbox("Todos os tipos", value=True, help="Marque para incluir todos os crimes")

        if todos_crimes:
            fato_selecionado = fatos_disponiveis
            st.info(f"✓ {len(fatos_disponiveis)} tipos selecionados")
        else:
            fato_selecionado = st.multiselect(
                "Tipo(s) de crime",
                options=fatos_disponiveis,
                default=[],
                help="Selecione tipos específicos de crime"
            )
            if not fato_selecionado:
                fato_selecionado = fatos_disponiveis

        # --- PERFIL DA VÍTIMA ---
        st.subheader("👥 PERFIL DA VÍTIMA")
        idade_selecionada = st.slider(
            "Faixa Etária",
            min_value=0,
            max_value=100,
            value=(0, 100),
            help="Ajuste o intervalo de idade das vítimas. Se o valor máximo for 100, incluirá todas as idades acima."
        )

        idade_max_texto = "100+ anos" if idade_selecionada[1] == 100 else f"{idade_selecionada[1]} anos"
        st.caption(f"Idades: {idade_selecionada[0]} a {idade_max_texto}")

        # --- CÁLCULOS PARA FILTROS POPULACIONAIS ---
        crimes_por_municipio_para_filtro = df_geral_filtrado_por_data[
            'municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio_para_filtro.columns = ['municipio_normalizado', 'total_fatos']

        df_populacional_metrics = pd.merge(
            st.session_state.df_populacao.copy(),
            crimes_por_municipio_para_filtro,
            on='municipio_normalizado',
            how='left'
        )
        df_populacional_metrics['total_fatos'] = df_populacional_metrics['total_fatos'].fillna(0)

        anos_no_filtro = df_geral_filtrado_por_data['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1

        df_populacional_metrics['media_anual_fatos'] = df_populacional_metrics['total_fatos'] / num_anos
        df_populacional_metrics['taxa_por_mil_mulheres'] = (
                                                                      (df_populacional_metrics['media_anual_fatos'] /
                                                                       df_populacional_metrics[
                                                                           'populacao_feminina']) * 1000).fillna(0)
        df_populacional_metrics['percentual_mulheres_vitimas'] = (
                                                                            (df_populacional_metrics[
                                                                                 'media_anual_fatos'] /
                                                                             df_populacional_metrics[
                                                                                 'populacao_feminina']) * 100).fillna(
            0)

        # --- FILTROS POPULACIONAIS ---
        st.subheader("📊 FILTROS POPULACIONAIS")

        min_pop = int(df_populacional_metrics['populacao_feminina'].min())
        max_pop = int(df_populacional_metrics['populacao_feminina'].max())
        pop_selecionada = st.slider(
            "População Feminina",
            min_value=min_pop, max_value=max_pop, value=(min_pop, max_pop)
        )

        min_media_fatos = float(df_populacional_metrics['media_anual_fatos'].min())
        max_media_fatos = float(df_populacional_metrics['media_anual_fatos'].max())
        media_fatos_selecionada = st.slider(
            "Média Anual de Fatos",
            min_value=min_media_fatos, max_value=max_media_fatos, value=(min_media_fatos, max_media_fatos)
        )

        min_taxa = float(df_populacional_metrics['taxa_por_mil_mulheres'].min())
        max_taxa = float(df_populacional_metrics['taxa_por_mil_mulheres'].max())
        taxa_selecionada = st.slider(
            "Fatos por Mil Mulheres",
            min_value=min_taxa, max_value=max_taxa, value=(min_taxa, max_taxa)
        )

        min_perc = float(df_populacional_metrics['percentual_mulheres_vitimas'].min())
        max_perc = float(df_populacional_metrics['percentual_mulheres_vitimas'].max())
        perc_selecionado = st.slider(
            "% de Mulheres Vítimas",
            min_value=min_perc, max_value=max_perc, value=(min_perc, max_perc)
        )

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Resetar Todos os Filtros", use_container_width=True):
        st.rerun()

    # --- LÓGICA DE FILTRAGEM FINAL ---
    idade_max_filtro = float('inf') if idade_selecionada[1] == 100 else idade_selecionada[1]

    municipios_filtrados_populacao = df_populacional_metrics[
        (df_populacional_metrics['populacao_feminina'] >= pop_selecionada[0]) &
        (df_populacional_metrics['populacao_feminina'] <= pop_selecionada[1]) &
        (df_populacional_metrics['media_anual_fatos'] >= media_fatos_selecionada[0]) &
        (df_populacional_metrics['media_anual_fatos'] <= media_fatos_selecionada[1]) &
        (df_populacional_metrics['taxa_por_mil_mulheres'] >= taxa_selecionada[0]) &
        (df_populacional_metrics['taxa_por_mil_mulheres'] <= taxa_selecionada[1]) &
        (df_populacional_metrics['percentual_mulheres_vitimas'] >= perc_selecionado[0]) &
        (df_populacional_metrics['percentual_mulheres_vitimas'] <= perc_selecionado[1])
        ]['municipio_normalizado']

    st.session_state.df_geral_filtrado = st.session_state.df_geral[
        (st.session_state.df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
        (st.session_state.df_geral['data_fato'].dt.date <= st.session_state.data_final) &
        (st.session_state.df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (st.session_state.df_geral['municipio'].isin(municipio_selecionado)) &
        (st.session_state.df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (st.session_state.df_geral['associacao'].isin(associacao_selecionado)) &
        (st.session_state.df_geral['idade_vitima'] >= idade_selecionada[0]) & (
                st.session_state.df_geral['idade_vitima'] <= idade_max_filtro) &
        (st.session_state.df_geral['municipio_normalizado'].isin(municipios_filtrados_populacao))
        ].copy()

    st.session_state.df_feminicidio_filtrado = st.session_state.df_feminicidio[
        (st.session_state.df_feminicidio['data_fato'].dt.date >= st.session_state.data_inicial) &
        (st.session_state.df_feminicidio['data_fato'].dt.date <= st.session_state.data_final) &
        (st.session_state.df_feminicidio['municipio'].isin(municipio_selecionado)) &
        (st.session_state.df_feminicidio['mesoregiao'].isin(mesoregiao_selecionado)) &
        (st.session_state.df_feminicidio['associacao'].isin(associacao_selecionado)) &
        (st.session_state.df_feminicidio['idade_vitima'] >= idade_selecionada[0]) & (
                st.session_state.df_feminicidio['idade_vitima'] <= idade_max_filtro) &
        (st.session_state.df_feminicidio['municipio_normalizado'].isin(municipios_filtrados_populacao))
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

# --- MENSAGEM DE ERRO SE DADOS NÃO FOREM CARREGADOS ---
if st.session_state.df_geral.empty or st.session_state.df_feminicidio.empty or st.session_state.geojson_sc is None or st.session_state.df_populacao.empty or st.session_state.df_calendario.empty:
    st.error("🚨 Falha no carregamento de um ou mais arquivos de dados.")
    st.warning(
        "Certifique-se de que os arquivos `base_geral.xlsx`, `base_feminicidio.xlsx`, `base_populacao.xlsx`, `base_regioes_associacoes.xlsx`, `base_calendario_feriados.xlsx` e `municipios_sc.json` existem na pasta `data/`.")
