import streamlit as st
import pandas as pd
import os
import unicodedata

# 1. Configuração da Página e Estilo Moderno (CSS)
st.set_page_config(page_title="My Scent Collection", layout="wide", page_icon="👃")

st.markdown("""
    <style>
    /* Cor de fundo e fonte geral */
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilo dos Cards de Estatísticas */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #6c757d;
    }
    /* Título mais fino e moderno */
    .main-title {
        color: #2c3e50;
        font-weight: 300;
        letter-spacing: 1px;
        margin-bottom: 30px;
    }
    /* Ajuste de tabelas */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "perfumes_data.csv"

# --- FUNÇÕES DE SUPORTE ---
def remover_acentos(texto):
    if not isinstance(texto, str): return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Categoria' in df.columns: df = df.rename(columns={'Categoria': 'Estações'})
            return df
        except:
            return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])
    return pd.DataFrame()

df = load_data()

# --- TÍTULO ---
st.markdown("<h2 class='main-title'>👃 Minha Caixa de Perfumes</h2>", unsafe_allow_html=True)

# --- SIDEBAR MODERNA ---
st.sidebar.header("📜 Menu")
menu = ["🔍 Explorar", "➕ Adicionar", "⚙️ Gerir"]
choice = st.sidebar.radio("", menu)

if choice == "🔍 Explorar":
    # --- DASHBOARD DE ESTATÍSTICAS ---
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-card'><h3>{len(df)}</h3><p>Frascos</p></div>", unsafe_allow_html=True)
        with col2:
            marcas = df['Marca'].nunique()
            st.markdown(f"<div class='metric-card'><h3>{marcas}</h3><p>Marcas</p></div>", unsafe_allow_html=True)
        with col3:
            favorita = df['Estações'].mode()[0] if not df['Estações'].empty else "-"
            st.markdown(f"<div class='metric-card'><h3>{favorita}</h3><p>Estação Principal</p></div>", unsafe_allow_html=True)
        with col4:
            ano_mais_antigo = df['Ano'].min() if not df.empty else "-"
            st.markdown(f"<div class='metric-card'><h3>{ano_mais_antigo}</h3><p>Ano Inicial</p></div>", unsafe_allow_html=True)

    st.divider()

    # --- PESQUISA ---
    search = st.text_input("", placeholder="Procure por nota, marca ou nome...", label_visibility="collapsed")
    
    if not df.empty:
        if search:
            search_norm = remover_acentos(search)
            mask = df.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(search_norm)).any(axis=1)
            result = df[mask]
        else:
            result = df
        
        # Mostrar em formato de tabela elegante
        st.dataframe(result, use_container_width=True, hide_index=True)

elif choice == "➕ Adicionar":
    st.markdown("### ➕ Novo Registo")
    with st.container(border=True):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "Geral"])
                nome = st.text_input("Nome do Perfume")
                marca = st.text_input("Marca")
            with c2:
                perf = st.text_input("Perfumista")
                fam = st.text_input("Família Olfativa")
                notas = st.text_area("Notas")
            
            if st.form_submit_button("Guardar na Coleção"):
                if nome:
                    new_row = pd.DataFrame([[est, nome, "", marca, perf, fam, notas]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Perfume guardado com sucesso!")
                    st.rerun()

elif choice == "⚙️ Gerir":
    tab1, tab2 = st.tabs(["📝 Editar", "🗑️ Apagar"])
    
    with tab1:
        if not df.empty:
            perfume_sel = st.selectbox("Escolha para editar:", df["Nome do Perfume"].tolist())
            index = df[df["Nome do Perfume"] == perfume_sel].index[0]
            with st.form("edit_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_est = st.text_input("Estação", value=df.at[index, "Estações"])
                    new_nome = st.text_input("Nome", value=df.at[index, "Nome do Perfume"])
                with col_e2:
                    new_notas = st.text_area("Notas", value=df.at[index, "Notas Olfativas"])
                if st.form_submit_button("Atualizar Alterações"):
                    df.at[index, "Estações"] = new_est
                    df.at[index, "Nome do Perfume"] = new_nome
                    df.at[index, "Notas Olfativas"] = new_notas
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Atualizado!")
                    st.rerun()

    with tab2:
        if not df.empty:
            perfume_del = st.selectbox("Escolha para remover:", df["Nome do Perfume"].tolist())
            if st.button("❌ Confirmar Eliminação"):
                df = df[df["Nome do Perfume"] != perfume_del]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.warning("Removido.")
                st.rerun()
                    
