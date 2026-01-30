import streamlit as st
import pandas as pd
import pygsheets
import json
import tempfile
import os
from datetime import datetime

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(
    page_title="Sistema de Laudos",
    layout="wide"
)

# ================================
# CABEÇALHO COM LOGO E TÍTULO
# ================================
col1, col2 = st.columns([0.15, 0.85])

with col1:
    st.image("HUGO.png", width=200)

with col2:
    st.title("LAUDOS CLINICA DR HUGO GURGEL")

# ================================
# AUTENTICAÇÃO COM GOOGLE SHEETS
# ================================
try:
    # transforma o secrets em dict normal
    service_account_info = dict(st.secrets["gcp_service_account"])

    # cria arquivo temporário JSON (compatível com Windows)
    fd, cred_path = tempfile.mkstemp(suffix=".json")

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(service_account_info, f)

    # autentica no Google Sheets
    credenciais = pygsheets.authorize(service_file=cred_path)

    # remove o arquivo temporário após autenticar
    os.remove(cred_path)

except Exception as e:
    st.error("Erro na autenticação com Google Sheets.")
    st.stop()

# ================================
# LEITURA DA PLANILHA GOOGLE SHEETS
# ================================
GOOGLE_SHEETS_ID = "16RO64B3Rp_Tln-9mjbF0N0trGBLTQzEHCe6Zndzsy_E"

try:
    arquivo = credenciais.open_by_key(GOOGLE_SHEETS_ID)
    aba = arquivo.worksheet_by_title("HUGO GURGEL")

    data = aba.get_all_values()

    headers = data[0][:7]
    conteudo = [linha[:7] for linha in data[1:]]

    df = pd.DataFrame(conteudo, columns=headers)

except Exception as e:
    st.error(f"Erro ao ler a planilha: {e}")
    st.stop()

# ================================
# FILTROS DE DATA E EXAME
# ================================
coluna_data = "DATA DO AQUIVO"
coluna_exame = "TIPO DE EXAME"

if coluna_data in df.columns:

    try:
        # converte coluna para datetime
        df[coluna_data] = pd.to_datetime(
            df[coluna_data],
            errors="coerce",
            dayfirst=True
        )

        # remove linhas inválidas
        df = df.dropna(subset=[coluna_data])

        # datas mínimas e máximas
        data_min = df[coluna_data].min()
        data_max = df[coluna_data].max()

        # inputs de filtro
        data_inicial = st.date_input(
            "Data inicial",
            value=data_min.date(),
            format="DD/MM/YYYY"
        )

        data_final = st.date_input(
            "Data final",
            value=data_max.date(),
            format="DD/MM/YYYY"
        )

        # aplica filtro
        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicial)) &
            (df[coluna_data] <= pd.to_datetime(data_final))
        ].copy()

        # filtro por exame
        if coluna_exame in df.columns:

            exames_disponiveis = ["ECG", "MAPA", "HOLTER"]

            exames_selecionados = st.multiselect(
                "Selecione o(s) tipos de exame(s):",
                options=exames_disponiveis,
                default=exames_disponiveis
            )

            if exames_selecionados:
                df_filtrado = df_filtrado[
                    df_filtrado[coluna_exame].isin(exames_selecionados)
                ]

        # formata data para exibição
        df_filtrado[coluna_data] = df_filtrado[coluna_data].dt.strftime("%d/%m/%Y")

    except Exception as e:
        st.error(f"Erro ao processar datas: {e}")
        df_filtrado = df.copy()

else:
    st.warning(f"A coluna '{coluna_data}' não foi encontrada.")
    df_filtrado = df.copy()

# ================================
# EXIBIÇÃO FINAL
# ================================
st.dataframe(
    df_filtrado.style.hide(axis="index"),
    height=800
)

