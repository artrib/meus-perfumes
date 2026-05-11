import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO (RESTAURADO)
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

st.markdown("""
    <style>
    /* Ajuste do topo para não cortar o título e manter menu acessível */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* REMOVER CONTORNO VERMELHO EM TODO O APP */
    *:focus, [data-baseweb="input"] > div:focus-within, [data-testid="stDataEditor"] *:focus {
        outline: none !important;
        border-color: #dcdcdc !important;
        box-shadow: none !important;
    }
    
    /* Menu Lateral (Estilo Anterior) */
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #4F709C !important;
    }
    
    /* Centralização Real do Botão */
    .centered-btn {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONSTANTES E BASE DE DADOS
DB_FILE = "perfumes_data.csv"
ESTACOES_LISTA = ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "GERAL"]
OCASIOES_OPCOES = ["CASUAL DIA", "CASUAL NOITE", "TRABALHO", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"]

def remover_acentos(texto):
    if not isinstance(texto, str): return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            return df.fillna("").astype(str)[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# 3. INTERFACE
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar... (Ex: 'Dio Fah')")
    
    result = df.copy()
    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            mask = result.apply(lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(), axis=1)
            result = result[mask]
    
    st.write(f"Total: {len(result)} Perfumes")
    
    if not df.empty:
        st.data_editor(result.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
        
        if not result.empty:
            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:
                csv = result.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']
        
        col1, col2 = st.columns(2)
        with col1:
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip().value_counts().reset_index()
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)
        
        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            c_not = n_s[n_s != ""].value_counts().nlargest(30).reset_index()
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=700, margin=dict(t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            # Alter
