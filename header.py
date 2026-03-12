import streamlit as st

def render_custom_header():
    """
    Renderiza o cabeçalho fixo customizado no topo da página.

    Layout:
    1. Botões de navegação (usando botões Streamlit nativos)
    2. Cards de resumo (Filtros atuais) - APENAS EM ABAS DE ANÁLISE
    3. Expander para detalhes de municípios (quando necessário)
    """
    
    # Verifica a aba ativa para determinar a visibilidade dos cards
    active_tab = st.session_state.get('active_tab', 'Análise Geral')
    show_info_cards = active_tab in ["Análise Geral", "Análise de Feminicídios"]

    # --- CSS PARA HEADER FIXO ---
    header_style = """
    <style>
        /* RESET & Compatibilidade */
        header[data-testid="stHeader"] {
            visibility: visible !important;
            background: transparent !important;
            box-shadow: none !important;
            z-index: 1000005 !important;
            pointer-events: none;
        }

        header[data-testid="stHeader"] > div {
            background: transparent !important;
        }

        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stToolbar"] button,
        header[data-testid="stHeader"] button {
            pointer-events: auto !important;
            color: white !important;
            fill: white !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            pointer-events: auto !important;
            color: white !important;
        }

        footer { visibility: hidden; }

        /* HEADER FIXO PRINCIPAL */
        .fixed-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            background: linear-gradient(180deg, #4a148c 0%, #6a1b9a 100%);
            z-index: 999999;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            padding: 0;
            font-family: "Inter", "Source Sans Pro", sans-serif;
            color: white;
            overflow: hidden;
        }

        /* LINHAS DO HEADER */
        .header-nav-row {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 1rem 2rem;
            gap: 0.75rem;
            border-bottom: 1px solid rgba(0,0,0,0.06);
            flex-wrap: nowrap;
            background: white;
            min-height: 70px;
        }

        .header-info-row {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem 2rem;
            gap: 0.5rem;
            flex-wrap: wrap;
            background: transparent; /* Use o fundo do pai (roxo) */
            min-height: auto;
        }

        /* CONTAINER DOS BOTÕES STREAMLIT */
        #header-tabs-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            background: linear-gradient(180deg, #4a148c 0%, #6a1b9a 100%);
            z-index: 999999;
            box-shadow: none;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 0.75rem 2rem;
            display: flex !important;
            gap: 0.75rem;
            align-items: center;
            justify-content: center; /* Centraliza os botões também */
            min-height: 60px;
        }

        /* Estiliza os botões Streamlit dentro do container */
        #header-tabs-container button[data-testid="baseButton-secondary"] {
            color: rgba(255,255,255,0.9) !important;
            font-weight: 500;
            padding: 0.5rem 1rem !important;
            border-radius: 20px !important; /* Mais arredondado */
            transition: all 0.2s ease;
            font-size: 13px !important;
            white-space: nowrap;
            border: 1px solid rgba(255,255,255,0.2) !important;
            background: rgba(255,255,255,0.1) !important;
            cursor: pointer;
            box-shadow: none !important;
            height: 36px !important;
            min-width: fit-content;
        }

        #header-tabs-container button[data-testid="baseButton-secondary"]:hover {
            color: white !important;
            background: rgba(255,255,255,0.2) !important;
            border-color: rgba(255,255,255,0.4) !important;
            transform: translateY(-1px);
        }

        /* Botão ativo (marcado quando está selecionado) */
        #header-tabs-container button[data-testid="baseButton-secondary"][kind="primary"],
        #header-tabs-container button[data-testid="baseButton-secondary"].active {
            background: white !important;
            color: #6a1b9a !important; /* Texto roxo no botão ativo branco */
            font-weight: 700 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
            border-color: white !important;
            border-radius: 20px !important;
        }

        /* CARDS DE INFO */
        .info-container {
            display: flex;
            gap: 0.5rem;
            width: 75%;
            justify-content: end;
            align-items: center;
            flex-wrap: wrap;
        }

        .info-container::-webkit-scrollbar {
            height: 0px; /* Remove scrollbar visual if it happens */
        }

        .info-card {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: white;
            border-radius: 12px;
            padding: 0.5rem 0.5rem;
            min-width: 150px;
            box-shadow: 0 2px 8px rgb(147 42 173);
            border: 1px solid rgb(74 20 140);
            transition: all 0.2s ease;
        }

        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.08);
            border-color: rgba(142,36,170,0.1);
        }

        .info-card h5 {
            margin: 0 0 -0.75rem 0;
            color: #888;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-align: center;
        }

        .info-card p {
            margin: 0;
            color: #333;
            font-weight: 700;
            font-size: 16px;
            text-align: center;
            line-height: 1.2;
        }

        .info-card span {
            font-size: 12px;
            color: #8e24aa;
            font-weight: 500;
            text-align: center;
            margin-top: 0rem;
        }

        /* EXPANDER HTML NO HEADER */
        .header-expander {
            margin-top: 0rem;
            padding: 0.5rem 0.5rem;
            background: white; /* Fundo branco sólido para contraste */
            border: 1px solid rgb(166 65 185);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 6px rgb(166 65 185);
            width: fit-content; /* Only take space needed */
            margin-left: auto;
            margin-right: auto; /* Ensure centering if full width */
            color: #4a148c; /* Texto roxo */
        }

        .header-expander:hover {
            background: #fdfdfd;
            border-color: rgba(142,36,170,0.2);
            transform: translateY(-1px);
        }

        .header-expander summary {
            font-weight: 600;
            color: #4a148c; /* Texto roxo forte */
            font-size: 13px;
            outline: none;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            justify-content: center;
        }

        .header-expander summary::-webkit-details-marker {
            color: #8e24aa;
        }

        .header-expander[open] summary {
            color: #6a1b9a;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            padding-bottom: 0.25rem;
        }

        .expander-content {
            font-size: 12px;
            color: #333; /* Texto escuro para leitura no fundo branco */
            line-height: 1.5;
            padding-top: 0.25rem;
            text-align: center;
        }

        .expander-content p {
            margin: 0.2rem 0;
            word-break: break-word;
        }

        .expander-content strong {
            color: #4a148c;
            font-weight: 700;
        }

        /* AJUSTES DE LAYOUT PRINCIPAL */
        .block-container {
            padding-top: 280px !important;
            margin-top: 0 !important;
        }

        section[data-testid="stSidebar"] {
            top: 0 !important;
            height: 100vh !important;
            padding-top: 0px !important;
            z-index: 999998;
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
        }

        /* RESPONSIVIDADE */
        @media (max-width: 1200px) {
            #header-tabs-container {
                padding: 0.75rem 1.5rem;
                gap: 0.5rem;
                min-height: 65px;
            }

            #header-tabs-container button[data-testid="baseButton-secondary"] {
                padding: 0.5rem 1rem !important;
                font-size: 12px !important;
                height: 36px !important;
            }

            .header-info-row {
                padding: 0.75rem 1.5rem;
                gap: 1rem;
                min-height: 85px;
            }

            .info-card {
                min-width: 150px;
            }

            .info-container {
                gap: 1.5rem;
            }

            .block-container {
                padding-top: 160px !important;
            }
        }

        @media (max-width: 900px) {
            #header-tabs-container {
                padding: 0.75rem 1rem;
                gap: 0.3rem;
                min-height: 60px;
            }

            #header-tabs-container button[data-testid="baseButton-secondary"] {
                padding: 0.4rem 0.8rem !important;
                font-size: 11px !important;
                height: 34px !important;
            }

            .info-container {
                gap: 1rem;
            }

            .header-info-row {
                padding: 0.75rem 1rem;
                gap: 0.75rem;
                min-height: auto;
                display: flex;
                flex-wrap: wrap;
            }

            .info-card {
                min-width: 140px;
                border-left-width: 3px;
                padding-left: 0.75rem;
            }

            .block-container {
                padding-top: 150px !important;
            }
        }

        @media (max-width: 600px) {
            #header-tabs-container {
                padding: 0.5rem;
                gap: 0.2rem;
                min-height: 55px;
            }

            #header-tabs-container button[data-testid="baseButton-secondary"] {
                padding: 0.3rem 0.5rem !important;
                font-size: 10px !important;
                height: 32px !important;
            }

            .header-info-row {
                display: none;
            }

            .block-container {
                padding-top: 70px !important;
            }
        }
    </style>
    """

    # --- AJUSTE DINÂMICO DE PADDING (Se cards ocultos) ---
    if not show_info_cards:
        # Reduz o padding do topo quando os cards não são exibidos
        header_style = header_style.replace("padding-top: 280px !important;", "padding-top: 110px !important;")
        header_style = header_style.replace("padding-top: 110px !important;", "padding-top: 90px !important;") # Sidebar
        
        # Ajustes responsivos para tablets/laptops pequenos
        header_style = header_style.replace("padding-top: 160px !important;", "padding-top: 110px !important;")
        header_style = header_style.replace("padding-top: 150px !important;", "padding-top: 110px !important;")

    # --- INJETAR CSS ---
    st.markdown(header_style, unsafe_allow_html=True)

    # --- CONSTRUIR INFO CARDS HTML ---
    def build_info_html():
        """Constrói os cards de informação dos filtros"""
        if 'data_inicial' not in st.session_state or 'df_geral_filtrado' not in st.session_state:
            return ""

        data_ini = st.session_state.data_inicial
        data_fim = st.session_state.data_final
        dias_totais = (data_fim - data_ini).days

        # --- MESORREGIÕES ---
        mesos_no_filtro = st.session_state.df_geral_filtrado['mesoregiao'].unique()
        mesos_reais = [m for m in mesos_no_filtro if m != 'Não informado']
        qtd_mesos = len(mesos_reais)

        if qtd_mesos >= 6:
            texto_meso = "Todo o Estado (SC)"
            detalhe_meso = None
        elif qtd_mesos <= 2:
            texto_meso = ", ".join(mesos_reais[:2])
            detalhe_meso = ", ".join(sorted(mesos_reais))
        else:
            texto_meso = f"{qtd_mesos} Mesorregiões"
            detalhe_meso = ", ".join(sorted(mesos_reais))

        # --- ASSOCIAÇÕES (NOVO) ---
        assocs_no_filtro = st.session_state.df_geral_filtrado['associacao'].unique()
        assocs_reais = [a for a in assocs_no_filtro if a != 'Não informado']
        qtd_assocs = len(assocs_reais)

        if qtd_assocs >= 20: # Valor arbitrário para "Muitas"
            texto_assoc = "Diversas Associações"
            detalhe_assoc = None
        elif qtd_assocs <= 1:
            texto_assoc = assocs_reais[0] if assocs_reais else "Nenhuma"
            detalhe_assoc = None
        elif qtd_assocs <= 3: # Mostra até 3 nomes no card
            texto_assoc = ", ".join(assocs_reais[:2]) + ("..." if qtd_assocs > 2 else "")
            detalhe_assoc = ", ".join(sorted(assocs_reais))
        else:
            texto_assoc = f"{qtd_assocs} Associações"
            detalhe_assoc = ", ".join(sorted(assocs_reais))

        # --- MUNICÍPIOS ---
        muns_selecionados = st.session_state.df_geral_filtrado['municipio'].unique()
        qtd_mun = len(muns_selecionados)

        if qtd_mun >= 293:
            texto_mun = "Todos os 295 Municípios"
            mostrar_expander_mun = False
        elif qtd_mun == 1:
            texto_mun = muns_selecionados[0]
            mostrar_expander_mun = False
        else:
            texto_mun = f"{qtd_mun} Municípios"
            mostrar_expander_mun = True # Sempre permitir ver a lista se não for todos

        # --- TIPOS DE CRIME (NOVO) ---
        crimes_selecionados = st.session_state.df_geral_filtrado['fato_comunicado'].unique()
        qtd_crimes = len(crimes_selecionados)
        # Assumindo que sabemos o total de tipos possíveis ou apenas baseando no count
        # Vamos assumir que se for > 5 é "Vários" ou listar
        
        if qtd_crimes <= 2:
            texto_crime = ", ".join(crimes_selecionados)
            detalhe_crime = None
        else:
            texto_crime = f"{qtd_crimes} Tipos de Crime"
            detalhe_crime = ", ".join(sorted(crimes_selecionados))


        # Monta HTML do expander se necessário
        expander_html = ""
        # Verifica se tem algum detalhe para mostrar
        tem_detalhe = any([detalhe_meso, detalhe_assoc, mostrar_expander_mun, detalhe_crime])
        
        if tem_detalhe:
            corpo_expander = ""
            if detalhe_meso: corpo_expander += f"<p><strong>Mesorregiões:</strong> {detalhe_meso}</p>"
            if detalhe_assoc: corpo_expander += f"<p><strong>Associações:</strong> {detalhe_assoc}</p>"
            if mostrar_expander_mun: 
                lista_mun = ", ".join(sorted(muns_selecionados))
                corpo_expander += f"<p><strong>Municípios:</strong> {lista_mun}</p>"
            if detalhe_crime: corpo_expander += f"<p><strong>Crimes:</strong> {detalhe_crime}</p>"

            expander_html = f'<details class="header-expander"><summary>🔎 Ver detalhes selecionados</summary><div class="expander-content">{corpo_expander}</div></details>'

        info_html = f"""
<div class="header-info-row">
<div class="info-container">
<div class="info-card">
<h5>📅 Período</h5>
<p>{data_ini.strftime("%d/%m/%Y")} - {data_fim.strftime("%d/%m/%Y")}</p>
<span>{dias_totais} dias</span>
</div>
<div class="info-card">
<h5>🗺️ Abrangência</h5>
<p>{texto_meso}</p>
<span>Mesorregiões</span>
</div>
<div class="info-card">
<h5>🏢 Associações</h5>
<p>{texto_assoc}</p>
<span>Selecionadas</span>
</div>
<div class="info-card">
<h5>📍 Municípios</h5>
<p>{texto_mun}</p>
<span>Selecionados</span>
</div>
<div class="info-card">
<h5>⚖️ Crimes</h5>
<p>{texto_crime}</p>
<span>Tipos</span>
</div>
</div>
{expander_html}
</div>
"""
        return info_html

    # Renderiza os cards de info APENAS se a aba permitir
    if show_info_cards:
        info_html = build_info_html()
        if info_html:
            # Envolvemos em uma classe específica para o CSS de impressão pegar
            # E adicionamos a div de quebra de página logo após
            # Envolvemos em uma classe específica para o CSS de impressão pegar
            # E adicionamos a div de quebra de página logo após
            st.markdown(f'''
<div class="custom-info-cards-wrapper" style="position: fixed; top: 70px; left: 0; width: 100vw; z-index: 999998;">
{info_html}
</div>
''', unsafe_allow_html=True)


