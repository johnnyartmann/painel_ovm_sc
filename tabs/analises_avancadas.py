import numpy as np
import pandas as pd
import streamlit as st
from plotting import (plot_barras_sazonal, plot_barras_vulnerabilidade, plot_contagio_geografico,
                    plot_efetividade_denuncia, plot_heatmap_sazonal, plot_heatmap_vulnerabilidade,
                    plot_mapa_letalidade)


def calcular_indice_letalidade(df_geral_filtrado, df_feminicidio_filtrado, agrupamento):
    """Calcula o Índice de Letalidade da Violência."""
    coluna_agrupamento_map = {
        "Município": "municipio_normalizado",
        "Mesorregião": "mesoregiao",
        "Associação": "associacao"
    }
    if agrupamento not in coluna_agrupamento_map:
        return pd.DataFrame()

    coluna_agrupamento = coluna_agrupamento_map[agrupamento]

    df_ocorrencias_puras = df_geral_filtrado[df_geral_filtrado['fato_comunicado'] != 'Feminicídio']
    total_ocorrencias = df_ocorrencias_puras.groupby(coluna_agrupamento).size().reset_index(name='total_ocorrencias')

    total_feminicidios = df_feminicidio_filtrado.groupby(coluna_agrupamento).size().reset_index(
        name='total_feminicidios')

    df_letalidade = pd.merge(total_ocorrencias, total_feminicidios, on=coluna_agrupamento, how='outer').fillna(0)

    df_letalidade['total_ocorrencias'] = df_letalidade['total_ocorrencias'].astype(int)
    df_letalidade['total_feminicidios'] = df_letalidade['total_feminicidios'].astype(int)

    soma_total = df_letalidade['total_ocorrencias'] + df_letalidade['total_feminicidios']
    df_letalidade['indice_letalidade'] = np.where(
        soma_total > 0,
        (df_letalidade['total_feminicidios'] / soma_total) * 100,
        0
    )

    df_letalidade['total_eventos'] = soma_total

    df_letalidade.rename(columns={coluna_agrupamento: 'localidade'}, inplace=True)

    df_final = df_letalidade[[
        'localidade',
        'total_eventos',
        'total_ocorrencias',
        'total_feminicidios',
        'indice_letalidade'
    ]]

    return df_final.sort_values(by='indice_letalidade', ascending=False)


