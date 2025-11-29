import streamlit as st
import pandas as pd
import ita_calc
import io

st.set_page_config(page_title="Calculadora ITA", layout="wide")

st.title("Calculadora de Índice de Trajetória Acadêmica (ITA)")

st.markdown("""
Esta aplicação calcula o ITA com base nas planilhas fornecidas.
Por favor, insira os links públicos (ou acessíveis) das planilhas do Google Sheets.
Certifique-se de que os links terminam com `export?format=xlsx` ou são links diretos para download.
""")

# Default URLs from the notebook for convenience
default_main = "https://docs.google.com/spreadsheets/d/1cpXhYwbhTlIexWjTprVITGAJA8jXMU83/export?format=xlsx"
default_criteria = "https://docs.google.com/spreadsheets/d/1fmyyHKp38u5CM0G3GYa-gbPbvokt4_SZ/export?format=xlsx"
default_form = "https://docs.google.com/spreadsheets/d/1HINITMZMllcojXwgq8gOwt_P6dK6MnOe/export?format=xlsx"

url_main = st.text_input("URL da Planilha Completa", value=default_main)
url_criteria = st.text_input("URL da Planilha de Critérios (Social/Psicologia/Geral)", value=default_criteria)
url_form = st.text_input("URL da Planilha de Formulário", value=default_form)

if st.button("Calcular ITA"):
    if not url_main or not url_criteria or not url_form:
        st.error("Por favor, preencha todos os campos de URL.")
    else:
        with st.spinner("Processando planilhas e calculando ITA..."):
            try:
                df_result = ita_calc.calculate_ita(url_main, url_criteria, url_form)
                
                st.success("Cálculo concluído com sucesso!")
                
                st.subheader("Resultados (Top 50)")
                st.dataframe(df_result.head(50))
                
                # Excel Download
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_result.to_excel(writer, index=False, sheet_name='ITA Calculado')
                
                st.download_button(
                    label="Baixar Planilha Completa (Excel)",
                    data=buffer.getvalue(),
                    file_name="ita_calculado.xlsx",
                    mime="application/vnd.ms-excel"
                )
                
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {e}")
                st.exception(e)
