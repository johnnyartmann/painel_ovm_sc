import streamlit as st

from plotting import (plot_bo_contra_autor, plot_distribuicao_idade, plot_feminicidio_por_ano,
                    plot_feminicidio_serie_temporal, plot_heatmap_cruzado, plot_localidade_crime,
                    plot_mapa_feminicidio, plot_meio_crime, plot_passagem_policial, plot_sankey_agressor,
                    plot_scatter_idade, plot_vinculo_autor)
import pandas as pd

from utils import to_csv, to_excel, calcular_cagr, colorir_percentual, formatar_seta_percentual


def criar_tabela_feminicidio_agrupado(df, coluna_agrupamento, nome_agrupamento):
    """Cria uma tabela consolidada com dados de feminicídios por [agrupamento]."""
    df_agrupado = df.groupby([coluna_agrupamento, 'ano']).size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(index=coluna_agrupamento, columns='ano', values='total_crime', fill_value=0)

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
    nome_coluna = f"Nome do {nome_agrupamento}" if nome_agrupamento == "Município" else nome_agrupamento
    df_consolidado.rename(columns={coluna_agrupamento: nome_coluna}, inplace=True)

    return df_consolidado


def criar_tabela_total_feminicidio(df):
    """Cria uma tabela consolidada com o total de feminicídios por ano."""
    if df.empty:
        return pd.DataFrame(columns=['Tipo de Crime', 'total'])

    df_agrupado = df.groupby('ano').size().reset_index(name='total_crime')
    df_pivot = df_agrupado.pivot_table(columns='ano', values='total_crime', fill_value=0)

    anos_existentes = [col for col in df.ano.unique() if isinstance(col, (int, float))]
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

    df_consolidado = df_pivot[ordem_final].reset_index(drop=True)
    df_consolidado.insert(0, 'Tipo de Crime', 'Feminicídio')

    return df_consolidado


