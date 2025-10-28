import streamlit as st
import pandas as pd
import plotly.express as px
import json
import unicodedata

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
        font-family: 'Inter', sans-serif;
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
        
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- NOVA FUNÇÃO AUXILIAR PARA NORMALIZAR TEXTO ---
def normalizar_nome(nome):
    """Remove acentos, caracteres especiais e converte para maiúsculo."""
    if isinstance(nome, str):
        nfkd_form = unicodedata.normalize('NFD', nome)
        nome_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return nome_sem_acento.upper().strip()
    return nome

# --- FUNÇÕES PARA CARREGAR OS DADOS ---

@st.cache_data
def carregar_geojson_sc():
    """Carrega o GeoJSON e adiciona uma chave normalizada para o nome do município."""
    try:
        with open('data/municipios_sc.json', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        for feature in geojson_data['features']:
            nome_original = feature['properties'].get('NM_MUN')
            if nome_original:
                feature['properties']['NM_MUN_NORMALIZADO'] = normalizar_nome(nome_original)
            
        return geojson_data
    except FileNotFoundError:
        st.error("Arquivo 'municipios_sc.json' não encontrado na pasta 'data'.")
        return None

@st.cache_data
def carregar_dados_gerais():
    """Carrega e trata os dados da base geral, normalizando nomes de municípios."""
    try:
        df = pd.read_excel('data/base_geral.xlsx')

        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False))

        df.rename(columns={
            'data_do_fato': 'data_fato', 'município': 'municipio',
            'mesoregião': 'mesoregiao', 'fato_comunicado': 'fato_comunicado', 'idade': 'idade_vitima'
        }, inplace=True)

        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        
        if 'municipio' in df.columns:
            df['municipio_normalizado'] = df['municipio'].apply(normalizar_nome)
        
        df['ano'] = df['data_fato'].dt.year
        df['mes'] = df['data_fato'].dt.month_name()
        
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base geral: A coluna {e} não foi encontrada.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_feminicidio():
    """Carrega e trata os dados da base de feminicídio de forma robusta."""
    try:
        df = pd.read_excel('data/base_feminicidio.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False))
        df.rename(columns={
            'relacao_com_o_autor': 'relacao_autor', 'município': 'municipio', 'idade_autor': 'idade_autor',
            'prisão': 'autor_preso', 'idade_vitima': 'idade_vitima', 'meio': 'meio_crime'
        }, inplace=True)
        if 'data' in df.columns: df.rename(columns={'data':'data_fato'}, inplace=True)
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        df['idade_autor'] = pd.to_numeric(df['idade_autor'], errors='coerce')
        df['ano'] = df['data_fato'].dt.year
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base de feminicídio: A coluna {e} não foi encontrada.")
        st.write("Colunas encontradas após limpeza:", df.columns.tolist())
        return pd.DataFrame()

# --- FUNÇÃO PARA CRIAR A TABELA CONSOLIDADA ---
def criar_tabela_consolidada(df):
    """Cria uma tabela consolidada com dados de crimes por município."""
    df_agrupado = df.groupby(['municipio', 'fato_comunicado', 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index=['municipio', 'fato_comunicado'], columns='ano', values='total_crime', fill_value=0)
    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)
    
    anos = sorted(df_agrupado['ano'].unique())
    if len(anos) > 1:
        for i in range(1, len(anos)):
            ano_atual = anos[i]
            ano_anterior = anos[i-1]
            df_pivot[f'evolucao_percentual_{ano_anterior}-{ano_atual}'] = (
                (df_pivot[ano_atual] - df_pivot[ano_anterior]) / df_pivot[ano_anterior].replace(0, pd.NA) * 100
            ).fillna(0)

    colunas_anos = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    colunas_evolucao = sorted([col for col in df_pivot.columns if 'evolucao' in str(col)])
    
    ordem_colunas = colunas_anos + colunas_evolucao + ['total']
    df_consolidado = df_pivot[ordem_colunas].reset_index()
    df_consolidado.rename(columns={'municipio': 'Nome do Município', 'fato_comunicado': 'Fato Comunicado'}, inplace=True)
    
    return df_consolidado
    
# Carregar os dados
geojson_sc = carregar_geojson_sc()
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://i.imgur.com/805nJ3j.png", width=80)
st.sidebar.title("Observatório da Violência Contra a Mulher")

# --- ESTRUTURA COM ABAS (TABS) ---
tab_geral, tab_feminicidio, tab_glossario = st.tabs([
    "📊 Análise Geral da Violência", "🚨 Análise de Feminicídios", "📖 Metodologia e Glossário"
])

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
if not df_geral.empty and not df_feminicidio.empty and geojson_sc is not None:
    st.sidebar.header("⚙️ Filtros de Análise")
    
    # Criar abas de filtros para melhor organização
    with st.sidebar.expander("📅 PERÍODO", expanded=True):
        anos_disponiveis = sorted(df_geral['ano'].unique())
        ano_selecionado = st.multiselect(
            "Ano(s)", 
            options=anos_disponiveis, 
            default=anos_disponiveis,
            help="Selecione um ou mais anos para análise"
        )
        
        meses_disponiveis = sorted(df_geral['mes'].unique(), key=lambda m: list(pd.to_datetime(df_geral['data_fato']).dt.month).index(list(df_geral[df_geral['mes'] == m]['data_fato'])[0].month))
        
        # Traduzir meses para português
        traducao_meses = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        meses_pt = [traducao_meses.get(m, m) for m in meses_disponiveis]
        
        mes_selecionado_pt = st.multiselect(
            "Mês(es)", 
            options=meses_pt, 
            default=meses_pt,
            help="Selecione um ou mais meses"
        )
        # Converter de volta para inglês para filtro
        mes_selecionado = [k for k, v in traducao_meses.items() if v in mes_selecionado_pt]
    
    with st.sidebar.expander("📍 LOCALIZAÇÃO", expanded=True):
        # Filtro por Mesoregião primeiro (mais agregado)
        mesoregioes_disponiveis = sorted(df_geral['mesoregiao'].unique())
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)", 
            options=mesoregioes_disponiveis, 
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina"
        )
        
        # Filtrar municípios baseado nas mesoregiões selecionadas
        if mesoregiao_selecionado:
            municipios_filtrados = df_geral[df_geral['mesoregiao'].isin(mesoregiao_selecionado)]['municipio'].unique()
        else:
            municipios_filtrados = df_geral['municipio'].unique()
        
        municipios_disponiveis = sorted(municipios_filtrados)
        
        # Opção de selecionar todos os municípios
        todos_municipios = st.checkbox("Todos os municípios", value=True, help="Marque para selecionar todos")
        
        if todos_municipios:
            municipio_selecionado = municipios_disponiveis
            st.info(f"✓ {len(municipios_disponiveis)} municípios selecionados")
        else:
            municipio_selecionado = st.multiselect(
                "Município(s) específico(s)", 
                options=municipios_disponiveis,
                default=[],
                help="Digite para buscar. Deixe vazio para todos"
            )
            if not municipio_selecionado:
                municipio_selecionado = municipios_disponiveis
    
    with st.sidebar.expander("👥 PERFIL DA VÍTIMA", expanded=True):
        idades_disponiveis = sorted(df_geral['idade_vitima'].dropna().unique())
        idade_selecionada = st.slider(
            "Faixa Etária", 
            min_value=int(idades_disponiveis[0]), 
            max_value=int(idades_disponiveis[-1]), 
            value=(int(idades_disponiveis[0]), int(idades_disponiveis[-1])),
            help="Ajuste o intervalo de idade das vítimas"
        )
        st.caption(f"Idades: {idade_selecionada[0]} a {idade_selecionada[1]} anos")
    
    with st.sidebar.expander("🚨 TIPO DE CRIME", expanded=True):
        fatos_disponiveis = sorted(df_geral['fato_comunicado'].unique())
        
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
    
    # Botão para resetar filtros
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Resetar Todos os Filtros", use_container_width=True):
        st.rerun()

    df_geral_filtrado = df_geral[
        (df_geral['ano'].isin(ano_selecionado)) & 
        (df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (df_geral['mes'].isin(mes_selecionado)) &
        (df_geral['municipio'].isin(municipio_selecionado)) &
        (df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_geral['idade_vitima'] >= idade_selecionada[0]) & (df_geral['idade_vitima'] <= idade_selecionada[1])
    ]
    df_feminicidio_filtrado = df_feminicidio[df_feminicidio['ano'].isin(ano_selecionado)]

    # --- ABA 1: ANÁLISE GERAL ---
    with tab_geral:
        st.header("Violência Contra a Mulher em Santa Catarina")
        st.markdown("Visão geral dos registros de ocorrências.")

        total_registros = df_geral_filtrado.shape[0]
        media_idade_vitima = 0.0
        if not df_geral_filtrado.empty and df_geral_filtrado['idade_vitima'].notna().any():
            media_idade_vitima = df_geral_filtrado['idade_vitima'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total de Registros de Crime", value=f"{total_registros:,}".replace(",", "."))
        with col2:
            st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
        st.markdown("---")

        st.subheader("Distribuição de Crimes por Município")
        crimes_por_municipio = df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio.columns = ['municipio_normalizado', 'quantidade']
        
        fig_mapa = px.choropleth_mapbox(
            crimes_por_municipio, geojson=geojson_sc, locations='municipio_normalizado',
            featureidkey="properties.NM_MUN_NORMALIZADO", color='quantidade',
            color_continuous_scale="Purples", mapbox_style="carto-positron",
            zoom=6, center={"lat": -27.59, "lon": -50.52}, opacity=0.7,
            labels={'quantidade': 'Quantidade de Registros'}
        )
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)
        st.markdown("---")

        st.subheader("Evolução dos Registros de Ocorrências (Série Temporal)")
        df_temporal = df_geral_filtrado.copy()
        df_temporal['ano_mes'] = df_temporal['data_fato'].dt.to_period('M').astype(str)
        registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values('ano_mes')
        fig_temporal = px.line(
            registros_por_mes_ano, x='ano_mes', y='quantidade',
            labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
            template='plotly_white', markers=True
        )
        fig_temporal.update_traces(line_color='#8A2BE2')
        st.plotly_chart(fig_temporal, use_container_width=True)
        st.markdown("---")

        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader("Registros de Ocorrências por Ano")
            registros_por_ano = df_geral_filtrado['ano'].value_counts().sort_index()
            fig_ano = px.bar(
                registros_por_ano, x=registros_por_ano.index, y=registros_por_ano.values,
                labels={'x': 'Ano', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_ano.values
            )
            fig_ano.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_ano, use_container_width=True)

        with col_graf2:
            st.subheader("Tipos de Crimes Mais Frequentes")
            registros_por_fato = df_geral_filtrado['fato_comunicado'].value_counts()
            fig_fato = px.bar(
                registros_por_fato, x=registros_por_fato.values, y=registros_por_fato.index, orientation='h',
                labels={'x': 'Quantidade', 'y': 'Tipo de Crime'}, template='plotly_white', text=registros_por_fato.values
            )
            fig_fato.update_traces(marker_color='#9370DB', textposition='auto')
            fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_fato, use_container_width=True)

        st.markdown("---")
        
        col_graf3, col_graf4 = st.columns(2)
        with col_graf3:
            st.subheader("Distribuição por Faixa Etária da Vítima")
            df_faixa_etaria = df_geral_filtrado.dropna(subset=['idade_vitima'])
            bins = [0, 17, 24, 34, 44, 59, 120]
            labels = ['0-17 anos', '18-24 anos', '25-34 anos', '35-44 anos', '45-59 anos', '60+ anos']
            df_faixa_etaria['faixa_etaria'] = pd.cut(df_faixa_etaria['idade_vitima'], bins=bins, labels=labels, right=True)
            registros_por_faixa = df_faixa_etaria['faixa_etaria'].value_counts().sort_index()
            fig_faixa_etaria = px.bar(
                registros_por_faixa, x=registros_por_faixa.index, y=registros_por_faixa.values,
                labels={'x': 'Faixa Etária', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_faixa.values
            )
            fig_faixa_etaria.update_traces(marker_color='#9370DB', textposition='outside')
            st.plotly_chart(fig_faixa_etaria, use_container_width=True)
        with col_graf4:
            st.subheader("Distribuição de Ocorrências por Mês")
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            df_geral_filtrado['mes_cat'] = pd.Categorical(df_geral_filtrado['mes'], categories=meses_ordem, ordered=True)
            registros_por_mes = df_geral_filtrado['mes_cat'].value_counts().sort_index()
            nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
            registros_por_mes.index = registros_por_mes.index.map(nomes_meses_pt)
            fig_mes = px.pie(
                values=registros_por_mes.values, names=registros_por_mes.index, hole=.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_mes.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_mes, use_container_width=True)
        
        st.markdown("---")

        st.subheader("Distribuição de Ocorrências por Dia da Semana")
        df_geral_filtrado['dia_semana'] = df_geral_filtrado['data_fato'].dt.day_name()
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_geral_filtrado['dia_semana_cat'] = pd.Categorical(df_geral_filtrado['dia_semana'], categories=dias_ordem, ordered=True)
        registros_por_dia = df_geral_filtrado['dia_semana_cat'].value_counts().sort_index()
        nomes_dias_pt = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        registros_por_dia.index = registros_por_dia.index.map(nomes_dias_pt)
        fig_dia_semana = px.bar(
            registros_por_dia, x=registros_por_dia.index, y=registros_por_dia.values,
            labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_dia.values
        )
        fig_dia_semana.update_traces(marker_color='#8A2BE2', textposition='outside')
        st.plotly_chart(fig_dia_semana, use_container_width=True)

        st.markdown("---")
        st.subheader("Tabela Consolidada de Crimes por Município")
        if not df_geral_filtrado.empty:
            tabela_consolidada = criar_tabela_consolidada(df_geral_filtrado)
            if not tabela_consolidada.empty:
                st.dataframe(tabela_consolidada, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
        else:
            st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")


    # --- ABA 2: ANÁLISE DE FEMINICÍDIOS ---
    with tab_feminicidio:
        st.header("Análise de Feminicídios Consumados")
        st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")
        
        total_feminicidios = df_feminicidio_filtrado.shape[0]
        idade_media_vitima_fem = df_feminicidio_filtrado['idade_vitima'].mean()
        idade_media_autor_fem = df_feminicidio_filtrado['idade_autor'].mean()
        texto_idade_vitima = f"{idade_media_vitima_fem:.1f} anos" if not pd.isna(idade_media_vitima_fem) else "Dados Insuficientes"
        texto_idade_autor = f"{idade_media_autor_fem:.1f} anos" if not pd.isna(idade_media_autor_fem) else "Dados Insuficientes"
        
        col1_fem, col2_fem, col3_fem = st.columns(3)
        with col1_fem:
            st.metric(label="Total de Feminicídios", value=total_feminicidios)
        with col2_fem:
            st.metric(label="Idade Média da Vítima", value=texto_idade_vitima)
        with col3_fem:
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
                labels={'x': 'Meio Utilizado', 'y': 'Quantidade'}, template='plotly_white', text=meio_crime.values
            )
            fig_meio.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_meio, use_container_width=True)