def render_tab_buttons():
    """
    Renderiza os botões de navegação das abas usando botões Streamlit nativos.
    Estes botões serão posicionados no header fixo via CSS.
    """

    # Callbacks para mudar de aba
    def mudar_aba(nome_aba):
        st.session_state.active_tab = nome_aba

    # Container com ID específico para o CSS posicionar
    st.markdown('<div id="header-tabs-container">', unsafe_allow_html=True)

    # Cria os botões em colunas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tipo = "primary" if st.session_state.get('active_tab') == "Análise Geral" else "secondary"
        st.button(
            "📊 Análise Geral",
            key="btn_analise_geral",
            on_click=mudar_aba,
            args=("Análise Geral",),
            type=tipo,
            use_container_width=True
        )

    with col2:
        tipo = "primary" if st.session_state.get('active_tab') == "Análise de Feminicídios" else "secondary"
        st.button(
            "🚨 Análise de Feminicídios",
            key="btn_feminicidios",
            on_click=mudar_aba,
            args=("Análise de Feminicídios",),
            type=tipo,
            use_container_width=True
        )

    with col3:
        tipo = "primary" if st.session_state.get('active_tab') == "Metodologia e Glossário" else "secondary"
        st.button(
            "📖 Metodologia e Glossário",
            key="btn_metodologia",
            on_click=mudar_aba,
            args=("Metodologia e Glossário",),
            type=tipo,
            use_container_width=True
        )

    with col4:
        tipo = "primary" if st.session_state.get('active_tab') == "Download de Dados" else "secondary"
        st.button(
            "📥 Download de Dados",
            key="btn_download",
            on_click=mudar_aba,
            args=("Download de Dados",),
            type=tipo,
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
