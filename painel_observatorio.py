import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
    st.session_state.df_geral = dfs.get('geral', pd.DataFrame())
    st.session_state.df_feminicidio = dfs.get('feminicidio', pd.DataFrame())
    st.session_state.df_populacao = dfs.get('populacao', pd.DataFrame())
    st.session_state.df_regioes = dfs.get('regioes', pd.DataFrame())
    st.session_state.df_calendario = dfs.get('calendario', pd.DataFrame())
    st.session_state.geojson_sc = geojson_data
else:
    st.error("🚨 Falha no carregamento dos dados processados.")
    st.warning("Execute o script 'preprocess_data.py' para gerar os arquivos de dados necessários.")
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Análise Geral"

# --- SIDEBAR E FILTROS ---
st.sidebar.image("logo_ovm.jpeg", use_container_width=True)

# Lógica de Filtros (Mantida e Executada ANTES do Header)
if not st.session_state.df_geral.empty:
    with st.sidebar:
        st.header("⚙️ Filtros de Análise")

        # --- VISUALIZAÇÃO / AGRUPAMENTO ---
        st.subheader("📊 VISUALIZAR POR")
        st.session_state.agrupamento_selecionado = st.selectbox(
            "Agrupar por",
            options=["Consolidado", "Município", "Mesorregião", "Associação"],
            index=0,
            help="Escolha como os dados devem ser agrupados nos gráficos e tabelas."
        )

        # --- PERÍODO ---
        st.subheader("📅 PERÍODO")
        min_date = st.session_state.df_geral['data_fato'].min().date()
        max_date = st.session_state.df_geral['data_fato'].max().date()

        st.session_state.data_inicial = st.date_input(
            "Data Inicial",
            value=min_date, # Mantendo valor inicial padrão
            min_value=min_date,
            max_value=max_date,
            help="Selecione a data de início do período.",
            format="DD/MM/YYYY"
        )

        st.session_state.data_final = st.date_input(
            "Data Final",
            value=max_date,
            min_value=st.session_state.data_inicial,
            max_value=max_date,
            help="Selecione a data de fim do período.",
            format="DD/MM/YYYY"
        )

        # DataFrame filtrado apenas por data para popular as opções dos outros filtros
        df_geral_filtrado_por_data = st.session_state.df_geral[
            (st.session_state.df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
            (st.session_state.df_geral['data_fato'].dt.date <= st.session_state.data_final)
        ]
        
        # --- LOCALIZAÇÃO ---
        st.subheader("📍 LOCALIZAÇÃO")
        
        # Filtro de Município
        municipios_disponiveis = sorted(df_geral_filtrado_por_data['municipio'].dropna().unique())
        todos_municipios = st.checkbox("Todos os municípios", value=True, help="Marque para selecionar todos")

        if todos_municipios:
            municipio_selecionado = municipios_disponiveis
        else:
            municipio_selecionado = st.multiselect(
                "Município(s) específico(s)",
                options=municipios_disponiveis,
                default=[]
            )
            if not municipio_selecionado:
                st.warning("Nenhum município selecionado. Exibindo dados de todos os municípios.")
                municipio_selecionado = municipios_disponiveis

        # Filtro de Mesorregião
        mesoregioes_disponiveis = sorted([m for m in df_geral_filtrado_por_data['mesoregiao'].unique() if m != 'Não informado'])
        mesoregiao_selecionado = st.multiselect(
            "Mesorregião(ões)",
            options=mesoregioes_disponiveis,
            default=mesoregioes_disponiveis,
            help="Filtre por mesorregião de Santa Catarina"
        )

        # Filtro de Associação
        associacoes_disponiveis = sorted([a for a in df_geral_filtrado_por_data['associacao'].dropna().unique() if a != 'Não informado'])
        associacao_selecionado = st.multiselect(
            "Associação(ões)",
            options=associacoes_disponiveis,
            default=associacoes_disponiveis,
            help="Filtre por associação de municípios"
        )
        
        # --- TIPO DE CRIME ---
        st.subheader("🚨 TIPO DE CRIME")
        fatos_disponiveis = sorted(df_geral_filtrado_por_data['fato_comunicado'].unique())
        todos_crimes = st.checkbox("Todos os tipos", value=True, help="Marque para incluir todos os crimes")

        if todos_crimes:
            fato_selecionado = fatos_disponiveis
        else:
            fato_selecionado = st.multiselect(
                "Tipo(s) de crime",
                options=fatos_disponiveis,
                default=[]
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
            help="Ajuste o intervalo de idade das vítimas. Se o valor máximo for 100, incluirá todas as idades acima."
        )
        idade_max_texto = "100+ anos" if idade_selecionada[1] == 100 else f"{idade_selecionada[1]} anos"
        st.caption(f"Idades: {idade_selecionada[0]} a {idade_max_texto}")

        # --- CÁLCULOS PARA FILTROS POPULACIONAIS ---
        crimes_por_municipio_para_filtro = df_geral_filtrado_por_data['municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio_para_filtro.columns = ['municipio_normalizado', 'total_fatos']

        df_populacional_metrics = pd.merge(st.session_state.df_populacao.copy(), crimes_por_municipio_para_filtro, on='municipio_normalizado', how='left')
        df_populacional_metrics['total_fatos'] = df_populacional_metrics['total_fatos'].fillna(0)
        
        anos_no_filtro = df_geral_filtrado_por_data['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
        
        df_populacional_metrics['media_anual_fatos'] = df_populacional_metrics['total_fatos'] / num_anos
        df_populacional_metrics['taxa_por_mil_mulheres'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 1000).fillna(0)
        df_populacional_metrics['percentual_mulheres_vitimas'] = ((df_populacional_metrics['media_anual_fatos'] / df_populacional_metrics['populacao_feminina']) * 100).fillna(0)

        # --- FILTROS POPULACIONAIS ---
        st.subheader("📊 FILTROS POPULACIONAIS")
        
        min_pop, max_pop = int(st.session_state.df_populacao['populacao_feminina'].min()), int(st.session_state.df_populacao['populacao_feminina'].max())
        pop_selecionada = st.slider("População Feminina", min_value=min_pop, max_value=max_pop, value=(min_pop, max_pop))

        min_media_fatos, max_media_fatos = float(df_populacional_metrics['media_anual_fatos'].min()), float(df_populacional_metrics['media_anual_fatos'].max())
        media_fatos_selecionada = st.slider("Média Anual de Fatos", min_value=min_media_fatos, max_value=max_media_fatos, value=(min_media_fatos, max_media_fatos))

        min_taxa, max_taxa = float(df_populacional_metrics['taxa_por_mil_mulheres'].min()), float(df_populacional_metrics['taxa_por_mil_mulheres'].max())
        taxa_selecionada = st.slider("Fatos por Mil Mulheres", min_value=min_taxa, max_value=max_taxa, value=(min_taxa, max_taxa))

        min_perc, max_perc = float(df_populacional_metrics['percentual_mulheres_vitimas'].min()), float(df_populacional_metrics['percentual_mulheres_vitimas'].max())
        perc_selecionado = st.slider("% de Mulheres Vítimas", min_value=min_perc, max_value=max_perc, value=(min_perc, max_perc))

        st.sidebar.markdown("---")
        
        # Botão de Impressão via JS
        components.html(
            """
            <script>
            function printPage() {
                window.parent.window.print();
            }
            </script>
            <style>
            .print-btn {
                display: block;
                width: 100%;
                background: linear-gradient(135deg, #8e24aa 0%, #ab47bc 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                cursor: pointer;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(142, 36, 170, 0.3);
            }
            .print-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(142, 36, 170, 0.4);
            }
            </style>
            <button class="print-btn" onclick="printPage()">🖨️ Imprimir / Salvar PDF</button>
            """,
            height=60
        )

        if st.sidebar.button("🔄 Resetar Todos os Filtros", use_container_width=True):
            st.session_state.clear()
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

    st.session_state.df_geral_filtrado = st.session_state.df_geral[
        (st.session_state.df_geral['data_fato'].dt.date >= st.session_state.data_inicial) &
        (st.session_state.df_geral['data_fato'].dt.date <= st.session_state.data_final) &
        (st.session_state.df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (st.session_state.df_geral['municipio'].isin(municipio_selecionado)) &
        (st.session_state.df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (st.session_state.df_geral['associacao'].isin(associacao_selecionado)) &
        (st.session_state.df_geral['idade_vitima'].between(idade_selecionada[0], idade_max_filtro, inclusive='both')) &
        (st.session_state.df_geral['municipio_normalizado'].isin(municipios_filtrados_populacao))
    ].copy()

    st.session_state.df_feminicidio_filtrado = st.session_state.df_feminicidio[
        (st.session_state.df_feminicidio['data_fato'].dt.date >= st.session_state.data_inicial) &
        (st.session_state.df_feminicidio['data_fato'].dt.date <= st.session_state.data_final) &
        (st.session_state.df_feminicidio['municipio'].isin(municipio_selecionado)) &
        (st.session_state.df_feminicidio['mesoregiao'].isin(mesoregiao_selecionado)) &
        (st.session_state.df_feminicidio['associacao'].isin(associacao_selecionado)) &
        (st.session_state.df_feminicidio['idade_vitima'].between(idade_selecionada[0], idade_max_filtro, inclusive='both')) &
        (st.session_state.df_feminicidio['municipio_normalizado'].isin(municipios_filtrados_populacao))
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