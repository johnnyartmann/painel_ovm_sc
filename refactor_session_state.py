import os
import re

files_to_refactor = ['painel_observatorio.py', 'header.py', 'tabs/analise_geral.py', 'tabs/analise_feminicidios.py']

# 1. Update painel_observatorio.py
with open('painel_observatorio.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace assignments
content = re.sub(r"st\.session_state\.df_geral = dfs\.get\('geral', pd\.DataFrame\(\)\)", "df_geral = dfs.get('geral', pd.DataFrame())", content)
content = re.sub(r"st\.session_state\.df_feminicidio = dfs\.get\('feminicidio', pd\.DataFrame\(\)\)", "df_feminicidio = dfs.get('feminicidio', pd.DataFrame())", content)
content = re.sub(r"st\.session_state\.df_populacao = dfs\.get\('populacao', pd\.DataFrame\(\)\)", "df_populacao = dfs.get('populacao', pd.DataFrame())", content)
content = re.sub(r"st\.session_state\.df_regioes = dfs\.get\('regioes', pd\.DataFrame\(\)\)", "df_regioes = dfs.get('regioes', pd.DataFrame())", content)
content = re.sub(r"st\.session_state\.df_calendario = dfs\.get\('calendario', pd\.DataFrame\(\)\)", "df_calendario = dfs.get('calendario', pd.DataFrame())", content)
content = re.sub(r"st\.session_state\.geojson_sc = geojson_data", "geojson_sc = geojson_data", content)

# Replace access (using negative lookahead to not match df_geral_filtrado)
content = re.sub(r"st\.session_state\.df_geral(?!_filtrado)", "df_geral", content)
content = re.sub(r"st\.session_state\.df_feminicidio(?!_filtrado)", "df_feminicidio", content)
content = re.sub(r"st\.session_state\.df_populacao", "df_populacao", content)
content = re.sub(r"st\.session_state\.df_regioes", "df_regioes", content)
content = re.sub(r"st\.session_state\.df_calendario", "df_calendario", content)
content = re.sub(r"st\.session_state\.geojson_sc", "geojson_sc", content)

with open('painel_observatorio.py', 'w', encoding='utf-8') as f:
    f.write(content)


# 2. Update tabs
def inject_and_replace(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace access
    content = re.sub(r"st\.session_state\.df_geral(?!_filtrado)", "df_geral", content)
    content = re.sub(r"st\.session_state\.df_feminicidio(?!_filtrado)", "df_feminicidio", content)
    content = re.sub(r"st\.session_state\.df_populacao", "df_populacao", content)
    content = re.sub(r"st\.session_state\.df_regioes", "df_regioes", content)
    content = re.sub(r"st\.session_state\.df_calendario", "df_calendario", content)
    content = re.sub(r"st\.session_state\.geojson_sc", "geojson_sc", content)
    
    # Inject imports and data load
    injection = """    from data_loader import carregar_dados_processados
    dfs, geojson_sc = carregar_dados_processados()
    df_geral = dfs.get('geral', pd.DataFrame())
    df_feminicidio = dfs.get('feminicidio', pd.DataFrame())
    df_populacao = dfs.get('populacao', pd.DataFrame())
    df_regioes = dfs.get('regioes', pd.DataFrame())
    df_calendario = dfs.get('calendario', pd.DataFrame())
"""
    
    if filepath.startswith('tabs/'):
        # Inject at the beginning of def render():
        content = re.sub(r"(def render\(\):\n)", r"\g<1>" + injection, content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

inject_and_replace('tabs/analise_geral.py')
inject_and_replace('tabs/analise_feminicidios.py')

print('Refactor complete')
