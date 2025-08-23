import streamlit as st
import pandas as pd
import pygsheets
import json
from datetime import datetime

# Configura a página com largura total
st.set_page_config(page_title="Sistema de Laudos", layout="wide")

# === CABEÇALHO COM LOGO E TÍTULO ===
col1, col2 = st.columns([0.15, 0.85])  # ajuste a proporção conforme necessário

with col1:
    # Substitua pelo caminho do arquivo local ou pela URL da logo
    st.image("HUGO.png", width=80)

with col2:
    st.title("SISTEMA DE LAUDOS ON-LINE")
    st.write("HUGO GURGEL")

# === AUTENTICAÇÃO COM GOOGLE SHEETS ===
with open("/tmp/cred.json", "w") as f:
    credentials_dict = {k: str(v) for k, v in st.secrets["gcp_service_account"].items()}
    json.dump(credentials_dict, f)

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
coluna_exame = "TIPO DE EXAME"

if coluna_data in df.columns:
    try:
        # Converte a coluna de datas
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce', dayfirst=True)
        df = df.dropna(subset=[coluna_data])

        # Intervalo mínimo e máximo
        data_min = df[coluna_data].min()
        data_max = df[coluna_data].max()

        # Seletores de data
        data_inicial = st.date_input("Data inicial", value=data_min.date(), format="DD/MM/YYYY")
        data_final = st.date_input("Data final", value=data_max.date(), format="DD/MM/YYYY")

        # --- FILTRO POR DATA ---
        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicial)) &
            (df[coluna_data] <= pd.to_datetime(data_final))
        ].copy()

        # --- FILTRO POR TIPO DE EXAME ---
        if coluna_exame in df.columns:
            exames_disponiveis = ["ECG", "MAPA", "HOLTER"]
            exames_selecionados = st.multiselect(
                "Selecione o(s) exame(s):",
                options=exames_disponiveis,
                default=exames_disponiveis
            )

            if exames_selecionados:
                df_filtrado = df_filtrado[df_filtrado[coluna_exame].isin(exames_selecionados)]

        # Formata a coluna de data
        df_filtrado[coluna_data] = df_filtrado[coluna_data].dt.strftime("%d/%m/%Y")

    except Exception as e:
        st.error(f"Erro ao processar datas: {e}")
        df_filtrado = df.copy()
else:
    st.warning(f"A coluna '{coluna_data}' não foi encontrada.")
    df_filtrado = df.copy()

# Exibe resultado
st.dataframe(df_filtrado.style.hide(axis="index"), height=800)


