import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import unicodedata
import numpy as np
from typing import Optional, List, Dict, Any, Union

# --- CONSTANTS ---
COL_DATA_FATO = 'data_fato'
COL_MUNICIPIO = 'municipio'
COL_FATO_COMUNICADO = 'fato_comunicado'
COL_IDADE_VITIMA = 'idade_vitima'
COL_MUN_NORMALIZADO = 'municipio_normalizado'
COL_MESOREGIAO = 'mesoregiao'
COL_ASSOCIACAO = 'associacao'
COL_ANO = 'ano'
COL_MES = 'mes'
COL_RELACAO_AUTOR = 'relacao_autor'
COL_BO_CONTRA_AUTOR = 'bo_de_vd_contra_o_autor'
COL_IDADE_AUTOR = 'idade_autor'
COL_PASSAGEM_POLICIAL = 'passagem_policial'
COL_PASSAGEM_VD = 'passagem_por_violencia_domestica'
COL_AUTOR_PRESO = 'autor_preso'
COL_MEIO_CRIME = 'meio_crime'
COL_LOCALIDADE = 'localidade'
COL_POPULACAO_FEMININA = 'populacao_feminina'
COL_TOTAL_FATOS = 'total_fatos'

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

# --- NOVA FUNÇÃO AUXILIAR PARA NORMALIZAR TEXTO ---
def normalizar_nome(nome: str) -> str:
    """Remove acentos, caracteres especiais e converte para maiúsculo."""
    if isinstance(nome, str):
        nfkd_form = unicodedata.normalize('NFD', nome)
        nome_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return nome_sem_acento.upper().strip()
    return nome

# --- FUNÇÕES PARA CARREGAR OS DADOS ---

@st.cache_data
def carregar_geojson_sc() -> Optional[Dict[str, Any]]:
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
def carregar_dados_gerais() -> pd.DataFrame:
    """Carrega e trata os dados da base geral, normalizando nomes de municípios."""
    try:
        df_regioes = carregar_dados_regioes()
        df_geral = pd.read_excel('data/base_geral.xlsx')

        df_geral.columns = (df_geral.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False))

        df_geral.rename(columns={
            'data_do_fato': COL_DATA_FATO, 'município': COL_MUNICIPIO,
            'fato_comunicado': COL_FATO_COMUNICADO, 'idade': COL_IDADE_VITIMA
        }, inplace=True)

        df_geral[COL_DATA_FATO] = pd.to_datetime(df_geral[COL_DATA_FATO])
        df_geral[COL_IDADE_VITIMA] = pd.to_numeric(df_geral[COL_IDADE_VITIMA], errors='coerce')
        
        if COL_MUNICIPIO in df_geral.columns:
            df_geral[COL_MUN_NORMALIZADO] = df_geral[COL_MUNICIPIO].apply(normalizar_nome)

        df_geral = pd.merge(df_geral, df_regioes[[COL_MUN_NORMALIZADO, COL_MESOREGIAO, COL_ASSOCIACAO]], on=COL_MUN_NORMALIZADO, how='left')
        df_geral[COL_MESOREGIAO].fillna('Não informado', inplace=True)
        df_geral[COL_ASSOCIACAO].fillna('Não informado', inplace=True)
        
        df_feminicidio_raw = carregar_dados_feminicidio()
        if not df_feminicidio_raw.empty:
            df_feminicidio_para_geral = df_feminicidio_raw.copy()
            df_feminicidio_para_geral[COL_FATO_COMUNICADO] = 'Feminicídio'
            
            df_final = pd.concat([df_geral, df_feminicidio_para_geral], ignore_index=True)
        else:
            df_final = df_geral

        df_final[COL_ANO] = df_final[COL_DATA_FATO].dt.year
        df_final[COL_MES] = df_final[COL_DATA_FATO].dt.month_name()
        
        return df_final
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' ou 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base geral: A coluna {e} não foi encontrada.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_feminicidio() -> pd.DataFrame:
    """Carrega e trata os dados da base de feminicídio de forma robusta."""
    try:
        df_regioes = carregar_dados_regioes()
        df = pd.read_excel('data/base_feminicidio.xlsx')

        df.rename(columns={
            'DATA': COL_DATA_FATO,
            'MUNICÍPIO': COL_MUNICIPIO,
            'RELAÇÃO COM O AUTOR': COL_RELACAO_AUTOR,
            'BO DE VD CONTRA O AUTOR': COL_BO_CONTRA_AUTOR,
            'IDADE AUTOR': COL_IDADE_AUTOR,
            'IDADE VITIMA': COL_IDADE_VITIMA,
            'PASSAGEM POLICIAL': COL_PASSAGEM_POLICIAL,
            'PASSAGEM POR VIOLÊNCIA DOMÉSTICA': COL_PASSAGEM_VD,
            'PRISÃO': COL_AUTOR_PRESO,
            'MEIO': COL_MEIO_CRIME
        }, inplace=True)

        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('ê', 'e', regex=False)
                      .str.replace('á', 'a', regex=False))

        df[COL_DATA_FATO] = pd.to_datetime(df[COL_DATA_FATO])
        df[COL_IDADE_VITIMA] = pd.to_numeric(df[COL_IDADE_VITIMA], errors='coerce')
        df[COL_IDADE_AUTOR] = pd.to_numeric(df[COL_IDADE_AUTOR], errors='coerce')
        
        if COL_MUNICIPIO in df.columns:
            df[COL_MUN_NORMALIZADO] = df[COL_MUNICIPIO].apply(normalizar_nome)

        df = pd.merge(df, df_regioes[[COL_MUN_NORMALIZADO, COL_MESOREGIAO, COL_ASSOCIACAO]], on=COL_MUN_NORMALIZADO, how='left')
        df[COL_MESOREGIAO].fillna('Não informado', inplace=True)
        df[COL_ASSOCIACAO].fillna('Não informado', inplace=True)
        
        df[COL_ANO] = df[COL_DATA_FATO].dt.year
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base de feminicídio: A coluna {e} não foi encontrada.")
        st.write("Verifique se os nomes de colunas no arquivo Excel correspondem exatamente aos da imagem fornecida.")
        st.write("Colunas encontradas no arquivo:", pd.read_excel('data/base_feminicidio.xlsx').columns.tolist())
        return pd.DataFrame()

# --- FUNÇÕES DE ESTILIZAÇÃO PARA A TABELA ---
def colorir_percentual(val: float) -> str:
    """Retorna a cor para o valor percentual."""
    if pd.isna(val) or val == 0:
        return ''
    color = 'red' if val > 0 else 'green'
    return f'color: {color}'

def formatar_seta_percentual(val: float) -> str:
    """Formata o valor com seta e percentual."""
    if pd.isna(val):
        return '-'
    seta = '▲' if val > 0 else '▼' if val < 0 else ''
    if seta:
        return f'{seta} {abs(val):.2f}%'
    return f'{abs(val):.2f}%'

def calcular_cagr(valor_inicial: Union[float, pd.Series], valor_final: Union[float, pd.Series], num_anos: int) -> Union[float, pd.Series]:
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

# --- FUNÇÕES DE GERAÇÃO DE TABELA UNIFICADAS ---

