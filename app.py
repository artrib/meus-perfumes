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
# FUNÇÕES DE TRATAMENTO
# =========================================================

def remover_acentos(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def padronizar_texto(texto):
    """Unifica termos (ex: Cítricos -> Citrico) para os gráficos"""
    if not texto or not isinstance(texto, str):
        return ""
    t = remover_acentos(texto).strip()
    # Unificação simples de plural
    if t.endswith('s') and len(t) > 4:
        t = t[:-1]
    return t.capitalize()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", 
            "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            return df.fillna("").astype(str)[cols]
        except Exception as e:
            st.error(f"Erro ao carregar CSV: {e}")
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# =========================================================
# CARREGAR DADOS E TÍTULO
# =========================================================

df = load_data()

st.markdown(
    "<h2 style='text-align:left; font-size:34px;'>Caixa dos Perfumes</h2>",
    unsafe_allow_html=True
)

# =========================================================
# MENU
# =========================================================

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar...")
    result = df.copy()

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            mask = result.apply(
                lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(),
                axis=1
            )
            result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

    if not df.empty:
        st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "Ano": st.column_config.TextColumn("Ano", width=55),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Marca": st.column_config.TextColumn("Marca", width=120),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=120),
                "Ocasiões de Uso": st.column_config.TextColumn("Ocasiões de Uso", width=120)
            }
        )

        if not result.empty:
            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:
                csv = result.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download (CSV)", csv, "meus_perfumes.csv", "text/csv", use_container_width=True)

        st.markdown("---")

        # CONFIGURAÇÕES VISUAIS
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']

        col1, col2 = st.columns(2)

        # COLUNA 1: ESTAÇÕES E OCASIÕES
        with col1:
            # Estações
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            c_est.columns = ["Estação", "count"]
            
            fig1 = px.bar(c_est, x="Estação", y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            st.write("") # Espaçador

            # Ocasiões
            c_oc = df["Ocasiões de Uso"].str.split
            
