import pandas as pd
import json
import os
from utils import normalizar_nome
import pyarrow as pa
import pyarrow.parquet as pq

def carregar_e_processar_dados():
    """
    Carrega todos os dados brutos, processa-os e retorna dicionários
    de dataframes e outros dados.
    """
    dfs = {}
    outros_dados = {}

    # Carregar e processar cada conjunto de dados
    try:
        df_regioes = pd.read_excel('data/base_regioes_associacoes.xlsx')
        df_regioes.columns = (df_regioes.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df_regioes['municipio_normalizado'] = df_regioes['municipio'].apply(normalizar_nome)
        dfs['regioes'] = df_regioes

        df_populacao = pd.read_excel('data/base_populacao.xlsx')
        df_populacao.columns = (df_populacao.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('í', 'i', regex=False))
        df_populacao['municipio_normalizado'] = df_populacao['municipio'].apply(normalizar_nome)
        dfs['populacao'] = df_populacao

        df_calendario = pd.read_excel('data/base_calendario_feriados.xlsx')
        df_calendario['data'] = pd.to_datetime(df_calendario['data'])
        dfs['calendario'] = df_calendario

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
        df_geral['municipio_normalizado'] = df_geral['municipio'].apply(normalizar_nome)
        df_geral = pd.merge(df_geral, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']],
                            on='municipio_normalizado', how='left')
        df_geral['mesoregiao'] = df_geral['mesoregiao'].fillna('Não informado')
        df_geral['associacao'] = df_geral['associacao'].fillna('Não informado')

        df_feminicidio = pd.read_excel('data/base_feminicidio.xlsx')
        df_feminicidio.rename(columns={
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
        df_feminicidio.columns = (df_feminicidio.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False)
                      .str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False)
                      .str.replace('ê', 'e', regex=False)
                      .str.replace('á', 'a', regex=False))
        df_feminicidio['data_fato'] = pd.to_datetime(df_feminicidio['data_fato'])
        df_feminicidio['idade_vitima'] = pd.to_numeric(df_feminicidio['idade_vitima'], errors='coerce')
        df_feminicidio['idade_autor'] = pd.to_numeric(df_feminicidio['idade_autor'], errors='coerce')
        df_feminicidio['municipio_normalizado'] = df_feminicidio['municipio'].apply(normalizar_nome)
        df_feminicidio = pd.merge(df_feminicidio, df_regioes[['municipio_normalizado', 'mesoregiao', 'associacao']], on='municipio_normalizado',
                      how='left')
        df_feminicidio['mesoregiao'] = df_feminicidio['mesoregiao'].fillna('Não informado')
        df_feminicidio['associacao'] = df_feminicidio['associacao'].fillna('Não informado')
        df_feminicidio['ano'] = df_feminicidio['data_fato'].dt.year
        dfs['feminicidio'] = df_feminicidio

        df_feminicidio_para_geral = df_feminicidio.copy()
        df_feminicidio_para_geral['fato_comunicado'] = 'Feminicídio'

        df_final = pd.concat([df_geral, df_feminicidio_para_geral], ignore_index=True)
        df_final['ano'] = df_final['data_fato'].dt.year
        df_final['mes'] = df_final['data_fato'].dt.month_name()
        dfs['geral'] = df_final

        with open('data/municipios_sc.json', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        for feature in geojson_data['features']:
            nome_original = feature['properties'].get('NM_MUN')
            if nome_original:
                feature['properties']['NM_MUN_NORMALIZADO'] = normalizar_nome(nome_original)
        outros_dados['geojson_sc'] = geojson_data

    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
        return None, None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None, None

    return dfs, outros_dados

def salvar_dados_processados(dfs, outros_dados, diretorio='data/processed'):
    """
    Salva cada dataframe como um arquivo Parquet e outros dados como JSON.
    """
    try:
        os.makedirs(diretorio, exist_ok=True)

        for key, df in dfs.items():
            caminho_arquivo = os.path.join(diretorio, f"{key}.parquet")
            df.to_parquet(caminho_arquivo)
            print(f"DataFrame '{key}' salvo em '{caminho_arquivo}'")

        for key, data in outros_dados.items():
            caminho_arquivo = os.path.join(diretorio, f"{key}.json")
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            print(f"Dado '{key}' salvo em '{caminho_arquivo}'")

    except Exception as e:
        print(f"Erro ao salvar os arquivos processados: {e}")


if __name__ == "__main__":
    print("Iniciando o pré-processamento dos dados...")
    dataframes, outros_dados_dict = carregar_e_processar_dados()
    if dataframes is not None:
        salvar_dados_processados(dataframes, outros_dados_dict)
        print("Pré-processamento concluído.")