def criar_tabela_agrupada(df: pd.DataFrame, coluna_agrupamento: str, nome_agrupamento: str, coluna_pivot: Optional[str] = None) -> pd.DataFrame:
    """
    Cria uma tabela consolidada e agrupada de forma genérica.
    - Se `coluna_pivot` for fornecida (ex: 'fato_comunicado'), a tabela é pivotada com base nessa coluna.
    - Caso contrário, um simples agrupamento por ano é realizado.
    """
    if df.empty:
        return pd.DataFrame()

    groupby_cols = [coluna_agrupamento, COL_ANO]
    if coluna_pivot:
        groupby_cols.insert(1, coluna_pivot)

    df_agrupado = df.groupby(groupby_cols).size().reset_index(name='total_crime')

    pivot_index = [coluna_agrupamento]
    if coluna_pivot:
        pivot_index.append(coluna_pivot)

    df_pivot = df_agrupado.pivot_table(index=pivot_index, columns=COL_ANO, values='total_crime', fill_value=0)

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
            df_pivot[coluna_evolucao] = ((df_pivot[ano_atual] - df_pivot[ano_anterior]) / denominador * 100)

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
            ano_anterior, ano_atual = anos_int[i-1], anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    df_consolidado = df_pivot[ordem_colunas].reset_index()
    
    nome_coluna_final = f"Nome do {nome_agrupamento}" if nome_agrupamento == "Município" else nome_agrupamento
    rename_dict = {coluna_agrupamento: nome_coluna_final}
    if coluna_pivot:
        rename_dict[coluna_pivot] = 'Fato Comunicado'
        
    df_consolidado.rename(columns=rename_dict, inplace=True)
    
    return df_consolidado

def criar_tabela_total(df: pd.DataFrame, coluna_pivot: Optional[str] = None) -> pd.DataFrame:
    """
    Cria uma tabela consolidada de totais de forma genérica.
    - Se `coluna_pivot` for fornecida, agrupa por essa coluna e por ano.
    - Caso contrário, agrupa apenas por ano (para o total de feminicídios).
    """
    if df.empty:
        return pd.DataFrame()

    groupby_cols = [COL_ANO]
    if coluna_pivot:
        groupby_cols.insert(0, coluna_pivot)

    df_agrupado = df.groupby(groupby_cols).size().reset_index(name='total_crime')
    
    df_pivot = df_agrupado.pivot_table(index=coluna_pivot, columns=COL_ANO, values='total_crime', fill_value=0)
    
    anos_existentes = [col for col in df.ano.unique() if isinstance(col, (int, float))]
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
            ano_atual, ano_anterior = anos[i], anos[i-1]
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
            ano_anterior, ano_atual = anos_int[i-1], anos_int[i]
            ordem_colunas.append(ano_atual)
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)
    
    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    if coluna_pivot:
        df_consolidado = df_pivot[ordem_colunas].reset_index()
        df_consolidado.rename(columns={coluna_pivot: 'Fato Comunicado'}, inplace=True)
    else:
        df_consolidado = df_pivot[ordem_colunas].reset_index(drop=True)
        df_consolidado.insert(0, 'Tipo de Crime', 'Feminicídio')
    
    return df_consolidado

# --- FUNÇÃO PARA CRIAR A TABELA POPULACIONAL AGRUPADA ---
def criar_tabela_populacional_agrupada(df_crimes: pd.DataFrame, df_pop: pd.DataFrame, df_regioes: pd.DataFrame, agrupamento: str, num_anos: int) -> pd.DataFrame:
    """Cria uma tabela de análise populacional, permitindo o agrupamento por diferentes níveis."""
    
    if num_anos == 0: num_anos = 1

    df_pop_com_regioes = pd.merge(df_pop, df_regioes.drop(columns=COL_MUNICIPIO), on=COL_MUN_NORMALIZADO, how='left')

    if agrupamento == "Consolidado":
        total_fatos = df_crimes.shape[0]
        municipios_presentes = df_crimes[COL_MUN_NORMALIZADO].unique()
        pop_filtrada = df_pop_com_regioes[df_pop_com_regioes[COL_MUN_NORMALIZADO].isin(municipios_presentes)]
        total_populacao = pop_filtrada[COL_POPULACAO_FEMININA].sum()
        
        media_anual = total_fatos / num_anos
        taxa = (media_anual / total_populacao) * 1000 if total_populacao > 0 else 0
        percentual = (media_anual / total_populacao) * 100 if total_populacao > 0 else 0
        
        tabela = pd.DataFrame([{'Localidade': 'Santa Catarina (Filtro Aplicado)', 'População Feminina': total_populacao,
                                'Média Anual de Fatos Ocorridos': media_anual, 'Fatos por Mil Mulheres (anual)': taxa,
                                '% de Mulheres Vítimas (anual)': percentual}])
        return tabela.set_index('Localidade')

    coluna_agrupamento = {
        "Município": COL_MUNICIPIO,
        "Mesorregião": COL_MESOREGIAO,
        "Associação": COL_ASSOCIACAO
    }[agrupamento]

    crimes_agrupado = df_crimes[coluna_agrupamento].value_counts().reset_index()
    crimes_agrupado.columns = [coluna_agrupamento, COL_TOTAL_FATOS]

    if agrupamento == "Município":
        pop_agrupada = df_pop_com_regioes[[coluna_agrupamento, COL_POPULACAO_FEMININA]]
    else:
        pop_agrupada = df_pop_com_regioes.groupby(coluna_agrupamento)[COL_POPULACAO_FEMININA].sum().reset_index()

    df_agregado = pd.merge(crimes_agrupado, pop_agrupada, on=coluna_agrupamento, how='left')

    df_agregado['media_anual_fatos'] = df_agregado[COL_TOTAL_FATOS] / num_anos
    df_agregado['taxa_por_mil_mulheres'] = ((df_agregado['media_anual_fatos'] / df_agregado[COL_POPULACAO_FEMININA]) * 1000).fillna(0)
    df_agregado['percentual_mulheres_vitimas'] = ((df_agregado['media_anual_fatos'] / df_agregado[COL_POPULACAO_FEMININA]) * 100).fillna(0)

    tabela_final = df_agregado.rename(columns={
        coluna_agrupamento: agrupamento,
        COL_POPULACAO_FEMININA: 'População Feminina',
        'media_anual_fatos': 'Média Anual de Fatos Ocorridos',
        'taxa_por_mil_mulheres': 'Fatos por Mil Mulheres (anual)',
        'percentual_mulheres_vitimas': '% de Mulheres Vítimas (anual)'
    })

    return tabela_final[[agrupamento, 'População Feminina', 'Média Anual de Fatos Ocorridos', 'Fatos por Mil Mulheres (anual)', '% de Mulheres Vítimas (anual)']].set_index(agrupamento)

def gerar_grafico_dinamico(df: pd.DataFrame, tipo_grafico: str, **kwargs) -> go.Figure:
    """
    Gera um gráfico dinâmico com base no tipo especificado e em argumentos variados.
    """
    if tipo_grafico == "bar":
        fig = px.bar(df, **kwargs)
    elif tipo_grafico == "pie":
        fig = px.pie(df, **kwargs)
    elif tipo_grafico == "line":
        fig = px.line(df, **kwargs)
    elif tipo_grafico == "area":
        fig = px.area(df, **kwargs)
    elif tipo_grafico == "histogram":
        fig = px.histogram(df, **kwargs)
    elif tipo_grafico == "violin":
        fig = px.violin(df, **kwargs)
    else:
        raise ValueError(f"Tipo de gráfico desconhecido: {tipo_grafico}")
    
    return fig

