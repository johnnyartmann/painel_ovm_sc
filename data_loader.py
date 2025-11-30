import json
import pandas as pd
import streamlit as st
from shapely.geometry import shape
import os

@st.cache_data
def carregar_dados_processados():
    """
    Carrega todos os dados pré-processados da pasta 'data/processed'.
    Retorna um dicionário de dataframes e o geojson.
    """
    diretorio = 'data/processed'
    dfs = {}
    geojson_data = None

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

    except FileNotFoundError:
        st.error(f"Diretório '{diretorio}' não encontrado. Execute o script 'preprocess_data.py' primeiro.")
        return None, None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados processados: {e}")
        return None, None
        
    return dfs, geojson_data

# --- CORREÇÃO APLICADA AQUI ---
# Função 'mapear_vizinhos' adicionada para corrigir o erro em 'analises_avancadas.py'
@st.cache_data
def mapear_vizinhos(geojson_data):
    """
    Mapeia os vizinhos de cada município a partir de um arquivo GeoJSON.
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
            
            # Verifica se as geometrias se tocam (são vizinhas)
            if geom1.touches(geom2):
                mapa_vizinhos[nome_mun1].append(nome_mun2)
                # Garante que a relação de vizinhança seja mútua
                if nome_mun2 not in mapa_vizinhos:
                    mapa_vizinhos[nome_mun2] = []
                mapa_vizinhos[nome_mun2].append(nome_mun1)
                
    return mapa_vizinhos
