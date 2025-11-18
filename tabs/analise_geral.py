import streamlit as st

from plotting import (plot_dia_semana, plot_faixa_etaria, plot_mapa_geral, plot_por_ano, plot_por_mes,
                    plot_serie_temporal, plot_tipo_crime)
from utils import to_csv, to_excel, calcular_cagr, colorir_percentual, formatar_seta_percentual


def criar_tabela_consolidada(df, coluna_agrupamento, nome_agrupamento):
    """Cria uma tabela consolidada com dados de crimes por [agrupamento]."""
    df_agrupado = df.groupby([coluna_agrupamento, 'fato_comunicado', 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index=[coluna_agrupamento, 'fato_comunicado'], columns='ano',
                                       values='total_crime', fill_value=0)

    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    ano_corrente = pd.Timestamp.now().year

    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)

    if len(anos_int) > 1:
        for i in range(1, len(anos_int)):
            ano_atual = anos_int[i]
            if ano_atual == ano_corrente:
                break
            ano_anterior = anos_int[i - 1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            df_pivot[coluna_evolucao] = (
                                                (df_pivot[ano_atual] - df_pivot[ano_anterior]) / df_pivot[
                                            ano_anterior].replace(0, pd.NA) * 100
                                        )

    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente]
    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    if ano_corrente in df_pivot.columns:
        df_pivot.rename(columns={ano_corrente: f'{ano_corrente} (Parcial)'}, inplace=True)

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i - 1]
            ano_atual = anos_int[i]

            if ano_atual == ano_corrente:
                ordem_colunas.append(f'{ano_atual} (Parcial)')
            else:
                ordem_colunas.append(ano_atual)

            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)

    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    ordem_final = [col for col in ordem_colunas if col in df_pivot.columns]

    # 1. Converte os nomes das colunas do DataFrame para texto
    df_pivot.columns = df_pivot.columns.map(str)

    # 2. Converte a lista de ordenação para texto também (para garantir a correspondência)
    ordem_final = [str(col) for col in ordem_final]

    df_consolidado = df_pivot[ordem_final].reset_index()
    nome_coluna = f"Nome do {nome_agrupamento}" if nome_agrupamento == "Município" else nome_agrupamento
    df_consolidado.rename(columns={coluna_agrupamento: nome_coluna, 'fato_comunicado': 'Fato Comunicado'}, inplace=True)

    return df_consolidado


