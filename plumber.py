
import streamlit as st
import pdfplumber
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title="Extração Arquivo PDF",
    page_icon="📁",
    layout="centered"
)


def extract_data(uploaded_file):
    invoice_no, codigo_pautal, peso_bruto, valor_num, pais_origem = '', '', '', '', ''
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            for line in page.extract_text().splitlines():
                if 'invoice no.' in line.lower():
                    invoice_no = line.split()[2][3:13]
                if '87019' in line.lower():
                    codigo_pautal = line.split()[4]
                if 'gross weight' in line.lower():
                    peso_bruto = line.split()[2]
                if 'engine number' in line.lower():
                    valor = line.split()[-2]
                if 'total amount eur' in line.lower():
                    valor_str = line.split()[-1]
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                    valor_num = float(valor_str)
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'country of origin' in line.lower():
                        if i + 1 < len(lines):
                            pais_origem = lines[i + 1].split()[0]

    data_atual = date.today()
    if data_atual.month == 1:  # Se o mês atual for janeiro, retroceda um ano
        ano_anterior = data_atual.year - 1
        mes_anterior = 12  # Dezembro
    else:
        ano_anterior = data_atual.year
        mes_anterior = data_atual.month - 1

    data_formatada = f"{ano_anterior}{mes_anterior:02}"

    return {
        'Fatura Numero': invoice_no,
        'Codigo Pautal': codigo_pautal,
        'Peso Bruto': peso_bruto,
        'Total': valor_num,
        'Pais Origem': pais_origem,
        'Data': data_formatada
    }

st.title("Upload e Extração de Dados de PDF")

# Upload de múltiplos arquivos PDF
uploaded_files = st.file_uploader("Selecione múltiplos arquivos PDF:page_facing_up:", type=["pdf"], accept_multiple_files=True)

results_list = []

if uploaded_files:
    total_files = len(uploaded_files)
    for i, uploaded_file in enumerate(uploaded_files, start=1):
        st.write(f"Processando arquivo {i} de {total_files}")
        data = extract_data(uploaded_file)
        if data:
            results_list.append(data)

    st.write("Todos os arquivos foram processados!")

if results_list:
    df = pd.DataFrame(results_list)
    st.dataframe(df)

     # Calcular o número total de faturas e o valor total faturado
    num_faturas = len(df)
    valor_total = df['Total'].sum()

    st.write(f"Número Total de Faturas: {num_faturas}")
    st.write(f"Valor Total Faturado: {valor_total:.2f} EUR")

else:
    st.write("Nenhum dado extraído dos PDFs selecionados.")


