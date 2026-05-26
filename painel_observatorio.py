import pandas as pd
import streamlit as st
from datetime import datetime
from data_loader import carregar_dados_processados
from tabs import analise_geral
from tabs import analise_feminicidios
from tabs import download
from tabs import glossario
import header  # Importa o módulo do cabeçalho

# --- FUNÇÃO PARA CARREGAR O CSS EXTERNO ---
def carregar_css(caminho_arquivo):
    """Lê um arquivo CSS e o retorna formatado para injeção no Streamlit."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            css = f.read()
        # Envolve o CSS lido com as tags <style>
        return f"<style>{css}</style>"
    except FileNotFoundError:
        st.error(f"Arquivo de estilo '{caminho_arquivo}' não encontrado.")
        return ""

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- INJEÇÃO DO CSS CUSTOMIZADO ---
# Carrega o CSS do arquivo externo e o aplica
css_personalizado = carregar_css("style.css")
st.markdown(css_personalizado, unsafe_allow_html=True)


# --- CARREGAMENTO DOS DADOS ---
dfs, geojson_data = carregar_dados_processados()

if dfs is not None and geojson_data is not None:
    df_geral = dfs.get('geral', pd.DataFrame())
    df_feminicidio = dfs.get('feminicidio', pd.DataFrame())
    df_populacao = dfs.get('populacao', pd.DataFrame())
    df_regioes = dfs.get('regioes', pd.DataFrame())
    df_calendario = dfs.get('calendario', pd.DataFrame())
    geojson_sc = geojson_data
else:
    st.error("🚨 Falha no carregamento dos dados processados.")
    st.warning("Execute o script 'preprocess_data.py' para gerar os arquivos de dados necessários.")
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Análise Geral"
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# Armazena dados compartilhados para evitar recarga nos tabs
st.session_state.df_populacao = df_populacao
st.session_state.df_regioes = df_regioes
st.session_state.df_calendario = df_calendario
st.session_state.geojson_sc = geojson_sc

# Prefixo dinâmico para forçar recriação dos widgets ao resetar
_rc = st.session_state.reset_counter

# --- SIDEBAR E FILTROS ---
st.sidebar.image("logo_ovm.png", use_container_width=True)

# Lógica de Filtros (Mantida e Executada ANTES do Header)
if not df_geral.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")

        # --- VISUALIZAÇÃO / AGRUPAMENTO ---
        st.subheader("📊 VISUALIZAR POR")
        st.session_state.agrupamento_selecionado = st.selectbox(
            "Agrupar por",
            options=["Consolidado", "Município", "Mesorregião", "Associação"],
            index=0,
            help="Escolha como os dados devem ser agrupados nos gráficos e tabelas.",
            key=f"agrupamento_selecionado_widget_{_rc}"
        )

        # --- PERÍODO ---
        st.subheader("📅 PERÍODO")
        min_date = df_geral['data_fato'].min().date()
        max_date = df_geral['data_fato'].max().date()

        st.session_state.data_inicial = st.date_input(
            "Data Inicial",
            value=min_date, # Mantendo valor inicial padrão
            min_value=min_date,
            max_value=max_date,
            help="Selecione a data de início do período.",
            format="DD/MM/YYYY",
            key=f"data_inicial_widget_{_rc}"
        )

        st.session_state.data_final = st.date_input(
            "Data Final",
            value=max_date,
            min_value=st.session_state.data_inicial,
            max_value=max_date,
            help="Selecione a data de fim do período.",
            format="DD/MM/YYYY",
            key=f"data_final_widget_{_rc}"
        )

        # DataFrame filtrado apenas por data para popular as opções dos outros filtros
        df_geral_filtrado_por_data = df_geral[
            (df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
            (df_geral['data_fato'].dt.date <= st.session_state.data_final)
        ]
        
        # --- LOCALIZAÇÃO ---
        st.subheader("📍 LOCALIZAÇÃO")
        
        # Filtro de Município
        municipios_disponiveis = sorted(df_geral_filtrado_por_data['municipio'].dropna().unique())
        todos_municipios = st.checkbox("Todos os municípios", value=True, help="Marque para selecionar todos", key=f"todos_municipios_check_{_rc}")

        if todos_municipios:
            municipio_selecionado = municipios_disponiveis
        else:
            municipio_selecionado = st.multiselect(
                "Município(s) específico(s)",
                options=municipios_disponiveis,
                default=[],
                key=f"municipio_selecionado_multi_{_rc}"
            )
            if not municipio_selecionado:
                st.warning("Nenhum município selecionado. Exibindo dados de todos os municípios.")
                municipio_selecionado = municipios_disponiveis

        # Filtro de Mesorregião
        mesoregioes_disponiveis = sorted(df_geral_filtrado_por_data['mesoregiao'].unique())
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)",
            options=mesoregioes_disponiveis,
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina",
            key=f"mesoregiao_selecionado_multi_{_rc}"
        )

        # Filtro de Associação
        associacoes_disponiveis = sorted(df_geral_filtrado_por_data['associacao'].dropna().unique())
        associacao_selecionado = st.multiselect(
            "Associação(ões)",
            options=associacoes_disponiveis,
            default=associacoes_disponiveis,
            help="Filtre por associação de municípios",
            key=f"associacao_selecionado_multi_{_rc}"
        )
        
        # --- TIPO DE CRIME ---
        st.subheader("🚨 TIPO DE CRIME")
        fatos_disponiveis = sorted(df_geral_filtrado_por_data['fato_comunicado'].unique())
        todos_crimes = st.checkbox("Todos os tipos", value=True, help="Marque para incluir todos os crimes", key=f"todos_crimes_check_{_rc}")

        if todos_crimes:
            fato_selecionado = fatos_disponiveis
        else:
            fato_selecionado = st.multiselect(
                "Tipo(s) de crime",
                options=fatos_disponiveis,
                default=[],
                key=f"fato_selecionado_multi_{_rc}"
            )
            if not fato_selecionado:
                st.warning("Nenhum tipo de crime selecionado. Exibindo todos os tipos.")
                fato_selecionado = fatos_disponiveis

        # --- PERFIL DA VÍTIMA ---
        st.subheader("👥 PERFIL DA VÍTIMA")
        idade_selecionada = st.slider(
            "Faixa Etária",
            min_value=0,
            max_value=100,
            value=(0, 100),
            help="Ajuste o intervalo de idade das vítimas. Se o valor máximo for 100, incluirá todas as idades acima.",
            key=f"idade_selecionada_slider_{_rc}"
        )
        idade_max_texto = "100+ anos" if idade_selecionada[1] == 100 else f"{idade_selecionada[1]} anos"
        st.caption(f"Idades: {idade_selecionada[0]} a {idade_max_texto}")

        # --- CÁLCULOS PARA FILTROS POPULACIONAIS ---
        crimes_por_municipio_para_filtro = df_geral_filtrado_por_data['municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio_para_filtro.columns = ['municipio_normalizado', 'total_fatos']

        df_populacional_metrics = pd.merge(df_populacao.copy(), crimes_por_municipio_para_filtro, on='municipio_normalizado', how='left')
        df_populacional_metrics['total_fatos'] = df_populacional_metrics['total_fatos'].fillna(0)
        
        anos_no_filtro = df_geral_filtrado_por_data['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
        
        df_populacional_metrics['media_anual_fatos'] = df_populacional_metrics['total_fatos'] / num_anos
        df_populacional_metrics['taxa_por_mil_mulheres'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 1000).fillna(0)
        df_populacional_metrics['percentual_mulheres_vitimas'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 100).fillna(0)

        # --- FILTROS POPULACIONAIS ---
        st.subheader("📊 FILTROS POPULACIONAIS")
        
        min_pop, max_pop = int(df_populacao['populacao_feminina'].min()), int(df_populacao['populacao_feminina'].max())
        pop_disabled = False
        if min_pop >= max_pop:
            max_pop = min_pop + 1
            pop_disabled = True
        pop_selecionada = st.slider("População Feminina", min_value=min_pop, max_value=max_pop, value=(min_pop, max_pop), disabled=pop_disabled, key=f"pop_selecionada_slider_{_rc}")

        min_media_fatos, max_media_fatos = float(df_populacional_metrics['media_anual_fatos'].min()), float(df_populacional_metrics['media_anual_fatos'].max())
        media_disabled = False
        if min_media_fatos >= max_media_fatos:
            max_media_fatos = min_media_fatos + 0.01
            media_disabled = True
        media_fatos_selecionada = st.slider("Média Anual de Fatos", min_value=min_media_fatos, max_value=max_media_fatos, value=(min_media_fatos, max_media_fatos), disabled=media_disabled, key=f"media_fatos_selecionada_slider_{_rc}")

        min_taxa, max_taxa = float(df_populacional_metrics['taxa_por_mil_mulheres'].min()), float(df_populacional_metrics['taxa_por_mil_mulheres'].max())
        taxa_disabled = False
        if min_taxa >= max_taxa:
            max_taxa = min_taxa + 0.01
            taxa_disabled = True
        taxa_selecionada = st.slider("Fatos por Mil Mulheres", min_value=min_taxa, max_value=max_taxa, value=(min_taxa, max_taxa), disabled=taxa_disabled, key=f"taxa_selecionada_slider_{_rc}")

        min_perc, max_perc = float(df_populacional_metrics['percentual_mulheres_vitimas'].min()), float(df_populacional_metrics['percentual_mulheres_vitimas'].max())
        perc_disabled = False
        if min_perc >= max_perc:
            max_perc = min_perc + 0.01
            perc_disabled = True
        perc_selecionado = st.slider("% de Mulheres Vítimas", min_value=min_perc, max_value=max_perc, value=(min_perc, max_perc), disabled=perc_disabled, key=f"perc_selecionado_slider_{_rc}")

        st.sidebar.markdown("---")
        

        if st.sidebar.button("🔄 Resetar Todos os Filtros", use_container_width=True):
            st.session_state.reset_counter += 1
            st.rerun()

    # --- LÓGICA DE FILTRAGEM FINAL ATUALIZADA ---
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

    st.session_state.df_geral_filtrado = df_geral[
        (df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
        (df_geral['data_fato'].dt.date <= st.session_state.data_final) &
        (df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (df_geral['municipio'].isin(municipio_selecionado)) &
        (df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_geral['associacao'].isin(associacao_selecionado)) &
        (df_geral['idade_vitima'].between(idade_selecionada[0], idade_max_filtro, inclusive='both')) &
        (df_geral['municipio_normalizado'].isin(municipios_filtrados_populacao))
    ].copy()

    st.session_state.df_feminicidio_filtrado = df_feminicidio[
        (df_feminicidio['data_fato'].dt.date >= st.session_state.data_inicial) &
        (df_feminicidio['data_fato'].dt.date <= st.session_state.data_final) &
        (df_feminicidio['municipio'].isin(municipio_selecionado)) &
        (df_feminicidio['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_feminicidio['associacao'].isin(associacao_selecionado)) &
        (df_feminicidio['idade_vitima'].between(idade_selecionada[0], idade_max_filtro, inclusive='both')) &
        (df_feminicidio['municipio_normalizado'].isin(municipios_filtrados_populacao))
    ].copy()

    # Renderiza o header fixo via módulo externo
    header.render_custom_header()

    # Renderiza os botões de navegação das abas
    header.render_tab_buttons()

    # --- RENDERIZAÇÃO DO CONTEÚDO (BASEADO NA ABA ATIVA) ---
    if st.session_state.active_tab == "Análise Geral":
        analise_geral.render()
    elif st.session_state.active_tab == "Análise de Feminicídios":
        analise_feminicidios.render()
    elif st.session_state.active_tab == "Metodologia e Glossário":
        glossario.render()
    elif st.session_state.active_tab == "Download de Dados":
        download.render()

else:
    st.error("🚨 Nenhum dado para exibir.")
    st.warning("Verifique se os arquivos de dados foram carregados corretamente ou se os filtros aplicados não resultaram em uma seleção vazia.")
