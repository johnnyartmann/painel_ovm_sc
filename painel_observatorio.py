import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import unicodedata
import numpy as np
import re
from shapely.geometry import shape, Point

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

def normalizar_nome(texto):
    """
    Limpa e padroniza uma string de texto para ser usada como
    chave de junção.
    """
    if not isinstance(texto, str):
        return ""
   
    texto = texto.lower()
   
    # --- 1. Mapa de Exceções (Hard-coded) ---
    mapa_excecoes = {
        'herval': 'herval d oeste'
        # (Mantemos a correção para o arquivo Geo)
    }
    if texto in mapa_excecoes:
        texto = mapa_excecoes[texto]
 
    # --- 2. Normalização de Acentos ---
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
   
    # --- 3. Normalização de Pontuação ---
    # Substitui qualquer coisa que NÃO seja (^) letra (a-z),
    # número (0-9) ou espaço (\s) por um espaço.
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
   
    # --- 4. Normalização de Palavras ---
    # Remove artigos/preposições (agora cercados por espaços)
    texto = re.sub(r'\b(de|do|da|d)\b', ' ', texto)
   
    # --- 5. Limpeza Final ---
    # Remove espaços múltiplos (criados pelas substituições)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto.upper()

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
def mapear_vizinhos(_geojson_data):
    """Cria um mapa de adjacência (municípios vizinhos) a partir do GeoJSON."""
    if _geojson_data is None:
        return {}
    
    geometrias = {}
    for feature in _geojson_data['features']:
        nome_normalizado = feature['properties'].get('NM_MUN_NORMALIZADO')
        if nome_normalizado:
            geometrias[nome_normalizado] = shape(feature['geometry'])

    vizinhos = {nome: [] for nome in geometrias.keys()}
    nomes_municipios = list(geometrias.keys())

    for i in range(len(nomes_municipios)):
        for j in range(i + 1, len(nomes_municipios)):
            nome1 = nomes_municipios[i]
            nome2 = nomes_municipios[j]
            geom1 = geometrias[nome1]
            geom2 = geometrias[nome2]
            
            # Verifica se as geometrias se tocam ou se intersectam
            if geom1.touches(geom2) or geom1.intersects(geom2):
                vizinhos[nome1].append(nome2)
                vizinhos[nome2].append(nome1)
    
    return vizinhos

def calcular_indice_letalidade(df_geral_filtrado, df_feminicidio_filtrado, agrupamento):
    """Calcula o Índice de Letalidade da Violência."""
    coluna_agrupamento_map = {
        "Município": "municipio_normalizado",
        "Mesorregião": "mesoregiao",
        "Associação": "associacao"
    }
    if agrupamento not in coluna_agrupamento_map:
        return pd.DataFrame()
    
    coluna_agrupamento = coluna_agrupamento_map[agrupamento]

    df_ocorrencias_puras = df_geral_filtrado[df_geral_filtrado['fato_comunicado'] != 'Feminicídio']
    total_ocorrencias = df_ocorrencias_puras.groupby(coluna_agrupamento).size().reset_index(name='total_ocorrencias')
    
    total_feminicidios = df_feminicidio_filtrado.groupby(coluna_agrupamento).size().reset_index(name='total_feminicidios')
    
    df_letalidade = pd.merge(total_ocorrencias, total_feminicidios, on=coluna_agrupamento, how='outer').fillna(0)
    
    df_letalidade['total_ocorrencias'] = df_letalidade['total_ocorrencias'].astype(int)
    df_letalidade['total_feminicidios'] = df_letalidade['total_feminicidios'].astype(int)
    
    soma_total = df_letalidade['total_ocorrencias'] + df_letalidade['total_feminicidios']
    df_letalidade['indice_letalidade'] = np.where(
        soma_total > 0,
        (df_letalidade['total_feminicidios'] / soma_total) * 100,
        0
    )
    
    df_letalidade['total_eventos'] = soma_total

    df_letalidade.rename(columns={coluna_agrupamento: 'localidade'}, inplace=True)
    
    df_final = df_letalidade[[
        'localidade', 
        'total_eventos',
        'total_ocorrencias', 
        'total_feminicidios', 
        'indice_letalidade'
    ]]

    return df_final.sort_values(by='indice_letalidade', ascending=False)

@st.cache_data
def carregar_dados_gerais():
    """Carrega e trata os dados da base geral, normalizando nomes de municípios."""
    try:
        df_regioes = carregar_dados_regioes()
        df_geral = pd.read_excel('data/base_geral.xlsx')

        df_geral.columns = (df_geral.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False))

        df_geral.rename(columns={
            'data_do_fato': 'data_fato', 'município': 'municipio',
            'fato_comunicado': 'fato_comunicado', 'idade': 'idade_vitima'
        }, inplace=True)

        df_geral['data_fato'] = pd.to_datetime(df_geral['data_fato'])
        df_geral['idade_vitima'] = pd.to_numeric(df_geral['idade_vitima'], errors='coerce')
        
        if 'municipio' in df_geral.columns:
            df_geral['municipio_normalizado'] = df_geral['municipio'].apply(normalizar_nome)

        df_geral = pd.merge(df_geral, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']], on='municipio_normalizado', how='left')
        df_geral['mesoregiao'].fillna('Não informado', inplace=True)
        df_geral['associacao'].fillna('Não informado', inplace=True)
        
        df_feminicidio_raw = carregar_dados_feminicidio()
        if not df_feminicidio_raw.empty:
            df_feminicidio_para_geral = df_feminicidio_raw.copy()
            df_feminicidio_para_geral['fato_comunicado'] = 'Feminicídio'
            
            df_final = pd.concat([df_geral, df_feminicidio_para_geral], ignore_index=True)
        else:
            df_final = df_geral

        df_final['ano'] = df_final['data_fato'].dt.year
        df_final['mes'] = df_final['data_fato'].dt.month_name()
        
        return df_final
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' ou 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base geral: A coluna {e} não foi encontrada.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_feminicidio():
    """Carrega e trata os dados da base de feminicídio de forma robusta."""
    try:
        df_regioes = carregar_dados_regioes()
        df = pd.read_excel('data/base_feminicidio.xlsx')

        df.rename(columns={
            'DATA': 'data_fato',
            'MUNICÍPIO': 'municipio',
            'RELAÇÃO COM O AUTOR': 'relacao_autor',
            'BO DE VD CONTRA O AUTOR': 'bo_de_vd_contra_o_autor',
            'IDADE AUTOR': 'idade_autor',
            'IDADE VITIMA': 'idade_vitima',
            'PASSAGEM POLICIAL': 'passagem_policial',
            'PASSAGEM POR VIOLÊNCIA DOMÉSTICA': 'passagem_por_violencia_domestica',
            'PRISÃO': 'autor_preso',
            'MEIO': 'meio_crime'
        }, inplace=True)

        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('ê', 'e', regex=False)
                      .str.replace('á', 'a', regex=False))

        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        df['idade_autor'] = pd.to_numeric(df['idade_autor'], errors='coerce')
        
        if 'municipio' in df.columns:
            df['municipio_normalizado'] = df['municipio'].apply(normalizar_nome)

        df = pd.merge(df, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']], on='municipio_normalizado', how='left')
        df['mesoregiao'].fillna('Não informado', inplace=True)
        df['associacao'].fillna('Não informado', inplace=True)
        
        df['ano'] = df['data_fato'].dt.year
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base de feminicídio: A coluna {e} não foi encontrada.")
        st.write("Verifique se os nomes de colunas no arquivo Excel correspondem exatamente aos da imagem fornecida.")
        st.write("Colunas encontradas no arquivo:", pd.read_excel('data/base_feminicidio.xlsx').columns.tolist())
        return pd.DataFrame()

@st.cache_data
def carregar_dados_calendario():
    """Carrega a base de calendário com feriados e datas especiais."""
    try:
        df = pd.read_excel('data/base_calendario_feriados.xlsx')
        df['data'] = pd.to_datetime(df['data'])
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_calendario_feriados.xlsx' não encontrado na pasta 'data'. Este arquivo é necessário para a Análise Sazonal.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados do calendário: {e}")
        return pd.DataFrame()

def colorir_percentual(val):
    """Retorna a cor para o valor percentual."""
    if pd.isna(val) or val == 0:
        return ''
    color = 'red' if val > 0 else 'green'
    return f'color: {color}'

def formatar_seta_percentual(val):
    """Formata o valor com seta e percentual."""
    if pd.isna(val):
        return '-'
    seta = '▲' if val > 0 else '▼' if val < 0 else ''
    if seta:
        return f'{seta} {abs(val):.2f}%'
    return f'{abs(val):.2f}%'

def calcular_cagr(valor_inicial, valor_final, num_anos):
    """Calcula a Taxa de Crescimento Anual Composta (CAGR)."""
    if isinstance(valor_inicial, pd.Series):
        cagr = pd.Series(np.nan, index=valor_inicial.index, dtype='float64')
        if num_anos < 3:
            return cagr

        mask = (valor_inicial.notna()) & (valor_final.notna()) & (valor_inicial != 0)

        cagr.loc[mask] = ((valor_final[mask] / valor_inicial[mask]) ** (1 / (num_anos - 1)) - 1) * 100
        return cagr
    else:
        if pd.isna(valor_inicial) or pd.isna(valor_final) or valor_inicial == 0 or num_anos < 3:
            return np.nan
        return ((valor_final / valor_inicial) ** (1 / (num_anos - 1)) - 1) * 100

def criar_tabela_consolidada(df, coluna_agrupamento, nome_agrupamento):
    """Cria uma tabela consolidada com dados de crimes por [agrupamento]."""
    df_agrupado = df.groupby([coluna_agrupamento, 'fato_comunicado', 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index=[coluna_agrupamento, 'fato_comunicado'], columns='ano', values='total_crime', fill_value=0)
    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)
    
    anos = sorted(df_agrupado['ano'].unique())
    if len(anos) > 1:
        for i in range(1, len(anos)):
            ano_atual = anos[i]
            ano_anterior = anos[i-1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            df_pivot[coluna_evolucao] = (
                (df_pivot[ano_atual] - df_pivot[ano_anterior]) / df_pivot[ano_anterior].replace(0, pd.NA) * 100
            )
    
    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    
    ano_corrente = pd.Timestamp.now().year
    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente]

    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i-1]
            ano_atual = anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')
        
    df_consolidado = df_pivot[ordem_colunas].reset_index()
    nome_coluna = f"Nome do {nome_agrupamento}" if nome_agrupamento == "Município" else nome_agrupamento
    df_consolidado.rename(columns={coluna_agrupamento: nome_coluna, 'fato_comunicado': 'Fato Comunicado'}, inplace=True)
    
    return df_consolidado

def criar_tabela_total_consolidada(df):
    """Cria uma tabela consolidada com o total de crimes por tipo."""
    df_agrupado = df.groupby(['fato_comunicado', 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index='fato_comunicado', columns='ano', values='total_crime', fill_value=0)
    
    anos_existentes = [col for col in df_pivot.columns if isinstance(col, (int, float))]
    if anos_existentes:
        anos_todos = range(int(min(anos_existentes)), int(max(anos_existentes)) + 1)
        for ano in anos_todos:
            if ano not in df_pivot.columns:
                df_pivot[ano] = 0

    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)
    
    anos = sorted([col for col in df_pivot.columns if isinstance(col, (int, float))])

    ano_corrente = pd.Timestamp.now().year # Pega o ano corrente

    if len(anos) > 1:
        for i in range(1, len(anos)):
            ano_atual = anos[i]
            
            # Se o ano atual for o ano corrente, não calcula a variação e interrompe o laço
            if ano_atual == ano_corrente:
                break
                
            ano_anterior = anos[i-1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            
            denominador = df_pivot[ano_anterior].replace(0, pd.NA)
            df_pivot[coluna_evolucao] = (df_pivot[ano_atual] - df_pivot[ano_anterior]) / denominador * 100

    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    
    ano_corrente_cagr = pd.Timestamp.now().year
    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente_cagr]

    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i-1]
            ano_atual = anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    df_consolidado = df_pivot[ordem_colunas].reset_index()
    df_consolidado.rename(columns={'fato_comunicado': 'Fato Comunicado'}, inplace=True)
    
    return df_consolidado

