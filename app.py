import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Gestão de Perfumes",
    page_icon="👃",
    layout="wide"
)

# =========================================================
# ESTILO
# =========================================================

st.markdown("""
<style>

/* Espaçamento superior */
.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}

/* Remover outline vermelho */
*:focus,
[data-baseweb="input"] > div:focus-within,
[data-testid="stDataEditor"] *:focus {
    outline: none !important;
    border-color: #dcdcdc !important;
    box-shadow: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] .stRadio label p {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #4F709C !important;
}

/* Título */
.main-title {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES
# =========================================================

DB_FILE = "perfumes_data.csv"

COLUNAS = [
    "Ano",
    "Nome do Perfume",
    "Estações do Ano",
    "Ocasiões de Uso",
    "Família Olfativa",
    "Notas Olfativas",
    "Marca",
    "Perfumista"
]

ESTACOES = [
    "COLÓNIAS",
    "PRIMAVERA",
    "VERÃO",
    "PRI/VER",
    "OUTONO",
    "INVERNO",
    "OUT/INV",
    "MEIA-ESTAÇÃO",
    "GERAL"
]

OCASIOES = [
    "CASUAL DIA",
    "CASUAL NOITE",
    "TRABALHO",
    "FORMAL DIA",
    "FORMAL NOITE",
    "ESPECIAL"
]

PALETA = [
    "#8EACCD",
    "#94A684",
    "#B0A695",
    "#C08261",
    "#607274",
    "#E5BA73"
]

CORES_FAMILIA = {
    "Cítrico aromático": "#94A684",
    "Aromático fougère": "#8EACCD"
}

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def remover_acentos(texto):
    """
    Remove acentos e converte para minúsculas.
    """

    if pd.isna(texto):
        return ""

    texto = str(texto)

    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    ).lower()


def garantir_colunas(df):
    """
    Garante que todas as colunas obrigatórias existem.
    """

    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = ""

    return df[COLUNAS]


def carregar_dados():
    """
    Carrega a base de dados CSV.
    """

    if not os.path.exists