@st.cache_data
def carregar_dados_regioes() -> pd.DataFrame:
    """Carrega a base de regiões e associações, normalizando o nome do município."""
    try:
        df = pd.read_excel('data/base_regioes_associacoes.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df[COL_MUN_NORMALIZADO] = df[COL_MUNICIPIO].apply(normalizar_nome)
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_regioes_associacoes.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados das regiões: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_populacao() -> pd.DataFrame:
    """Carrega a base de população, normalizando o nome do município."""
    try:
        df = pd.read_excel('data/base_populacao.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df[COL_MUN_NORMALIZADO] = df[COL_MUNICIPIO].apply(normalizar_nome)
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_populacao.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados da população: {e}")
        return pd.DataFrame()

# Carregar os dados
geojson_sc = carregar_geojson_sc()
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()
df_populacao = carregar_dados_populacao()
df_regioes = carregar_dados_regioes()


# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("logo_ovm.jpeg", use_container_width=True)

# --- ESTRUTURA COM ABAS (TABS) ---
tab_geral, tab_feminicidio, tab_glossario, tab_download = st.tabs([
    "📊 Análise Geral da Violência", "🚨 Análise de Feminicídios", "📖 Metodologia e Glossário", "📥 Download de Dados"
])

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
if not df_geral.empty and not df_feminicidio.empty and geojson_sc is not None and not df_populacao.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")
        
        st.subheader("📅 PERÍODO")
        min_date = df_geral[COL_DATA_FATO].min().date()
        max_date = df_geral[COL_DATA_FATO].max().date()

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
            (df_geral[COL_DATA_FATO].dt.date >= data_inicial) &
            (df_geral[COL_DATA_FATO].dt.date <= data_final)
        ]
        
        crimes_por_municipio_para_filtro = df_geral_filtrado_por_data[COL_MUN_NORMALIZADO].value_counts().reset_index()
        crimes_por_municipio_para_filtro.columns = [COL_MUN_NORMALIZADO, COL_TOTAL_FATOS]

        df_populacional_metrics = pd.merge(
            df_populacao.copy(),
            crimes_por_municipio_para_filtro,
            on=COL_MUN_NORMALIZADO,
            how='left'
        )
        df_populacional_metrics[COL_TOTAL_FATOS].fillna(0, inplace=True)

        anos_no_filtro = df_geral_filtrado_por_data[COL_ANO].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1

        df_populacional_metrics['media_anual_fatos'] = df_populacional_metrics[COL_TOTAL_FATOS] / num_anos
        df_populacional_metrics['taxa_por_mil_mulheres'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics[COL_POPULACAO_FEMININA]) * 1000).fillna(0)
        df_populacional_metrics['percentual_mulheres_vitimas'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics[COL_POPULACAO_FEMININA]) * 100).fillna(0)


        st.subheader("📊 FILTROS POPULACIONAIS")
        
        min_pop = int(df_populacional_metrics[COL_POPULACAO_FEMININA].min())
        max_pop = int(df_populacional_metrics[COL_POPULACAO_FEMININA].max())
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

        st.subheader("📍 LOCALIZAÇÃO")
        mesoregioes_disponiveis = sorted(df_geral[COL_MESOREGIAO].unique())
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)", 
            options=mesoregioes_disponiveis, 
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina"
        )
        
        associacoes_disponiveis = sorted(df_geral[COL_ASSOCIACAO].dropna().unique())
        associacao_selecionado = st.multiselect(
            "Associação(ões)",
            options=associacoes_disponiveis,
            default=associacoes_disponiveis,
            help="Filtre por associação de municípios"
        )
        
        if mesoregiao_selecionado:
            municipios_filtrados = df_geral[df_geral[COL_MESOREGIAO].isin(mesoregiao_selecionado)][COL_MUNICIPIO].unique()
        else:
            municipios_filtrados = df_geral[COL_MUNICIPIO].unique()
        
        municipios_disponiveis = sorted(municipios_filtrados)
        
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
        
        st.subheader("🚨 TIPO DE CRIME")
        fatos_disponiveis = sorted(df_geral[COL_FATO_COMUNICADO].unique())
        
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
        
        st.subheader("📊 AGRUPAMENTO DE DADOS")
        agrupamento_selecionado = st.selectbox(
            "Agrupar por",
            options=["Consolidado", "Município", "Mesorregião", "Associação"],
            index=0,
            help="Escolha como os dados devem ser agrupados nos gráficos e tabelas."
        )
    

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Resetar Todos os Filtros", use_container_width=True):
        st.rerun()

    idade_max_filtro = float('inf') if idade_selecionada[1] == 100 else idade_selecionada[1]

    municipios_filtrados_populacao = df_populacional_metrics[
        (df_populacional_metrics[COL_POPULACAO_FEMININA] >= pop_selecionada[0]) &
        (df_populacional_metrics[COL_POPULACAO_FEMININA] <= pop_selecionada[1]) &
        (df_populacional_metrics['media_anual_fatos'] >= media_fatos_selecionada[0]) &
        (df_populacional_metrics['media_anual_fatos'] <= media_fatos_selecionada[1]) &
        (df_populacional_metrics['taxa_por_mil_mulheres'] >= taxa_selecionada[0]) &
        (df_populacional_metrics['taxa_por_mil_mulheres'] <= taxa_selecionada[1]) &
        (df_populacional_metrics['percentual_mulheres_vitimas'] >= perc_selecionado[0]) &
        (df_populacional_metrics['percentual_mulheres_vitimas'] <= perc_selecionado[1])
    ][COL_MUN_NORMALIZADO]

    df_geral_filtrado = df_geral[
        (df_geral[COL_DATA_FATO].dt.date >= data_inicial) &
        (df_geral[COL_DATA_FATO].dt.date <= data_final) &
        (df_geral[COL_FATO_COMUNICADO].isin(fato_selecionado)) &
        (df_geral[COL_MUNICIPIO].isin(municipio_selecionado)) &
        (df_geral[COL_MESOREGIAO].isin(mesoregiao_selecionado)) &
        (df_geral[COL_ASSOCIACAO].isin(associacao_selecionado)) &
        (df_geral[COL_IDADE_VITIMA] >= idade_selecionada[0]) & (df_geral[COL_IDADE_VITIMA] <= idade_max_filtro) &
        (df_geral[COL_MUN_NORMALIZADO].isin(municipios_filtrados_populacao))
    ]
    
    df_feminicidio_filtrado = df_feminicidio[
        (df_feminicidio[COL_DATA_FATO].dt.date >= data_inicial) &
        (df_feminicidio[COL_DATA_FATO].dt.date <= data_final) &
        (df_feminicidio[COL_MUNICIPIO].isin(municipio_selecionado)) &
        (df_feminicidio[COL_MESOREGIAO].isin(mesoregiao_selecionado)) &
        (df_feminicidio[COL_ASSOCIACAO].isin(associacao_selecionado)) &
        (df_feminicidio[COL_IDADE_VITIMA] >= idade_selecionada[0]) & (df_feminicidio[COL_IDADE_VITIMA] <= idade_max_filtro) &
        (df_feminicidio[COL_MUN_NORMALIZADO].isin(municipios_filtrados_populacao))
    ]

    with tab_geral:
        st.header("Violência Contra a Mulher em Santa Catarina")
        st.markdown("Visão geral dos registros de ocorrências.")

        total_registros = df_geral_filtrado.shape[0]
        media_idade_vitima = 0.0
        if not df_geral_filtrado.empty and df_geral_filtrado[COL_IDADE_VITIMA].notna().any():
            media_idade_vitima = df_geral_filtrado[COL_IDADE_VITIMA].mean()

        num_dias = (data_final - data_inicial).days + 1
        
        crimes_por_dia = total_registros / num_dias if num_dias > 0 else 0
        crimes_por_hora = total_registros / (num_dias * 24) if num_dias > 0 else 0
        
        df_cagr_kpi = df_geral_filtrado[df_geral_filtrado[COL_ANO] != pd.Timestamp.now().year]
        anos_unicos = sorted(df_cagr_kpi[COL_ANO].unique())
        num_anos_total = len(anos_unicos)

        if num_anos_total >= 3:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total de Registros no Período", value=f"{total_registros:,}".replace(",", "."))
                st.metric(label="Média de Crimes por Dia", value=f"{crimes_por_dia:.1f}")

            with col2:
                dados_por_ano = df_cagr_kpi.groupby(COL_ANO).size()
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
        
        view_type = st.radio(
            "Selecione a visualização do mapa:",
            ("Soma dos Crimes", "Crimes por Mil Mulheres", "% de Mulheres Vítimas"),
            horizontal=True,
            key="map_view_type"
        )

        map_df = pd.DataFrame()
        color_col = 'value'
        label_text = 'Valor'

        if view_type == "Soma dos Crimes":
            color_col = 'quantidade'
            label_text = f'Total de Registros ({agrupamento_selecionado})'
        elif view_type == "Crimes por Mil Mulheres":
            color_col = 'taxa_por_mil_mulheres'
            label_text = f'Crimes por Mil Mulheres ({agrupamento_selecionado})'
        else: # % de Mulheres Vítimas
            color_col = 'percentual_mulheres_vitimas'
            label_text = f'% de Mulheres Vítimas ({agrupamento_selecionado})'

        base_map_df = df_geral_filtrado[COL_MUN_NORMALIZADO].value_counts().reset_index()
        base_map_df.columns = [COL_MUN_NORMALIZADO, COL_TOTAL_FATOS]

        if view_type != "Soma dos Crimes":
            base_map_df = pd.merge(base_map_df, df_populacao, on=COL_MUN_NORMALIZADO, how='left')
            base_map_df.dropna(subset=[COL_POPULACAO_FEMININA], inplace=True)

            anos_no_filtro = df_geral_filtrado[COL_ANO].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            base_map_df['media_anual_fatos'] = base_map_df[COL_TOTAL_FATOS] / num_anos

            if view_type == "Crimes por Mil Mulheres":
                base_map_df[color_col] = ((base_map_df['media_anual_fatos'] / base_map_df[COL_POPULACAO_FEMININA]) * 1000).fillna(0)
            else: # % de Mulheres Vítimas
                base_map_df[color_col] = ((base_map_df['media_anual_fatos'] / base_map_df[COL_POPULACAO_FEMININA]) * 100).fillna(0)
        else:
            base_map_df.rename(columns={COL_TOTAL_FATOS: color_col}, inplace=True)


        if agrupamento_selecionado == "Município" or agrupamento_selecionado == "Consolidado":
            map_df = base_map_df[[COL_MUN_NORMALIZADO, color_col]]
        else: 
            agrupamento_col = COL_MESOREGIAO if agrupamento_selecionado == "Mesorregião" else COL_ASSOCIACAO
            
            municipio_grupo_mapping = df_geral_filtrado[[COL_MUN_NORMALIZADO, agrupamento_col]].drop_duplicates()
            df_with_groups = pd.merge(base_map_df, municipio_grupo_mapping, on=COL_MUN_NORMALIZADO, how='left')
            
            if view_type == "Soma dos Crimes":
                crimes_por_grupo = df_with_groups.groupby(agrupamento_col)[color_col].sum().reset_index()
                map_df = pd.merge(municipio_grupo_mapping, crimes_por_grupo, on=agrupamento_col, how='left').fillna(0)
            else: 
                grouped_pop = df_with_groups.groupby(agrupamento_col).agg(
                    total_fatos_grupo=(COL_TOTAL_FATOS, 'sum'),
                    populacao_feminina_grupo=(COL_POPULACAO_FEMININA, 'sum')
                ).reset_index()
                
                anos_no_filtro = df_geral_filtrado[COL_ANO].unique()
                num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
                grouped_pop['media_anual_grupo'] = grouped_pop['total_fatos_grupo'] / num_anos

                if view_type == "Crimes por Mil Mulheres":
                    grouped_pop[color_col] = ((grouped_pop['media_anual_grupo'] / grouped_pop['populacao_feminina_grupo']) * 1000).fillna(0)
                else:
                    grouped_pop[color_col] = ((grouped_pop['media_anual_grupo'] / grouped_pop['populacao_feminina_grupo']) * 100).fillna(0)
                    
                map_df = pd.merge(municipio_grupo_mapping, grouped_pop[[agrupamento_col, color_col]], on=agrupamento_col, how='left').fillna(0)


        if not map_df.empty:
            map_df = map_df[map_df[COL_MUN_NORMALIZADO].isin(df_geral_filtrado[COL_MUN_NORMALIZADO].unique())]


        fig_mapa = px.choropleth_mapbox(
            map_df, 
            geojson=geojson_sc, 
            locations=COL_MUN_NORMALIZADO,
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
            coloraxis_showscale=True
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

        st.markdown("---")

        st.subheader("Evolução dos Registros de Ocorrências (Série Temporal)")

        # Dicionário de mapeamento para traduzir as opções
        grafico_map = {
            "Linha": "line",
            "Área": "area",
            "Barras": "bar"
        }

        chart_type_temporal_label = st.selectbox(
            "Tipo de Gráfico",
            options=list(grafico_map.keys()), # Opções amigáveis para o usuário
            key="chart_type_temporal"
        )
        # Traduz a opção selecionada para o valor que a função espera
        chart_type_temporal_value = grafico_map[chart_type_temporal_label]

        df_temporal = df_geral_filtrado.copy()
        df_temporal['ano_mes'] = df_temporal[COL_DATA_FATO].dt.to_period('M').astype(str)

        color_param_temporal = None
        if agrupamento_selecionado == "Consolidado":
            registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values('ano_mes')
        else:
            mapa_agrupamento_tabela = {
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            registros_por_mes_ano = df_temporal.groupby(['ano_mes', coluna_agrupamento]).size().reset_index(name='quantidade').sort_values('ano_mes')
            color_param_temporal = coluna_agrupamento

        fig_temporal = gerar_grafico_dinamico(
            registros_por_mes_ano,
            tipo_grafico=chart_type_temporal_value,  # <- Usa o valor traduzido
            x='ano_mes',
            y='quantidade',
            color=color_param_temporal,
            labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
            template='plotly_white',
            markers=True if chart_type_temporal_label == "Linha" else False
        )

        if agrupamento_selecionado == "Consolidado":
            color = '#8A2BE2'
            if chart_type_temporal_label == "Barras":
                fig_temporal.update_traces(marker_color=color)
            else:
                fig_temporal.update_traces(line_color=color)

        st.plotly_chart(fig_temporal, use_container_width=True)
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
                registros_por_ano = df_geral_filtrado[COL_ANO].value_counts().sort_index().reset_index()
                registros_por_ano.columns = [COL_ANO, 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": COL_MUNICIPIO,
                    "Mesorregião": COL_MESOREGIAO,
                    "Associação": COL_ASSOCIACAO
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                registros_por_ano = df_geral_filtrado.groupby([COL_ANO, coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_ano == "Pizza":
                pie_names = COL_ANO if agrupamento_selecionado == "Consolidado" else color_param
                fig_ano = gerar_grafico_dinamico(
                    registros_por_ano, 'pie', names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_ano.update_traces(textinfo='percent+label', textposition='outside')
            else:
                fig_ano = gerar_grafico_dinamico(
                    registros_por_ano, chart_type_ano.lower(), x=COL_ANO, y='Quantidade', color=color_param,
                    labels={COL_ANO: 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white',
                    text='Quantidade' if chart_type_ano == "Barras" else None,
                    markers=True if chart_type_ano == "Linha" else False
                )
                if agrupamento_selecionado == "Consolidado":
                    color = '#8A2BE2'
                    if chart_type_ano == "Barras":
                        fig_ano.update_traces(marker_color=color, textposition='outside')
                    else:
                        fig_ano.update_traces(line_color=color)
            st.plotly_chart(fig_ano, use_container_width=True)

        with col_graf2:
            st.subheader("Tipos de Crimes Mais Frequentes")
            chart_type_fato = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_fato"
            )
            if agrupamento_selecionado == "Consolidado":
                registros_por_fato = df_geral_filtrado[COL_FATO_COMUNICADO].value_counts().reset_index()
                registros_por_fato.columns = [COL_FATO_COMUNICADO, 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": COL_MUNICIPIO,
                    "Mesorregião": COL_MESOREGIAO,
                    "Associação": COL_ASSOCIACAO
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                registros_por_fato = df_geral_filtrado.groupby([COL_FATO_COMUNICADO, coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_fato == "Barras":
                fig_fato = gerar_grafico_dinamico(
                    registros_por_fato, 'bar', x='Quantidade', y=COL_FATO_COMUNICADO, color=color_param, orientation='h',
                    labels={COL_FATO_COMUNICADO: 'Tipo de Crime', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_fato.update_traces(marker_color='#9370DB')
                fig_fato.update_traces(textposition='auto')
                fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
            else:
                pie_names = COL_FATO_COMUNICADO if agrupamento_selecionado == "Consolidado" else color_param
                fig_fato = gerar_grafico_dinamico(
                    registros_por_fato, 'pie', names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_fato.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_fato, use_container_width=True)

        st.markdown("---")
        
        col_graf3, col_graf4 = st.columns(2)
        with col_graf3:
            st.subheader("Distribuição por Faixa Etária da Vítima")
            chart_type_faixa_etaria = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_faixa_etaria"
            )
            df_faixa_etaria = df_geral_filtrado.dropna(subset=[COL_IDADE_VITIMA])
            bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
            labels = ['0-12 anos', '13-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '61-70 anos', '71-79 anos', '80+ anos']
            df_faixa_etaria['faixa_etaria'] = pd.cut(df_faixa_etaria[COL_IDADE_VITIMA], bins=bins, labels=labels, right=True)
            registros_por_faixa = df_faixa_etaria['faixa_etaria'].value_counts().sort_index().reset_index()
            registros_por_faixa.columns = ['Faixa Etária', 'Quantidade']

            if chart_type_faixa_etaria == "Barras":
                fig_faixa_etaria = gerar_grafico_dinamico(
                    registros_por_faixa, 'bar', x='Faixa Etária', y='Quantidade',
                    labels={'x': 'Faixa Etária', 'y': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_faixa_etaria.update_traces(marker_color='#9370DB', textposition='outside')
            else:
                fig_faixa_etaria = gerar_grafico_dinamico(
                    registros_por_faixa, 'pie', names='Faixa Etária', values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_faixa_etaria.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_faixa_etaria, use_container_width=True)
        with col_graf4:
            st.subheader("Distribuição de Ocorrências por Mês")
            chart_type_mes = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras", "Linha", "Área"),
                key="chart_type_mes"
            )
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            df_geral_filtrado['mes_cat'] = pd.Categorical(df_geral_filtrado[COL_MES], categories=meses_ordem, ordered=True)
            registros_por_mes = df_geral_filtrado['mes_cat'].value_counts().sort_index().reset_index()
            registros_por_mes.columns = ['Mês', 'Quantidade']
            nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
            registros_por_mes['Mês'] = registros_por_mes['Mês'].map(nomes_meses_pt)

            if chart_type_mes == "Pizza":
                fig_mes = gerar_grafico_dinamico(
                    registros_por_mes, 'pie', names='Mês', values='Quantidade', hole=.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_mes.update_traces(textinfo='percent+label', textposition='outside', sort=False)
            else:
                fig_mes = gerar_grafico_dinamico(
                    registros_por_mes, chart_type_mes.lower(), x='Mês', y='Quantidade',
                    labels={'x': 'Mês', 'y': 'Quantidade'}, template='plotly_white',
                    text='Quantidade' if chart_type_mes == 'Barras' else None,
                    markers=True if chart_type_mes == 'Linha' else False
                )
                fig_mes.update_traces(line_color='#9370DB')
                if chart_type_mes == 'Barras':
                    fig_mes.update_traces(marker_color='#9370DB', textposition='outside')
            st.plotly_chart(fig_mes, use_container_width=True)
        
        st.markdown("---")

        st.subheader("Distribuição de Ocorrências por Dia da Semana")
        chart_type_dia_semana = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Pizza", "Linha", "Área"),
            key="chart_type_dia_semana"
        )
        df_geral_filtrado['dia_semana'] = df_geral_filtrado[COL_DATA_FATO].dt.day_name()
        dias_ordem = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        df_geral_filtrado['dia_semana_cat'] = pd.Categorical(df_geral_filtrado['dia_semana'], categories=dias_ordem, ordered=True)
        registros_por_dia = df_geral_filtrado['dia_semana_cat'].value_counts().sort_index().reset_index()
        registros_por_dia.columns = ['Dia da Semana', 'Quantidade']
        nomes_dias_pt = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        registros_por_dia['Dia da Semana'] = registros_por_dia['Dia da Semana'].map(nomes_dias_pt)

        if chart_type_dia_semana == "Pizza":
            fig_dia_semana = gerar_grafico_dinamico(
                registros_por_dia, 'pie', names='Dia da Semana', values='Quantidade',
                hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_dia_semana.update_traces(textinfo='percent+label', textposition='outside')
        else:
            fig_dia_semana = gerar_grafico_dinamico(
                registros_por_dia, chart_type_dia_semana.lower(), x='Dia da Semana', y='Quantidade',
                labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white',
                text='Quantidade' if chart_type_dia_semana == 'Barras' else None,
                markers=True if chart_type_dia_semana == 'Linha' else False
            )
            fig_dia_semana.update_traces(line_color='#8A2BE2')
            if chart_type_dia_semana == 'Barras':
                fig_dia_semana.update_traces(marker_color='#8A2BE2', textposition='outside')
        st.plotly_chart(fig_dia_semana, use_container_width=True)

        st.markdown("---")
        
        st.subheader("Análise Populacional dos Crimes por Município")
        
        anos_no_filtro = df_geral_filtrado[COL_ANO].unique()
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
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento_tabela = mapa_agrupamento_tabela[agrupamento_selecionado]
            
            st.subheader(f"Tabela Consolidada de Crimes por {agrupamento_selecionado}")
            tabela_consolidada = criar_tabela_agrupada(df_geral_filtrado, coluna_agrupamento_tabela, agrupamento_selecionado, coluna_pivot=COL_FATO_COMUNICADO)
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

                styler = tabela_consolidada.style.applymap(colorir_percentual, subset=colunas_para_colorir).format(format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
        else:
            st.subheader("Tabela Consolidada de Crimes (Total SC)")
            tabela_total = criar_tabela_total(df_geral_filtrado, coluna_pivot=COL_FATO_COMUNICADO)
            if not tabela_total.empty:
                colunas_evolucao = [col for col in tabela_total.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                anos_int = [col for col in tabela_total.columns if isinstance(col, int)]
                for ano in anos_int:
                    format_dict[ano] = '{:.0f}'
                format_dict['total'] = '{:.0f}'
                if 'Tendência (CAGR %)' in tabela_total.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_total.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_total.style.applymap(colorir_percentual, subset=colunas_para_colorir).format(format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")


    with tab_feminicidio:
        st.header("Análise de Feminicídios Consumados")
        st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")
        
        total_feminicidios = df_feminicidio_filtrado.shape[0]
        idade_media_vitima_fem = df_feminicidio_filtrado[COL_IDADE_VITIMA].mean()
        idade_media_autor_fem = df_feminicidio_filtrado[COL_IDADE_AUTOR].mean()
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
            map_df_fem = df_feminicidio_filtrado[COL_MUN_NORMALIZADO].value_counts().reset_index()
            map_df_fem.columns = [COL_MUN_NORMALIZADO, 'quantidade']
        else:
            agrupamento_col_fem = COL_MESOREGIAO if agrupamento_selecionado == "Mesorregião" else COL_ASSOCIACAO
            
            feminicidios_por_grupo = df_feminicidio_filtrado.groupby(agrupamento_col_fem).size().reset_index(name='quantidade_grupo')
            
            municipio_grupo_mapping_fem = df_feminicidio_filtrado[[COL_MUN_NORMALIZADO, agrupamento_col_fem]].drop_duplicates()
            
            map_df_fem = pd.merge(municipio_grupo_mapping_fem, feminicidios_por_grupo, on=agrupamento_col_fem)
            map_df_fem = map_df_fem.rename(columns={'quantidade_grupo': 'quantidade'})

        fig_mapa_fem = px.choropleth_mapbox(
            map_df_fem, 
            geojson=geojson_sc, 
            locations=COL_MUN_NORMALIZADO,
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
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_mapa_fem, use_container_width=True)

        st.markdown("---")
        
        st.subheader("Raio-X do Agressor")
        st.markdown("""
        Análise aprofundada sobre o perfil do agressor, incluindo a dinâmica de idade com a vítima e seu histórico criminal. 
        Estes gráficos ajudam a identificar padrões e possíveis pontos de falha na prevenção.
        """)
        
        col_raiox1, col_raiox2 = st.columns(2)
        
        with col_raiox1:
            if not df_feminicidio_filtrado.empty and df_feminicidio_filtrado[[COL_IDADE_VITIMA, COL_IDADE_AUTOR]].notna().all(axis=1).any():
                fig_scatter_idade = px.scatter(
                    df_feminicidio_filtrado.dropna(subset=[COL_IDADE_VITIMA, COL_IDADE_AUTOR]),
                    x=COL_IDADE_VITIMA,
                    y=COL_IDADE_AUTOR,
                    title="Dinâmica de Idade: Vítima vs. Agressor",
                    labels={COL_IDADE_VITIMA: 'Idade da Vítima', COL_IDADE_AUTOR: 'Idade do Autor'},
                    color_discrete_sequence=['#8e24aa'],
                    hover_data=[COL_MUNICIPIO, COL_RELACAO_AUTOR, COL_MEIO_CRIME]
                )
                
                max_idade = max(
                    df_feminicidio_filtrado[COL_IDADE_VITIMA].max(),
                    df_feminicidio_filtrado[COL_IDADE_AUTOR].max()
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
                st.plotly_chart(fig_scatter_idade, use_container_width=True)
            else:
                st.info("Não há dados suficientes para exibir o gráfico de correlação de idades.")

        with col_raiox2:
            if not df_feminicidio_filtrado.empty and COL_PASSAGEM_POLICIAL in df_feminicidio_filtrado.columns and COL_PASSAGEM_VD in df_feminicidio_filtrado.columns:
                total_agressores = len(df_feminicidio_filtrado)
                com_passagem = df_feminicidio_filtrado[COL_PASSAGEM_POLICIAL].value_counts().get('SIM', 0)
                sem_passagem = total_agressores - com_passagem
                
                com_bo_vd = len(df_feminicidio_filtrado[
                    (df_feminicidio_filtrado[COL_PASSAGEM_POLICIAL] == 'SIM') &
                    (df_feminicidio_filtrado[COL_PASSAGEM_VD] == 'SIM')
                ])
                com_bo_outros = com_passagem - com_bo_vd

                if total_agressores > 0:
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="black", width=0.5),
                            label=["Total de Agressores", "Com Passagem Policial", "Sem Passagem Policial", "Com B.O. por Violência Doméstica", "Com B.O. por Outros Crimes"],
                            color=["#4a148c", "#8e24aa", "#e0e0e0", "#ab47bc", "#ce93d8"]
                        ),
                        link=dict(
                            source=[0, 0, 1, 1],
                            target=[1, 2, 3, 4],
                            value=[com_passagem, sem_passagem, com_bo_vd, com_bo_outros],
                            color=["rgba(142, 36, 170, 0.6)", "rgba(189, 189, 189, 0.6)", "rgba(171, 71, 188, 0.6)", "rgba(206, 147, 216, 0.6)"]
                        ))])

                    fig_sankey.update_layout(
                        title_text="Histórico do Agressor: A Escalada da Violência",
                        font_size=12
                    )
                    st.plotly_chart(fig_sankey, use_container_width=True)
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
                vinculo_autor = df_feminicidio_filtrado[COL_RELACAO_AUTOR].value_counts().reset_index()
                vinculo_autor.columns = [COL_RELACAO_AUTOR, 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": COL_MUNICIPIO,
                    "Mesorregião": COL_MESOREGIAO,
                    "Associação": COL_ASSOCIACAO
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                vinculo_autor = df_feminicidio_filtrado.groupby([COL_RELACAO_AUTOR, coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento
            
            if chart_type_vinculo == "Barras":
                fig_vinculo = gerar_grafico_dinamico(
                    vinculo_autor, 'bar', x='Quantidade', y=COL_RELACAO_AUTOR, color=color_param, orientation='h',
                    labels={COL_RELACAO_AUTOR: 'Vínculo com o Autor', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_vinculo.update_traces(marker_color='#8A2BE2')
                fig_vinculo.update_traces(textposition='auto')
                fig_vinculo.update_layout(yaxis={'categoryorder':'total ascending'})
            else:
                pie_names = COL_RELACAO_AUTOR if agrupamento_selecionado == "Consolidado" else color_param
                fig_vinculo = gerar_grafico_dinamico(
                    vinculo_autor, 'pie', names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_vinculo.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_vinculo, use_container_width=True)
        
        with col_graf_fem2:
            st.subheader("Meio Utilizado para o Crime")
            chart_type_meio = st.selectbox(
                "Tipo de Gráfico",
                ("Barras", "Pizza"),
                key="chart_type_meio"
            )
            if agrupamento_selecionado == "Consolidado":
                meio_crime = df_feminicidio_filtrado[COL_MEIO_CRIME].value_counts().reset_index()
                meio_crime.columns = [COL_MEIO_CRIME, 'Quantidade']
                color_param = None
            else:
                mapa_agrupamento_tabela = {
                    "Município": COL_MUNICIPIO,
                    "Mesorregião": COL_MESOREGIAO,
                    "Associação": COL_ASSOCIACAO
                }
                coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
                meio_crime = df_feminicidio_filtrado.groupby([COL_MEIO_CRIME, coluna_agrupamento]).size().reset_index(name='Quantidade')
                color_param = coluna_agrupamento

            if chart_type_meio == "Barras":
                fig_meio = gerar_grafico_dinamico(
                    meio_crime, 'bar', x=COL_MEIO_CRIME, y='Quantidade', color=color_param,
                    labels={COL_MEIO_CRIME: 'Meio Utilizado', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                if agrupamento_selecionado == "Consolidado":
                    fig_meio.update_traces(marker_color='#8A2BE2')
                fig_meio.update_traces(textposition='outside')
            else:
                pie_names = COL_MEIO_CRIME if agrupamento_selecionado == "Consolidado" else color_param
                fig_meio = gerar_grafico_dinamico(
                    meio_crime, 'pie', names=pie_names, values='Quantidade',
                    hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_meio.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_meio, use_container_width=True)
        st.markdown("---")
        
        col_graf_fem1, col_graf_fem2 = st.columns(2)
        with col_graf_fem1:
            st.subheader("Distribuição de Idade da Vítima")
            chart_type_idade_vitima = st.selectbox(
                "Tipo de Gráfico",
                ("Histograma", "Gráfico de Densidade"),
                key="chart_type_idade_vitima"
            )
            df_idade_vitima = df_feminicidio_filtrado.dropna(subset=[COL_IDADE_VITIMA])
            if chart_type_idade_vitima == "Histograma":
                fig_idade_vitima = gerar_grafico_dinamico(
                    df_idade_vitima, 'histogram', x=COL_IDADE_VITIMA, nbins=20,
                    labels={COL_IDADE_VITIMA: 'Idade da Vítima', 'count': 'Quantidade'},
                    template='plotly_white', color_discrete_sequence=['#8e24aa']
                )
            else:
                fig_idade_vitima = gerar_grafico_dinamico(
                    df_idade_vitima, 'violin', y=COL_IDADE_VITIMA,
                    labels={COL_IDADE_VITIMA: 'Idade da Vítima'},
                    template='plotly_white', color_discrete_sequence=['#8e24aa'],
                    box=True, points="all"
                )
            st.plotly_chart(fig_idade_vitima, use_container_width=True)
        
        with col_graf_fem2:
            st.subheader("Distribuição de Idade do Autor")
            chart_type_idade_autor = st.selectbox(
                "Tipo de Gráfico",
                ("Histograma", "Gráfico de Densidade"),
                key="chart_type_idade_autor"
            )
            df_idade_autor = df_feminicidio_filtrado.dropna(subset=[COL_IDADE_AUTOR])
            if chart_type_idade_autor == "Histograma":
                fig_idade_autor = gerar_grafico_dinamico(
                    df_idade_autor, 'histogram', x=COL_IDADE_AUTOR, nbins=20,
                    labels={COL_IDADE_AUTOR: 'Idade do Autor', 'count': 'Quantidade'},
                    template='plotly_white', color_discrete_sequence=['#ab47bc']
                )
            else:
                fig_idade_autor = gerar_grafico_dinamico(
                    df_idade_autor, 'violin', y=COL_IDADE_AUTOR,
                    labels={COL_IDADE_AUTOR: 'Idade do Autor'},
                    template='plotly_white', color_discrete_sequence=['#ab47bc'],
                    box=True, points="all"
                )
            st.plotly_chart(fig_idade_autor, use_container_width=True)

        st.markdown("---")

        col_graf_fem3, col_graf_fem4 = st.columns(2)
        with col_graf_fem3:
            st.subheader("Vítima Possuía B.O. contra o Autor?")
            chart_type_bo = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_bo"
            )
            bo_contra_autor = df_feminicidio_filtrado[COL_BO_CONTRA_AUTOR].value_counts().reset_index()
            bo_contra_autor.columns = ['Resposta', 'Quantidade']
            
            if chart_type_bo == "Barras":
                fig_bo = gerar_grafico_dinamico(
                    bo_contra_autor, 'bar', x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_bo.update_traces(marker_color='#8e24aa', textposition='outside')
            else:
                fig_bo = gerar_grafico_dinamico(
                    bo_contra_autor, 'pie', names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_bo, use_container_width=True)

        with col_graf_fem4:
            st.subheader("Autor Foi Preso?")
            chart_type_preso = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_preso"
            )
            autor_preso = df_feminicidio_filtrado[COL_AUTOR_PRESO].value_counts().reset_index()
            autor_preso.columns = ['Resposta', 'Quantidade']

            if chart_type_preso == "Barras":
                fig_preso = gerar_grafico_dinamico(
                    autor_preso, 'bar', x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_preso.update_traces(marker_color='#ab47bc', textposition='outside')
            else:
                fig_preso = gerar_grafico_dinamico(
                    autor_preso, 'pie', names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_preso, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("Localidade do Crime")
        chart_type_localidade = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Pizza"),
            key="chart_type_localidade"
        )
        if agrupamento_selecionado == "Consolidado":
            localidade_crime = df_feminicidio_filtrado[COL_LOCALIDADE].value_counts().reset_index()
            localidade_crime.columns = [COL_LOCALIDADE, 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            localidade_crime = df_feminicidio_filtrado.groupby([COL_LOCALIDADE, coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento

        if chart_type_localidade == "Barras":
            fig_localidade = gerar_grafico_dinamico(
                localidade_crime, 'bar', x=COL_LOCALIDADE, y='Quantidade', color=color_param,
                labels={COL_LOCALIDADE: 'Localidade', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
            )
            if agrupamento_selecionado == "Consolidado":
                fig_localidade.update_traces(marker_color='#8A2BE2')
            fig_localidade.update_traces(textposition='outside')
        else:
            pie_names = COL_LOCALIDADE if agrupamento_selecionado == "Consolidado" else color_param
            fig_localidade = gerar_grafico_dinamico(
                localidade_crime, 'pie', names=pie_names, values='Quantidade',
                hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_localidade.update_traces(textinfo='percent+label', textposition='outside')
        st.plotly_chart(fig_localidade, use_container_width=True)
        
        st.markdown("---")

        col_graf_fem5, col_graf_fem6 = st.columns(2)
        with col_graf_fem5:
            st.subheader("Autor com Registro de B.O.?")
            chart_type_autor_bo = st.selectbox(
                "Tipo de Gráfico",
                ("Pizza", "Barras"),
                key="chart_type_autor_bo"
            )
            autor_bo = df_feminicidio_filtrado[COL_PASSAGEM_POLICIAL].value_counts().reset_index()
            autor_bo.columns = ['Resposta', 'Quantidade']
            if chart_type_autor_bo == "Barras":
                fig_autor_bo = gerar_grafico_dinamico(
                    autor_bo, 'bar', x='Resposta', y='Quantidade',
                    labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                )
                fig_autor_bo.update_traces(marker_color='#8e24aa', textposition='outside')
            else:
                fig_autor_bo = gerar_grafico_dinamico(
                    autor_bo, 'pie', names='Resposta', values='Quantidade', hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
            st.plotly_chart(fig_autor_bo, use_container_width=True)

        with col_graf_fem6:
            st.subheader("Autor com B.O. por Violência Doméstica?")
            if COL_PASSAGEM_VD in df_feminicidio_filtrado.columns:
                chart_type_autor_bo_vd = st.selectbox(
                    "Tipo de Gráfico",
                    ("Pizza", "Barras"),
                    key="chart_type_autor_bo_vd"
                )
                autor_bo_vd = df_feminicidio_filtrado[COL_PASSAGEM_VD].value_counts().reset_index()
                autor_bo_vd.columns = ['Resposta', 'Quantidade']
                
                if not autor_bo_vd.empty:
                    if chart_type_autor_bo_vd == "Barras":
                        fig_autor_bo_vd = gerar_grafico_dinamico(
                            autor_bo_vd, 'bar', x='Resposta', y='Quantidade',
                            labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'}, template='plotly_white', text='Quantidade'
                        )
                        fig_autor_bo_vd.update_traces(marker_color='#ab47bc', textposition='outside')
                    else:
                        fig_autor_bo_vd = gerar_grafico_dinamico(
                            autor_bo_vd, 'pie', names='Resposta', values='Quantidade', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Purples_r
                        )
                    st.plotly_chart(fig_autor_bo_vd, use_container_width=True)
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
        df_feminicidio_filtrado['ano_mes'] = df_feminicidio_filtrado[COL_DATA_FATO].dt.to_period('M').astype(str)
        if agrupamento_selecionado == "Consolidado":
            feminicidios_por_mes = df_feminicidio_filtrado.groupby('ano_mes').size().reset_index(name='Quantidade')
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            feminicidios_por_mes = df_feminicidio_filtrado.groupby(['ano_mes', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento
        feminicidios_por_mes.rename(columns={'ano_mes': 'Mês/Ano'}, inplace=True)

        fig_mes_ano = gerar_grafico_dinamico(
            feminicidios_por_mes, chart_type_fem_mes_ano.lower(), x='Mês/Ano', y='Quantidade', color=color_param,
            labels={'x': 'Mês/Ano', 'y': 'Quantidade'}, template='plotly_white',
            text='Quantidade' if chart_type_fem_mes_ano == 'Barras' else None,
            markers=True if chart_type_fem_mes_ano == 'Linha' else False
        )
        if agrupamento_selecionado == "Consolidado":
            color = '#8A2BE2'
            if chart_type_fem_mes_ano == "Barras":
                fig_mes_ano.update_traces(marker_color=color, textposition='outside')
            else:
                fig_mes_ano.update_traces(line_color=color)
        st.plotly_chart(fig_mes_ano, use_container_width=True)
        
        st.markdown("---")

        st.subheader("Quantidade de Feminicídios por Ano")
        chart_type_fem_ano = st.selectbox(
            "Tipo de Gráfico",
            ("Barras", "Linha", "Área"),
            key="chart_type_fem_ano"
        )
        if agrupamento_selecionado == "Consolidado":
            feminicidios_por_ano = df_feminicidio_filtrado[COL_ANO].value_counts().sort_index().reset_index()
            feminicidios_por_ano.columns = [COL_ANO, 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento = mapa_agrupamento_tabela[agrupamento_selecionado]
            feminicidios_por_ano = df_feminicidio_filtrado.groupby([COL_ANO, coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento
        
        fig_ano_fem = gerar_grafico_dinamico(
            feminicidios_por_ano, chart_type_fem_ano.lower(), x=COL_ANO, y='Quantidade', color=color_param,
            labels={COL_ANO: 'Ano', 'Quantidade': 'Quantidade'}, template='plotly_white',
            text='Quantidade' if chart_type_fem_ano == 'Barras' else None,
            markers=True if chart_type_fem_ano == 'Linha' else False
        )
        if agrupamento_selecionado == "Consolidado":
            color = '#6a1b9a'
            if chart_type_fem_ano == "Barras":
                fig_ano_fem.update_traces(marker_color=color, textposition='outside')
            else:
                fig_ano_fem.update_traces(line_color=color)
        st.plotly_chart(fig_ano_fem, use_container_width=True)

        st.markdown("---")

        if agrupamento_selecionado != "Consolidado":
            mapa_agrupamento_tabela = {
                "Município": COL_MUNICIPIO,
                "Mesorregião": COL_MESOREGIAO,
                "Associação": COL_ASSOCIACAO
            }
            coluna_agrupamento_tabela = mapa_agrupamento_tabela[agrupamento_selecionado]
            
            st.subheader(f"Tabela Consolidada de Feminicídios por {agrupamento_selecionado}")
            tabela_feminicidio = criar_tabela_agrupada(df_feminicidio_filtrado, coluna_agrupamento_tabela, agrupamento_selecionado)
            if not tabela_feminicidio.empty:
                colunas_evolucao = [col for col in tabela_feminicidio.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                anos_int = [col for col in tabela_feminicidio.columns if isinstance(col, int)]
                for ano in anos_int:
                    format_dict[ano] = '{:.0f}'
                format_dict['total'] = '{:.0f}'
                if 'Tendência (CAGR %)' in tabela_feminicidio.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'
                
                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_feminicidio.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_feminicidio.style.applymap(colorir_percentual, subset=colunas_para_colorir).format(format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
        else:
            st.subheader("Tabela Consolidada de Feminicídios (Total SC)")
            tabela_total_fem = criar_tabela_total(df_feminicidio_filtrado)
            if not tabela_total_fem.empty:
                colunas_evolucao = [col for col in tabela_total_fem.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}
                anos_int = [col for col in tabela_total_fem.columns if isinstance(col, int)]
                for ano in anos_int:
                    format_dict[ano] = '{:.0f}'
                format_dict['total'] = '{:.0f}'
                if 'Tendência (CAGR %)' in tabela_total_fem.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_total_fem.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_total_fem.style.applymap(colorir_percentual, subset=colunas_para_colorir).format(format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")

else:
    with tab_geral:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx`, `base_feminicidio.xlsx` e `municipios_sc.json` existem na pasta `data`.")
    with tab_feminicidio:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data`.")

with tab_glossario:
    st.header("Metodologia e Glossário")
    
    st.subheader("Metodologia")
    st.markdown("""
    Os dados que constam neste painel foram fornecidos pela **Gerência de Estatística e Análise Criminal da Secretaria de Estado da Segurança Pública** (GEAC | DINE | SSP | SC).
    
    Eles foram organizados e processados para possibilitar clareza no entendimento das informações e permitir a interação dos usuários.
    
    A elaboração do painel é uma parceria entre o **Observatório da Violência Contra a Mulher (OVM/SC)** e o **Ministério Público de Contas de Santa Catarina (MPC/SC)**.
    """)

    st.subheader("Análise de Tendências: Entendendo o CAGR")
    st.markdown("""
    Além de comparar um ano com o anterior, este painel utiliza a **Taxa de Crescimento Anual Composta (CAGR)** para analisar tendências de longo prazo.

    **O que é?** O CAGR é uma medida que suaviza a volatilidade dos números anuais e nos informa qual teria sido a taxa de crescimento constante e média ao longo de todo um período.

    **Por que é importante?** Enquanto a variação ano a ano pode mostrar picos e quedas bruscas, o CAGR revela a verdadeira trajetória do problema. Uma pequena queda em um único ano pode mascarar um crescimento consistente da violência ao longo de cinco anos. O CAGR ajuda a identificar problemas crônicos e a avaliar o impacto real e duradouro das políticas públicas, para além das flutuações de curto prazo.

    **Como interpretar:** Um CAGR positivo (ex: +5%) indica uma tendência de crescimento no número de ocorrências, enquanto um CAGR negativo (ex: -3%) aponta para uma tendência de redução no longo prazo.
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

st.markdown("""
<div class='footer'>
    Observatório da Violência Contra a Mulher - SC | 2025
</div>
""", unsafe_allow_html=True)

with tab_download:
    st.header("Download das Fontes de Dados")
    st.markdown("Faça o download dos arquivos de dados utilizados neste painel.")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Base Geral de Crimes")
        st.markdown("Contém todos os registros de violência contra a mulher, exceto feminicídios.")
        with open("data/base_geral.xlsx", "rb") as fp:
            st.download_button(
                label="Download (XLSX)",
                data=fp,
                file_name="base_geral.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col2:
        st.subheader("Base de Feminicídios")
        st.markdown("Contém os registros de feminicídios consumados.")
        with open("data/base_feminicidio.xlsx", "rb") as fp:
            st.download_button(
                label="Download (XLSX)",
                data=fp,
                file_name="base_feminicidio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col3:
        st.subheader("Mapa de Municípios (GeoJSON)")
        st.markdown("Arquivo com as geometrias dos municípios de Santa Catarina.")
        with open("data/municipios_sc.json", "rb") as fp:
            st.download_button(
                label="Download (JSON)",
                data=fp,
                file_name="municipios_sc.json",
                mime="application/json"
            )
