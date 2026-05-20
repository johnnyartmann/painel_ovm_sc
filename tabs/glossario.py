import streamlit as st

def render():
    try:
        with open("metodologia_glossario.txt", "r", encoding="utf-8") as f:
            texto_metodologia = f.read()
        st.markdown(texto_metodologia, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo 'metodologia_glossario.txt' não encontrado.")
        st.info("Por favor, certifique-se de que o arquivo com a metodologia e o glossário está na mesma pasta que o script principal.")