def criar_tabela_populacional_agrupada(df_crimes, df_pop, df_regioes, agrupamento, num_anos):
    """Cria uma tabela de análise populacional, permitindo o agrupamento por diferentes níveis."""
    
    if num_anos == 0: num_anos = 1

    df_pop_com_regioes = pd.merge(df_pop, df_regioes.drop(columns='municipio'), on='municipio_normalizado', how='left')

    if agrupamento == "Consolidado":
        total_fatos = df_crimes.shape[0]
        municipios_presentes = df_crimes['municipio_normalizado'].unique()
        pop_filtrada = df_pop_com_regioes[df_pop_com_regioes['municipio_normalizado'].isin(municipios_presentes)]
        total_populacao = pop_filtrada['populacao_feminina'].sum()
        
        media_anual = total_fatos / num_anos
        taxa = (media_anual / total_populacao) * 1000 if total_populacao > 0 else 0
        percentual = (media_anual / total_populacao) * 100 if total_populacao > 0 else 0
        
        tabela = pd.DataFrame([{'Localidade': 'Santa Catarina (Filtro Aplicado)', 'População Feminina': total_populacao,
                                'Média Anual de Fatos Ocorridos': media_anual, 'Fatos por Mil Mulheres (anual)': taxa,
                                '% de Mulheres Vítimas (anual)': percentual}])
        return tabela.set_index('Localidade')

    coluna_agrupamento = {
        "Município": "municipio",
        "Mesorregião": "mesoregiao",
        "Associação": "associacao"
    }[agrupamento]

    crimes_agrupado = df_crimes[coluna_agrupamento].value_counts().reset_index()
    crimes_agrupado.columns = [coluna_agrupamento, 'total_fatos']

    if agrupamento == "Município":
        pop_agrupada = df_pop_com_regioes[[coluna_agrupamento, 'populacao_feminina']]
    else:
        pop_agrupada = df_pop_com_regioes.groupby(coluna_agrupamento)['populacao_feminina'].sum().reset_index()

    df_agregado = pd.merge(crimes_agrupado, pop_agrupada, on=coluna_agrupamento, how='left')

    df_agregado['media_anual_fatos'] = df_agregado['total_fatos'] / num_anos
    df_agregado['taxa_por_mil_mulheres'] = ((df_agregado['media_anual_fatos'] / df_agregado['populacao_feminina']) * 1000).fillna(0)
    df_agregado['percentual_mulheres_vitimas'] = ((df_agregado['media_anual_fatos'] / df_agregado['populacao_feminina']) * 100).fillna(0)

    tabela_final = df_agregado.rename(columns={
        coluna_agrupamento: agrupamento,
        'populacao_feminina': 'População Feminina',
        'media_anual_fatos': 'Média Anual de Fatos Ocorridos',
        'taxa_por_mil_mulheres': 'Fatos por Mil Mulheres (anual)',
        'percentual_mulheres_vitimas': '% de Mulheres Vítimas (anual)'
    })

    return tabela_final[[agrupamento, 'População Feminina', 'Média Anual de Fatos Ocorridos', 'Fatos por Mil Mulheres (anual)', '% de Mulheres Vítimas (anual)']].set_index(agrupamento)


def criar_tabela_feminicidio_agrupado(df, coluna_agrupamento, nome_agrupamento):
    """Cria uma tabela consolidada com dados de feminicídios por [agrupamento]."""
    df_agrupado = df.groupby([coluna_agrupamento, 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index=coluna_agrupamento, columns='ano', values='total_crime', fill_value=0)
    
    anos_existentes = [col for col in df_pivot.columns if isinstance(col, (int, float))]
    if anos_existentes:
        anos_todos = range(int(min(anos_existentes)), int(max(anos_existentes)) + 1)
        for ano in anos_todos:
            if ano not in df_pivot.columns:
                df_pivot[ano] = 0

    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)
    
    anos = sorted([col for col in df_pivot.columns if isinstance(col, (int, float))])

    if len(anos) > 1:
        for i in range(1, len(anos)):
            ano_atual = anos[i]
            ano_anterior = anos[i-1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            denominador = df_pivot[ano_anterior].replace(0, pd.NA)
            df_pivot[coluna_evolucao] = (df_pivot[ano_atual] - df_pivot[ano_anterior]) / denominador * 100

    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    
    ano_corrente = pd.Timestamp.now().year
    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente]

    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i-1]
            ano_atual = anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    df_consolidado = df_pivot[ordem_colunas].reset_index()
    nome_coluna = f"Nome do {nome_agrupamento}" if nome_agrupamento == "Município" else nome_agrupamento
    df_consolidado.rename(columns={coluna_agrupamento: nome_coluna}, inplace=True)
    
    return df_consolidado

def criar_tabela_total_feminicidio(df):
    """Cria uma tabela consolidada com o total de feminicídios por ano."""
    if df.empty:
        return pd.DataFrame(columns=['Tipo de Crime', 'total'])
        
    df_agrupado = df.groupby('ano').size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(columns='ano', values='total_crime', fill_value=0)
    
    anos_existentes = [col for col in df.ano.unique() if isinstance(col, (int, float))]
    if anos_existentes:
        anos_todos = range(int(min(anos_existentes)), int(max(anos_existentes)) + 1)
        for ano in anos_todos:
            if ano not in df_pivot.columns:
                df_pivot[ano] = 0
    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)

    df_pivot['total'] = df_pivot.sum(axis=1)
    
    anos = sorted([col for col in df_pivot.columns if isinstance(col, (int, float))])

    ano_corrente = pd.Timestamp.now().year

    if len(anos) > 1:
        for i in range(1, len(anos)):
            ano_atual = anos[i]

            if ano_atual == ano_corrente:
                break

            ano_anterior = anos[i-1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            denominador = df_pivot[ano_anterior].replace(0, pd.NA)
            df_pivot[coluna_evolucao] = (df_pivot[ano_atual] - df_pivot[ano_anterior]) / denominador * 100

    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    
    ano_corrente_cagr = pd.Timestamp.now().year
    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente_cagr]

    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i-1]
            ano_atual = anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    df_consolidado = df_pivot[ordem_colunas].reset_index(drop=True)
    df_consolidado.insert(0, 'Tipo de Crime', 'Feminicídio')
    
    return df_consolidado
    
