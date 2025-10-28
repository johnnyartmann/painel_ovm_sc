import streamlit as st
import pandas as pd
import plotly.express as px
import json
import unicodedata # Biblioteca para normalizar texto (remover acentos)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Observatório da Violência Contra a Mulher - SC",
    page_icon="💜",
    layout="wide"
)

# --- NOVA FUNÇÃO AUXILIAR PARA NORMALIZAR TEXTO ---
def normalizar_nome(nome):
    """Remove acentos, caracteres especiais e converte para maiúsculo."""
    if isinstance(nome, str):
        nfkd_form = unicodedata.normalize('NFD', nome)
        nome_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return nome_sem_acento.upper().strip()
    return nome

# --- FUNÇÕES PARA CARREGAR OS DADOS ---

@st.cache_data
def carregar_geojson_sc():
    """Carrega o GeoJSON e adiciona uma chave normalizada para o nome do município."""
    try:
        with open('data/municipios_sc.json', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Cria uma nova propriedade normalizada dentro do GeoJSON para garantir a correspondência
        for feature in geojson_data['features']:
            nome_original = feature['properties'].get('NM_MUN') # .get() é mais seguro
            if nome_original:
                feature['properties']['NM_MUN_NORMALIZADO'] = normalizar_nome(nome_original)
            
        return geojson_data
    except FileNotFoundError:
        st.error("Arquivo 'municipios_sc.json' não encontrado na pasta 'data'.")
        return None

@st.cache_data
def carregar_dados_gerais():
    """
    Carrega e trata os dados da base geral, normalizando nomes de municípios.
    """
    try:
        df = pd.read_excel('data/base_geral.xlsx')

        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False))

        df.rename(columns={
            'data_do_fato': 'data_fato', 'município': 'municipio',
            'mesoregião': 'mesoregiao', 'fato_comunicado': 'fato_comunicado', 'idade': 'idade_vitima'
        }, inplace=True)

        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        
        # Cria uma nova coluna com o nome do município normalizado
        if 'municipio' in df.columns:
            df['municipio_normalizado'] = df['municipio'].apply(normalizar_nome)
        
        df['ano'] = df['data_fato'].dt.year
        df['mes'] = df['data_fato'].dt.month_name()
        
        return df
        
    except FileNotFoundError:
        st.error("Arquivo 'base_geral.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base geral: A coluna {e} não foi encontrada.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_feminicidio():
    """
    Carrega e trata os dados da base de feminicídio de forma robusta.
    """
    try:
        df = pd.read_excel('data/base_feminicidio.xlsx')
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_', regex=False).str.replace('ã', 'a', regex=False)
                      .str.replace('ç', 'c', regex=False).str.replace('ú', 'u', regex=False)
                      .str.replace('ô', 'o', regex=False))
        df.rename(columns={
            'relacao_com_o_autor': 'relacao_autor', 'município': 'municipio', 'idade_autor': 'idade_autor',
            'prisão': 'autor_preso', 'idade_vitima': 'idade_vitima', 'meio': 'meio_crime'
        }, inplace=True)
        if 'data' in df.columns: df.rename(columns={'data':'data_fato'}, inplace=True)
        df['data_fato'] = pd.to_datetime(df['data_fato'])
        df['idade_vitima'] = pd.to_numeric(df['idade_vitima'], errors='coerce')
        df['idade_autor'] = pd.to_numeric(df['idade_autor'], errors='coerce')
        df['ano'] = df['data_fato'].dt.year
        return df
    except FileNotFoundError:
        st.error("Arquivo 'base_feminicidio.xlsx' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Erro de Chave (KeyError) na base de feminicídio: A coluna {e} não foi encontrada.")
        st.write("Colunas encontradas após limpeza:", df.columns.tolist())
        return pd.DataFrame()

# Carregar os dados
geojson_sc = carregar_geojson_sc()
df_geral = carregar_dados_gerais()
df_feminicidio = carregar_dados_feminicidio()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://i.imgur.com/805nJ3j.png", width=80)
st.sidebar.title("Observatório da Violência Contra a Mulher")

