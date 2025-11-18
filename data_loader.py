import json
import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_dados_processados():
    """
    Carrega todos os dados pré-processados da pasta 'data/processed'.
    Retorna um dicionário de dataframes, o geojson e o mapa de vizinhos.
    """
    diretorio = 'data/processed'
    dfs = {}
    geojson_data = None
    vizinhos_data = None

    try:
        # Carregar todos os arquivos Parquet
        for filename in os.listdir(diretorio):
            if filename.endswith('.parquet'):
                key = filename.replace('.parquet', '')
                caminho_arquivo = os.path.join(diretorio, filename)
                dfs[key] = pd.read_parquet(caminho_arquivo)

        # Carregar o arquivo GeoJSON
        caminho_geojson = os.path.join(diretorio, 'geojson_sc.json')
        if os.path.exists(caminho_geojson):
            with open(caminho_geojson, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        else:
            st.error("Arquivo 'geojson_sc.json' não encontrado no diretório de dados processados.")

        # Carregar o mapa de vizinhos
        caminho_vizinhos = os.path.join(diretorio, 'vizinhos.json')
        if os.path.exists(caminho_vizinhos):
            with open(caminho_vizinhos, 'r', encoding='utf-8') as f:
                vizinhos_data = json.load(f)
        else:
            st.error("Arquivo 'vizinhos.json' não encontrado no diretório de dados processados.")

    except FileNotFoundError:
        st.error(f"Diretório '{diretorio}' não encontrado. Execute o script 'preprocess_data.py' primeiro.")
        return None, None, None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados processados: {e}")
        return None, None, None

    return dfs, geojson_data, vizinhos_data