def criar_tabela_total_consolidada(df):
    """Cria uma tabela consolidada com o total de crimes por tipo."""
    df_agrupado = df.groupby(['fato_comunicado', 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index='fato_comunicado', columns='ano', values='total_crime', fill_value=0)

    anos_existentes = [col for col in df_pivot.columns if isinstance(col, (int, float))]
    if anos_existentes:
        anos_todos = range(int(min(anos_existentes)), int(max(anos_existentes)) + 1)
        for ano in anos_todos:
            if ano not in df_pivot.columns:
                df_pivot[ano] = 0

    anos_int = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    ano_corrente = pd.Timestamp.now().year

    df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
    df_pivot['total'] = df_pivot.sum(axis=1)

    if len(anos_int) > 1:
        for i in range(1, len(anos_int)):
            ano_atual = anos_int[i]
            if ano_atual == ano_corrente:
                break
            ano_anterior = anos_int[i - 1]
            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            denominador = df_pivot[ano_anterior].replace(0, pd.NA)
            df_pivot[coluna_evolucao] = (df_pivot[ano_atual] - df_pivot[ano_anterior]) / denominador * 100

    anos_para_cagr = [ano for ano in anos_int if ano != ano_corrente]
    if len(anos_para_cagr) >= 3:
        valor_inicial = df_pivot[anos_para_cagr[0]]
        valor_final = df_pivot[anos_para_cagr[-1]]
        df_pivot['Tendência (CAGR %)'] = calcular_cagr(valor_inicial, valor_final, len(anos_para_cagr))

    if ano_corrente in df_pivot.columns:
        df_pivot.rename(columns={ano_corrente: f'{ano_corrente} (Parcial)'}, inplace=True)

    ordem_colunas = []
    if anos_int:
        ordem_colunas.append(anos_int[0])
        for i in range(1, len(anos_int)):
            ano_anterior = anos_int[i - 1]
            ano_atual = anos_int[i]

            if ano_atual == ano_corrente:
                ordem_colunas.append(f'{ano_atual} (Parcial)')
            else:
                ordem_colunas.append(ano_atual)

            coluna_evolucao = f'Diferença {ano_anterior}-{ano_atual}'
            if coluna_evolucao in df_pivot.columns:
                ordem_colunas.append(coluna_evolucao)

    ordem_colunas.append('total')
    if 'Tendência (CAGR %)' in df_pivot.columns:
        ordem_colunas.append('Tendência (CAGR %)')

    ordem_final = [col for col in ordem_colunas if col in df_pivot.columns]

    df_pivot.columns = df_pivot.columns.map(str)
    ordem_final = [str(col) for col in ordem_final]

    df_consolidado = df_pivot[ordem_final].reset_index()
    df_consolidado.rename(columns={'fato_comunicado': 'Fato Comunicado'}, inplace=True)

    return df_consolidado


def criar_tabela_populacional_agrupada(df_crimes, df_pop, df_regioes, agrupamento, num_anos):
    """Cria uma tabela de análise populacional, permitindo o agrupamento por diferentes níveis."""

    if num_anos == 0: num_anos = 1

    df_pop_com_regioes = pd.merge(df_pop, df_regioes.drop(columns='municipio'), on='municipio_normalizado', how='left')

    if agrupamento == "Consolidado":
        total_fatos = df_crimes.shape[0]
        municipios_presentes = df_crimes['municipio_normalizado'].unique()
        pop_filtrada = df_pop_com_regioes[df_pop_com_regioes['municipio_normalizado'].isin(municipios_presentes)]
        total_populacao = pop_filtrada['populacao_feminina'].sum()

        media_anual = total_fatos / num_anos
        taxa = (media_anual / total_populacao) * 1000 if total_populacao > 0 else 0
        percentual = (media_anual / total_populacao) * 100 if total_populacao > 0 else 0

        tabela = pd.DataFrame([{'Localidade': 'Santa Catarina (Filtro Aplicado)', 'População Feminina': total_populacao,
                                'Média Anual de Fatos Ocorridos': media_anual, 'Fatos por Mil Mulheres (anual)': taxa,
                                '% de Mulheres Vítimas (anual)': percentual}])
        return tabela.set_index('Localidade')

    coluna_agrupamento = {
        "Município": "municipio",
        "Mesorregião": "mesoregiao",
        "Associação": "associacao"
    }[agrupamento]

    crimes_agrupado = df_crimes[coluna_agrupamento].value_counts().reset_index()
    crimes_agrupado.columns = [coluna_agrupamento, 'total_fatos']

    if agrupamento == "Município":
        pop_agrupada = df_pop_com_regioes[[coluna_agrupamento, 'populacao_feminina']]
    else:
        pop_agrupada = df_pop_com_regioes.groupby(coluna_agrupamento)['populacao_feminina'].sum().reset_index()

    df_agregado = pd.merge(crimes_agrupado, pop_agrupada, on=coluna_agrupamento, how='left')

    df_agregado['media_anual_fatos'] = df_agregado['total_fatos'] / num_anos
    df_agregado['taxa_por_mil_mulheres'] = (
                                                      (df_agregado['media_anual_fatos'] / df_agregado[
                                                          'populacao_feminina']) * 1000).fillna(0)
    df_agregado['percentual_mulheres_vitimas'] = (
                                                            (df_agregado['media_anual_fatos'] / df_agregado[
                                                                'populacao_feminina']) * 100).fillna(0)

    tabela_final = df_agregado.rename(columns={
        coluna_agrupamento: agrupamento,
        'populacao_feminina': 'População Feminina',
        'media_anual_fatos': 'Média Anual de Fatos Ocorridos',
        'taxa_por_mil_mulheres': 'Fatos por Mil Mulheres (anual)',
        'percentual_mulheres_vitimas': '% de Mulheres Vítimas (anual)'
    })

    return tabela_final[
        [agrupamento, 'População Feminina', 'Média Anual de Fatos Ocorridos', 'Fatos por Mil Mulheres (anual)',
         '% de Mulheres Vítimas (anual)']].set_index(agrupamento)


def render():
    st.header("Violência Contra a Mulher em Santa Catarina")
    st.markdown(
        "Visão geral dos registros de ocorrências de violência com a mulher no âmbito doméstico (Lei Maria da Penha), no Estado de Santa Catarina.")

    # KPIs
    total_registros = st.session_state.df_geral_filtrado.shape[0]
    media_idade_vitima = 0.0
    if not st.session_state.df_geral_filtrado.empty and st.session_state.df_geral_filtrado[
        'idade_vitima'].notna().any():
        media_idade_vitima = st.session_state.df_geral_filtrado['idade_vitima'].mean()

    num_dias = (st.session_state.data_final - st.session_state.data_inicial).days + 1

    crimes_por_dia = total_registros / num_dias if num_dias > 0 else 0
    crimes_por_hora = total_registros / (num_dias * 24) if num_dias > 0 else 0

    df_cagr_kpi = st.session_state.df_geral_filtrado[
        st.session_state.df_geral_filtrado['ano'] != pd.Timestamp.now().year]
    anos_unicos = sorted(df_cagr_kpi['ano'].unique())
    num_anos_total = len(anos_unicos)

    if num_anos_total >= 3:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total de Registros no Período", value=f"{total_registros:,}".replace(",", "."))
            st.metric(label="Média de Crimes por Dia", value=f"{crimes_por_dia:.1f}")

        with col2:
            dados_por_ano = df_cagr_kpi.groupby('ano').size()
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

    # Distribuição de Crimes por Município
    st.subheader(f"Distribuição Geográfica das Ocorrências por {st.session_state.agrupamento_selecionado}")
    with st.expander("Como interpretar este mapa?"):
        st.info(
            """
            - **O que mostra:** A concentração de ocorrências no território catarinense.
            - **Como ler:** Tons mais escuros indicam uma maior concentração de registros (seja em número absoluto ou em taxas por população).
            - **Interatividade:** Passe o mouse sobre uma localidade para ver os detalhes. Use os botões acima para alternar entre a visualização de números totais e as taxas por mil mulheres.
            """
        )
    if 'map_view_type' not in st.session_state:
        st.session_state.map_view_type = 'Soma dos Crimes'

    def set_map_view(view_type):
        st.session_state.map_view_type = view_type

    st.markdown("""
    <style>
        div[data-testid="stButton"] > button[kind="secondary"] { background-color: #ab47bc; color: rgba(255, 255, 255, 0.6); border: none; box-shadow: none; font-weight: 600; transition: all 0.2s ease-in-out; }
        div[data-testid="stButton"] > button[kind="secondary"]:hover { background-color: #9c27b0; color: rgba(255, 255, 255, 0.9); }
        div[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg, #8e24aa 0%, #ab47bc 100%); color: white; border: none; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15); font-weight: 600; }
        div[data-testid="stButton"] > button:focus { box-shadow: 0 0 0 3px rgba(142, 36, 170, 0.5) !important; outline: none !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button(label="Soma dos Crimes", on_click=set_map_view, args=('Soma dos Crimes',), use_container_width=True,
                  type="primary" if st.session_state.map_view_type == 'Soma dos Crimes' else "secondary")
    with col2:
        st.button(label="Crimes por Mil Mulheres", on_click=set_map_view, args=('Crimes por Mil Mulheres',),
                  use_container_width=True,
                  type="primary" if st.session_state.map_view_type == 'Crimes por Mil Mulheres' else "secondary")
    with col3:
        st.button(label="% de Mulheres Vítimas", on_click=set_map_view, args=('% de Mulheres Vítimas',),
                  use_container_width=True,
                  type="primary" if st.session_state.map_view_type == '% de Mulheres Vítimas' else "secondary")

    view_type = st.session_state.map_view_type
    color_col, label_text = ('quantidade', f'Total de Registros ({st.session_state.agrupamento_selecionado})') if view_type == "Soma dos Crimes" else \
        ('taxa_por_mil_mulheres',
         f'Crimes por Mil Mulheres ({st.session_state.agrupamento_selecionado})') if view_type == "Crimes por Mil Mulheres" else \
            ('percentual_mulheres_vitimas', f'% de Mulheres Vítimas ({st.session_state.agrupamento_selecionado})')

    base_map_df = st.session_state.df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
    base_map_df.columns = ['municipio_normalizado', 'total_fatos']

    if view_type != "Soma dos Crimes":
        base_map_df = pd.merge(base_map_df, st.session_state.df_populacao, on='municipio_normalizado', how='left')
        base_map_df.dropna(subset=['populacao_feminina'], inplace=True)
        anos_no_filtro = st.session_state.df_geral_filtrado['ano'].unique()
        num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
        base_map_df['media_anual_fatos'] = base_map_df['total_fatos'] / num_anos
        if view_type == "Crimes por Mil Mulheres":
            base_map_df[color_col] = (
                                                 (base_map_df['media_anual_fatos'] / base_map_df[
                                                     'populacao_feminina']) * 1000).fillna(
                0)
        else:
            base_map_df[color_col] = (
                                                 (base_map_df['media_anual_fatos'] / base_map_df[
                                                     'populacao_feminina']) * 100).fillna(
                0)
    else:
        base_map_df.rename(columns={'total_fatos': color_col}, inplace=True)

    if st.session_state.agrupamento_selecionado == "Município" or st.session_state.agrupamento_selecionado == "Consolidado":
        map_df = base_map_df[['municipio_normalizado', color_col]]
    else:
        agrupamento_col = "mesoregiao" if st.session_state.agrupamento_selecionado == "Mesorregião" else "associacao"
        municipio_grupo_mapping = st.session_state.df_geral_filtrado[
            ['municipio_normalizado', agrupamento_col]].drop_duplicates()
        df_with_groups = pd.merge(base_map_df, municipio_grupo_mapping, on='municipio_normalizado', how='left')
        if view_type == "Soma dos Crimes":
            crimes_por_grupo = df_with_groups.groupby(agrupamento_col)[color_col].sum().reset_index()
            map_df = pd.merge(municipio_grupo_mapping, crimes_por_grupo, on=agrupamento_col, how='left').fillna(0)
        else:
            grouped_pop = df_with_groups.groupby(agrupamento_col).agg(
                total_fatos_grupo=('total_fatos', 'sum'),
                populacao_feminina_grupo=('populacao_feminina', 'sum')).reset_index()
            anos_no_filtro = st.session_state.df_geral_filtrado['ano'].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            grouped_pop['media_anual_grupo'] = grouped_pop['total_fatos_grupo'] / num_anos
            if view_type == "Crimes por Mil Mulheres":
                grouped_pop[color_col] = (
                                                     (grouped_pop['media_anual_grupo'] / grouped_pop[
                                                         'populacao_feminina_grupo']) * 1000).fillna(
                    0)
            else:
                grouped_pop[color_col] = (
                                                     (grouped_pop['media_anual_grupo'] / grouped_pop[
                                                         'populacao_feminina_grupo']) * 100).fillna(
                    0)
            map_df = pd.merge(municipio_grupo_mapping, grouped_pop[[agrupamento_col, color_col]], on=agrupamento_col,
                              how='left').fillna(0)

    if not map_df.empty:
        map_df = map_df[
            map_df['municipio_normalizado'].isin(st.session_state.df_geral_filtrado['municipio_normalizado'].unique())]

    fig_mapa = plot_mapa_geral(map_df, st.session_state.geojson_sc, color_col, label_text,
                               st.session_state.agrupamento_selecionado)
    st.plotly_chart(fig_mapa, use_container_width=True, key="mapa_geral")
    st.markdown("---")

    # Evolução dos Registros de Ocorrências (Série Temporal)
    st.subheader("Série Histórica de Ocorrências")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            """
            - **O que mostra:** A evolução do número de registros ao longo do tempo (mês a mês).
            - **Como ler:** O eixo horizontal representa o tempo, e o vertical, a quantidade de ocorrências.
            - **Utilidade:** Ajuda a identificar tendências de alta ou queda, picos sazonais e o impacto de eventos ou políticas públicas.
            """
        )
    chart_type_temporal = st.selectbox("Tipo de Gráfico", ("Linha", "Área", "Barras"), key="chart_type_temporal")
    df_temporal = st.session_state.df_geral_filtrado.copy()
    df_temporal['ano_mes'] = df_temporal['data_fato'].dt.to_period('M').astype(str)
    if st.session_state.agrupamento_selecionado == "Consolidado":
        registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values(
            'ano_mes')
        color_param_temporal = None
    else:
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        registros_por_mes_ano = df_temporal.groupby(['ano_mes', coluna_agrupamento]).size().reset_index(
            name='quantidade').sort_values('ano_mes')
        color_param_temporal = coluna_agrupamento

    fig_temporal = plot_serie_temporal(registros_por_mes_ano, chart_type_temporal,
                                       st.session_state.agrupamento_selecionado, color_param_temporal)
    st.plotly_chart(fig_temporal, use_container_width=True, key="temporal_geral")
    st.markdown("---")

    # Distribuição de Ocorrências por Dia da Semana
    st.subheader("Distribuição de Ocorrências por Dia da Semana")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            """
            - **O que mostra:** Em quais dias da semana as ocorrências são mais frequentes.
            - **Como ler:** Cada barra (ou fatia de pizza) representa um dia da semana. A altura da barra indica o volume de registros naquele dia.
            - **Utilidade:** Permite identificar padrões semanais, como aumentos aos sábados e domingos, auxiliando no planejamento de recursos de segurança e apoio.
            """
        )
    chart_type_dia_semana = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza", "Linha", "Área"),
                                         key="chart_type_dia_semana")
    st.session_state.df_geral_filtrado['dia_semana'] = st.session_state.df_geral_filtrado['data_fato'].dt.day_name()
    dias_ordem = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    st.session_state.df_geral_filtrado['dia_semana_cat'] = pd.Categorical(
        st.session_state.df_geral_filtrado['dia_semana'],
        categories=dias_ordem, ordered=True)
    registros_por_dia = st.session_state.df_geral_filtrado['dia_semana_cat'].value_counts().sort_index().reset_index()
    registros_por_dia.columns = ['Dia da Semana', 'Quantidade']
    nomes_dias_pt = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
                     'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    registros_por_dia['Dia da Semana'] = registros_por_dia['Dia da Semana'].map(nomes_dias_pt)

    fig_dia_semana = plot_dia_semana(registros_por_dia, chart_type_dia_semana)
    st.plotly_chart(fig_dia_semana, use_container_width=True, key="dia_semana_geral")
    st.markdown("---")

    # Gráficos em colunas
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        # Registros de Ocorrências por Ano
        st.subheader("Registros de Ocorrências por Ano")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Mostra o total de ocorrências em cada ano do período selecionado, permitindo uma visão macro da evolução anual do problema.")
        chart_type_ano = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza", "Linha", "Área"), key="chart_type_ano")

        ano_corrente = pd.Timestamp.now().year
        if st.session_state.agrupamento_selecionado == "Consolidado":
            registros_por_ano = st.session_state.df_geral_filtrado['ano'].value_counts().sort_index().reset_index()
            registros_por_ano.columns = ['ano', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao",
                                       "Associação": "associacao"}
            coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
            registros_por_ano = st.session_state.df_geral_filtrado.groupby(['ano', coluna_agrupamento]).size().reset_index(
                name='Quantidade')
            color_param = coluna_agrupamento

        if not registros_por_ano.empty:
            registros_por_ano['ano'] = registros_por_ano['ano'].apply(
                lambda x: f'{x} (Parcial)' if x == ano_corrente else str(x)
            )

        fig_ano = plot_por_ano(registros_por_ano, chart_type_ano, st.session_state.agrupamento_selecionado, color_param)
        st.plotly_chart(fig_ano, use_container_width=True, key="ano_geral")

    with col_graf2:
        # Distribuição de Ocorrências por Mês
        st.subheader("Distribuição de Ocorrências por Mês")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Agrupa todas as ocorrências pelo mês em que ocorreram, independentemente do ano. É útil para identificar sazonalidades, como aumentos em meses de férias ou festividades.")
        chart_type_mes = st.selectbox("Tipo de Gráfico", ("Pizza", "Barras", "Linha", "Área"), key="chart_type_mes")
        meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                       'October', 'November', 'December']
        st.session_state.df_geral_filtrado['mes_cat'] = pd.Categorical(st.session_state.df_geral_filtrado['mes'],
                                                                       categories=meses_ordem, ordered=True)
        registros_por_mes = st.session_state.df_geral_filtrado['mes_cat'].value_counts().sort_index().reset_index()
        registros_por_mes.columns = ['Mês', 'Quantidade']
        nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
                          'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
                          'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
        registros_por_mes['Mês'] = registros_por_mes['Mês'].map(nomes_meses_pt)

        fig_mes = plot_por_mes(registros_por_mes, chart_type_mes)
        st.plotly_chart(fig_mes, use_container_width=True, key="mes_geral")

    st.markdown("---")

    # Mais gráficos em colunas
    col_graf3, col_graf4 = st.columns(2)
    with col_graf3:
        # Distribuição por Faixa Etária da Vítima
        st.subheader("Distribuição por Faixa Etária da Vítima")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Mostra quais faixas etárias concentram o maior número de vítimas, ajudando a direcionar campanhas de prevenção e políticas públicas para os grupos mais vulneráveis.")
        chart_type_faixa_etaria = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza"), key="chart_type_faixa_etaria")
        df_faixa_etaria = st.session_state.df_geral_filtrado.dropna(subset=['idade_vitima'])
        bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
        labels = ['0-12 anos', '13-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '61-70 anos',
                  '71-79 anos', '80+ anos']
        df_faixa_etaria['faixa_etaria'] = pd.cut(df_faixa_etaria['idade_vitima'], bins=bins, labels=labels,
                                                right=True)
        registros_por_faixa = df_faixa_etaria['faixa_etaria'].value_counts().sort_index().reset_index()
        registros_por_faixa.columns = ['Faixa Etária', 'Quantidade']

        fig_faixa_etaria = plot_faixa_etaria(registros_por_faixa, chart_type_faixa_etaria)
        st.plotly_chart(fig_faixa_etaria, use_container_width=True, key="faixa_etaria_geral")

    with col_graf4:
        # Tipos de Crimes Mais Frequentes
        st.subheader("Natureza das Ocorrências Mais Frequentes")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Classifica os tipos de crime do mais para o menos frequente. Isso revela a 'porta de entrada' da violência (geralmente ameaças) e a prevalência de cada tipo de agressão.")
        chart_type_fato = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza"), key="chart_type_fato")
        if st.session_state.agrupamento_selecionado == "Consolidado":
            registros_por_fato = st.session_state.df_geral_filtrado['fato_comunicado'].value_counts().reset_index()
            registros_por_fato.columns = ['fato_comunicado', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao",
                                       "Associação": "associacao"}
            coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
            registros_por_fato = st.session_state.df_geral_filtrado.groupby(
                ['fato_comunicado', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento

        fig_fato = plot_tipo_crime(registros_por_fato, chart_type_fato, st.session_state.agrupamento_selecionado,
                                   color_param)
        st.plotly_chart(fig_fato, use_container_width=True, key="fato_geral")

    st.markdown("---")

    # Tabela Consolidada de Crimes por Município
    if st.session_state.agrupamento_selecionado != "Consolidado":
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento_tabela = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        st.subheader(f"Tabela Consolidada de Ocorrências por {st.session_state.agrupamento_selecionado}")
        with st.expander("Como interpretar esta tabela?"):
            st.info(
                """
                - **O que mostra:** Um detalhamento anual do número de ocorrências por tipo de crime e localidade.
                - **Colunas de Diferença:** Mostram a variação percentual (aumento ou queda) de um ano para o outro.
                - **Tendência (CAGR %):** A Taxa de Crescimento Anual Composta indica a tendência de longo prazo (mínimo 3 anos), suavizando flutuações anuais. Um CAGR positivo indica uma tendência de crescimento; negativo, de queda.
                """
            )
        if not st.session_state.df_geral_filtrado.empty:
            tabela_consolidada = criar_tabela_consolidada(st.session_state.df_geral_filtrado,
                                                          coluna_agrupamento_tabela,
                                                          st.session_state.agrupamento_selecionado)
            if not tabela_consolidada.empty:
                # --- BOTÕES DE DOWNLOAD ---
                st.markdown("##### Exportar Dados da Tabela")
                col1_export, col2_export = st.columns(2)  # Ajustado de 3 para 2
                with col1_export:
                    st.download_button(
                        label="📥 Exportar para CSV",
                        data=to_csv(tabela_consolidada),
                        file_name=f'ocorrencias_por_{st.session_state.agrupamento_selecionado}.csv',
                        mime='text/csv',
                        key='csv_consolidada_geral'
                    )
                with col2_export:
                    st.download_button(
                        label="📥 Exportar para Excel",
                        data=to_excel(tabela_consolidada),
                        file_name=f'ocorrencias_por_{st.session_state.agrupamento_selecionado}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        key='excel_consolidada_geral'
                    )
                # O botão de PDF foi removido daqui

                # --- EXIBIÇÃO DA TABELA ---
                colunas_evolucao = [col for col in tabela_consolidada.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}

                ano_corrente_parcial = f'{pd.Timestamp.now().year} (Parcial)'
                colunas_de_anos = [col for col in tabela_consolidada.columns if isinstance(col, int)]
                if ano_corrente_parcial in tabela_consolidada.columns:
                    colunas_de_anos.append(ano_corrente_parcial)

                for col in colunas_de_anos:
                    format_dict[col] = '{:.0f}'
                format_dict['total'] = '{:.0f}'

                if 'Tendência (CAGR %)' in tabela_consolidada.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_consolidada.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_consolidada.style.map(colorir_percentual, subset=colunas_para_colorir).format(
                    format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
        else:
            st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
    else:
        st.subheader("Tabela Consolidada de Ocorrências (Total SC)")
        with st.expander("Como interpretar esta tabela?"):
            st.info(
                """
                - **O que mostra:** Um detalhamento anual do número de ocorrências por tipo de crime para todo o estado (considerando os filtros aplicados).
                - **Colunas de Diferença:** Mostram a variação percentual (aumento ou queda) de um ano para o outro.
                - **Tendência (CAGR %):** A Taxa de Crescimento Anual Composta indica a tendência de longo prazo (mínimo 3 anos), suavizando flutuações anuais. Um CAGR positivo indica uma tendência de crescimento; negativo, de queda.
                """
            )
        if not st.session_state.df_geral_filtrado.empty:
            tabela_total = criar_tabela_total_consolidada(st.session_state.df_geral_filtrado)
            if not tabela_total.empty:
                # --- BOTÕES DE DOWNLOAD ---
                st.markdown("##### Exportar Dados da Tabela")
                col1_export, col2_export = st.columns(2)  # Ajustado de 3 para 2
                with col1_export:
                    st.download_button(
                        label="📥 Exportar para CSV",
                        data=to_csv(tabela_total),
                        file_name='ocorrencias_consolidadas_sc.csv',
                        mime='text/csv',
                        key='csv_total_geral'
                    )
                with col2_export:
                    st.download_button(
                        label="📥 Exportar para Excel",
                        data=to_excel(tabela_total),
                        file_name='ocorrencias_consolidadas_sc.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        key='excel_total_geral'
                    )
                # O botão de PDF foi removido daqui

                # --- EXIBIÇÃO DA TABELA ---
                colunas_evolucao = [col for col in tabela_total.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}

                ano_corrente_parcial = f'{pd.Timestamp.now().year} (Parcial)'
                colunas_de_anos = [col for col in tabela_total.columns if isinstance(col, int)]
                if ano_corrente_parcial in tabela_total.columns:
                    colunas_de_anos.append(ano_corrente_parcial)

                for col in colunas_de_anos:
                    format_dict[col] = '{:.0f}'
                format_dict['total'] = '{:.0f}'

                if 'Tendência (CAGR %)' in tabela_total.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_total.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_total.style.map(colorir_percentual, subset=colunas_para_colorir).format(format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")
        else:
            st.warning("Não há dados para exibir na tabela consolidada com os filtros selecionados.")

    st.markdown("---")

    # Análise Populacional dos Crimes por Município
    st.subheader("Taxa de Ocorrências por População Feminina ")
    with st.expander("Como interpretar esta tabela?"):
        st.info(
            """
            - **O que mostra:** Esta tabela ajusta os números absolutos de crimes pela população feminina de cada localidade, permitindo uma comparação mais justa entre locais de tamanhos diferentes.
            - **Fatos por Mil Mulheres:** Indica quantas mulheres, em um grupo de mil, foram vítimas em média por ano. É a principal métrica para comparar o risco entre diferentes localidades.
            - **% de Mulheres Vítimas:** Mostra a porcentagem da população feminina total que foi vítima em média por ano.
            """
        )
    anos_no_filtro = st.session_state.df_geral_filtrado['ano'].unique()
    num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
    tabela_populacional = criar_tabela_populacional_agrupada(st.session_state.df_geral_filtrado,
                                                            st.session_state.df_populacao,
                                                            st.session_state.df_regioes,
                                                            st.session_state.agrupamento_selecionado, num_anos)

    # --- BOTÕES DE DOWNLOAD PARA TABELA POPULACIONAL ---
    if not tabela_populacional.empty:
        df_para_exportar_pop = tabela_populacional.reset_index()
        st.markdown("##### Exportar Dados da Tabela")
        col1_export_pop, col2_export_pop = st.columns(2)  # Ajustado de 3 para 2
        with col1_export_pop:
            st.download_button(
                label="📥 Exportar para CSV",
                data=to_csv(df_para_exportar_pop),
                file_name=f'taxa_populacional_{st.session_state.agrupamento_selecionado}.csv',
                mime='text/csv',
                key='csv_populacional'
            )
        with col2_export_pop:
            st.download_button(
                label="📥 Exportar para Excel",
                data=to_excel(df_para_exportar_pop),
                file_name=f'taxa_populacional_{st.session_state.agrupamento_selecionado}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key='excel_populacional'
            )
        # O botão de PDF foi removido daqui

    # --- EXIBIÇÃO DA TABELA ---
    st.dataframe(tabela_populacional.style.format(
        {'Média Anual de Fatos Ocorridos': '{:.2f}', 'Fatos por Mil Mulheres (anual)': '{:.2f}',
         '% de Mulheres Vítimas (anual)': '{:.2f}%', 'População Feminina': '{:,.0f}',
         'Tendência (CAGR %)': '{:+.1f}%'}), use_container_width=True)