# --- ESTRUTURA COM ABAS (TABS) ---
tab_geral, tab_feminicidio, tab_glossario = st.tabs([
    "📊 Análise Geral da Violência", "🚨 Análise de Feminicídios", "📖 Metodologia e Glossário"
])

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
if not df_geral.empty and not df_feminicidio.empty and geojson_sc is not None:
    st.sidebar.header("Filtros")
    anos_disponiveis = sorted(df_geral['ano'].unique())
    ano_selecionado = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)
    
    meses_disponiveis = sorted(df_geral['mes'].unique(), key=lambda m: list(pd.to_datetime(df_geral['data_fato']).dt.month).index(list(df_geral[df_geral['mes'] == m]['data_fato'])[0].month))
    mes_selecionado = st.sidebar.multiselect("Selecione o Mês", options=meses_disponiveis, default=meses_disponiveis)
    
    municipios_disponiveis = sorted(df_geral['municipio'].unique())
    municipio_selecionado = st.sidebar.multiselect("Selecione o Município", options=municipios_disponiveis, default=municipios_disponiveis)

    mesoregioes_disponiveis = sorted(df_geral['mesoregiao'].unique())
    mesoregiao_selecionado = st.sidebar.multiselect("Selecione a Mesoregião", options=mesoregioes_disponiveis, default=mesoregioes_disponiveis)
    
    idades_disponiveis = sorted(df_geral['idade_vitima'].dropna().unique())
    idade_selecionada = st.sidebar.slider("Selecione a Faixa Etária", 
                                          min_value=int(idades_disponiveis[0]), 
                                          max_value=int(idades_disponiveis[-1]), 
                                          value=(int(idades_disponiveis[0]), int(idades_disponiveis[-1])))

    fatos_disponiveis = sorted(df_geral['fato_comunicado'].unique())
    fato_selecionado = st.sidebar.multiselect("Selecione o Tipo de Crime", options=fatos_disponiveis, default=fatos_disponiveis)

    df_geral_filtrado = df_geral[
        (df_geral['ano'].isin(ano_selecionado)) & 
        (df_geral['fato_comunicado'].isin(fato_selecionado)) &
        (df_geral['mes'].isin(mes_selecionado)) &
        (df_geral['municipio'].isin(municipio_selecionado)) &
        (df_geral['mesoregiao'].isin(mesoregiao_selecionado)) &
        (df_geral['idade_vitima'] >= idade_selecionada[0]) & (df_geral['idade_vitima'] <= idade_selecionada[1])
    ]
    df_feminicidio_filtrado = df_feminicidio[df_feminicidio['ano'].isin(ano_selecionado)]

    # --- ABA 1: ANÁLISE GERAL ---
    with tab_geral:
        st.header("Violência Contra a Mulher em Santa Catarina")
        st.markdown("Visão geral dos registros de ocorrências.")

        total_registros = df_geral_filtrado.shape[0]
        media_idade_vitima = 0.0
        if not df_geral_filtrado.empty and df_geral_filtrado['idade_vitima'].notna().any():
            media_idade_vitima = df_geral_filtrado['idade_vitima'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total de Registros de Crime", value=f"{total_registros:,}".replace(",", "."))
        with col2:
            st.metric(label="Idade Média da Vítima", value=f"{media_idade_vitima:.1f} anos")
        st.markdown("---")

        st.subheader("Distribuição de Crimes por Município")
        crimes_por_municipio = df_geral_filtrado['municipio_normalizado'].value_counts().reset_index()
        crimes_por_municipio.columns = ['municipio_normalizado', 'quantidade']
        
        fig_mapa = px.choropleth_mapbox(
            crimes_por_municipio, geojson=geojson_sc, locations='municipio_normalizado',
            featureidkey="properties.NM_MUN_NORMALIZADO", color='quantidade',
            color_continuous_scale="Purples", mapbox_style="carto-positron",
            zoom=6, center={"lat": -27.59, "lon": -50.52}, opacity=0.7,
            labels={'quantidade': 'Quantidade de Registros'}
        )
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa, use_container_width=True)
        st.markdown("---")

        st.subheader("Evolução dos Registros de Ocorrências (Série Temporal)")
        df_temporal = df_geral_filtrado.copy()
        df_temporal['ano_mes'] = df_temporal['data_fato'].dt.to_period('M').astype(str)
        registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values('ano_mes')
        fig_temporal = px.line(
            registros_por_mes_ano, x='ano_mes', y='quantidade',
            labels={'ano_mes': 'Mês/Ano', 'quantidade': 'Quantidade de Registros'},
            template='plotly_white', markers=True
        )
        fig_temporal.update_traces(line_color='#8A2BE2')
        st.plotly_chart(fig_temporal, use_container_width=True)
        st.markdown("---")

        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader("Registros de Ocorrências por Ano")
            registros_por_ano = df_geral_filtrado['ano'].value_counts().sort_index()
            fig_ano = px.bar(
                registros_por_ano, x=registros_por_ano.index, y=registros_por_ano.values,
                labels={'x': 'Ano', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_ano.values
            )
            fig_ano.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_ano, use_container_width=True)

        with col_graf2:
            st.subheader("Tipos de Crimes Mais Frequentes")
            registros_por_fato = df_geral_filtrado['fato_comunicado'].value_counts()
            fig_fato = px.bar(
                registros_por_fato, x=registros_por_fato.values, y=registros_por_fato.index, orientation='h',
                labels={'x': 'Quantidade', 'y': 'Tipo de Crime'}, template='plotly_white', text=registros_por_fato.values
            )
            fig_fato.update_traces(marker_color='#9370DB', textposition='auto')
            fig_fato.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_fato, use_container_width=True)

        st.markdown("---")
        
        col_graf3, col_graf4 = st.columns(2)
        with col_graf3:
            st.subheader("Distribuição por Faixa Etária da Vítima")
            df_faixa_etaria = df_geral_filtrado.dropna(subset=['idade_vitima'])
            bins = [0, 17, 24, 34, 44, 59, 120]
            labels = ['0-17 anos', '18-24 anos', '25-34 anos', '35-44 anos', '45-59 anos', '60+ anos']
            df_faixa_etaria['faixa_etaria'] = pd.cut(df_faixa_etaria['idade_vitima'], bins=bins, labels=labels, right=True)
            registros_por_faixa = df_faixa_etaria['faixa_etaria'].value_counts().sort_index()
            fig_faixa_etaria = px.bar(
                registros_por_faixa, x=registros_por_faixa.index, y=registros_por_faixa.values,
                labels={'x': 'Faixa Etária', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_faixa.values
            )
            fig_faixa_etaria.update_traces(marker_color='#9370DB', textposition='outside')
            st.plotly_chart(fig_faixa_etaria, use_container_width=True)
        with col_graf4:
            st.subheader("Distribuição de Ocorrências por Mês")
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            df_geral_filtrado['mes_cat'] = pd.Categorical(df_geral_filtrado['mes'], categories=meses_ordem, ordered=True)
            registros_por_mes = df_geral_filtrado['mes_cat'].value_counts().sort_index()
            nomes_meses_pt = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
            registros_por_mes.index = registros_por_mes.index.map(nomes_meses_pt)
            fig_mes = px.pie(
                values=registros_por_mes.values, names=registros_por_mes.index, hole=.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_mes.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_mes, use_container_width=True)
        
        st.markdown("---")

        st.subheader("Distribuição de Ocorrências por Dia da Semana")
        df_geral_filtrado['dia_semana'] = df_geral_filtrado['data_fato'].dt.day_name()
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_geral_filtrado['dia_semana_cat'] = pd.Categorical(df_geral_filtrado['dia_semana'], categories=dias_ordem, ordered=True)
        registros_por_dia = df_geral_filtrado['dia_semana_cat'].value_counts().sort_index()
        nomes_dias_pt = {'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        registros_por_dia.index = registros_por_dia.index.map(nomes_dias_pt)
        fig_dia_semana = px.bar(
            registros_por_dia, x=registros_por_dia.index, y=registros_por_dia.values,
            labels={'x': 'Dia da Semana', 'y': 'Quantidade'}, template='plotly_white', text=registros_por_dia.values
        )
        fig_dia_semana.update_traces(marker_color='#8A2BE2', textposition='outside')
        st.plotly_chart(fig_dia_semana, use_container_width=True)


    # --- ABA 2: ANÁLISE DE FEMINICÍDIOS ---
    with tab_feminicidio:
        st.header("Análise de Feminicídios Consumados")
        st.markdown("Indicadores específicos sobre os crimes de feminicídio no estado.")
        total_feminicidios = df_feminicidio_filtrado.shape[0]
        idade_media_vitima_fem = df_feminicidio_filtrado['idade_vitima'].mean()
        idade_media_autor_fem = df_feminicidio_filtrado['idade_autor'].mean()
        texto_idade_vitima = f"{idade_media_vitima_fem:.1f} anos" if not pd.isna(idade_media_vitima_fem) else "Dados Insuficientes"
        texto_idade_autor = f"{idade_media_autor_fem:.1f} anos" if not pd.isna(idade_media_autor_fem) else "Dados Insuficientes"
        col1_fem, col2_fem, col3_fem = st.columns(3)
        with col1_fem:
            st.metric(label="Total de Feminicídios", value=total_feminicidios)
        with col2_fem:
            st.metric(label="Idade Média da Vítima", value=texto_idade_vitima)
        with col3_fem:
            st.metric(label="Idade Média do Autor", value=texto_idade_autor)
        st.markdown("---")
        col_graf_fem1, col_graf_fem2 = st.columns(2)
        with col_graf_fem1:
            st.subheader("Vínculo entre a Vítima e o Autor")
            vinculo_autor = df_feminicidio_filtrado['relacao_autor'].value_counts()
            fig_vinculo = px.pie(
                values=vinculo_autor.values, names=vinculo_autor.index, hole=.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            st.plotly_chart(fig_vinculo, use_container_width=True)
        with col_graf_fem2:
            st.subheader("Meio Utilizado para o Crime")
            meio_crime = df_feminicidio_filtrado['meio_crime'].value_counts()
            fig_meio = px.bar(
                meio_crime, x=meio_crime.index, y=meio_crime.values,
                labels={'x': 'Meio Utilizado', 'y': 'Quantidade'}, template='plotly_white', text=meio_crime.values
            )
            fig_meio.update_traces(marker_color='#8A2BE2', textposition='outside')
            st.plotly_chart(fig_meio, use_container_width=True)

else:
    with tab_geral:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx`, `base_feminicidio.xlsx` e `municipios_sc.json` existem na pasta `data`.")
    with tab_feminicidio:
        st.error("🚨 Dados não carregados. Verifique os arquivos em `data/`.")
        st.warning("Certifique-se de que os arquivos `base_geral.xlsx` e `base_feminicidio.xlsx` existem na pasta `data`.")

# --- ABA 3: GLOSSÁRIO (Sempre visível) ---
with tab_glossario:
    st.header("Metodologia e Glossário")
    st.subheader("Metodologia")
    st.markdown("""
    Os dados que constam neste painel foram fornecidos pela Gerência de Estatística e Análise Criminal da Secretaria de Estado da Segurança Pública - GEAC | DINE | SSP | SC.
    Eles foram organizados e processados para possibilitar clareza no entendimento das informações e permitir a interação dos usuários.
    A elaboração do painel é uma parceria entre o Observatório da Violência Contra a Mulher (OVM/SC) e o Ministério Público de Contas de Santa Catarina (MPC/SC).
    """)
    st.subheader("Glossário de Tipos de Crimes")
    st.markdown("""
    - **Ameaça:** Ameaçar alguém, por palavra, escrito ou gesto, ou qualquer outro meio simbólico, de causar-lhe mal injusto e grave.
    - **Lesão Corporal Dolosa:** A lesão corporal caracteriza-se por ofender a integridade corporal ou a saúde de outrem. O crime doloso ocorre quando o agente quis o resultado ou assumiu o risco de produzi-lo.
    - **Estupro:** Constranger alguém, mediante violência ou grave ameaça, a ter conjunção carnal ou a praticar ou permitir que com ele se pratique outro ato libidinoso.
    - **Feminicídio:** Homicídio contra a mulher por razões da condição de sexo feminino. Considera-se que há razões de condição de sexo feminino quando o crime envolve: violência doméstica e familiar ou menosprezo ou discriminação à condição de mulher.
    - **Vias de fato:** São atos agressivos praticados contra alguém, que não cheguem a causar lesão corporal. Exemplos: empurrar, sacudir, puxar cabelo, etc.
    """)
    st.markdown("---")
    st.info("Fonte: Código Penal Brasileiro, Lei do Feminicídio (Lei nº 13.104/2015), Lei Maria da Penha (Lei nº 11.340/2.006).")