@st.cache_data
def carregar_dados_regioes():
    """Carrega a base de regiões e associações, normalizando o nome do município."""
    try:
        df = pd.read_excel('data/base_regioes_associacoes.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df['municipio_normalizado'] = df['municipio'].apply(normalizar_nome)
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_regioes_associacoes.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados das regiões: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_populacao():
    """Carrega a base de população, normalizando o nome do município."""
    try:
        df = pd.read_excel('data/base_populacao.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df['municipio_normalizado'] = df['municipio'].apply(normalizar_nome)
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_populacao.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados da população: {e}")
        return pd.DataFrame()

geojson_sc = carregar_geojson_sc()
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()
df_populacao = carregar_dados_populacao()
df_regioes = carregar_dados_regioes()
df_calendario = carregar_dados_calendario()


st.sidebar.image("logo_ovm.jpeg", use_container_width=True)

tab_geral, tab_feminicidio, tab_analises_avancadas, tab_glossario, tab_download = st.tabs([
    "📊 Análise Geral", 
    "🚨 Análise de Feminicídios",
    "🔬 Análises Avançadas",
    "📖 Metodologia e Glossário", 
    "📥 Download de Dados"
])

if not df_geral.empty and not df_feminicidio.empty and geojson_sc is not None and not df_populacao.empty and not df_calendario.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")

        # --- VISUALIZAÇÃO / AGRUPAMENTO (MOVIMENTEI PARA CIMA) ---
        st.subheader("📊 VISUALIZAR POR")
        agrupamento_selecionado = st.selectbox(
            "Agrupar por",
            options=["Consolidado", "Município", "Mesorregião", "Associação"],
            index=0,
            help="Escolha como os dados devem ser agrupados nos gráficos e tabelas."
        )
        
        # --- PERÍODO ---
        st.subheader("📅 PERÍODO")
        min_date = df_geral['data_fato'].min().date()
        max_date = df_geral['data_fato'].max().date()

        data_inicial = st.date_input(
            "Data Inicial",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            help="Selecione a data de início do período."
        )

        data_final = st.date_input(
            "Data Final",
            value=max_date,
            min_value=data_inicial,
            max_value=max_date,
            help="Selecione a data de fim do período."
        )
        
        df_geral_filtrado_por_data = df_geral[
            (df_geral['data_fato'].dt.date >= data_inicial) &
            (df_geral['data_fato'].dt.date <= data_final)
        ]

        # --- LOCALIZAÇÃO ---
        st.subheader("📍 LOCALIZAÇÃO")
        
        municipios_disponiveis = sorted(df_geral_filtrado_por_data['municipio'].dropna().unique())
        
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
        
        mesoregioes_disponiveis = sorted([m for m in df_geral['mesoregiao'].unique() if m != 'Não informado'])
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)", 
            options=mesoregioes_disponiveis, 
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina"
        )
        
        associacoes_disponiveis = sorted([a for a in df_geral['associacao'].dropna().unique() if a != 'Não informado'])
        associacao_selecionado = st.multiselect(
            "Associação(ões)",
            options=associacoes_disponiveis,
            default=associacoes_disponiveis,
            help="Filtre por associação de municípios"
        )

        # --- TIPO DE CRIME ---
        st.subheader("🚨 TIPO DE CRIME")
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
        crimes_por_municipio_para_filtro = df_geral_filtrado_por_data['municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio_para_filtro.columns = ['municipio_normalizado', 'total_fatos']

        df_populacional_metrics = pd.merge(
            df_populacao.copy(),
            crimes_por_municipio_para_filtro,
            on='municipio_normalizado',
            how='left'
        )
        df_populacional_metrics['total_fatos'].fillna(0, inplace=True)

        anos_no_filtro = df_geral_filtrado_por_data['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1

        df_populacional_metrics['media_anual_fatos'] = df_populacional_metrics['total_fatos'] / num_anos
        df_populacional_metrics['taxa_por_mil_mulheres'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 1000).fillna(0)
        df_populacional_metrics['percentual_mulheres_vitimas'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 100).fillna(0)

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

    df_geral_filtrado = df_geral[
        (df_geral['data_fato'].dt.date >= data_inicial) &
        (df_geral['data_fato'].dt.date <= data_final) &
        (df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (df_geral['municipio'].isin(municipio_selecionado)) &
        (df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_geral['associacao'].isin(associacao_selecionado)) &
        (df_geral['idade_vitima'] >= idade_selecionada[0]) & (df_geral['idade_vitima'] <= idade_max_filtro) &
        (df_geral['municipio_normalizado'].isin(municipios_filtrados_populacao))
    ]
    
    df_feminicidio_filtrado = df_feminicidio[
        (df_feminicidio['data_fato'].dt.date >= data_inicial) &
        (df_feminicidio['data_fato'].dt.date <= data_final) &
        (df_feminicidio['municipio'].isin(municipio_selecionado)) &
        (df_feminicidio['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_feminicidio['associacao'].isin(associacao_selecionado)) &
        (df_feminicidio['idade_vitima'] >= idade_selecionada[0]) & (df_feminicidio['idade_vitima'] <= idade_max_filtro) &
        (df_feminicidio['municipio_normalizado'].isin(municipios_filtrados_populacao))
    ]

    with tab_geral:
        st.header("Violência Contra a Mulher em Santa Catarina")
        st.markdown("Visão geral dos registros de ocorrências.")

        total_registros = df_geral_filtrado.shape[0]
        media_idade_vitima = 0.0
        if not df_geral_filtrado.empty and df_geral_filtrado['idade_vitima'].notna().any():
            media_idade_vitima = df_geral_filtrado['idade_vitima'].mean()

        num_dias = (data_final - data_inicial).days + 1
        
        crimes_por_dia = total_registros / num_dias if num_dias > 0 else 0
        crimes_por_hora = total_registros / (num_dias * 24) if num_dias > 0 else 0
        
        df_cagr_kpi = df_geral_filtrado[df_geral_filtrado['ano'] != pd.Timestamp.now().year]
        anos_unicos = sorted(df_cagr_kpi['ano'].unique())
        num_anos_total = len(anos_unicos)

        if num_anos_total >= 3:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total de Registros no Período", value=f"{total_registros:,}".replace(",", "."))
                st.metric(label="Média de Crimes por Dia", value=f"{crimes_por_dia:.1f}")

            with col2:
                dados_por_ano = df_cagr_kpi.groupby('ano').size()
                valor_inicial = dados_por_ano.iloc[0]
                valor_final = dados_por_ano.iloc[-1]
                
                cagr = calcular_cagr(valor_inicial, valor_final, num_anos_total)
                
                if pd.notna(cagr):
                    delta_cagr = f"{cagr:.1f}% ao ano"
                    icone_cagr = "📈" if cagr > 0 else "📉"
                    st.metric(label=f"Tendência de Longo Prazo (CAGR) {icone_cagr}", value=delta_cagr,
                              help="Taxa de Crescimento Anual Composta no período selecionado.")
                else:
                    st.metric(label="Tendência de Longo Prazo (CAGR)", value="N/A", help="Dados insuficientes para cálculo.")
                
                st.metric(label="Média de Crimes por Hora", value=f"{crimes_por_hora:.2f}")

            with col3:
                st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total de Registros", value=f"{total_registros:,}".replace(",", "."))
                st.metric(label="Média de Crimes por Dia", value=f"{crimes_por_dia:.1f}")
            with col2:
                st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
                st.metric(label="Média de Crimes por Hora", value=f"{crimes_por_hora:.2f}")

        st.markdown("---")
        
        st.subheader(f"Distribuição de Crimes por {agrupamento_selecionado}")

        if 'map_view_type' not in st.session_state:
            st.session_state.map_view_type = 'Soma dos Crimes'

        def set_map_view(view_type):
            st.session_state.map_view_type = view_type

        st.markdown("""
        <style>
            /* Estilo para o botão INATIVO (muted) */
            div[data-testid="stButton"] > button[kind="secondary"] {
                background-color: #ab47bc; /* Um roxo mais claro e menos saturado */
                color: rgba(255, 255, 255, 0.6); /* Texto branco com transparência */
                border: none; /* Remove a borda padrão */
                box-shadow: none; /* Remove a sombra padrão */
                font-weight: 600;
                transition: all 0.2s ease-in-out;
            }

            /* Efeito ao passar o mouse no botão INATIVO */
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                background-color: #9c27b0; /* Escurece um pouco no hover */
            color: rgba(255, 255, 255, 0.9);
            }

            /* Estilo para o botão ATIVO (vibrante) */
            div[data-testid="stButton"] > button[kind="primary"] {
                background: linear-gradient(135deg, #8e24aa 0%, #ab47bc 100%);
                color: white;
                border: none;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15); /* Sombra para dar destaque */
                font-weight: 600;
            }
    
            /* Efeito de foco para acessibilidade em ambos os botões */
            div[data-testid="stButton"] > button:focus {
                box-shadow: 0 0 0 3px rgba(142, 36, 170, 0.5) !important;
                outline: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button(
                label="Soma dos Crimes",
                on_click=set_map_view,
                args=('Soma dos Crimes',),
                use_container_width=True,
                type="primary" if st.session_state.map_view_type == 'Soma dos Crimes' else "secondary"
            )

        with col2:
            st.button(
                label="Crimes por Mil Mulheres",
                on_click=set_map_view,
                args=('Crimes por Mil Mulheres',),
                use_container_width=True,
                type="primary" if st.session_state.map_view_type == 'Crimes por Mil Mulheres' else "secondary"
            )

        with col3:
            st.button(
                label="% de Mulheres Vítimas", # Usando o texto completo para clareza
                on_click=set_map_view,
                args=('% de Mulheres Vítimas',),
                use_container_width=True,
                type="primary" if st.session_state.map_view_type == '% de Mulheres Vítimas' else "secondary"
            )

        view_type = st.session_state.map_view_type

        map_df = pd.DataFrame()
        color_col = 'value'
        label_text = 'Valor'

        if view_type == "Soma dos Crimes":
            color_col = 'quantidade'
            label_text = f'Total de Registros ({agrupamento_selecionado})'
        elif view_type == "Crimes por Mil Mulheres":
            color_col = 'taxa_por_mil_mulheres'
            label_text = f'Crimes por Mil Mulheres ({agrupamento_selecionado})'
        else:
            color_col = 'percentual_mulheres_vitimas'
            label_text = f'% de Mulheres Vítimas ({agrupamento_selecionado})'

        base_map_df = df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
        base_map_df.columns = ['municipio_normalizado', 'total_fatos']

        if view_type != "Soma dos Crimes":
            base_map_df = pd.merge(base_map_df, df_populacao, on='municipio_normalizado', how='left')
            base_map_df.dropna(subset=['populacao_feminina'], inplace=True)

            anos_no_filtro = df_geral_filtrado['ano'].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            base_map_df['media_anual_fatos'] = base_map_df['total_fatos'] / num_anos

            if view_type == "Crimes por Mil Mulheres":
                base_map_df[color_col] = ((base_map_df['media_anual_fatos'] / base_map_df['populacao_feminina']) * 1000).fillna(0)
            else:
                base_map_df[color_col] = ((base_map_df['media_anual_fatos'] / base_map_df['populacao_feminina']) * 100).fillna(0)
        else:
            base_map_df.rename(columns={'total_fatos': color_col}, inplace=True)

        if agrupamento_selecionado == "Município" or agrupamento_selecionado == "Consolidado":
            map_df = base_map_df[['municipio_normalizado', color_col]]
        else: 
            agrupamento_col = "mesoregiao" if agrupamento_selecionado == "Mesorregião" else "associacao"
            
            municipio_grupo_mapping = df_geral_filtrado[['municipio_normalizado', agrupamento_col]].drop_duplicates()
            df_with_groups = pd.merge(base_map_df, municipio_grupo_mapping, on='municipio_normalizado', how='left')
            
            if view_type == "Soma dos Crimes":
                crimes_por_grupo = df_with_groups.groupby(agrupamento_col)[color_col].sum().reset_index()
                map_df = pd.merge(municipio_grupo_mapping, crimes_por_grupo, on=agrupamento_col, how='left').fillna(0)
            else: 
                grouped_pop = df_with_groups.groupby(agrupamento_col).agg(
                    total_fatos_grupo=('total_fatos', 'sum'),
                    populacao_feminina_grupo=('populacao_feminina', 'sum')
                ).reset_index()
                
                anos_no_filtro = df_geral_filtrado['ano'].unique()
                num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
                grouped_pop['media_anual_grupo'] = grouped_pop['total_fatos_grupo'] / num_anos

                if view_type == "Crimes por Mil Mulheres":
                    grouped_pop[color_col] = ((grouped_pop['media_anual_grupo'] / grouped_pop['populacao_feminina_grupo']) * 1000).fillna(0)
                else:
                    grouped_pop[color_col] = ((grouped_pop['media_anual_grupo'] / grouped_pop['populacao_feminina_grupo']) * 100).fillna(0)
                    
                map_df = pd.merge(municipio_grupo_mapping, grouped_pop[[agrupamento_col, color_col]], on=agrupamento_col, how='left').fillna(0)

        if not map_df.empty:
            map_df = map_df[map_df['municipio_normalizado'].isin(df_geral_filtrado['municipio_normalizado'].unique())]

        fig_mapa = px.choropleth_mapbox(
            map_df, 
            geojson=geojson_sc, 
            locations='municipio_normalizado',
            featureidkey="properties.NM_MUN_NORMALIZADO", 
            color=color_col,
            color_continuous_scale="Purples", 
            mapbox_style="carto-positron",
            zoom=6, 
            center={"lat": -27.59, "lon": -50.52}, 
            opacity=0.7,
            labels={color_col: label_text}
        )
        fig_mapa.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig_mapa, use_container_width=True, key="mapa_geral")

        st.markdown("---")

        st.subheader("Evolução dos Registros de Ocorrências (Série Temporal)")
        chart_type_temporal = st.selectbox(
            "Tipo de Gráfico",
            ("Linha", "Área", "Barras"),
            key="chart_type_temporal"
        )
        df_temporal = df_geral_filtrado.copy()
        df_temporal['ano_mes'] = df_temporal['data_fato'].dt.to_period('M').astype(str)
        
        color_param_temporal = None
        if agrupamento_selecionado == "Consolidado":
            registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values('ano_mes')
        else:
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            registros_por_mes_ano = df_temporal.groupby(['ano_mes', coluna_agrupamento]).size().reset_index(name='quantidade').sort_values('ano_mes')
            color_param_temporal = coluna_agrupamento

        if chart_type_temporal == "Barras":
            fig_temporal = px.bar(
                registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
                template='plotly_white'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_temporal.update_traces(marker_color='#8A2BE2')
        elif chart_type_temporal == "Área":
            fig_temporal = px.area(
                registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
                template='plotly_white'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_temporal.update_traces(line_color='#8A2BE2')
        else: # Linha
            fig_temporal = px.line(
                registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
                template='plotly_white', markers=True
            )
            if agrupamento_selecionado == "Consolidado":
                fig_temporal.update_traces(line_color='#8A2BE2')
        st.plotly_chart(fig_temporal, use_container_width=True, key="temporal_geral")
        st.markdown("---")

        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader("Registros de Ocorrências por Ano")
            chart_type_ano = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza", "Linha", "Área"),
                key="chart_type_ano"
            )
            if agrupamento_selecionado == "Consolidado":
                registros_por_ano = df_geral_filtrado['ano'].value_counts().sort_index().reset_index()
                registros_por_ano.columns = ['ano', 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": "municipio",
                    "Mesorregião": "mesoregiao",
                    "Associação": "associacao"
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                registros_por_ano = df_geral_filtrado.groupby(['ano', coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_ano == "Barras":
                fig_ano = px.bar(
                    registros_por_ano, x='ano', y='Quantidade', color=color_param,
                    labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_ano.update_traces(marker_color='#8A2BE2')
                fig_ano.update_traces(textposition='outside')
            elif chart_type_ano == "Linha":
                fig_ano = px.line(
                    registros_por_ano, x='ano', y='Quantidade', color=color_param,
                    labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white', markers=True
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_ano.update_traces(line_color='#8A2BE2')
            elif chart_type_ano == "Área":
                fig_ano = px.area(
                    registros_por_ano, x='ano', y='Quantidade', color=color_param,
                    labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_ano.update_traces(line_color='#8A2BE2')
            else: # Pizza
                pie_names = 'ano' if agrupamento_selecionado == "Consolidado" else color_param
                fig_ano = px.pie(
                    registros_por_ano, names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_ano.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_ano, use_container_width=True, key="ano_geral")

        with col_graf2:
            st.subheader("Tipos de Crimes Mais Frequentes")
            chart_type_fato = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_fato"
            )
            if agrupamento_selecionado == "Consolidado":
                registros_por_fato = df_geral_filtrado['fato_comunicado'].value_counts().reset_index()
                registros_por_fato.columns = ['fato_comunicado', 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": "municipio",
                    "Mesorregião": "mesoregiao",
                    "Associação": "associacao"
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                registros_por_fato = df_geral_filtrado.groupby(['fato_comunicado', coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_fato == "Barras":
                fig_fato = px.bar(
                    registros_por_fato, x='Quantidade', y='fato_comunicado', color=color_param, orientation='h',
                    labels={'fato_comunicado': 'Tipo de Crime', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_fato.update_traces(marker_color='#9370DB')
                fig_fato.update_traces(textposition='auto')
                fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
            else:
                pie_names = 'fato_comunicado' if agrupamento_selecionado == "Consolidado" else color_param
                fig_fato = px.pie(
                    registros_por_fato, names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_fato.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_fato, use_container_width=True, key="fato_geral")

        st.markdown("---")
        
        col_graf3, col_graf4 = st.columns(2)
        with col_graf3:
            st.subheader("Distribuição por Faixa Etária da Vítima")
            chart_type_faixa_etaria = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_faixa_etaria"
            )
            df_faixa_etaria = df_geral_filtrado.dropna(subset=['idade_vitima'])
            bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
            labels = ['0-12 anos', '13-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '61-70 anos', '71-79 anos', '80+ anos']
            df_faixa_etaria['faixa_etaria'] = pd.cut(df_faixa_etaria['idade_vitima'], bins=bins, labels=labels, right=True)
            registros_por_faixa = df_faixa_etaria['faixa_etaria'].value_counts().sort_index().reset_index()
            registros_por_faixa.columns = ['Faixa Etária', 'Quantidade']

            if chart_type_faixa_etaria == "Barras":
                fig_faixa_etaria = px.bar(
                    registros_por_faixa, x='Faixa Etária', y='Quantidade',
                    labels={'x': 'Faixa Etária', 'y': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_faixa_etaria.update_traces(marker_color='#9370DB', textposition='outside')
            else:
                fig_faixa_etaria = px.pie(
                    registros_por_faixa, names='Faixa Etária', values='Quantidade',
                    hole=.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_faixa_etaria.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_faixa_etaria, use_container_width=True, key="faixa_etaria_geral")
        with col_graf4:
            st.subheader("Distribuição de Ocorrências por Mês")
            chart_type_mes = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras", "Linha", "Área"),
                key="chart_type_mes"
            )
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            df_geral_filtrado['mes_cat'] = pd.Categorical(df_geral_filtrado['mes'], categories=meses_ordem, ordered=True)
            registros_por_mes = df_geral_filtrado['mes_cat'].value_counts().sort_index().reset_index()
            registros_por_mes.columns = ['Mês', 'Quantidade']
            nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
            registros_por_mes['Mês'] = registros_por_mes['Mês'].map(nomes_meses_pt)

            if chart_type_mes == "Barras":
                fig_mes = px.bar(
                    registros_por_mes, x='Mês', y='Quantidade',
                    labels={'x': 'Mês', 'y': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_mes.update_traces(marker_color='#9370DB', textposition='outside')
            elif chart_type_mes == "Linha":
                fig_mes = px.line(
                    registros_por_mes, x='Mês', y='Quantidade',
                    labels={'x': 'Mês', 'y': 'Quantidade'}, template='plotly_white', markers=True
                )
                fig_mes.update_traces(line_color='#9370DB')
            elif chart_type_mes == "Área":
                fig_mes = px.area(
                    registros_por_mes, x='Mês', y='Quantidade',
                    labels={'x': 'Mês', 'y': 'Quantidade'}, template='plotly_white'
                )
                fig_mes.update_traces(line_color='#9370DB')
            else: 
                fig_mes = px.pie(
                    registros_por_mes, names='Mês', values='Quantidade', hole=.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_mes.update_traces(textinfo='percent+label', textposition='outside', sort=False)
            st.plotly_chart(fig_mes, use_container_width=True, key="mes_geral")
        
        st.markdown("---")

        st.subheader("Distribuição de Ocorrências por Dia da Semana")
        chart_type_dia_semana = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Pizza", "Linha", "Área"),
            key="chart_type_dia_semana"
        )
        df_geral_filtrado['dia_semana'] = df_geral_filtrado['data_fato'].dt.day_name()
        dias_ordem = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        df_geral_filtrado['dia_semana_cat'] = pd.Categorical(df_geral_filtrado['dia_semana'], categories=dias_ordem, ordered=True)
        registros_por_dia = df_geral_filtrado['dia_semana_cat'].value_counts().sort_index().reset_index()
        registros_por_dia.columns = ['Dia da Semana', 'Quantidade']
        nomes_dias_pt = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        registros_por_dia['Dia da Semana'] = registros_por_dia['Dia da Semana'].map(nomes_dias_pt)

        if chart_type_dia_semana == "Barras":
            fig_dia_semana = px.bar(
                registros_por_dia, x='Dia da Semana', y='Quantidade',
                labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white', text='Quantidade'
            )
            fig_dia_semana.update_traces(marker_color='#8A2BE2', textposition='outside')
        elif chart_type_dia_semana == "Linha":
            fig_dia_semana = px.line(
                registros_por_dia, x='Dia da Semana', y='Quantidade',
                labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white', markers=True
            )
            fig_dia_semana.update_traces(line_color='#8A2BE2')
        elif chart_type_dia_semana == "Área":
            fig_dia_semana = px.area(
                registros_por_dia, x='Dia da Semana', y='Quantidade',
                labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white'
            )
            fig_dia_semana.update_traces(line_color='#8A2BE2')
        else:
            fig_dia_semana = px.pie(
                registros_por_dia, names='Dia da Semana', values='Quantidade',
                hole=.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_dia_semana.update_traces(textinfo='percent+label', textposition='outside')
        st.plotly_chart(fig_dia_semana, use_container_width=True, key="dia_semana_geral")

        st.markdown("---")
        
        st.subheader("Análise Populacional dos Crimes por Município")
        
        anos_no_filtro = df_geral_filtrado['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
        
        tabela_populacional = criar_tabela_populacional_agrupada(
            df_geral_filtrado, df_populacao, df_regioes, agrupamento_selecionado, num_anos
        )
        
        st.dataframe(
            tabela_populacional.style.format({
                'Média Anual de Fatos Ocorridos': '{:.2f}',
                'Fatos por Mil Mulheres (anual)': '{:.2f}',
                '% de Mulheres Vítimas (anual)': '{:.2f}%',
                'População Feminina': '{:,.0f}',
                'Tendência (CAGR %)': '{:+.1f}%'
            }),
            use_container_width=True
        )

        st.markdown("---")

        if agrupamento_selecionado != "Consolidado":
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento_tabela = mapa_agrupamento_tabela[agrupamento_selecionado]
            
            st.subheader(f"Tabela Consolidada de Crimes por {agrupamento_selecionado}")
            if not df_geral_filtrado.empty:
                tabela_consolidada = criar_tabela_consolidada(df_geral_filtrado, coluna_agrupamento_tabela, agrupamento_selecionado)
                if not tabela_consolidada.empty:
                    colunas_evolucao = [col for col in tabela_consolidada.columns if 'Diferença' in str(col)]

                    format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                    
                    anos_int = [col for col in tabela_consolidada.columns if isinstance(col, int)]
                    for ano in anos_int:
                        format_dict[ano] = '{:.0f}'
                    format_dict['total'] = '{:.0f}'
                    if 'Tendência (CAGR %)' in tabela_consolidada.columns:
                        format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                    colunas_para_colorir = colunas_evolucao[:]
                    if 'Tendência (CAGR %)' in tabela_consolidada.columns:
                        colunas_para_colorir.append('Tendência (CAGR %)')

                    styler = tabela_consolidada.style.applymap(
                        colorir_percentual,
                        subset=colunas_para_colorir
                    ).format(format_dict)
                    
                    st.dataframe(styler, use_container_width=True)
                else:
                    st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
        else:
            st.subheader("Tabela Consolidada de Crimes (Total SC)")
            if not df_geral_filtrado.empty:
                tabela_total = criar_tabela_total_consolidada(df_geral_filtrado)
                if not tabela_total.empty:
                    colunas_evolucao = [col for col in tabela_total.columns if 'Diferença' in str(col)]

                    format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                    
                    anos_int = [col for col in tabela_total.columns if isinstance(col, int)]
                    for ano in anos_int:
                        format_dict[ano] = '{:.0f}'
                    format_dict['total'] = '{:.0f}'
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                    colunas_para_colorir = colunas_evolucao[:]
                    if 'Tendência (CAGR %)' in tabela_total.columns:
                        colunas_para_colorir.append('Tendência (CAGR %)')

                    styler = tabela_total.style.applymap(
                        colorir_percentual,
                        subset=colunas_para_colorir
                    ).format(format_dict)
                    
                    st.dataframe(styler, use_container_width=True)
                else:
                    st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")

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

        st.subheader(f"Distribuição de Feminicídios por {agrupamento_selecionado}")

        if agrupamento_selecionado == "Município" or agrupamento_selecionado == "Consolidado":
            map_df_fem = df_feminicidio_filtrado['municipio_normalizado'].value_counts().reset_index()
            map_df_fem.columns = ['municipio_normalizado', 'quantidade']
        else: 
            agrupamento_col_fem = "mesoregiao" if agrupamento_selecionado == "Mesorregião" else "associacao"
            
            feminicidios_por_grupo = df_feminicidio_filtrado.groupby(agrupamento_col_fem).size().reset_index(name='quantidade_grupo')
            
            municipio_grupo_mapping_fem = df_feminicidio_filtrado[['municipio_normalizado', agrupamento_col_fem]].drop_duplicates()
            
            map_df_fem = pd.merge(municipio_grupo_mapping_fem, feminicidios_por_grupo, on=agrupamento_col_fem)
            map_df_fem = map_df_fem.rename(columns={'quantidade_grupo': 'quantidade'})

        fig_mapa_fem = px.choropleth_mapbox(
            map_df_fem, 
            geojson=geojson_sc, 
            locations='municipio_normalizado',
            featureidkey="properties.NM_MUN_NORMALIZADO", 
            color='quantidade',
            color_continuous_scale="Reds", 
            mapbox_style="carto-positron",
            zoom=6, 
            center={"lat": -27.59, "lon": -50.52}, 
            opacity=0.7,
            labels={'quantidade': f'Total de Feminicídios ({agrupamento_selecionado})'}
        )
        fig_mapa_fem.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig_mapa_fem, use_container_width=True, key="mapa_fem")

        st.markdown("---")
        
        st.subheader("Raio-X do Agressor")
        st.markdown("""
        Análise aprofundada sobre o perfil do agressor, incluindo a dinâmica de idade com a vítima e seu histórico criminal. 
        Estes gráficos ajudam a identificar padrões e possíveis pontos de falha na prevenção.
        """)
        
        col_raiox1, col_raiox2 = st.columns(2)
        
        with col_raiox1:
            if not df_feminicidio_filtrado.empty and df_feminicidio_filtrado[['idade_vitima', 'idade_autor']].notna().all(axis=1).any():
                fig_scatter_idade = px.scatter(
                    df_feminicidio_filtrado.dropna(subset=['idade_vitima', 'idade_autor']),
                    x='idade_vitima',
                    y='idade_autor',
                    title="Dinâmica de Idade: Vítima vs. Agressor",
                    labels={'idade_vitima': 'Idade da Vítima', 'idade_autor': 'Idade do Autor'},
                    color_discrete_sequence=['#8e24aa'],
                    hover_data=['municipio', 'relacao_autor', 'meio_crime']
                )
                
                max_idade = max(
                    df_feminicidio_filtrado['idade_vitima'].max(),
                    df_feminicidio_filtrado['idade_autor'].max()
                )
                
                fig_scatter_idade.add_shape(
                    type='line',
                    x0=0, y0=0,
                    x1=max_idade, y1=max_idade,
                    line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash'),
                    name='Idade Igual'
                )
                
                fig_scatter_idade.update_layout(
                    xaxis_title="Idade da Vítima",
                    yaxis_title="Idade do Autor",
                    legend_title="Legenda"
                )
                st.plotly_chart(fig_scatter_idade, use_container_width=True, key="scatter_idade_fem")
            else:
                st.info("Não há dados suficientes para exibir o gráfico de correlação de idades.")

        with col_raiox2:
            if not df_feminicidio_filtrado.empty and 'passagem_policial' in df_feminicidio_filtrado.columns and 'passagem_por_violencia_domestica' in df_feminicidio_filtrado.columns:
                total_agressores = len(df_feminicidio_filtrado)
                com_passagem = df_feminicidio_filtrado['passagem_policial'].value_counts().get('SIM', 0)
                sem_passagem = total_agressores - com_passagem
                
                com_bo_vd = len(df_feminicidio_filtrado[
                    (df_feminicidio_filtrado['passagem_policial'] == 'SIM') &
                    (df_feminicidio_filtrado['passagem_por_violencia_domestica'] == 'SIM')
                ])
                com_bo_outros = com_passagem - com_bo_vd

                if total_agressores > 0:
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=20,
                            thickness=25,
                            line=dict(color="white", width=2),
                            label=["Total de Agressores", "Com Passagem Policial", "Sem Passagem Policial", "Com B.O. por Violência Doméstica", "Com B.O. por Outros Crimes"],
                            color=["#4a148c", "#d32f2f", "#757575", "#e91e63", "#ff6f00"],
                        ),
                        link=dict(
                            source=[0, 0, 1, 1],
                            target=[1, 2, 3, 4],
                            value=[com_passagem, sem_passagem, com_bo_vd, com_bo_outros],
                            color=["rgba(211, 47, 47, 0.4)", "rgba(117, 117, 117, 0.3)", "rgba(233, 30, 99, 0.5)", "rgba(255, 111, 0, 0.4)"]
                        ),
                        textfont=dict(
                            family="Inter, sans-serif",
                            size=14,
                            color="white"
                        )
                    )])

                    fig_sankey.update_layout(
                        title={
                            'text': "Histórico do Agressor: A Escalada da Violência",
                            'font': {'size': 16, 'family': 'Inter, sans-serif', 'color': '#4a148c'}
                    },
                    font=dict(size=13, family="Inter, sans-serif"),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500
                    )

                    fig_sankey.add_annotation(
                        text="Fluxo da esquerda para direita mostra a progressão do histórico criminal",
                        xref="paper", yref="paper",
                        x=0.5, y=-0.1,
                        showarrow=False,
                        font=dict(size=11, color="#666")
                    )
                    st.plotly_chart(fig_sankey, use_container_width=True, key="sankey_fem")
                else:
                    st.info("Não há dados para exibir o gráfico de histórico do agressor.")
            else:
                st.info("Não há dados suficientes ou as colunas necessárias não existem para exibir o gráfico de histórico do agressor.")
        
        st.markdown("---")

        col_graf_fem1, col_graf_fem2 = st.columns(2)
        with col_graf_fem1:
            st.subheader("Vínculo entre a Vítima e o Autor")
            chart_type_vinculo = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_vinculo"
            )
            if agrupamento_selecionado == "Consolidado":
                vinculo_autor = df_feminicidio_filtrado['relacao_autor'].value_counts().reset_index()
                vinculo_autor.columns = ['relacao_autor', 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": "municipio",
                    "Mesorregião": "mesoregiao",
                    "Associação": "associacao"
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                vinculo_autor = df_feminicidio_filtrado.groupby(['relacao_autor', coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento
            
            if chart_type_vinculo == "Barras":
                fig_vinculo = px.bar(
                    vinculo_autor, x='Quantidade', y='relacao_autor', color=color_param, orientation='h',
                    labels={'relacao_autor': 'Vínculo com o Autor', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_vinculo.update_traces(marker_color='#8A2BE2')
                fig_vinculo.update_traces(textposition='auto')
                fig_vinculo.update_layout(yaxis={'categoryorder':'total ascending'})
            else:
                pie_names = 'relacao_autor' if agrupamento_selecionado == "Consolidado" else color_param
                fig_vinculo = px.pie(
                    vinculo_autor, names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_vinculo.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_vinculo, use_container_width=True, key="vinculo_fem")
        
        with col_graf_fem2:
            st.subheader("Meio Utilizado para o Crime")
            chart_type_meio = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_meio"
            )
            if agrupamento_selecionado == "Consolidado":
                meio_crime = df_feminicidio_filtrado['meio_crime'].value_counts().reset_index()
                meio_crime.columns = ['meio_crime', 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": "municipio",
                    "Mesorregião": "mesoregiao",
                    "Associação": "associacao"
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                meio_crime = df_feminicidio_filtrado.groupby(['meio_crime', coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_meio == "Barras":
                fig_meio = px.bar(
                    meio_crime, x='meio_crime', y='Quantidade', color=color_param,
                    labels={'meio_crime': 'Meio Utilizado', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_meio.update_traces(marker_color='#8A2BE2')
                fig_meio.update_traces(textposition='outside')
            else:
                pie_names = 'meio_crime' if agrupamento_selecionado == "Consolidado" else color_param
                fig_meio = px.pie(
                    meio_crime, names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_meio.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_meio, use_container_width=True, key="meio_fem")
        st.markdown("---")
        
        col_graf_fem1, col_graf_fem2 = st.columns(2)
        with col_graf_fem1:
            st.subheader("Distribuição de Idade da Vítima")
            chart_type_idade_vitima = st.selectbox(
                "Tipo de Gráfico",
                ("Histograma", "Gráfico de Densidade"),
                key="chart_type_idade_vitima"
            )
            df_idade_vitima = df_feminicidio_filtrado.dropna(subset=['idade_vitima'])
            if chart_type_idade_vitima == "Histograma":
                fig_idade_vitima = px.histogram(
                    df_idade_vitima, x='idade_vitima', nbins=20,
                    labels={'idade_vitima': 'Idade da Vítima', 'count': 'Quantidade'},
                    template='plotly_white', color_discrete_sequence=['#8e24aa']
                )
            else: 
                fig_idade_vitima = px.violin(
                    df_idade_vitima, y='idade_vitima',
                    labels={'idade_vitima': 'Idade da Vítima'},
                    template='plotly_white', color_discrete_sequence=['#8e24aa'],
                    box=True, points="all"
                )
            st.plotly_chart(fig_idade_vitima, use_container_width=True, key="idade_vitima_fem")
        
        with col_graf_fem2:
            st.subheader("Distribuição de Idade do Autor")
            chart_type_idade_autor = st.selectbox(
                "Tipo de Gráfico",
                ("Histograma", "Gráfico de Densidade"),
                key="chart_type_idade_autor"
            )
            df_idade_autor = df_feminicidio_filtrado.dropna(subset=['idade_autor'])
            if chart_type_idade_autor == "Histograma":
                fig_idade_autor = px.histogram(
                    df_idade_autor, x='idade_autor', nbins=20,
                    labels={'idade_autor': 'Idade do Autor', 'count': 'Quantidade'},
                    template='plotly_white', color_discrete_sequence=['#ab47bc']
                )
            else:
                fig_idade_autor = px.violin(
                    df_idade_autor, y='idade_autor',
                    labels={'idade_autor': 'Idade do Autor'},
                    template='plotly_white', color_discrete_sequence=['#ab47bc'],
                    box=True, points="all"
                )
            st.plotly_chart(fig_idade_autor, use_container_width=True, key="idade_autor_fem")

        st.markdown("---")

        col_graf_fem3, col_graf_fem4 = st.columns(2)
        with col_graf_fem3:
            st.subheader("Vítima Possuía B.O. contra o Autor?")
            chart_type_bo = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_bo"
            )
            bo_contra_autor = df_feminicidio_filtrado['bo_de_vd_contra_o_autor'].value_counts().reset_index()
            bo_contra_autor.columns = ['Resposta', 'Quantidade']
            
            if chart_type_bo == "Barras":
                fig_bo = px.bar(
                    bo_contra_autor, x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_bo.update_traces(marker_color='#8e24aa', textposition='outside')
            else:
                fig_bo = px.pie(
                    bo_contra_autor, names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_bo, use_container_width=True, key="bo_fem")

        with col_graf_fem4:
            st.subheader("Autor Foi Preso?")
            chart_type_preso = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_preso"
            )
            autor_preso = df_feminicidio_filtrado['autor_preso'].value_counts().reset_index()
            autor_preso.columns = ['Resposta', 'Quantidade']

            if chart_type_preso == "Barras":
                fig_preso = px.bar(
                    autor_preso, x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_preso.update_traces(marker_color='#ab47bc', textposition='outside')
            else:
                fig_preso = px.pie(
                    autor_preso, names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_preso, use_container_width=True, key="preso_fem")
        
        st.markdown("---")
        
        st.subheader("Localidade do Crime")
        chart_type_localidade = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Pizza"),
            key="chart_type_localidade"
        )
        if agrupamento_selecionado == "Consolidado":
            localidade_crime = df_feminicidio_filtrado['localidade'].value_counts().reset_index()
            localidade_crime.columns = ['localidade', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            localidade_crime = df_feminicidio_filtrado.groupby(['localidade', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento

        if chart_type_localidade == "Barras":
            fig_localidade = px.bar(
                localidade_crime, x='localidade', y='Quantidade', color=color_param,
                labels={'localidade': 'Localidade', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_localidade.update_traces(marker_color='#8A2BE2')
            fig_localidade.update_traces(textposition='outside')
        else:
            pie_names = 'localidade' if agrupamento_selecionado == "Consolidado" else color_param
            fig_localidade = px.pie(
                localidade_crime, names=pie_names, values='Quantidade',
                hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_localidade.update_traces(textinfo='percent+label', textposition='outside')
        st.plotly_chart(fig_localidade, use_container_width=True, key="localidade_fem")
        
        st.markdown("---")

        col_graf_fem5, col_graf_fem6 = st.columns(2)
        with col_graf_fem5:
            st.subheader("Autor com Registro de B.O.?")
            chart_type_autor_bo = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_autor_bo"
            )
            autor_bo = df_feminicidio_filtrado['passagem_policial'].value_counts().reset_index()
            autor_bo.columns = ['Resposta', 'Quantidade']
            if chart_type_autor_bo == "Barras":
                fig_autor_bo = px.bar(
                    autor_bo, x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_autor_bo.update_traces(marker_color='#8e24aa', textposition='outside')
            else:
                fig_autor_bo = px.pie(
                    autor_bo, names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_autor_bo, use_container_width=True, key="autor_bo_fem")

        with col_graf_fem6:
            st.subheader("Autor com B.O. por Violência Doméstica?")
            if 'passagem_por_violencia_domestica' in df_feminicidio_filtrado.columns:
                chart_type_autor_bo_vd = st.selectbox(
                    "Tipo de Gráfico",
                    ("Pizza", "Barras"),
                    key="chart_type_autor_bo_vd"
                )
                autor_bo_vd = df_feminicidio_filtrado['passagem_por_violencia_domestica'].value_counts().reset_index()
                autor_bo_vd.columns = ['Resposta', 'Quantidade']
                
                if not autor_bo_vd.empty:
                    if chart_type_autor_bo_vd == "Barras":
                        fig_autor_bo_vd = px.bar(
                            autor_bo_vd, x='Resposta', y='Quantidade',
                            labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                        )
                        fig_autor_bo_vd.update_traces(marker_color='#ab47bc', textposition='outside')
                    else:
                        fig_autor_bo_vd = px.pie(
                            autor_bo_vd, names='Resposta', values='Quantidade', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Purples_r
                        )
                    st.plotly_chart(fig_autor_bo_vd, use_container_width=True, key="autor_bo_vd_fem")
                else:
                    st.info("Não há dados sobre B.O. por violência doméstica para os filtros selecionados.")
            else:
                st.warning("A coluna 'Passagem por Violência Doméstica' não foi encontrada na base de dados.")

        st.markdown("---")

        st.subheader("Quantidade de Feminicídios por Mês/Ano")
        chart_type_fem_mes_ano = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Linha", "Área"),
            key="chart_type_fem_mes_ano"
        )
        df_feminicidio_filtrado['ano_mes'] = df_feminicidio_filtrado['data_fato'].dt.to_period('M').astype(str)
        if agrupamento_selecionado == "Consolidado":
            feminicidios_por_mes = df_feminicidio_filtrado.groupby('ano_mes').size().reset_index(name='Quantidade')
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            feminicidios_por_mes = df_feminicidio_filtrado.groupby(['ano_mes', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento
        feminicidios_por_mes.rename(columns={'ano_mes': 'Mês/Ano'}, inplace=True)
        if chart_type_fem_mes_ano == "Linha":
            fig_mes_ano = px.line(
                feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                template='plotly_white', markers=True
            )
            if agrupamento_selecionado == "Consolidado":
                fig_mes_ano.update_traces(line_color='#8A2BE2')
        elif chart_type_fem_mes_ano == "Área":
            fig_mes_ano = px.area(
                feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                template='plotly_white'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_mes_ano.update_traces(line_color='#8A2BE2')
        else: # Barras
            fig_mes_ano = px.bar(
                feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                template='plotly_white', text='Quantidade'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_mes_ano.update_traces(marker_color='#8A2BE2')
            fig_mes_ano.update_traces(textposition='outside')
        st.plotly_chart(fig_mes_ano, use_container_width=True, key="mes_ano_fem")
        
        st.markdown("---")

        st.subheader("Quantidade de Feminicídios por Ano")
        chart_type_fem_ano = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Linha", "Área"),
            key="chart_type_fem_ano"
        )
        if agrupamento_selecionado == "Consolidado":
            feminicidios_por_ano = df_feminicidio_filtrado['ano'].value_counts().sort_index().reset_index()
            feminicidios_por_ano.columns = ['ano', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            feminicidios_por_ano = df_feminicidio_filtrado.groupby(['ano', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento
        
        if chart_type_fem_ano == "Linha":
            fig_ano_fem = px.line(
                feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white', markers=True
            )
            if agrupamento_selecionado == "Consolidado":
                fig_ano_fem.update_traces(line_color='#6a1b9a')
        elif chart_type_fem_ano == "Área":
            fig_ano_fem = px.area(
                feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_ano_fem.update_traces(line_color='#6a1b9a')
        else: # Barras
            fig_ano_fem = px.bar(
                feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                labels={'ano': 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_ano_fem.update_traces(marker_color='#6a1b9a')
            fig_ano_fem.update_traces(textposition='outside')
        st.plotly_chart(fig_ano_fem, use_container_width=True, key="ano_fem")

        st.markdown("---")

        if agrupamento_selecionado != "Consolidado":
            mapa_agrupamento_tabela = {
                "Município": "municipio",
                "Mesorregião": "mesoregiao",
                "Associação": "associacao"
            }
            coluna_agrupamento_tabela = mapa_agrupamento_tabela[agrupamento_selecionado]
            
            st.subheader(f"Tabela Consolidada de Feminicídios por {agrupamento_selecionado}")
            if not df_feminicidio_filtrado.empty:
                tabela_feminicidio = criar_tabela_feminicidio_agrupado(df_feminicidio_filtrado, coluna_agrupamento_tabela, agrupamento_selecionado)
                if not tabela_feminicidio.empty:
                    colunas_evolucao = [col for col in tabela_feminicidio.columns if 'Diferença' in str(col)]
                    format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                    anos_int = [col for col in tabela_feminicidio.columns if isinstance(col, int)]
                    for ano in anos_int:
                        format_dict[ano] = '{:.0f}'
                    format_dict['total'] = '{:.0f}'
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'
                    
                    colunas_para_colorir = colunas_evolucao[:]
                    if 'Tendência (CAGR %)' in tabela_feminicidio.columns:
                        colunas_para_colorir.append('Tendência (CAGR %)')

                    styler = tabela_feminicidio.style.applymap(
                        colorir_percentual,
                        subset=colunas_para_colorir
                    ).format(format_dict)
                    
                    st.dataframe(styler, use_container_width=True)
                else:
                    st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
        else:
            st.subheader("Tabela Consolidada de Feminicídios (Total SC)")
            if not df_feminicidio_filtrado.empty:
                tabela_total_fem = criar_tabela_total_feminicidio(df_feminicidio_filtrado)
                if not tabela_total_fem.empty:
                    colunas_evolucao = [col for col in tabela_total_fem.columns if 'Diferença' in str(col)]
                    format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                    anos_int = [col for col in tabela_total_fem.columns if isinstance(col, int)]
                    for ano in anos_int:
                        format_dict[ano] = '{:.0f}'
                    format_dict['total'] = '{:.0f}'
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                    colunas_para_colorir = colunas_evolucao[:]
                    if 'Tendência (CAGR %)' in tabela_total_fem.columns:
                        colunas_para_colorir.append('Tendência (CAGR %)')

                    styler = tabela_total_fem.style.applymap(
                        colorir_percentual,
                        subset=colunas_para_colorir
                    ).format(format_dict)
                    
                    st.dataframe(styler, use_container_width=True)
                else:
                    st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")

with tab_analises_avancadas:
    st.header("Análises Avançadas sobre a Violência")
    st.markdown("Explore métricas e correlações mais profundas para entender as dinâmicas da violência contra a mulher em Santa Catarina.")
    
    with st.expander("📈 Índice de Letalidade da Violência", expanded=False):
        st.header("Índice de Letalidade da Violência")
        st.markdown("""
        **A Grande Pergunta:** Qual a probabilidade de uma denúncia de violência em um determinado município escalar para um feminicídio?

        Este índice diferencia o volume de denúncias da **falha fatal do sistema de prevenção**. Um município pode ter poucas denúncias, mas uma alta taxa de letalidade, indicando um problema gravíssimo e silencioso. O índice é calculado como:
        
        `Índice = (Total de Feminicídios / (Total de Ocorrências de Violência + Total de Feminicídios)) * 100`

        Isso representa: *"Para cada 100 ocorrências de violência contra a mulher, X resultam em morte."*
        """)
        
        # O agrupamento "Consolidado" não faz sentido para este índice, pois queremos comparar localidades.
        if agrupamento_selecionado == "Consolidado":
            st.warning("Por favor, selecione um nível de agrupamento (Município, Mesorregião ou Associação) para visualizar o Índice de Letalidade.")
        else:
            # Calcular o índice
            df_letalidade_calculado = calcular_indice_letalidade(df_geral_filtrado, df_feminicidio_filtrado, agrupamento_selecionado)
            
            if df_letalidade_calculado.empty:
                st.info("Não há dados suficientes para calcular o Índice de Letalidade com os filtros selecionados.")
            else:
                st.subheader(f"Mapa Coroplético do Índice de Letalidade por {agrupamento_selecionado}")

                if agrupamento_selecionado == "Município":
                    map_df_letalidade = df_letalidade_calculado.rename(columns={'localidade': 'municipio_normalizado'})
                else: 
                    mapa_grupo_para_indice = df_letalidade_calculado.set_index('localidade')['indice_letalidade']
                    
                    coluna_agrupamento = "mesoregiao" if agrupamento_selecionado == "Mesorregião" else "associacao"
                    
                    municipios_no_filtro = df_geral_filtrado[['municipio_normalizado', coluna_agrupamento]].drop_duplicates()
                    
                    municipios_no_filtro['indice_letalidade'] = municipios_no_filtro[coluna_agrupamento].map(mapa_grupo_para_indice)
                    map_df_letalidade = municipios_no_filtro.fillna(0)

                fig_mapa_letalidade = px.choropleth_mapbox(
                    map_df_letalidade, 
                    geojson=geojson_sc, 
                    locations='municipio_normalizado',
                    featureidkey="properties.NM_MUN_NORMALIZADO", 
                    color='indice_letalidade',
                    color_continuous_scale="OrRd", 
                    mapbox_style="carto-positron",
                    zoom=6, 
                    center={"lat": -27.59, "lon": -50.52}, 
                    opacity=0.7,
                    labels={'indice_letalidade': f'Índice de Letalidade (a cada 100 eventos)'}
                )
                fig_mapa_letalidade.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0},
                    coloraxis_colorbar=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.1,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig_mapa_letalidade, use_container_width=True, key="mapa_letalidade")

                st.markdown("---")
                
                st.subheader(f"Ranking do Índice de Letalidade por {agrupamento_selecionado}")
                st.markdown("A tabela abaixo classifica as localidades com maior risco de letalidade. O índice alto, mesmo com poucas ocorrências, é um sinal de alerta.")
                
                # Formatar a tabela de ranking
                df_ranking = df_letalidade_calculado.rename(columns={
                    'localidade': agrupamento_selecionado,
                    'total_eventos': 'Total de Eventos (Ocorrências + Feminicídios)',
                    'total_ocorrencias': 'Ocorrências de Violência',
                    'total_feminicidios': 'Feminicídios',
                    'indice_letalidade': 'Índice de Letalidade'
                }).set_index(agrupamento_selecionado)

                st.dataframe(
                    df_ranking.style.format({
                        'Índice de Letalidade': '{:.2f}',
                        'Total de Eventos (Ocorrências + Feminicídios)': '{:.0f}',
                        'Ocorrências de Violência': '{:.0f}',
                        'Feminicídios': '{:.0f}'
                    }).background_gradient(cmap='OrRd', subset=['Índice de Letalidade']),
                    use_container_width=True
                )

    with st.expander("🎯 Análise de Vulnerabilidade", expanded=False):
        st.header("Análise de Vulnerabilidade por Faixa Etária e Tipo de Crime")
        st.markdown("""
        Esta análise segmenta o problema por demografia, em vez de geografia, para identificar janelas de vulnerabilidade específicas na vida de uma mulher para certos tipos de crime. O objetivo é permitir a criação de campanhas de prevenção e políticas de proteção mais direcionadas.
        
        **A grande questão:** O perfil da violência muda drasticamente conforme a idade da vítima?
        """)

        st.subheader("Visualização da Distribuição de Crimes por Faixa Etária")
        
        df_vulnerabilidade = df_geral_filtrado.dropna(subset=['idade_vitima']).copy()
        bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
        labels = ['0-12 anos', '13-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '61-70 anos', '71-79 anos', '80+ anos']
        df_vulnerabilidade['faixa_etaria'] = pd.cut(df_vulnerabilidade['idade_vitima'], bins=bins, labels=labels, right=True)

        if not df_vulnerabilidade.empty:
            crime_counts = df_vulnerabilidade.groupby(['faixa_etaria', 'fato_comunicado']).size().unstack(fill_value=0)
            
            crime_percentages = crime_counts.div(crime_counts.sum(axis=1), axis=0) * 100
            
            crime_percentages = crime_percentages.reset_index()
            
            df_plot = crime_percentages.melt(
                id_vars='faixa_etaria', 
                var_name='fato_comunicado', 
                value_name='percentual'
            )

            fig_barras_vulnerabilidade = px.bar(
                df_plot,
                x='faixa_etaria',
                y='percentual',
                color='fato_comunicado',
                title="Distribuição Percentual de Tipos de Crime por Faixa Etária",
                labels={'faixa_etaria': 'Faixa Etária da Vítima', 'percentual': 'Percentual de Ocorrências (%)', 'fato_comunicado': 'Tipo de Crime'},
                template='plotly_white',
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_barras_vulnerabilidade.update_layout(
                barmode='stack',
                yaxis_ticksuffix='%'
            )
            st.plotly_chart(fig_barras_vulnerabilidade, use_container_width=True, key="barras_vulnerabilidade")
        else:
            st.warning("Não há dados suficientes para gerar o gráfico de vulnerabilidade com os filtros selecionados.")

        st.markdown("---")

        st.subheader("Análise de Concentração: Heatmap de Crimes por Faixa Etária")
        st.markdown("""
        O heatmap abaixo mostra a concentração de tipos de crime em cada faixa etária. Células mais escuras indicam uma maior concentração (em números absolutos), destacando quais crimes são mais prevalentes em determinados períodos da vida da mulher.
        """)

        if not df_vulnerabilidade.empty:
            crime_counts_heatmap = df_vulnerabilidade.groupby(['faixa_etaria', 'fato_comunicado']).size().unstack(fill_value=0)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=crime_counts_heatmap.values,
                x=crime_counts_heatmap.columns,
                y=crime_counts_heatmap.index,
                colorscale='Purples',
                hoverongaps=False
            ))

            fig_heatmap.update_layout(
                title="Concentração de Crimes (Absoluto) por Faixa Etária e Tipo",
                xaxis_title="Tipo de Crime",
                yaxis_title="Faixa Etária da Vítima",
            )
            st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_vulnerabilidade")
        else:
            st.warning("Não há dados suficientes para gerar o heatmap com os filtros selecionados.")

    with st.expander("🔎 Efetividade da Denúncia", expanded=False):
        st.header("Índice de Efetividade da Denúncia")
        st.markdown("""
        **A Grande Pergunta:** Em um município, um alto número de denúncias de crimes "menores" (como ameaça) está correlacionado a um menor número de crimes graves (lesão corporal, feminicídio)? Ou seja, a denúncia está funcionando como um mecanismo de prevenção eficaz?

        Este é um proxy para medir a efetividade da resposta do sistema de segurança e apoio. Um sistema eficaz deveria intervir após a primeira denúncia, impedindo a escalada da violência.
        """)

        crimes_leves = ["Ameaça", "Vias de Fato"]
        crimes_graves = ["Lesão Corporal Dolosa", "Estupro", "Feminicídio"]

        if not df_geral_filtrado.empty and not df_populacao.empty:
            df_leves = df_geral_filtrado[df_geral_filtrado['fato_comunicado'].isin(crimes_leves)]
            contagem_leves = df_leves.groupby('municipio_normalizado').size().reset_index(name='total_crimes_leves')

            df_graves = df_geral_filtrado[df_geral_filtrado['fato_comunicado'].isin(crimes_graves)]
            contagem_graves = df_graves.groupby('municipio_normalizado').size().reset_index(name='total_crimes_graves')

            df_efetividade = pd.merge(contagem_leves, contagem_graves, on='municipio_normalizado', how='outer').fillna(0)

            df_efetividade = pd.merge(df_efetividade, df_populacao[['municipio_normalizado', 'municipio', 'populacao_feminina']], on='municipio_normalizado', how='left')
            df_efetividade.dropna(subset=['populacao_feminina', 'municipio'], inplace=True)
            df_efetividade = df_efetividade[df_efetividade['populacao_feminina'] > 0]

            df_efetividade['taxa_crimes_leves'] = (df_efetividade['total_crimes_leves'] / df_efetividade['populacao_feminina']) * 1000
            df_efetividade['taxa_crimes_graves'] = (df_efetividade['total_crimes_graves'] / df_efetividade['populacao_feminina']) * 1000

            st.subheader("Gráfico de Dispersão: Relação entre Denúncias Leves e Ocorrências Graves")
            fig_efetividade = px.scatter(
                df_efetividade,
                x='taxa_crimes_leves',
                y='taxa_crimes_graves',
                hover_name='municipio',
                hover_data={
                    'total_crimes_leves': ':.0f',
                    'total_crimes_graves': ':.0f',
                    'populacao_feminina': ':.0f',
                    'municipio': False
                },
                trendline="ols",  
                labels={
                    'taxa_crimes_leves': 'Taxa de Crimes Leves (por 1.000 mulheres)',
                    'taxa_crimes_graves': 'Taxa de Crimes Graves (por 1.000 mulheres)'
                },
                title="Efetividade da Denúncia: Crimes Leves vs. Graves por Município"
            )
            fig_efetividade.update_traces(marker=dict(size=10, opacity=0.7, color='#8e24aa'))
            st.plotly_chart(fig_efetividade, use_container_width=True, key="scatter_efetividade")

            st.markdown("---")
            st.subheader("Como Interpretar o Gráfico")
            st.markdown("""
            - **Correlação Negativa (Pontos formam uma linha que desce da esquerda para a direita):** Cenário Ideal. Municípios onde as mulheres denunciam mais os crimes leves tendem a ter menos crimes graves. Isso sugere que a denúncia e a intervenção precoce estão funcionando.
            - **Correlação Positiva (Pontos formam uma linha que sobe):** Pior Cenário. Municípios com muitas denúncias leves também têm muitos crimes graves. Isso pode indicar um sistema que apenas registra as ocorrências, mas falha em proteger a vítima e impedir a escalada da violência.
            - **Sem Correlação (Nuvem de pontos dispersa):** Indica que a relação não é direta e outros fatores (socioeconômicos, culturais) são mais determinantes.
            """)
            st.info("Este insight não mede apenas o crime, mas tenta avaliar a resposta do ecossistema de proteção. Ele gera hipóteses sobre a efetividade da polícia, medidas protetivas e redes de apoio, apontando para municípios que podem precisar de uma auditoria em seus processos de atendimento à mulher.")

        else:
            st.warning("Não há dados suficientes para gerar a análise de efetividade com os filtros selecionados.")

    with st.expander("🌐 Contágio Geográfico", expanded=False):
        st.header("Análise de Contágio Geográfico (Hotspots de Vizinhança)")
        st.markdown("""
        **A Grande Pergunta:** A violência em um município é um fenômeno isolado ou é influenciada pela situação de seus vizinhos? Existem "clusters" regionais de violência que transcendem as fronteiras municipais?

        Esta análise trata a violência como um fenômeno que pode se "espalhar" ou se concentrar em microrregiões, requerendo soluções coordenadas entre múltiplos municípios.
        """)
        
        if not df_geral_filtrado.empty and not df_populacao.empty:
            mapa_vizinhos = mapear_vizinhos(geojson_sc)

            crimes_por_municipio = df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
            crimes_por_municipio.columns = ['municipio_normalizado', 'total_fatos']

            df_taxas = pd.merge(crimes_por_municipio, df_populacao[['municipio_normalizado', 'municipio', 'populacao_feminina']], on='municipio_normalizado', how='left')
            df_taxas.dropna(subset=['populacao_feminina', 'municipio'], inplace=True)
            df_taxas = df_taxas[df_taxas['populacao_feminina'] > 0]
            
            anos_no_filtro = df_geral_filtrado['ano'].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            media_anual_fatos = df_taxas['total_fatos'] / num_anos

            df_taxas['taxa_propria'] = (media_anual_fatos / df_taxas['populacao_feminina']) * 1000

            taxa_por_municipio_map = df_taxas.set_index('municipio_normalizado')['taxa_propria']
            
            taxas_vizinhanca = []
            for municipio in df_taxas['municipio_normalizado']:
                vizinhos = mapa_vizinhos.get(municipio, [])
                if vizinhos:
                    taxas_dos_vizinhos = taxa_por_municipio_map.reindex(vizinhos).dropna()
                    if not taxas_dos_vizinhos.empty:
                        taxas_vizinhanca.append(taxas_dos_vizinhos.mean())
                    else:
                        taxas_vizinhanca.append(0)
                else:
                    taxas_vizinhanca.append(0)
            
            df_taxas['taxa_vizinhanca'] = taxas_vizinhanca

            st.subheader("Gráfico de Dispersão: Taxa de Violência Própria vs. Vizinhança")
            
            media_propria = df_taxas['taxa_propria'].mean()
            media_vizinhanca = df_taxas['taxa_vizinhanca'].mean()

            fig_contagio = px.scatter(
                df_taxas,
                x='taxa_propria',
                y='taxa_vizinhanca',
                hover_name='municipio',
                hover_data={'taxa_propria': ':.2f', 'taxa_vizinhanca': ':.2f', 'municipio': False},
                labels={
                    'taxa_propria': 'Taxa de Violência do Próprio Município (por mil mulheres)',
                    'taxa_vizinhanca': 'Taxa Média de Violência da Vizinhança (por mil mulheres)'
                },
                title="Análise de Hotspots: Violência Local vs. Influência da Vizinhança"
            )

            fig_contagio.add_vline(x=media_propria, line_width=1, line_dash="dash", line_color="gray")
            fig_contagio.add_hline(y=media_vizinhanca, line_width=1, line_dash="dash", line_color="gray")

            max_x = df_taxas['taxa_propria'].max() * 1.05
            max_y = df_taxas['taxa_vizinhanca'].max() * 1.05
            fig_contagio.add_annotation(x=media_propria, y=max_y, text="Municípios em Risco", showarrow=False, xanchor='center', yanchor='top', font=dict(color="orange"))
            fig_contagio.add_annotation(x=max_x, y=max_y, text="Hotspots (Alto-Alto)", showarrow=False, xanchor='right', yanchor='top', font=dict(color="red"))
            fig_contagio.add_annotation(x=0, y=0, text="Pontos Frios (Baixo-Baixo)", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color="green"))
            fig_contagio.add_annotation(x=max_x, y=0, text="Ilhas de Violência", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color="purple"))
            
            fig_contagio.update_traces(marker=dict(size=10, opacity=0.7, color='#8e24aa'))
            st.plotly_chart(fig_contagio, use_container_width=True, key="scatter_contagio")

            st.markdown("---")
            st.subheader("Como Interpretar os Quadrantes")
            st.markdown("""
            - **🔴 Hotspots (Superior Direito):** Municípios com alta violência, cercados por vizinhos também com alta violência. Indicam um *cluster* geográfico de risco que exige ações regionais coordenadas.
            - **🟠 Municípios em Risco (Superior Esquerdo):** Baixa violência interna, mas cercados por vizinhos violentos. Estão em risco de "contágio" ou "transbordamento" da violência. Ações preventivas são cruciais aqui.
            - **🟣 Ilhas de Violência (Inferior Direito):** Alta violência interna, mas cercados por vizinhos mais pacíficos. O problema é mais localizado e pode estar ligado a fatores específicos do município.
            - **🟢 Pontos Frios (Inferior Esquerdo):** Baixa violência, cercados por vizinhos também com baixa violência. São áreas de resiliência que podem oferecer *insights* sobre políticas públicas eficazes.
            """)
        else:
            st.warning("Não há dados suficientes para gerar a Análise de Contágio Geográfico com os filtros selecionados.")
    
    with st.expander("📅 Análise Sazonal", expanded=False):
        st.header("Sazonalidade e Eventos-Chave: O Calendário do Risco")
        st.markdown("""
        **A Grande Pergunta:** A violência contra a mulher aumenta de forma previsível em torno de datas ou eventos específicos (feriados, fins de semana prolongados, períodos de férias)?
        
        Esta análise vai além do gráfico mensal, investigando micro-padrões temporais que podem orientar ações de segurança e campanhas de conscientização.
        """)

        df_geral_filtrado['dia_semana'] = df_geral_filtrado['data_fato'].dt.day_name()
        df_geral_filtrado['mes'] = df_geral_filtrado['data_fato'].dt.month_name()

        if not df_geral_filtrado.empty:
            st.subheader("Impacto de Feriados e Fins de Semana na Média Diária de Ocorrências")

            df_geral_filtrado_sazonal = df_geral_filtrado.copy()
            df_geral_filtrado_sazonal['data_fato_date'] = df_geral_filtrado_sazonal['data_fato'].dt.date
            df_calendario['data_fato_date'] = df_calendario['data'].dt.date

            df_geral_filtrado_sazonal = pd.merge(
                df_geral_filtrado_sazonal,
                df_calendario[['data_fato_date', 'is_feriado', 'is_fim_de_semana', 'is_vespera_feriado', 'is_pos_feriado']],
                on='data_fato_date',
                how='left'
            )
            df_geral_filtrado_sazonal[['is_feriado', 'is_vespera_feriado', 'is_pos_feriado']] = df_geral_filtrado_sazonal[['is_feriado', 'is_vespera_feriado', 'is_pos_feriado']].fillna(False)

            datas_periodo_filtrado = pd.date_range(start=data_inicial, end=data_final)
            df_periodo_completo = pd.DataFrame(datas_periodo_filtrado, columns=['data'])
            df_periodo_completo['data_fato_date'] = df_periodo_completo['data'].dt.date

            df_periodo_completo_com_eventos = pd.merge(
                df_periodo_completo,
                df_calendario[['data_fato_date', 'is_feriado', 'is_fim_de_semana', 'is_vespera_feriado', 'is_pos_feriado']],
                on='data_fato_date',
                how='left'
            )
            df_periodo_completo_com_eventos.fillna(False, inplace=True)

            total_dias_feriado = df_periodo_completo_com_eventos['is_feriado'].sum()
            total_dias_vespera = df_periodo_completo_com_eventos['is_vespera_feriado'].sum()
            total_dias_pos = df_periodo_completo_com_eventos['is_pos_feriado'].sum()
            total_dias_fds = df_periodo_completo_com_eventos['is_fim_de_semana'].sum()
            total_dias_uteis_comuns = len(df_periodo_completo_com_eventos[
                (df_periodo_completo_com_eventos['is_feriado'] == False) &
                (df_periodo_completo_com_eventos['is_fim_de_semana'] == False) &
                (df_periodo_completo_com_eventos['is_vespera_feriado'] == False) &
                (df_periodo_completo_com_eventos['is_pos_feriado'] == False)
            ])

            ocorrencias_feriado = df_geral_filtrado_sazonal['is_feriado'].sum()
            ocorrencias_vespera = df_geral_filtrado_sazonal['is_vespera_feriado'].sum()
            ocorrencias_pos = df_geral_filtrado_sazonal['is_pos_feriado'].sum()
            ocorrencias_fds = df_geral_filtrado_sazonal['is_fim_de_semana'].sum()
            ocorrencias_uteis_comuns = len(df_geral_filtrado_sazonal[
                (df_geral_filtrado_sazonal['is_feriado'] == False) &
                (df_geral_filtrado_sazonal['is_fim_de_semana'] == False) &
                (df_geral_filtrado_sazonal['is_vespera_feriado'] == False) &
                (df_geral_filtrado_sazonal['is_pos_feriado'] == False)
            ])

            media_feriado = (ocorrencias_feriado / total_dias_feriado) if total_dias_feriado > 0 else 0
            media_vespera = (ocorrencias_vespera / total_dias_vespera) if total_dias_vespera > 0 else 0
            media_pos = (ocorrencias_pos / total_dias_pos) if total_dias_pos > 0 else 0
            media_fds = (ocorrencias_fds / total_dias_fds) if total_dias_fds > 0 else 0
            media_uteis_comuns = (ocorrencias_uteis_comuns / total_dias_uteis_comuns) if total_dias_uteis_comuns > 0 else 0
            
            df_medias = pd.DataFrame({
                'Tipo de Dia': ['Dia Útil Comum', 'Fim de Semana', 'Véspera de Feriado', 'Feriado', 'Pós-Feriado'],
                'Média Diária de Ocorrências': [media_uteis_comuns, media_fds, media_vespera, media_feriado, media_pos]
            }).sort_values('Média Diária de Ocorrências', ascending=False)
            
            fig_barras_sazonal = px.bar(
                df_medias,
                x='Tipo de Dia',
                y='Média Diária de Ocorrências',
                text='Média Diária de Ocorrências',
                title="Média de Ocorrências por Tipo de Dia",
                labels={'Média Diária de Ocorrências': 'Média de Ocorrências por Dia', 'Tipo de Dia': ''},
                template='plotly_white'
            )
            fig_barras_sazonal.update_traces(
                marker_color='#8e24aa',
                texttemplate='%{text:.2f}',
                textposition='outside'
            )
            st.plotly_chart(fig_barras_sazonal, use_container_width=True, key="barras_sazonal")

            st.markdown("---")

            st.subheader("Heatmap de Risco: Dia da Semana vs. Mês")
            st.markdown("A cor de cada célula representa a quantidade média de crimes, destacando os períodos mais 'quentes' do ano.")
            
            datas_periodo_filtrado_hm = pd.to_datetime(pd.date_range(start=data_inicial, end=data_final))

            df_periodo_completo_hm = pd.DataFrame(datas_periodo_filtrado_hm, columns=['data_fato'])
            df_periodo_completo_hm['mes'] = df_periodo_completo_hm['data_fato'].dt.month_name()
            df_periodo_completo_hm['dia_semana'] = df_periodo_completo_hm['data_fato'].dt.day_name()

            contagem_dias_hm = df_periodo_completo_hm.groupby(['mes', 'dia_semana']).size().reset_index(name='total_dias_no_periodo')

            ocorrencias_hm = df_geral_filtrado.groupby(['mes', 'dia_semana']).size().reset_index(name='total_ocorrencias')

            df_media_hm = pd.merge(
                contagem_dias_hm,
                ocorrencias_hm,
                on=['mes', 'dia_semana'],
                how='left'
            ).fillna({'total_ocorrencias': 0})

            df_media_hm['media_diaria'] = df_media_hm['total_ocorrencias'] / df_media_hm['total_dias_no_periodo']
            
            heatmap_pivot = df_media_hm.pivot_table(index='mes', columns='dia_semana', values='media_diaria').fillna(0)
            
            # 8. Ordenar meses e dias da semana
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
            dias_ordem = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            nomes_dias_pt = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
            
            heatmap_pivot = heatmap_pivot.reindex(index=meses_ordem, columns=dias_ordem, fill_value=0)
            
            heatmap_pivot.index = heatmap_pivot.index.map(nomes_meses_pt)
            heatmap_pivot.columns = [nomes_dias_pt[col] for col in heatmap_pivot.columns]
            
            fig_heatmap_sazonal = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns,
                y=heatmap_pivot.index,
                colorscale='Purples',
                hoverongaps=False,
                text=heatmap_pivot.values,
                texttemplate="%{text:.2f}"
            ))

            fig_heatmap_sazonal.update_layout(
                title="Concentração Média de Ocorrências por Mês e Dia da Semana",
                xaxis_title="Dia da Semana",
                yaxis_title="Mês",
                xaxis={'type': 'category'}, 
                yaxis={'type': 'category', 'categoryorder': 'array', 'categoryarray': list(nomes_meses_pt.values())}
            )
            st.plotly_chart(fig_heatmap_sazonal, use_container_width=True, key="heatmap_sazonal")
            
            st.markdown("---")
            st.info("""
            **Por que é Avançado:** Transforma a análise temporal de descritiva ("o que aconteceu") para preditiva ("o que provavelmente vai acontecer"). Isso permite um planejamento proativo, como o reforço de patrulhas e a intensificação de campanhas "Ligue 180" durante o Carnaval ou as festas de fim de ano, por exemplo.
            """)

        else:
            st.warning("Não há dados para exibir a Análise Sazonal com os filtros selecionados.")


    if not df_geral_filtrado.empty:
        pass
    else:
        with tab_geral:
            st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
            st.warning("Certifique-se de que os arquivos `base_geral.xlsx`, `base_feminicidio.xlsx` e `municipios_sc.json` existem na pasta `data`.")
        with tab_feminicidio:
            st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
            st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data`.")

with tab_glossario:
    try:
        with open("metodologia_glossario.txt", "r", encoding="utf-8") as f:
            texto_metodologia = f.read()
        st.markdown(texto_metodologia, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo 'metodologia_glossario.txt' não encontrado.")
        st.info("Por favor, certifique-se de que o arquivo com a metodologia e o glossário está na mesma pasta que o script principal.")

with tab_download:
    st.header("Download das Fontes de Dados")
    st.markdown("Faça o download dos arquivos de dados brutos utilizados para a construção deste painel.")
    st.markdown("---")

    # --- Primeira Linha de Downloads ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Base Geral de Crimes")
        st.markdown("Registros de violência contra a mulher (exceto feminicídios).")
        try:
            with open("data/base_geral.xlsx", "rb") as fp:
                st.download_button(
                    label="Download (XLSX)",
                    data=fp,
                    file_name="base_geral.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_geral"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'base_geral.xlsx' não encontrado.")

    with col2:
        st.subheader("Base de Feminicídios")
        st.markdown("Registros detalhados de feminicídios consumados.")
        try:
            with open("data/base_feminicidio.xlsx", "rb") as fp:
                st.download_button(
                    label="Download (XLSX)",
                    data=fp,
                    file_name="base_feminicidio.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_feminicidio"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'base_feminicidio.xlsx' não encontrado.")

    with col3:
        st.subheader("Base Populacional")
        st.markdown("Dados da população feminina por município.")
        try:
            with open("data/base_populacao.xlsx", "rb") as fp:
                st.download_button(
                    label="Download (XLSX)",
                    data=fp,
                    file_name="base_populacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_populacao"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'base_populacao.xlsx' não encontrado.")

    st.markdown("---")

    # --- Segunda Linha de Downloads ---
    col4, col5, col6 = st.columns(3)

    with col4:
        st.subheader("Base de Regiões")
        st.markdown("Mapeamento de municípios para mesorregiões e associações.")
        try:
            with open("data/base_regioes_associacoes.xlsx", "rb") as fp:
                st.download_button(
                    label="Download (XLSX)",
                    data=fp,
                    file_name="base_regioes_associacoes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_regioes"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'base_regioes_associacoes.xlsx' não encontrado.")

    with col5:
        st.subheader("Base de Calendário")
        st.markdown("Mapeamento de feriados para análise sazonal.")
        try:
            with open("data/base_calendario_feriados.xlsx", "rb") as fp:
                st.download_button(
                    label="Download (XLSX)",
                    data=fp,
                    file_name="base_calendario_feriados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_calendario"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'base_calendario_feriados.xlsx' não encontrado.")

    with col6:
        st.subheader("Mapa de Municípios")
        st.markdown("Arquivo GeoJSON com as geometrias dos municípios de SC.")
        try:
            with open("data/municipios_sc.json", "rb") as fp:
                st.download_button(
                    label="Download (JSON)",
                    data=fp,
                    file_name="municipios_sc.json",
                    mime="application/json",
                    key="download_geojson"
                )
        except FileNotFoundError:
            st.warning("Arquivo 'municipios_sc.json' não encontrado.")
