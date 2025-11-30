import streamlit as st


def render():
    st.header("Download das Fontes de Dados")
    st.markdown("Faça o download dos arquivos de dados brutos utilizados para a construção deste painel.")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Base Geral de Crimes")
        st.markdown("Registros de violência contra a mulher (exceto feminicídios).")
        try:
            with open("data/base_geral.xlsx", "rb") as fp:
                st.download_button(label="Download (XLSX)", data=fp, file_name="base_geral.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="download_geral")
        except FileNotFoundError:
            st.warning("Arquivo 'base_geral.xlsx' não encontrado.")
    with col2:
        st.subheader("Base de Feminicídios")
        st.markdown("Registros detalhados de feminicídios consumados.")
        try:
            with open("data/base_feminicidio.xlsx", "rb") as fp:
                st.download_button(label="Download (XLSX)", data=fp, file_name="base_feminicidio.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="download_feminicidio")
        except FileNotFoundError:
            st.warning("Arquivo 'base_feminicidio.xlsx' não encontrado.")
    with col3:
        st.subheader("Base Populacional")
        st.markdown("Dados da população feminina por município.")
        try:
            with open("data/base_populacao.xlsx", "rb") as fp:
                st.download_button(label="Download (XLSX)", data=fp, file_name="base_populacao.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="download_populacao")
        except FileNotFoundError:
            st.warning("Arquivo 'base_populacao.xlsx' não encontrado.")
    st.markdown("---")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Base de Regiões")
        st.markdown("Mapeamento de municípios para mesorregiões e associações.")
        try:
            with open("data/base_regioes_associacoes.xlsx", "rb") as fp:
                st.download_button(label="Download (XLSX)", data=fp, file_name="base_regioes_associacoes.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="download_regioes")
        except FileNotFoundError:
            st.warning("Arquivo 'base_regioes_associacoes.xlsx' não encontrado.")
    with col5:
        st.subheader("Base de Calendário")
        st.markdown("Mapeamento de feriados para análise sazonal.")
        try:
            with open("data/base_calendario_feriados.xlsx", "rb") as fp:
                st.download_button(label="Download (XLSX)", data=fp, file_name="base_calendario_feriados.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="download_calendario")
        except FileNotFoundError:
            st.warning("Arquivo 'base_calendario_feriados.xlsx' não encontrado.")
    with col6:
        st.subheader("Mapa de Municípios")
        st.markdown("Arquivo GeoJSON com as geometrias dos municípios de SC.")
        try:
            with open("data/municipios_sc.json", "rb") as fp:
                st.download_button(label="Download (JSON)", data=fp, file_name="municipios_sc.json",
                                   mime="application/json", key="download_geojson")
        except FileNotFoundError:
            st.warning("Arquivo 'municipios_sc.json' não encontrado.")
