import streamlit as st
import pandas as pd
import pygsheets
import json
from datetime import datetime

# Configura a página com largura total
st.set_page_config(page_title="Sistema de Laudos", layout="wide")

# Título do app
st.title("SISTEMA DE LAUDOS ON-LINE")
st.write("HUGO GURGEL")

# === AUTENTICAÇÃO COM GOOGLE SHEETS ===
with open("/tmp/cred.json", "w") as f:
    json.dump(st.secrets["gcp_service_account"], f)

credenciais = pygsheets.authorize(service_file="/tmp/cred.json")

# === LEITURA DA PLANILHA GOOGLE SHEETS ===
GOOGLE_SHEETS_ID = '16RO64B3Rp_Tln-9mjbF0N0trGBLTQzEHCe6Zndzsy_E'
arquivo = credenciais.open_by_key(GOOGLE_SHEETS_ID)
aba = arquivo.worksheet_by_title("HUGO GURGEL")

data = aba.get_all_values()
headers = data[0][:7]
conteudo = [linha[:7] for linha in data[1:]]

df = pd.DataFrame(conteudo, columns=headers)
coluna_data = "DATA DO AQUIVO"

if coluna_data in df.columns:
    try:
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce', dayfirst=True)
        df = df.dropna(subset=[coluna_data])

        data_min = df[coluna_data].min()
        data_max = df[coluna_data].max()

        data_inicial = st.date_input("Data inicial", value=data_min.date(), format="DD/MM/YYYY")
        data_final = st.date_input("Data final", value=data_max.date(), format="DD/MM/YYYY")

        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicial)) &
            (df[coluna_data] <= pd.to_datetime(data_final))
        ].copy()

        df_filtrado[coluna_data] = df_filtrado[coluna_data].dt.strftime("%d/%m/%Y")

    except Exception as e:
        st.error(f"Erro ao processar datas: {e}")
        df_filtrado = df.copy()
else:
    st.warning(f"A coluna '{coluna_data}' não foi encontrada.")
    df_filtrado = df.copy()

st.dataframe(df_filtrado.style.hide(axis="index"), height=800)