else:
    with tab_geral:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx`, `base_feminicidio.xlsx` e `municipios_sc.json` existem na pasta `data`.")
    with tab_feminicidio:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data`.")

# --- ABA 3: GLOSSÁRIO (Sempre visível) ---
with tab_glossario:
    st.header("Metodologia e Glossário")
    
    st.subheader("Metodologia")
    st.markdown("""
    Os dados que constam neste painel foram fornecidos pela **Gerência de Estatística e Análise Criminal da Secretaria de Estado da Segurança Pública** (GEAC | DINE | SSP | SC).
    
    Eles foram organizados e processados para possibilitar clareza no entendimento das informações e permitir a interação dos usuários.
    
    A elaboração do painel é uma parceria entre o **Observatório da Violência Contra a Mulher (OVM/SC)** e o **Ministério Público de Contas de Santa Catarina (MPC/SC)**.
    """)
    
    st.markdown("---")
    
    st.subheader("Glossário de Tipos de Crimes")
    
    with st.expander("🔹 Ameaça", expanded=False):
        st.markdown("""
        Ameaçar alguém, por palavra, escrito ou gesto, ou qualquer outro meio simbólico, de causar-lhe mal injusto e grave.
        
        **Base Legal:** Art. 147 do Código Penal Brasileiro
        """)
    
    with st.expander("🔹 Lesão Corporal Dolosa", expanded=False):
        st.markdown("""
        A lesão corporal caracteriza-se por ofender a integridade corporal ou a saúde de outrem. O crime doloso ocorre quando o agente quis o resultado ou assumiu o risco de produzi-lo.
        
        **Base Legal:** Art. 129 do Código Penal Brasileiro
        """)
    
    with st.expander("🔹 Estupro", expanded=False):
        st.markdown("""
        Constranger alguém, mediante violência ou grave ameaça, a ter conjunção carnal ou a praticar ou permitir que com ele se pratique outro ato libidinoso.
        
        **Base Legal:** Art. 213 do Código Penal Brasileiro
        """)
    
    with st.expander("🔹 Feminicídio", expanded=False):
        st.markdown("""
        Homicídio contra a mulher por razões da condição de sexo feminino. 
        
        Considera-se que há razões de condição de sexo feminino quando o crime envolve:
        - Violência doméstica e familiar
        - Menosprezo ou discriminação à condição de mulher
        
        **Base Legal:** Art. 121, §2º-A do Código Penal (Lei nº 13.104/2015)
        """)
    
    with st.expander("🔹 Vias de Fato", expanded=False):
        st.markdown("""
        São atos agressivos praticados contra alguém, que não cheguem a causar lesão corporal. 
        
        **Exemplos:** empurrar, sacudir, puxar cabelo, etc.
        
        **Base Legal:** Art. 21 da Lei de Contravenções Penais
        """)
    
    st.markdown("---")
    
    st.info("**Fontes:** Código Penal Brasileiro, Lei do Feminicídio (Lei nº 13.104/2015), Lei Maria da Penha (Lei nº 11.340/2006).")
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f4fb 0%, #ffffff 100%); border-radius: 10px; margin-top: 2rem;'>
        <h4 style='color: #6a1b9a; margin-bottom: 1rem;'>💜 Em caso de violência, denuncie!</h4>
        <p style='font-size: 1.2rem; font-weight: 600; color: #4a148c;'>Ligue 180 - Central de Atendimento à Mulher</p>
        <p style='color: #666; margin-top: 0.5rem;'>Disque 190 - Polícia Militar | 197 - Polícia Civil</p>
    </div>
    """, unsafe_allow_html=True)

# Rodapé
st.markdown("""
<div class='footer'>
    💜 Observatório da Violência Contra a Mulher - SC | Parceria OVM/SC e MPC/SC | 2025
</div>
""", unsafe_allow_html=True)
