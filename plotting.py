import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_mapa_geral(map_df, geojson_sc, color_col, label_text, agrupamento_selecionado):
    """Gera o mapa coroplético para a análise geral."""
    fig_mapa = px.choropleth_mapbox(map_df, geojson=geojson_sc, locations='municipio_normalizado',
                                    featureidkey="properties.NM_MUN_NORMALIZADO",
                                    color=color_col, color_continuous_scale="Purples", mapbox_style="carto-positron",
                                    zoom=6,
                                    center={"lat": -27.59, "lon": -50.52}, opacity=0.7,
                                    labels={color_col: label_text})
    fig_mapa.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=True,
                           coloraxis_colorbar=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
    return fig_mapa


def plot_serie_temporal(registros_por_mes_ano, chart_type, agrupamento_selecionado, color_param_temporal):
    """Gera o gráfico de série temporal."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                     labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'}, template='plotly_white')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
    elif chart_type == "Área":
        fig = px.area(registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                      labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'}, template='plotly_white')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    else:  # Linha
        fig = px.line(registros_por_mes_ano, x='ano_mes', y='quantidade', color=color_param_temporal,
                      labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'}, template='plotly_white',
                      markers=True)
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    return fig


def plot_dia_semana(registros_por_dia, chart_type):
    """Gera o gráfico de distribuição por dia da semana."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_dia, x='Dia da Semana', y='Quantidade',
                     labels={'x': 'Dia da Semana', 'y': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color='#8A2BE2', textposition='outside')
    elif chart_type == "Linha":
        fig = px.line(registros_por_dia, x='Dia da Semana', y='Quantidade',
                      labels={'x': 'Dia da Semana', 'y': 'Quantidade'},
                      template='plotly_white', markers=True)
        fig.update_traces(line_color='#8A2BE2')
    elif chart_type == "Área":
        fig = px.area(registros_por_dia, x='Dia da Semana', y='Quantidade',
                      labels={'x': 'Dia da Semana', 'y': 'Quantidade'},
                      template='plotly_white')
        fig.update_traces(line_color='#8A2BE2')
    else:  # Pizza
        fig = px.pie(registros_por_dia, names='Dia da Semana', values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_por_ano(registros_por_ano, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de ocorrências por ano."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_ano, x='ano', y='Quantidade', color=color_param,
                     labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
        fig.update_traces(textposition='outside')
    elif chart_type == "Linha":
        fig = px.line(registros_por_ano, x='ano', y='Quantidade', color=color_param,
                      labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                      template='plotly_white', markers=True)
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    elif chart_type == "Área":
        fig = px.area(registros_por_ano, x='ano', y='Quantidade', color=color_param,
                      labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                      template='plotly_white')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    else:  # Pizza
        pie_names = 'ano' if agrupamento_selecionado == "Consolidado" else color_param
        fig = px.pie(registros_por_ano, names=pie_names, values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_por_mes(registros_por_mes, chart_type):
    """Gera o gráfico de ocorrências por mês."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_mes, x='Mês', y='Quantidade', labels={'x': 'Mês', 'y': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color='#9370DB', textposition='outside')
    elif chart_type == "Linha":
        fig = px.line(registros_por_mes, x='Mês', y='Quantidade', labels={'x': 'Mês', 'y': 'Quantidade'},
                      template='plotly_white', markers=True)
        fig.update_traces(line_color='#9370DB')
    elif chart_type == "Área":
        fig = px.area(registros_por_mes, x='Mês', y='Quantidade', labels={'x': 'Mês', 'y': 'Quantidade'},
                      template='plotly_white')
        fig.update_traces(line_color='#9370DB')
    else:
        fig = px.pie(registros_por_mes, names='Mês', values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside', sort=False)
    return fig


def plot_faixa_etaria(registros_por_faixa, chart_type):
    """Gera o gráfico de distribuição por faixa etária."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_faixa, x='Faixa Etária', y='Quantidade',
                     labels={'x': 'Faixa Etária', 'y': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color='#9370DB', textposition='outside')
    else:  # Pizza
        fig = px.pie(registros_por_faixa, names='Faixa Etária', values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_tipo_crime(registros_por_fato, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de tipos de crimes mais frequentes."""
    if chart_type == "Barras":
        fig = px.bar(registros_por_fato, x='Quantidade', y='fato_comunicado', color=color_param, orientation='h',
                     labels={'fato_comunicado': 'Tipo de Crime', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#9370DB')
        fig.update_traces(textposition='auto')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:  # Pizza
        pie_names = 'fato_comunicado' if agrupamento_selecionado == "Consolidado" else color_param
        fig = px.pie(registros_por_fato, names=pie_names, values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_mapa_feminicidio(map_df_fem, geojson_sc, agrupamento_selecionado):
    """Gera o mapa coroplético de feminicídios."""
    fig = px.choropleth_mapbox(map_df_fem, geojson=geojson_sc, locations='municipio_normalizado',
                               featureidkey="properties.NM_MUN_NORMALIZADO",
                               color='quantidade', color_continuous_scale="Reds", mapbox_style="carto-positron", zoom=6,
                               center={"lat": -27.59, "lon": -50.52}, opacity=0.7,
                               labels={'quantidade': f'Total de Feminicídios ({agrupamento_selecionado})'})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=True,
                      coloraxis_colorbar=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
    return fig


def plot_feminicidio_serie_temporal(feminicidios_por_mes, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de série temporal de feminicídios."""
    if chart_type == "Linha":
        fig = px.line(feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                      labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                      template='plotly_white', markers=True)
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    elif chart_type == "Área":
        fig = px.area(feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                      labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                      template='plotly_white')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#8A2BE2')
    else:  # Barras
        fig = px.bar(feminicidios_por_mes, x='Mês/Ano', y='Quantidade', color=color_param,
                     labels={'x': 'Mês/Ano', 'y': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
        fig.update_traces(textposition='outside')
    return fig


def plot_feminicidio_por_ano(feminicidios_por_ano, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de feminicídios por ano."""
    if chart_type == "Linha":
        fig = px.line(feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                      labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                      template='plotly_white', markers=True)
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#6a1b9a')
    elif chart_type == "Área":
        fig = px.area(feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                      labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                      template='plotly_white')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(line_color='#6a1b9a')
    else:  # Barras
        fig = px.bar(feminicidios_por_ano, x='ano', y='Quantidade', color=color_param,
                     labels={'ano': 'Ano', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#6a1b9a')
        fig.update_traces(textposition='outside')
    return fig


def plot_vinculo_autor(vinculo_autor, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de vínculo entre vítima e autor."""
    if chart_type == "Barras":
        fig = px.bar(vinculo_autor, x='Quantidade', y='relacao_autor', color=color_param, orientation='h',
                     labels={'relacao_autor': 'Vínculo com o Autor', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
        fig.update_traces(textposition='auto')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:  # Pizza
        pie_names = 'relacao_autor' if agrupamento_selecionado == "Consolidado" else color_param
        fig = px.pie(vinculo_autor, names=pie_names, values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_bo_contra_autor(bo_contra_autor, chart_type):
    """Gera o gráfico de B.O. da vítima contra o autor."""
    if chart_type == "Barras":
        fig = px.bar(bo_contra_autor, x='Resposta', y='Quantidade',
                     labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color='#8e24aa', textposition='outside')
    else:  # Pizza
        fig = px.pie(bo_contra_autor, names='Resposta', values='Quantidade', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
    return fig


def plot_distribuicao_idade(df_idade, column_name, chart_type, x_axis_label, color):
    """Gera o gráfico de distribuição de idade."""
    if chart_type == "Histograma":
        fig = px.histogram(df_idade, x=column_name, nbins=20,
                           labels={column_name: x_axis_label, 'count': 'Quantidade'},
                           template='plotly_white', color_discrete_sequence=[color])
    else: 
        fig = px.violin(df_idade, y=column_name,
                        labels={column_name: x_axis_label},
                        template='plotly_white', color_discrete_sequence=[color], box=True, points="all")
    return fig


def plot_scatter_idade(df_feminicidio_filtrado):
    """Gera o gráfico de dispersão de idades (vítima vs. autor)."""
    fig = px.scatter(df_feminicidio_filtrado.dropna(subset=['idade_vitima', 'idade_autor']),
                     x='idade_vitima', y='idade_autor',
                     labels={'idade_vitima': 'Idade da Vítima', 'idade_autor': 'Idade do Autor'},
                     color_discrete_sequence=['#8e24aa'],
                     hover_data=['municipio', 'relacao_autor', 'meio_crime'])
    max_idade = max(df_feminicidio_filtrado['idade_vitima'].max(), df_feminicidio_filtrado['idade_autor'].max())
    fig.add_shape(type='line', x0=0, y0=0, x1=max_idade, y1=max_idade,
                  line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash'), name='Idade Igual')
    fig.update_layout(xaxis_title="Idade da Vítima", yaxis_title="Idade do Autor", legend_title="Legenda")
    return fig


def plot_sankey_agressor(df_feminicidio_filtrado):
    """Gera o gráfico de Sankey para o histórico do agressor."""
    total_agressores = len(df_feminicidio_filtrado)
    com_passagem = df_feminicidio_filtrado['passagem_policial'].value_counts().get('SIM', 0)
    sem_passagem = total_agressores - com_passagem
    com_bo_vd = len(df_feminicidio_filtrado[
                        (df_feminicidio_filtrado['passagem_policial'] == 'SIM') & (
                                df_feminicidio_filtrado['passagem_por_violencia_domestica'] == 'SIM')])
    com_bo_outros = com_passagem - com_bo_vd

    if total_agressores > 0:
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=25, line=dict(color="white", width=2),
                      label=["Total de Agressores", "Com Passagem Policial", "Sem Passagem Policial",
                             "Com B.O. por Violência Doméstica", "Com B.O. por Outros Crimes"],
                      color=["#4a148c", "#d32f2f", "#757575", "#e91e63", "#ff6f00"]),
            link=dict(source=[0, 0, 1, 1], target=[1, 2, 3, 4],
                      value=[com_passagem, sem_passagem, com_bo_vd, com_bo_outros],
                      color=["rgba(211, 47, 47, 0.4)", "rgba(117, 117, 117, 0.3)", "rgba(233, 30, 99, 0.5)",
                             "rgba(255, 111, 0, 0.4)"]),
            textfont=dict(family="Inter, sans-serif", size=14, color="white"))])
        fig.update_layout(font=dict(size=13, family="Inter, sans-serif"), plot_bgcolor='white', paper_bgcolor='white')
        return fig
    return None


def plot_heatmap_cruzado(df_heatmap_cruzado):
    """Gera o heatmap de análise cruzada (vítima vs. agressor)."""
    bins = [0, 17, 29, 40, 50, 60, 120]
    labels = ['0-17 anos', '18-29 anos', '30-40 anos', '41-50 anos', '51-60 anos', '60+ anos']

    df_heatmap_cruzado['faixa_etaria_vitima'] = pd.cut(df_heatmap_cruzado['idade_vitima'], bins=bins, labels=labels,
                                                      right=True)
    df_heatmap_cruzado['faixa_etaria_autor'] = pd.cut(df_heatmap_cruzado['idade_autor'], bins=bins, labels=labels,
                                                     right=True)

    df_heatmap_cruzado['faixa_etaria_vitima'] = pd.Categorical(df_heatmap_cruzado['faixa_etaria_vitima'],
                                                              categories=labels, ordered=True)
    df_heatmap_cruzado['faixa_etaria_autor'] = pd.Categorical(df_heatmap_cruzado['faixa_etaria_autor'],
                                                             categories=labels, ordered=True)

    heatmap_data = df_heatmap_cruzado.groupby(['faixa_etaria_vitima', 'faixa_etaria_autor'],
                                              observed=False).size().unstack(fill_value=0)

    heatmap_data = heatmap_data.reindex(index=labels, columns=labels, fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Purples',
        hoverongaps=False,
        text=heatmap_data.values,
        texttemplate="%{text}"
    ))

    fig.update_layout(
        title="Concentração de Casos por Faixa Etária: Vítima vs. Agressor",
        xaxis_title="Faixa Etária do Agressor",
        yaxis_title="Faixa Etária da Vítima"
    )
    return fig


def plot_meio_crime(meio_crime, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de meio utilizado para o crime."""
    if chart_type == "Barras":
        fig = px.bar(meio_crime, x='meio_crime', y='Quantidade', color=color_param,
                     labels={'meio_crime': 'Meio Utilizado', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
        fig.update_traces(textposition='outside')
    else:  # Pizza
        pie_names = 'meio_crime' if agrupamento_selecionado == "Consolidado" else color_param
        fig = px.pie(meio_crime, names=pie_names, values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_autor_preso(autor_preso, chart_type):
    """Gera o gráfico se o autor foi preso."""
    if chart_type == "Barras":
        fig = px.bar(autor_preso, x='Resposta', y='Quantidade',
                     labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color='#ab47bc', textposition='outside')
    else:  # Pizza
        fig = px.pie(autor_preso, names='Resposta', values='Quantidade', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
    return fig


def plot_passagem_policial(autor_bo, chart_type, title, color):
    """Gera o gráfico de passagem policial do autor."""
    if chart_type == "Barras":
        fig = px.bar(autor_bo, x='Resposta', y='Quantidade',
                     labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        fig.update_traces(marker_color=color, textposition='outside')
    else:  # Pizza
        fig = px.pie(autor_bo, names='Resposta', values='Quantidade', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
    return fig


def plot_localidade_crime(localidade_crime, chart_type, agrupamento_selecionado, color_param):
    """Gera o gráfico de localidade do crime."""
    if chart_type == "Barras":
        fig = px.bar(localidade_crime, x='localidade', y='Quantidade', color=color_param,
                     labels={'localidade': 'Localidade', 'Quantidade': 'Quantidade'},
                     template='plotly_white', text='Quantidade')
        if agrupamento_selecionado == "Consolidado":
            fig.update_traces(marker_color='#8A2BE2')
        fig.update_traces(textposition='outside')
    else:  # Pizza
        pie_names = 'localidade' if agrupamento_selecionado == "Consolidado" else color_param
        fig = px.pie(localidade_crime, names=pie_names, values='Quantidade', hole=.4,
                     color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_traces(textinfo='percent+label', textposition='outside')
    return fig


def plot_mapa_letalidade(map_df_letalidade, geojson_sc):
    """Gera o mapa coroplético do índice de letalidade."""
    fig = px.choropleth_mapbox(map_df_letalidade, geojson=geojson_sc, locations='municipio_normalizado',
                               featureidkey="properties.NM_MUN_NORMALIZADO",
                               color='indice_letalidade', color_continuous_scale="OrRd",
                               mapbox_style="carto-positron", zoom=6,
                               center={"lat": -27.59, "lon": -50.52}, opacity=0.7,
                               labels={'indice_letalidade': f'Índice de Letalidade (a cada 100 eventos)'})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      coloraxis_colorbar=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
    return fig


def plot_barras_vulnerabilidade(df_plot):
    """Gera o gráfico de barras de vulnerabilidade."""
    fig = px.bar(df_plot, x='faixa_etaria', y='percentual', color='fato_comunicado',
                 title="Distribuição Percentual de Tipos de Crime por Faixa Etária",
                 labels={'faixa_etaria': 'Faixa Etária da Vítima', 'percentual': 'Percentual de Ocorrências (%)',
                         'fato_comunicado': 'Tipo de Crime'},
                 template='plotly_white', color_discrete_sequence=px.colors.sequential.Purples_r)
    fig.update_layout(barmode='stack', yaxis_ticksuffix='%')
    return fig


def plot_heatmap_vulnerabilidade(crime_counts_heatmap):
    """Gera o heatmap de vulnerabilidade com normalização por coluna (tipo de crime)."""
    # Normaliza cada coluna dividindo pelo valor máximo daquela coluna
    df_normalized = crime_counts_heatmap.div(crime_counts_heatmap.max(axis=0), axis=1).fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=df_normalized.values,
        x=crime_counts_heatmap.columns,
        y=crime_counts_heatmap.index,
        colorscale='Purples',
        hoverongaps=False,
        customdata=crime_counts_heatmap.values,
        hovertemplate='<b>%{x}</b><br>%{y}<br>Ocorrências: %{customdata}<extra></extra>'
    ))
    fig.update_layout(title="Concentração de Crimes por Faixa Etária (Normalizado por Tipo de Crime)",
                      xaxis_title="Tipo de Crime", yaxis_title="Faixa Etária da Vítima")
    return fig


def plot_efetividade_denuncia(df_efetividade):
    """Gera o gráfico de dispersão para a efetividade da denúncia."""
    fig = px.scatter(df_efetividade, x='taxa_crimes_leves', y='taxa_crimes_graves', hover_name='municipio',
                     hover_data={'total_crimes_leves': ':.0f', 'total_crimes_graves': ':.0f',
                                 'populacao_feminina': ':.0f', 'municipio': False},
                     trendline="ols",
                     labels={'taxa_crimes_leves': 'Taxa de Crimes Leves (por 1.000 mulheres)',
                             'taxa_crimes_graves': 'Taxa de Crimes Graves (por 1.000 mulheres)'},
                     title="Efetividade da Denúncia: Crimes Leves vs. Graves por Município")
    fig.update_traces(marker=dict(size=10, opacity=0.7, color='#8e24aa'))
    return fig


def plot_barras_sazonal(df_medias):
    """Gera o gráfico de barras para a análise sazonal."""
    fig = px.bar(df_medias, x='Tipo de Dia', y='Média Diária de Ocorrências', text='Média Diária de Ocorrências',
                 title="Média de Ocorrências por Tipo de Dia",
                 labels={'Média Diária de Ocorrências': 'Média de Ocorrências por Dia', 'Tipo de Dia': ''},
                 template='plotly_white')
    fig.update_traces(marker_color='#8e24aa', texttemplate='%{text:.2f}', textposition='outside')
    return fig


def plot_heatmap_sazonal(heatmap_pivot):
    """Gera o heatmap para a análise sazonal."""
    fig = go.Figure(data=go.Heatmap(z=heatmap_pivot.values, x=heatmap_pivot.columns, y=heatmap_pivot.index,
                                    colorscale='Purples', hoverongaps=False, text=heatmap_pivot.values,
                                    texttemplate="%{text:.2f}"))
    fig.update_layout(title="Concentração Média de Ocorrências por Mês e Dia da Semana",
                      xaxis_title="Dia da Semana", yaxis_title="Mês",
                      xaxis={'type': 'category'},
                      yaxis={'type': 'category', 'categoryorder': 'array',
                             'categoryarray': list(heatmap_pivot.index)})
    return fig


def plot_barras_feriados(df_feriados):
    """Gera o gráfico de barras para os feriados com mais ocorrências."""
    fig = px.bar(df_feriados, x='nome_feriado', y='total_ocorrencias',
                 title="Ocorrências por Feriado",
                 labels={'nome_feriado': 'Feriado', 'total_ocorrencias': 'Quantidade de Ocorrências'},
                 template='plotly_white', text='total_ocorrencias')
    fig.update_traces(marker_color='#8e24aa', textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    return fig
