import json

import pandas as pd
import streamlit as st
from shapely.geometry import shape

from utils import normalizar_nome


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

        df_geral = pd.merge(df_geral, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']],
                            on='municipio_normalizado', how='left')
        # --- ALTERAÇÃO AQUI ---
        df_geral['mesoregiao'] = df_geral['mesoregiao'].fillna('Não informado')
        df_geral['associacao'] = df_geral['associacao'].fillna('Não informado')

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

        df = pd.merge(df, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']], on='municipio_normalizado',
                      how='left')
        # --- ALTERAÇÃO AQUI ---
        df['mesoregiao'] = df['mesoregiao'].fillna('Não informado')
        df['associacao'] = df['associacao'].fillna('Não informado')

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
        st.error(
            "Arquivo 'base_calendario_feriados.xlsx' não encontrado na pasta 'data'. Este arquivo é necessário para a Análise Sazonal.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados do calendário: {e}")
        return pd.DataFrame()


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