def render():
    st.header("Análises Avançadas sobre a Violência")
    st.markdown(
        "Explore métricas e correlações mais profundas para entender as dinâmicas da violência contra a mulher em Santa Catarina.")

    with st.expander("📈 Índice de Letalidade da Violência", expanded=False):
        # ... (seu código para "Índice de Letalidade" continua aqui, sem alterações)
        st.header("Índice de Letalidade da Violência")
        st.markdown("""
        **A Grande Pergunta:** Qual a probabilidade de uma denúncia de violência em um determinado município escalar para um feminicídio?

        Este índice diferencia o volume de denúncias da **falha fatal do sistema de prevenção**. Um município pode ter poucas denúncias, mas uma alta taxa de letalidade, indicando um problema gravíssimo e silencioso. O índice é calculado como:

        `Índice = (Total de Feminicídios / (Total de Ocorrências de Violência + Total de Feminicídios)) * 100`

        Isso representa: *"Para cada 100 ocorrências de violência contra a mulher, X resultam em morte."*
        """)

        if st.session_state.agrupamento_selecionado == "Consolidado":
            st.warning(
                "Por favor, selecione um nível de agrupamento (Município, Mesorregião ou Associação) para visualizar o Índice de Letalidade.")
        else:
            df_letalidade_calculado = calcular_indice_letalidade(st.session_state.df_geral_filtrado,
                                                                 st.session_state.df_feminicidio_filtrado,
                                                                 st.session_state.agrupamento_selecionado)

            if df_letalidade_calculado.empty:
                st.info("Não há dados suficientes para calcular o Índice de Letalidade com os filtros selecionados.")
            else:
                st.subheader(
                    f"Mapa Coroplético do Índice de Letalidade por {st.session_state.agrupamento_selecionado}")
                with st.expander("Como interpretar este mapa?"):
                    st.info(
                        """
                        - **O que mostra:** O risco de uma ocorrência de violência se tornar um feminicídio em cada localidade.
                        - **Como ler:** Tons mais escuros (vermelho/laranja) indicam uma maior letalidade, ou seja, uma maior proporção de casos que terminam em morte, mesmo que o número total de ocorrências seja baixo. É um indicador de falha na rede de proteção.
                        """
                    )
                if st.session_state.agrupamento_selecionado == "Município":
                    map_df_letalidade = df_letalidade_calculado.rename(columns={'localidade': 'municipio_normalizado'})
                else:
                    mapa_grupo_para_indice = df_letalidade_calculado.set_index('localidade')['indice_letalidade']
                    coluna_agrupamento = "mesoregiao" if st.session_state.agrupamento_selecionado == "Mesorregião" else "associacao"
                    municipios_no_filtro = st.session_state.df_geral_filtrado[
                        ['municipio_normalizado', coluna_agrupamento]].drop_duplicates()
                    municipios_no_filtro['indice_letalidade'] = municipios_no_filtro[coluna_agrupamento].map(
                        mapa_grupo_para_indice)
                    map_df_letalidade = municipios_no_filtro.fillna(0)

                fig_mapa_letalidade = plot_mapa_letalidade(map_df_letalidade, st.session_state.geojson_sc)
                st.plotly_chart(fig_mapa_letalidade, use_container_width=True, key="mapa_letalidade")
                st.markdown("---")

                st.subheader(f"Ranking do Índice de Letalidade por {st.session_state.agrupamento_selecionado}")
                st.markdown(
                    "A tabela abaixo classifica as localidades com maior risco de letalidade. O índice alto, mesmo com poucas ocorrências, é um sinal de alerta.")
                df_ranking = df_letalidade_calculado.rename(
                    columns={'localidade': st.session_state.agrupamento_selecionado,
                             'total_eventos': 'Total de Eventos (Ocorrências + Feminicídios)',
                             'total_ocorrencias': 'Ocorrências de Violência',
                             'total_feminicidios': 'Feminicídios',
                             'indice_letalidade': 'Índice de Letalidade'}).set_index(
                    st.session_state.agrupamento_selecionado)
                st.dataframe(df_ranking.style.format(
                    {'Índice de Letalidade': '{:.2f}', 'Total de Eventos (Ocorrências + Feminicídios)': '{:.0f}',
                     'Ocorrências de Violência': '{:.0f}', 'Feminicídios': '{:.0f}'}).background_gradient(
                    cmap='OrRd', subset=['Índice de Letalidade']), use_container_width=True)

    with st.expander("🎯 Análise de Vulnerabilidade", expanded=False):
        # ... (seu código para "Análise de Vulnerabilidade" continua aqui, sem alterações)
        st.header("Análise de Vulnerabilidade por Faixa Etária e Tipo de Crime")
        st.markdown("""
        Esta análise segmenta o problema por demografia, em vez de geografia, para identificar janelas de vulnerabilidade específicas na vida de uma mulher para certos tipos de crime. O objetivo é permitir a criação de campanhas de prevenção e políticas de proteção mais direcionadas.

        **A grande questão:** O perfil da violência muda drasticamente conforme a idade da vítima?
        """)

        st.subheader("Visualização da Distribuição de Crimes por Faixa Etária")
        with st.expander("Como interpretar este gráfico?"):
            st.info(
                """
                - **O que mostra:** A proporção de cada tipo de crime dentro de uma mesma faixa etária.
                - **Como ler:** Cada barra representa 100% das ocorrências para aquela faixa etária. As cores mostram qual a porcentagem de cada tipo de crime.
                - **Utilidade:** Permite ver, por exemplo, se a ameaça é mais comum entre jovens e a lesão corporal entre mulheres mais velhas, indicando como a natureza da violência evolui com a idade.
                """
            )
        df_vulnerabilidade = st.session_state.df_geral_filtrado.dropna(subset=['idade_vitima']).copy()
        bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
        labels = ['0-12 anos', '13-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '61-70 anos',
                  '71-79 anos', '80+ anos']
        df_vulnerabilidade['faixa_etaria'] = pd.cut(df_vulnerabilidade['idade_vitima'], bins=bins, labels=labels,
                                                    right=True)

        if not df_vulnerabilidade.empty:
            crime_counts = df_vulnerabilidade.groupby(['faixa_etaria', 'fato_comunicado'],
                                                      observed=False).size().unstack(fill_value=0)
            crime_percentages = crime_counts.div(crime_counts.sum(axis=1), axis=0) * 100
            crime_percentages = crime_percentages.reset_index()
            df_plot = crime_percentages.melt(id_vars='faixa_etaria', var_name='fato_comunicado', value_name='percentual')

            fig_barras_vulnerabilidade = plot_barras_vulnerabilidade(df_plot)
            st.plotly_chart(fig_barras_vulnerabilidade, use_container_width=True, key="barras_vulnerabilidade")
        else:
            st.warning("Não há dados suficientes para gerar o gráfico de vulnerabilidade com os filtros selecionados.")

        st.markdown("---")

        st.subheader("Análise de Concentração: Heatmap de Crimes por Faixa Etária")
        st.markdown(
            "O heatmap abaixo mostra a concentração de tipos de crime em cada faixa etária. Células mais escuras indicam uma maior concentração (em números absolutos), destacando quais crimes são mais prevalentes em determinados períodos da vida da mulher.")

        if not df_vulnerabilidade.empty:
            crime_counts_heatmap = df_vulnerabilidade.groupby(['faixa_etaria', 'fato_comunicado'],
                                                              observed=False).size().unstack(fill_value=0)
            fig_heatmap = plot_heatmap_vulnerabilidade(crime_counts_heatmap)
            st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_vulnerabilidade")
        else:
            st.warning("Não há dados suficientes para gerar o heatmap com os filtros selecionados.")

    with st.expander("🔎 Efetividade da Denúncia", expanded=False):
        # ... (seu código para "Efetividade da Denúncia" continua aqui, sem alterações)
        st.header("Índice de Efetividade da Denúncia")
        st.markdown("""
        **A Grande Pergunta:** Em um município, um alto número de denúncias de crimes "menores" (como ameaça) está correlacionado a um menor número de crimes graves (lesão corporal, feminicídio)? Ou seja, a denúncia está funcionando como um mecanismo de prevenção eficaz?

        Este é um proxy para medir a efetividade da resposta do sistema de segurança e apoio. Um sistema eficaz deveria intervir após a primeira denúncia, impedindo a escalada da violência.
        """)

        crimes_leves = ["Ameaça", "Vias de Fato"]
        crimes_graves = ["Lesão Corporal Dolosa", "Estupro", "Feminicídio"]

        if not st.session_state.df_geral_filtrado.empty and not st.session_state.df_populacao.empty:
            df_leves = st.session_state.df_geral_filtrado[
                st.session_state.df_geral_filtrado['fato_comunicado'].isin(crimes_leves)]
            contagem_leves = df_leves.groupby('municipio_normalizado').size().reset_index(name='total_crimes_leves')
            df_graves = st.session_state.df_geral_filtrado[
                st.session_state.df_geral_filtrado['fato_comunicado'].isin(crimes_graves)]
            contagem_graves = df_graves.groupby('municipio_normalizado').size().reset_index(name='total_crimes_graves')
            df_efetividade = pd.merge(contagem_leves, contagem_graves, on='municipio_normalizado',
                                      how='outer').fillna(0)
            df_efetividade = pd.merge(df_efetividade,
                                      st.session_state.df_populacao[
                                          ['municipio_normalizado', 'municipio', 'populacao_feminina']],
                                      on='municipio_normalizado', how='left')
            df_efetividade.dropna(subset=['populacao_feminina', 'municipio'], inplace=True)
            df_efetividade = df_efetividade[df_efetividade['populacao_feminina'] > 0]
            df_efetividade['taxa_crimes_leves'] = (df_efetividade['total_crimes_leves'] / df_efetividade[
                'populacao_feminina']) * 1000
            df_efetividade['taxa_crimes_graves'] = (df_efetividade['total_crimes_graves'] / df_efetividade[
                'populacao_feminina']) * 1000

            st.subheader("Gráfico de Dispersão: Relação entre Denúncias Leves e Ocorrências Graves")
            fig_efetividade = plot_efetividade_denuncia(df_efetividade)
            st.plotly_chart(fig_efetividade, use_container_width=True, key="scatter_efetividade")

            with st.expander("Como interpretar este gráfico?"):
                st.markdown("""
                - **O que mostra:** A relação entre a taxa de crimes considerados "leves" (como ameaça) e a taxa de crimes "graves" (como lesão corporal) em cada município. Cada ponto é um município.
                - **Linha de Tendência:** A linha tracejada mostra a tendência geral.
                - **Correlação Negativa (linha desce):** Cenário Ideal. Municípios onde as mulheres denunciam mais os crimes leves tendem a ter menos crimes graves. Isso sugere que a denúncia e a intervenção precoce estão funcionando.
                - **Correlação Positiva (linha sobe):** Pior Cenário. Municípios com muitas denúncias leves também têm muitos crimes graves. Isso pode indicar um sistema que apenas registra as ocorrências, mas falha em proteger a vítima e impedir a escalada da violência.
                - **Sem Correlação (linha horizontal):** Indica que a relação não é direta e outros fatores são mais determinantes.
                """)
            st.info(
                "Este insight não mede apenas o crime, mas tenta avaliar a resposta do ecossistema de proteção. Ele gera hipóteses sobre a efetividade da polícia, medidas protetivas e redes de apoio, apontando para municípios que podem precisar de uma auditoria em seus processos de atendimento à mulher.")
        else:
            st.warning("Não há dados suficientes para gerar a análise de efetividade com os filtros selecionados.")

    # --- INÍCIO DA CORREÇÃO ---
    # Todo o código a seguir foi indentado para ficar dentro da função render()
    with st.expander("🌐 Contágio Geográfico", expanded=False):
        st.header("Análise de Contágio Geográfico (Hotspots de Vizinhança)")
        st.markdown("""
        **A Grande Pergunta:** A violência em um município é um fenômeno isolado ou é influenciada pela situação de seus vizinhos? Existem "clusters" regionais de violência que transcendem as fronteiras municipais?

        Esta análise trata a violência como um fenômeno que pode se "espalhar" ou se concentrar em microrregiões, requerendo soluções coordenadas entre múltiplos municípios.
        """)
        
        if not st.session_state.df_geral_filtrado.empty and not st.session_state.df_populacao.empty:
            mapa_vizinhos = st.session_state.vizinhos
            crimes_por_municipio = st.session_state.df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
            crimes_por_municipio.columns = ['municipio_normalizado', 'total_fatos']
            df_taxas = pd.merge(crimes_por_municipio,
                                st.session_state.df_populacao[['municipio_normalizado', 'municipio', 'populacao_feminina']],
                                on='municipio_normalizado', how='left')
            df_taxas.dropna(subset=['populacao_feminina', 'municipio'], inplace=True)
            df_taxas = df_taxas[df_taxas['populacao_feminina'] > 0]
            anos_no_filtro = st.session_state.df_geral_filtrado['ano'].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            media_anual_fatos = df_taxas['total_fatos'] / num_anos
            df_taxas['taxa_propria'] = (media_anual_fatos / df_taxas['populacao_feminina']) * 1000
            taxa_por_municipio_map = df_taxas.set_index('municipio_normalizado')['taxa_propria']
            taxas_vizinhanca = []
            for municipio in df_taxas['municipio_normalizado']:
                vizinhos = mapa_vizinhos.get(municipio, [])
                if vizinhos:
                    taxas_dos_vizinhos = taxa_por_municipio_map.reindex(vizinhos).dropna()
                    taxas_vizinhanca.append(taxas_dos_vizinhos.mean() if not taxas_dos_vizinhos.empty else 0)
                else:
                    taxas_vizinhanca.append(0)
            df_taxas['taxa_vizinhanca'] = taxas_vizinhanca

            st.subheader("Gráfico de Dispersão: Taxa de Violência Própria vs. Vizinhança")
            fig_contagio = plot_contagio_geografico(df_taxas)
            st.plotly_chart(fig_contagio, use_container_width=True, key="scatter_contagio")

            with st.expander("Como interpretar os quadrantes deste gráfico?"):
                st.markdown("""
                As linhas cinzas representam a média estadual. Cada ponto é um município, posicionado de acordo com sua própria taxa de violência (eixo X) e a taxa média de seus vizinhos (eixo Y).

                - **🔴 Hotspots (Superior Direito):** Municípios com alta violência, cercados por vizinhos também com alta violência. Indicam um *cluster* geográfico de risco que exige ações regionais coordenadas.
                - **🟠 Municípios em Risco (Superior Esquerdo):** Baixa violência interna, mas cercados por vizinhos violentos. Estão em risco de "contágio" ou "transbordamento" da violência. Ações preventivas são cruciais aqui.
                - **🟣 Ilhas de Violência (Inferior Direito):** Alta violência interna, mas cercados por vizinhos mais pacíficos. O problema é mais localizado e pode estar ligado a fatores específicos do município.
                - **🟢 Pontos Frios (Inferior Esquerdo):** Baixa violência, cercados por vizinhos também com baixa violência. São áreas de resiliência que podem oferecer *insights* sobre políticas públicas eficazes.
                """)
        else:
            st.warning("Não há dados suficientes para gerar a Análise de Contágio Geográfico com os filtros selecionados.")

    with st.expander("📅 Análise Sazonal", expanded=False):
        st.header("Sazonalidade e Eventos-Chave: O Calendário do Risco")
        st.markdown("""
        **A Grande Pergunta:** A violência contra a mulher aumenta de forma previsível em torno de datas ou eventos específicos (feriados, fins de semana prolongados, períodos de férias)?

        Esta análise vai além do gráfico mensal, investigando micro-padrões temporais que podem orientar ações de segurança e campanhas de conscientização.
        """)

        df_geral_filtrado_sazonal = st.session_state.df_geral_filtrado.copy()
        df_geral_filtrado_sazonal['dia_semana'] = df_geral_filtrado_sazonal['data_fato'].dt.day_name()
        df_geral_filtrado_sazonal['mes'] = df_geral_filtrado_sazonal['data_fato'].dt.month_name()

        if not df_geral_filtrado_sazonal.empty:
            st.subheader("Impacto de Feriados e Fins de Semana na Média Diária de Ocorrências")
            with st.expander("Como interpretar este gráfico?"):
                st.info(
                    "Este gráfico compara a média de crimes em dias úteis comuns com dias especiais (feriados, vésperas, fins de semana). Barras mais altas em dias não úteis sugerem uma forte correlação entre o aumento de convivência e o aumento da violência.")
            df_geral_filtrado_sazonal['data_fato_date'] = df_geral_filtrado_sazonal['data_fato'].dt.date
            st.session_state.df_calendario['data_fato_date'] = st.session_state.df_calendario['data'].dt.date
            df_geral_filtrado_sazonal = pd.merge(df_geral_filtrado_sazonal,
                                                 st.session_state.df_calendario[
                                                     ['data_fato_date', 'is_feriado', 'is_fim_de_semana',
                                                      'is_vespera_feriado', 'is_pos_feriado']],
                                                 on='data_fato_date', how='left')
            df_geral_filtrado_sazonal[
                ['is_feriado', 'is_vespera_feriado', 'is_pos_feriado']] = df_geral_filtrado_sazonal[
                ['is_feriado', 'is_vespera_feriado', 'is_pos_feriado']].fillna(False)
            df_periodo_completo = pd.DataFrame(
                pd.date_range(start=st.session_state.data_inicial, end=st.session_state.data_final),
                columns=['data'])
            df_periodo_completo['data_fato_date'] = df_periodo_completo['data'].dt.date
            df_periodo_completo_com_eventos = pd.merge(df_periodo_completo,
                                                       st.session_state.df_calendario[
                                                           ['data_fato_date', 'is_feriado', 'is_fim_de_semana',
                                                            'is_vespera_feriado', 'is_pos_feriado']],
                                                       on='data_fato_date', how='left').fillna(False)
            total_dias_feriado = df_periodo_completo_com_eventos['is_feriado'].sum()
            total_dias_vespera = df_periodo_completo_com_eventos['is_vespera_feriado'].sum()
            total_dias_pos = df_periodo_completo_com_eventos['is_pos_feriado'].sum()
            total_dias_fds = df_periodo_completo_com_eventos['is_fim_de_semana'].sum()
            total_dias_uteis_comuns = len(df_periodo_completo_com_eventos[
                                              (df_periodo_completo_com_eventos['is_feriado'] == False) & (
                                                      df_periodo_completo_com_eventos[
                                                          'is_fim_de_semana'] == False) & (
                                                      df_periodo_completo_com_eventos[
                                                          'is_vespera_feriado'] == False) & (
                                                      df_periodo_completo_com_eventos[
                                                          'is_pos_feriado'] == False)])
            ocorrencias_feriado, ocorrencias_vespera, ocorrencias_pos, ocorrencias_fds = \
                df_geral_filtrado_sazonal[
                    'is_feriado'].sum(), df_geral_filtrado_sazonal['is_vespera_feriado'].sum(), \
                df_geral_filtrado_sazonal[
                    'is_pos_feriado'].sum(), df_geral_filtrado_sazonal['is_fim_de_semana'].sum()
            ocorrencias_uteis_comuns = len(df_geral_filtrado_sazonal[
                                               (df_geral_filtrado_sazonal['is_feriado'] == False) & (
                                                       df_geral_filtrado_sazonal['is_fim_de_semana'] == False) & (
                                                       df_geral_filtrado_sazonal[
                                                           'is_vespera_feriado'] == False) & (
                                                       df_geral_filtrado_sazonal['is_pos_feriado'] == False)])
            media_feriado, media_vespera, media_pos, media_fds, media_uteis_comuns = (
                                                                                         ocorrencias_feriado / total_dias_feriado) if total_dias_feriado > 0 else 0, (
                                                                                                                                                                             ocorrencias_vespera / total_dias_vespera) if total_dias_vespera > 0 else 0, (
                                                                                                                                                                                                                                                                 ocorrencias_pos / total_dias_pos) if total_dias_pos > 0 else 0, (
                                                                                                                                                                                                                                                                                                                                       ocorrencias_fds / total_dias_fds) if total_dias_fds > 0 else 0, (
                                                                                                                                                                                                                                                                                                                                                                                                             ocorrencias_uteis_comuns / total_dias_uteis_comuns) if total_dias_uteis_comuns > 0 else 0
            df_medias = pd.DataFrame(
                {'Tipo de Dia': ['Dia Útil Comum', 'Fim de Semana', 'Véspera de Feriado', 'Feriado', 'Pós-Feriado'],
                 'Média Diária de Ocorrências': [media_uteis_comuns, media_fds, media_vespera, media_feriado,
                                                 media_pos]}).sort_values(
                'Média Diária de Ocorrências', ascending=False)
            fig_barras_sazonal = plot_barras_sazonal(df_medias)
            st.plotly_chart(fig_barras_sazonal, use_container_width=True, key="barras_sazonal")
            st.markdown("---")
            st.subheader("Heatmap de Risco: Dia da Semana vs. Mês")
            st.markdown("A cor de cada célula representa a quantidade média de crimes, destacando os períodos mais 'quentes' do ano.")
            df_periodo_completo_hm = pd.DataFrame(
                pd.to_datetime(pd.date_range(start=st.session_state.data_inicial, end=st.session_state.data_final)),
                columns=['data_fato'])
            df_periodo_completo_hm['mes'], df_periodo_completo_hm['dia_semana'] = df_periodo_completo_hm[
                                                                                      'data_fato'].dt.month_name(), \
                                                                                  df_periodo_completo_hm[
                                                                                      'data_fato'].dt.day_name()
            contagem_dias_hm = df_periodo_completo_hm.groupby(['mes', 'dia_semana']).size().reset_index(
                name='total_dias_no_periodo')
            ocorrencias_hm = df_geral_filtrado_sazonal.groupby(['mes', 'dia_semana']).size().reset_index(
                name='total_ocorrencias')
            df_media_hm = pd.merge(contagem_dias_hm, ocorrencias_hm, on=['mes', 'dia_semana'], how='left').fillna(
                {'total_ocorrencias': 0})
            df_media_hm['media_diaria'] = df_media_hm['total_ocorrencias'] / df_media_hm['total_dias_no_periodo']
            heatmap_pivot = df_media_hm.pivot_table(index='mes', columns='dia_semana', values='media_diaria').fillna(0)
            meses_ordem, nomes_meses_pt = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                           'September', 'October', 'November', 'December'], {'January': 'Janeiro',
                                                                                             'February': 'Fevereiro',
                                                                                             'March': 'Março',
                                                                                             'April': 'Abril',
                                                                                             'May': 'Maio',
                                                                                             'June': 'Junho',
                                                                                             'July': 'Julho',
                                                                                             'August': 'Agosto',
                                                                                             'September': 'Setembro',
                                                                                             'October': 'Outubro',
                                                                                             'November': 'Novembro',
                                                                                             'December': 'Dezembro'}
            dias_ordem, nomes_dias_pt = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                                         'Saturday'], {'Monday': 'Segunda', 'Tuesday': 'Terça',
                                                       'Wednesday': 'Quarta', 'Thursday': 'Quinta',
                                                       'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
            heatmap_pivot = heatmap_pivot.reindex(index=meses_ordem, columns=dias_ordem, fill_value=0)
            heatmap_pivot.index, heatmap_pivot.columns = heatmap_pivot.index.map(nomes_meses_pt), [nomes_dias_pt[col]
                                                                                                    for col in
                                                                                                    heatmap_pivot.columns]
            fig_heatmap_sazonal = plot_heatmap_sazonal(heatmap_pivot)
            st.plotly_chart(fig_heatmap_sazonal, use_container_width=True, key="heatmap_sazonal")
            st.markdown("---")
            st.info(
                """**Por que é Avançado:** Transforma a análise temporal de descritiva ("o que aconteceu") para preditiva ("o que provavelmente vai acontecer"). Isso permite um planejamento proativo, como o reforço de patrulhas e a intensificação de campanhas "Ligue 180" durante o Carnaval ou as festas de fim de ano, por exemplo.""")
        else:
            st.warning("Não há dados para exibir a Análise Sazonal com os filtros selecionados.")