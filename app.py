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
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def padronizar_texto(texto):
    if not texto or not isinstance(texto, str):
        return ""
    texto_limpo = remover_acentos(texto).strip()
    if texto_limpo.endswith('s') and len(texto_limpo) > 4:
        texto_limpo = texto_limpo[:-1]
    return texto_limpo.capitalize()

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
# CARREGAR DADOS
# =========================================================

df = load_data()

# =========================================================
# TÍTULO
# =========================================================

st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
default_index = 2 if st.session_state.edit_perfume else 0
choice = st.sidebar.radio("MENU DE GESTÃO", menu, index=default_index)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == "🔍 Pesquisar":
    col_busca, col_filtro = st.columns([3, 1])
    
    with col_busca:
        search = st.text_input("pesquisa", placeholder="...")
    
    with col_filtro:
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", "Estações do Ano", "Ocasiões de Uso", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca)
        
    result = df.copy()
    result.insert(0, "Editar", False)

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            if local_busca == "Tudo":
                mask = result.apply(lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(), axis=1)
            else:
                mask = result[local_busca].astype(str).map(remover_acentos).str.contains(t_norm)
            result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

    if not df.empty:
        edited_df = st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Editar": st.column_config.CheckboxColumn("", default=False), # Removido o ícone aqui
                "Ano": st.column_config.TextColumn("Ano", width=55),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Marca": st.column_config.TextColumn("Marca", width=120),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=120),
                "Ocasiões de Uso": st.column_config.TextColumn("Ocasiões de Uso", width=120)
            },
            disabled=[c for c in result.columns if c != "Editar"]
        )

        check_click = edited_df[edited_df["Editar"] == True]
        if not check_click.empty:
            st.session_state.edit_perfume = check_click.iloc[0]["Nome do Perfume"]
            st.rerun()

        if not result.empty:
            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:
                csv = result.drop(columns=["Editar"]).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")
    
