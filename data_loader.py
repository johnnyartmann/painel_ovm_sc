import json
import pandas as pd
import streamlit as st
from shapely.geometry import shape
import os

@st.cache_data(ttl=86400)
def carregar_parquets():
    """Carrega todos os DataFrames da pasta 'data/processed'. Usa cache_data para seguranca contra mutacao."""
    diretorio = 'data/processed'
    dfs = {}

    try:
        for filename in os.listdir(diretorio):
            if filename.endswith('.parquet'):
                key = filename.replace('.parquet', '')
                caminho_arquivo = os.path.join(diretorio, filename)
                dfs[key] = pd.read_parquet(caminho_arquivo)
    except FileNotFoundError:
        st.error(f"Diretorio '{diretorio}' nao encontrado. Execute o script 'preprocess_data.py' primeiro.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados processados: {e}")
        return None

    return dfs


@st.cache_resource
def carregar_geojson():
    """Carrega o GeoJSON com @st.cache_resource para evitar copias desnecessarias na RAM."""
    caminho_geojson = os.path.join('data', 'processed', 'geojson_sc.json')
    try:
        if os.path.exists(caminho_geojson):
            with open(caminho_geojson, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            st.error("Arquivo 'geojson_sc.json' nao encontrado no diretorio de dados processados.")
            return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o GeoJSON: {e}")
        return None


def carregar_dados_processados():
    """
    Carrega todos os dados pre-processados.
    Retorna um dicionario de DataFrames e o GeoJSON.
    Mantida para compatibilidade com chamadas existentes.
    """
    dfs = carregar_parquets()
    geojson_data = carregar_geojson()

    return dfs, geojson_data


@st.cache_resource
def mapear_vizinhos(geojson_data):
    """
    Mapeia os vizinhos de cada municipio a partir de um arquivo GeoJSON.
    Requer a biblioteca 'shapely'.
    """
    municipios = geojson_data['features']
    geometrias = {
        feature['properties']['NM_MUN_NORMALIZADO']: shape(feature['geometry'])
        for feature in municipios if feature.get('geometry')
    }

    mapa_vizinhos = {}
    lista_nomes = list(geometrias.keys())

    for i in range(len(lista_nomes)):
        nome_mun1 = lista_nomes[i]
        geom1 = geometrias[nome_mun1]
        mapa_vizinhos[nome_mun1] = []

        for j in range(i + 1, len(lista_nomes)):
            nome_mun2 = lista_nomes[j]
            geom2 = geometrias[nome_mun2]

            if geom1.touches(geom2):
                mapa_vizinhos[nome_mun1].append(nome_mun2)
                if nome_mun2 not in mapa_vizinhos:
                    mapa_vizinhos[nome_mun2] = []
                mapa_vizinhos[nome_mun2].append(nome_mun1)

    return mapa_vizinhos