def render():
    st.header("Análise de Feminicídios Consumados")
    st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")

    # KPIs
    total_feminicidios = st.session_state.df_feminicidio_filtrado.shape[0]
    idade_media_vitima_fem = st.session_state.df_feminicidio_filtrado['idade_vitima'].mean()
    idade_media_autor_fem = st.session_state.df_feminicidio_filtrado['idade_autor'].mean()
    texto_idade_vitima = f"{idade_media_vitima_fem:.1f} anos" if not pd.isna(
        idade_media_vitima_fem) else "Dados Insuficientes"
    texto_idade_autor = f"{idade_media_autor_fem:.1f} anos" if not pd.isna(
        idade_media_autor_fem) else "Dados Insuficientes"
    col1_fem, col2_fem, col3_fem = st.columns(3)
    with col1_fem: st.metric(label="Total de Feminicídios", value=total_feminicidios)
    with col2_fem: st.metric(label="Idade Média da Vítima", value=texto_idade_vitima)
    with col3_fem: st.metric(label="Idade Média do Autor", value=texto_idade_autor)
    st.markdown("---")

    # Distribuição de Feminicídios por Município
    st.subheader(f"Distribuição Geográfica dos Feminicídios por {st.session_state.agrupamento_selecionado}")
    with st.expander("Como interpretar este mapa?"):
        st.info(
            """
            - **O que mostra:** A localização dos feminicídios no estado.
            - **Como ler:** Tons mais escuros indicam um maior número de casos na localidade. Este mapa mostra os números absolutos, destacando as áreas com maior ocorrência do crime mais grave.
            """
        )
    if st.session_state.agrupamento_selecionado == "Município" or st.session_state.agrupamento_selecionado == "Consolidado":
        map_df_fem = st.session_state.df_feminicidio_filtrado['municipio_normalizado'].value_counts().reset_index()
        map_df_fem.columns = ['municipio_normalizado', 'quantidade']
    else:
        agrupamento_col_fem = "mesoregiao" if st.session_state.agrupamento_selecionado == "Mesorregião" else "associacao"
        feminicidios_por_grupo = st.session_state.df_feminicidio_filtrado.groupby(
            agrupamento_col_fem).size().reset_index(
            name='quantidade_grupo')
        municipio_grupo_mapping_fem = st.session_state.df_feminicidio_filtrado[
            ['municipio_normalizado', agrupamento_col_fem]].drop_duplicates()
        map_df_fem = pd.merge(municipio_grupo_mapping_fem, feminicidios_por_grupo, on=agrupamento_col_fem)
        map_df_fem = map_df_fem.rename(columns={'quantidade_grupo': 'quantidade'})
    fig_mapa_fem = plot_mapa_feminicidio(map_df_fem, st.session_state.geojson_sc,
                                         st.session_state.agrupamento_selecionado)
    st.plotly_chart(fig_mapa_fem, use_container_width=True, key="mapa_fem")
    st.markdown("---")

    # Quantidade de Feminicídios por Mês/Ano
    st.subheader("Quantidade de Feminicídios por Mês/Ano")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            "Mostra a evolução mensal dos casos de feminicídio. Devido ao número menor de casos, este gráfico pode apresentar mais volatilidade, mas ainda é útil para identificar picos e tendências.")
    chart_type_fem_mes_ano = st.selectbox("Tipo de Gráfico", ("Barras", "Linha", "Área"), key="chart_type_fem_mes_ano")
    st.session_state.df_feminicidio_filtrado['ano_mes'] = st.session_state.df_feminicidio_filtrado[
        'data_fato'].dt.to_period(
        'M').astype(str)
    if st.session_state.agrupamento_selecionado == "Consolidado":
        feminicidios_por_mes = st.session_state.df_feminicidio_filtrado.groupby('ano_mes').size().reset_index(
            name='Quantidade')
        color_param = None
    else:
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        feminicidios_por_mes = st.session_state.df_feminicidio_filtrado.groupby(
            ['ano_mes', coluna_agrupamento]).size().reset_index(name='Quantidade')
        color_param = coluna_agrupamento
    feminicidios_por_mes.rename(columns={'ano_mes': 'Mês/Ano'}, inplace=True)

    fig_mes_ano = plot_feminicidio_serie_temporal(feminicidios_por_mes, chart_type_fem_mes_ano,
                                                  st.session_state.agrupamento_selecionado, color_param)
    st.plotly_chart(fig_mes_ano, use_container_width=True, key="mes_ano_fem")
    st.markdown("---")

    # Quantidade de Feminicídios por Ano
    st.subheader("Quantidade de Feminicídios por Ano")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            "Apresenta o total de feminicídios a cada ano, oferecendo uma visão clara da tendência de longo prazo para o crime mais extremo de violência contra a mulher.")
    chart_type_fem_ano = st.selectbox("Tipo de Gráfico", ("Barras", "Linha", "Área"), key="chart_type_fem_ano")

    ano_corrente = pd.Timestamp.now().year
    if st.session_state.agrupamento_selecionado == "Consolidado":
        feminicidios_por_ano = st.session_state.df_feminicidio_filtrado['ano'].value_counts().sort_index().reset_index()
        feminicidios_por_ano.columns = ['ano', 'Quantidade']
        color_param = None
    else:
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        feminicidios_por_ano = st.session_state.df_feminicidio_filtrado.groupby(
            ['ano', coluna_agrupamento]).size().reset_index(
            name='Quantidade')
        color_param = coluna_agrupamento

    if not feminicidios_por_ano.empty:
        feminicidios_por_ano['ano'] = feminicidios_por_ano['ano'].apply(
            lambda x: f'{x} (Parcial)' if x == ano_corrente else str(x)
        )

    fig_ano_fem = plot_feminicidio_por_ano(feminicidios_por_ano, chart_type_fem_ano,
                                           st.session_state.agrupamento_selecionado, color_param)
    st.plotly_chart(fig_ano_fem, use_container_width=True, key="ano_fem")
    st.markdown("---")

    # Vínculo e B.O.
    col_graf_fem1, col_graf_fem2 = st.columns(2)
    with col_graf_fem1:
        st.subheader("Vínculo entre a Vítima e o Autor")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Mostra a relação que a vítima tinha com o agressor. Geralmente, evidencia que a maioria dos feminicídios é cometida por parceiros ou ex-parceiros, reforçando a natureza íntima do crime.")
        chart_type_vinculo = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza"), key="chart_type_vinculo")
        if st.session_state.agrupamento_selecionado == "Consolidado":
            vinculo_autor = st.session_state.df_feminicidio_filtrado['relacao_autor'].value_counts().reset_index()
            vinculo_autor.columns = ['relacao_autor', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
            coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
            vinculo_autor = st.session_state.df_feminicidio_filtrado.groupby(
                ['relacao_autor', coluna_agrupamento]).size().reset_index(name='Quantidade')
            color_param = coluna_agrupamento

        fig_vinculo = plot_vinculo_autor(vinculo_autor, chart_type_vinculo, st.session_state.agrupamento_selecionado,
                                         color_param)
        st.plotly_chart(fig_vinculo, use_container_width=True, key="vinculo_fem")

    with col_graf_fem2:
        st.subheader("Vítima Possuía B.O. contra o Autor?")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Indica a porcentagem de vítimas que já haviam registrado um Boletim de Ocorrência por violência doméstica contra o mesmo autor. Um número alto de 'Não' pode indicar que as vítimas não buscaram ajuda ou não se sentiram seguras para denunciar.")
        chart_type_bo = st.selectbox("Tipo de Gráfico", ("Pizza", "Barras"), key="chart_type_bo")
        bo_contra_autor = st.session_state.df_feminicidio_filtrado[
            'bo_de_vd_contra_o_autor'].value_counts().reset_index()
        bo_contra_autor.columns = ['Resposta', 'Quantidade']

        fig_bo = plot_bo_contra_autor(bo_contra_autor, chart_type_bo)
        st.plotly_chart(fig_bo, use_container_width=True, key="bo_fem")
    st.markdown("---")

    # Idades
    col_graf_fem3, col_graf_fem4 = st.columns(2)
    with col_graf_fem3:
        st.subheader("Distribuição de Idade da Vítima")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Mostra a concentração de idades das vítimas de feminicídio, ajudando a identificar os períodos da vida de maior risco para este crime.")
        chart_type_idade_vitima = st.selectbox("Tipo de Gráfico", ("Histograma", "Gráfico de Densidade"),
                                               key="chart_type_idade_vitima")
        df_idade_vitima = st.session_state.df_feminicidio_filtrado.dropna(subset=['idade_vitima'])

        fig_idade_vitima = plot_distribuicao_idade(df_idade_vitima, chart_type_idade_vitima, 'Idade da Vítima',
                                                   '#8e24aa')
        st.plotly_chart(fig_idade_vitima, use_container_width=True, key="idade_vitima_fem")

    with col_graf_fem4:
        st.subheader("Distribuição de Idade do Autor")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Similar ao gráfico da vítima, mostra a concentração de idades dos autores de feminicídio, ajudando a traçar o perfil do agressor.")
        chart_type_idade_autor = st.selectbox("Tipo de Gráfico", ("Histograma", "Gráfico de Densidade"),
                                              key="chart_type_idade_autor")
        df_idade_autor = st.session_state.df_feminicidio_filtrado.dropna(subset=['idade_autor'])

        fig_idade_autor = plot_distribuicao_idade(df_idade_autor, chart_type_idade_autor, 'Idade do Autor', '#ab47bc')
        st.plotly_chart(fig_idade_autor, use_container_width=True, key="idade_autor_fem")
    st.markdown("---")

    # Raio X do Agressor
    st.subheader("Raio-X do Agressor")
    st.markdown(
        "Análise aprofundada sobre o perfil do agressor, incluindo a dinâmica de idade com a vítima e seu histórico criminal. Estes gráficos ajudam a identificar padrões e possíveis pontos de falha na prevenção.")
    col_raiox1, col_raiox2 = st.columns(2)
    with col_raiox1:
        st.markdown("##### Dinâmica de Idade: Vítima vs. Agressor")
        with st.expander("Como interpretar este gráfico?"):
            st.info("""
            - **O que mostra:** A correlação entre a idade da vítima (eixo X) e a do agressor (eixo Y).
            - **Como ler:** Cada ponto é um caso. A linha tracejada vermelha representa onde a vítima e o agressor teriam a mesma idade.
            - **Pontos acima da linha:** Agressor mais velho que a vítima.
            - **Pontos abaixo da linha:** Agressor mais novo que a vítima.
            """)
        if not st.session_state.df_feminicidio_filtrado.empty and st.session_state.df_feminicidio_filtrado[
            ['idade_vitima', 'idade_autor']].notna().all(axis=1).any():
            fig_scatter_idade = plot_scatter_idade(st.session_state.df_feminicidio_filtrado)
            st.plotly_chart(fig_scatter_idade, use_container_width=True, key="scatter_idade_fem")
        else:
            st.info("Não há dados suficientes para exibir o gráfico de correlação de idades.")
    with col_raiox2:
        st.markdown("##### Histórico do Agressor: A Escalada da Violência")
        with st.expander("Como interpretar este gráfico?"):
            st.info("""
            - **O que mostra:** O fluxo do histórico criminal dos agressores.
            - **Como ler:** Siga as faixas da esquerda para a direita. O gráfico mostra, do total de agressores, quantos já tinham passagem policial e, destes, quantos tinham registros específicos de violência doméstica.
            - **Utilidade:** Revela se o feminicídio foi um ato isolado ou o ápice de um histórico de violência.
            """)
        if not st.session_state.df_feminicidio_filtrado.empty and 'passagem_policial' in st.session_state.df_feminicidio_filtrado.columns and 'passagem_por_violencia_domestica' in st.session_state.df_feminicidio_filtrado.columns:
            fig_sankey = plot_sankey_agressor(st.session_state.df_feminicidio_filtrado)
            if fig_sankey:
                st.plotly_chart(fig_sankey, use_container_width=True, key="sankey_fem")
            else:
                st.info("Não há dados para exibir o gráfico de histórico do agressor.")
        else:
            st.info(
                "Não há dados suficientes ou as colunas necessárias não existem para exibir o gráfico de histórico do agressor.")
    st.markdown("---")

    # Análise Cruzada de Vítima e Agressor
    st.subheader("Análise Cruzada de Vítima e Agressor")
    st.markdown(
        "Este mapa de calor cruza as faixas etárias de vítimas e agressores, revelando padrões de relacionamento etário nos crimes de feminicídio. Células mais escuras indicam uma maior concentração de casos.")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            """
            - **O que mostra:** A concentração de casos de feminicídio no cruzamento entre a faixa etária da vítima (eixo Y) e a do agressor (eixo X).
            - **Como ler:** Células mais escuras indicam uma combinação de faixas etárias onde ocorreram mais crimes.
            - **Utilidade:** Ajuda a identificar se existem padrões etários específicos, como homens mais velhos vitimando mulheres mais novas, ou violência concentrada em casais da mesma faixa etária.
            """
        )
    df_heatmap_cruzado = st.session_state.df_feminicidio_filtrado.dropna(subset=['idade_vitima', 'idade_autor']).copy()

    if not df_heatmap_cruzado.empty:
        fig_heatmap_cruzado = plot_heatmap_cruzado(df_heatmap_cruzado)
        st.plotly_chart(fig_heatmap_cruzado, use_container_width=True, key="heatmap_cruzado_fem")
    else:
        st.info("Não há dados suficientes (com idade da vítima e do autor) para gerar a análise cruzada.")

    st.markdown("---")

    # Outras características
    col_graf_fem5, col_graf_fem6 = st.columns(2)
    with col_graf_fem5:
        st.subheader("Meio Utilizado para o Crime")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Mostra quais foram os instrumentos ou métodos utilizados para cometer o feminicídio. Ajuda a entender a brutalidade dos crimes e a prevalência de, por exemplo, armas brancas ou de fogo.")
        chart_type_meio = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza"), key="chart_type_meio")
        if st.session_state.agrupamento_selecionado == "Consolidado":
            meio_crime = st.session_state.df_feminicidio_filtrado['meio_crime'].value_counts().reset_index()
            meio_crime.columns = ['meio_crime', 'Quantidade']
            color_param = None
        else:
            mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
            coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
            meio_crime = st.session_state.df_feminicidio_filtrado.groupby(
                ['meio_crime', coluna_agrupamento]).size().reset_index(
                name='Quantidade')
            color_param = coluna_agrupamento

        fig_meio = plot_meio_crime(meio_crime, chart_type_meio, st.session_state.agrupamento_selecionado, color_param)
        st.plotly_chart(fig_meio, use_container_width=True, key="meio_fem")

    with col_graf_fem6:
        st.subheader("Autor Foi Preso?")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Indica a taxa de prisão dos autores (flagrante ou posterior). Um número alto de 'Sim' reflete a resposta das forças de segurança na resolução do crime.")
        chart_type_preso = st.selectbox("Tipo de Gráfico", ("Pizza", "Barras"), key="chart_type_preso")
        autor_preso = st.session_state.df_feminicidio_filtrado['autor_preso'].value_counts().reset_index()
        autor_preso.columns = ['Resposta', 'Quantidade']

        fig_preso = plot_autor_preso(autor_preso, chart_type_preso)
        st.plotly_chart(fig_preso, use_container_width=True, key="preso_fem")
    st.markdown("---")

    # Histórico do autor
    col_graf_fem7, col_graf_fem8 = st.columns(2)
    with col_graf_fem7:
        st.subheader("Autor com Registro de B.O.?")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Verifica se o autor já tinha passagem pela polícia por *qualquer* tipo de crime. Ajuda a entender se o agressor já estava no radar do sistema de segurança.")
        chart_type_autor_bo = st.selectbox("Tipo de Gráfico", ("Pizza", "Barras"), key="chart_type_autor_bo")
        autor_bo = st.session_state.df_feminicidio_filtrado['passagem_policial'].value_counts().reset_index()
        autor_bo.columns = ['Resposta', 'Quantidade']

        fig_autor_bo = plot_passagem_policial(autor_bo, chart_type_autor_bo, "Autor com Registro de B.O.?",
                                              '#8e24aa')
        st.plotly_chart(fig_autor_bo, use_container_width=True, key="autor_bo_fem")

    with col_graf_fem8:
        st.subheader("Autor com B.O. por Violência Doméstica?")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                "Este é um indicador crítico. Mostra se o autor já tinha histórico *específico* de violência doméstica. Um 'Sim' aqui indica uma falha do sistema em impedir a escalada da violência após denúncias anteriores.")
        if 'passagem_por_violencia_domestica' in st.session_state.df_feminicidio_filtrado.columns:
            chart_type_autor_bo_vd = st.selectbox("Tipo de Gráfico", ("Pizza", "Barras"),
                                                  key="chart_type_autor_bo_vd")
            autor_bo_vd = st.session_state.df_feminicidio_filtrado[
                'passagem_por_violencia_domestica'].value_counts().reset_index()
            autor_bo_vd.columns = ['Resposta', 'Quantidade']
            if not autor_bo_vd.empty:
                fig_autor_bo_vd = plot_passagem_policial(autor_bo_vd, chart_type_autor_bo_vd,
                                                         "Autor com B.O. por Violência Doméstica?", '#ab47bc')
                st.plotly_chart(fig_autor_bo_vd, use_container_width=True, key="autor_bo_vd_fem")
            else:
                st.info("Não há dados sobre B.O. por violência doméstica para os filtros selecionados.")
        else:
            st.warning("A coluna 'Passagem por Violência Doméstica' não foi encontrada na base de dados.")
    st.markdown("---")

    # Localidade do crime
    st.subheader("Localidade do Crime")
    with st.expander("Como interpretar este gráfico?"):
        st.info(
            "Mostra onde os feminicídios ocorreram em zona rural ou urbana. Esta informação é vital para entender o contexto do crime e pode influenciar estratégias de prevenção e resposta.")
    chart_type_localidade = st.selectbox("Tipo de Gráfico", ("Barras", "Pizza"), key="chart_type_localidade")
    if st.session_state.agrupamento_selecionado == "Consolidado":
        localidade_crime = st.session_state.df_feminicidio_filtrado['localidade'].value_counts().reset_index()
        localidade_crime.columns = ['localidade', 'Quantidade']
        color_param = None
    else:
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        localidade_crime = st.session_state.df_feminicidio_filtrado.groupby(
            ['localidade', coluna_agrupamento]).size().reset_index(
            name='Quantidade')
        color_param = coluna_agrupamento

    fig_localidade = plot_localidade_crime(localidade_crime, chart_type_localidade,
                                           st.session_state.agrupamento_selecionado, color_param)
    st.plotly_chart(fig_localidade, use_container_width=True, key="localidade_fem")
    st.markdown("---")

    # Tabela Consolidada de Feminicídios por Município
    if st.session_state.agrupamento_selecionado != "Consolidado":
        mapa_agrupamento_tabela = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
        coluna_agrupamento_tabela = mapa_agrupamento_tabela[st.session_state.agrupamento_selecionado]
        st.subheader(f"Tabela Consolidada de Feminicídios por {st.session_state.agrupamento_selecionado}")
        with st.expander("Como interpretar esta tabela?"):
            st.info(
                """
                - **O que mostra:** Um detalhamento anual do número de feminicídios por localidade.
                - **Colunas de Diferença:** Mostram a variação percentual de um ano para o outro.
                - **Tendência (CAGR %):** Indica a tendência de longo prazo (mínimo 3 anos).
                """
            )
        if not st.session_state.df_feminicidio_filtrado.empty:
            tabela_feminicidio = criar_tabela_feminicidio_agrupado(st.session_state.df_feminicidio_filtrado,
                                                                   coluna_agrupamento_tabela,
                                                                   st.session_state.agrupamento_selecionado)
            if not tabela_feminicidio.empty:
                # --- BOTÕES DE DOWNLOAD ---
                st.markdown("##### Exportar Dados da Tabela")
                col1_export_fem, col2_export_fem = st.columns(2)  # Ajustado de 3 para 2
                with col1_export_fem:
                    st.download_button(
                        label="📥 Exportar para CSV",
                        data=to_csv(tabela_feminicidio),
                        file_name=f'feminicidios_por_{st.session_state.agrupamento_selecionado}.csv',
                        mime='text/csv',
                        key='csv_consolidada_fem'
                    )
                with col2_export_fem:
                    st.download_button(
                        label="📥 Exportar para Excel",
                        data=to_excel(tabela_feminicidio),
                        file_name=f'feminicidios_por_{st.session_state.agrupamento_selecionado}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        key='excel_consolidada_fem'
                    )
                # O botão de PDF foi removido daqui

                # --- EXIBIÇÃO DA TABELA ---
                colunas_evolucao = [col for col in tabela_feminicidio.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}

                ano_corrente_parcial = f'{pd.Timestamp.now().year} (Parcial)'
                colunas_de_anos = [col for col in tabela_feminicidio.columns if isinstance(col, int)]
                if ano_corrente_parcial in tabela_feminicidio.columns:
                    colunas_de_anos.append(ano_corrente_parcial)

                for col in colunas_de_anos:
                    format_dict[col] = '{:.0f}'
                format_dict['total'] = '{:.0f}'

                if 'Tendência (CAGR %)' in tabela_feminicidio.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_feminicidio.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_feminicidio.style.map(colorir_percentual, subset=colunas_para_colorir).format(
                    format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
        else:
            st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
    else:
        st.subheader("Tabela Consolidada de Feminicídios (Total SC)")
        with st.expander("Como interpretar esta tabela?"):
            st.info(
                """
                - **O que mostra:** Um detalhamento anual do número de feminicídios para todo o estado (considerando os filtros).
                - **Colunas de Diferença:** Mostram a variação percentual de um ano para o outro.
                - **Tendência (CAGR %):** Indica a tendência de longo prazo (mínimo 3 anos).
                """
            )
        if not st.session_state.df_feminicidio_filtrado.empty:
            tabela_total_fem = criar_tabela_total_feminicidio(st.session_state.df_feminicidio_filtrado)
            if not tabela_total_fem.empty:
                # --- BOTÕES DE DOWNLOAD ---
                st.markdown("##### Exportar Dados da Tabela")
                col1_export_total_fem, col2_export_total_fem = st.columns(2)  # Ajustado de 3 para 2
                with col1_export_total_fem:
                    st.download_button(
                        label="📥 Exportar para CSV",
                        data=to_csv(tabela_total_fem),
                        file_name='feminicidios_consolidados_sc.csv',
                        mime='text/csv',
                        key='csv_total_fem'
                    )
                with col2_export_total_fem:
                    st.download_button(
                        label="📥 Exportar para Excel",
                        data=to_excel(tabela_total_fem),
                        file_name='feminicidios_consolidados_sc.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        key='excel_total_fem'
                    )
                # O botão de PDF foi removido daqui

                # --- EXIBIÇÃO DA TABELA ---
                colunas_evolucao = [col for col in tabela_total_fem.columns if 'Diferença' in str(col)]
                format_dict = {col: formatar_seta_percentual for col in colunas_evolucao}

                ano_corrente_parcial = f'{pd.Timestamp.now().year} (Parcial)'
                colunas_de_anos = [col for col in tabela_total_fem.columns if isinstance(col, int)]
                if ano_corrente_parcial in tabela_total_fem.columns:
                    colunas_de_anos.append(ano_corrente_parcial)

                for col in colunas_de_anos:
                    format_dict[col] = '{:.0f}'
                format_dict['total'] = '{:.0f}'

                if 'Tendência (CAGR %)' in tabela_total_fem.columns:
                    format_dict['Tendência (CAGR %)'] = '{:+.1f}%'

                colunas_para_colorir = colunas_evolucao[:]
                if 'Tendência (CAGR %)' in tabela_total_fem.columns:
                    colunas_para_colorir.append('Tendência (CAGR %)')

                styler = tabela_total_fem.style.map(colorir_percentual, subset=colunas_para_colorir).format(
                    format_dict)
                st.dataframe(styler, use_container_width=True)
            else:
                st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
        else:
            st.warning("Não há dados para exibir na tabela de feminicídios com os filtros selecionados.")
