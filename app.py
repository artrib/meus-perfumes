import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# =========================================================
# GESTÃO DE ESTADO (Para Edição Direta)
# =========================================================
if "edit_perfume" not in st.session_state:
    st.session_state.edit_perfume = None

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Gestão de Perfumes",
    layout="wide",
    page_icon="👃"
)

# =========================================================
# CSS PERSONALIZADO
# =========================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 1rem !important;
}
*:focus,
[data-baseweb="input"] > div:focus-within,
[data-testid="stDataEditor"] *:focus {
    outline: none !important;
    border-color: #dcdcdc !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stRadio label p {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #4F709C !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES
# =========================================================

DB_FILE = "perfumes_data.csv"

ESTACOES_LISTA = [
    "COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", 
    "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "GERAL"
]

OCASIOES_OPCOES = [
    "CASUAL DIA", "CASUAL NOITE", "TRABALHO", 
    "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"
]

# =========================================================
# FUNÇÕES DE TRATAMENTO DE TEXTO
# =========================================================

def remover_acentos(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    return "".join(
        c for c in unicodedata
    
