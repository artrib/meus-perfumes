import streamlit as st
import pandas as pd
import os
import unicodedata

# 1. Configuração Inicial
st.set_page_config(page_title="My Scent Collection", layout="wide", page_icon="👃")

# CSS para melhorar o visual sem quebrar o layout
st.markdown("""
    <style>
    .stApp {
        background-color: #fcfcfc;
    }
    h1, h2 {
        color: #1e1e1e;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "perfumes_data.csv"

# --- FUNÇÕES ---
def remover_acentos(texto):
    if not isinstance(texto, str): return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            # Garante que as colunas existem para não dar erro branco
            df = df.rename(columns={'Categoria': 'Estações'})
            return df
        except:
            return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])
    return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])

df = load_data()

# --- HEADER ---
st.markdown("<h2 style='text-align: left; margin-bottom: 0px;'>👃 Minha Caixa de Perfumes</h2>", unsafe_allow_html=True)
st.caption("Gestão Inteligente de Fragrâncias")
st.divider()

# --- SIDEBAR ---
menu = ["🔍 Explorar Coleção", "⚙️ Gestão Total"]
choice = st.sidebar.radio("Navegação", menu)

if choice == "🔍 Explorar Coleção":
    # Métrica Simples (Nativa do Streamlit - Mais Segura)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Frascos", len(df))
        m2.metric("Marcas Diferentes", df['Marca'].nunique() if 'Marca' in df.columns else 0)
        m3.metric("Estação Favorita", df['Estações'].mode()[0] if not df['Estações'].empty else "N/A")
    
    st.write("###") # Espaçamento
    
    # Barra de Pesquisa Moderna
    search = st.text_input("Pesquise por qualquer termo (sem preocupar com acentos ou maiúsculas):", placeholder="Ex: Guerlain, Couro, Inverno...")
    
    if not df.empty:
        if search:
            search_norm = remover_acentos(search)
            mask = df.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(search_norm)).any(axis=1)
            result = df[mask]
        else:
            result = df
        
        st.dataframe(result, use_container_width=True, hide_index=True)
    else:
        st.info("A sua coleção ainda está vazia. Comece por adicionar um perfume!")

else:
    # Área de Gestão com Tabs (Moderna)
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar Novo", "📝 Editar", "🗑️ Apagar"])
    
    with tab1:
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "Geral"])
                nome = st.text_input("Nome do Perfume *")
                marca = st.text_input("Marca")
            with c2:
                perf = st.text_input("Perfumista")
                fam = st.text_input("Família Olfativa")
                notas = st.text_area("Notas Olfativas")
            if st.form_submit_button("Adicionar à Prateleira"):
                if nome:
                    new_row = pd.DataFrame([[est, nome, "", marca, perf, fam, notas]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Perfume adicionado!")
                    st.rerun()

    with tab2:
        if not df.empty:
            perfume_sel = st.selectbox("Escolha o perfume para alterar:", df["Nome do Perfume"].tolist())
            idx = df[df["Nome do Perfume"] == perfume_sel].index[0]
            with st.form("edit_f"):
                e_est = st.text_input("Estação", value=str(df.at[idx, "Estações"]))
                e_nome = st.text_input("Nome", value=str(df.at[idx, "Nome do Perfume"]))
                e_notas = st.text_area("Notas", value=str(df.at[idx, "Notas Olfativas"]))
                if st.form_submit_button("Salvar Alterações"):
                    df.at[idx, "Estações"] = e_est
                    df.at[idx, "Nome do Perfume"] = e_nome
                    df.at[idx, "Notas Olfativas"] = e_notas
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Atualizado!")
                    st.rerun()

    with tab3:
        if not df.empty:
            p_del = st.selectbox("Remover perfume permanentemente:", df["Nome do Perfume"].tolist())
            if st.button("Confirmar Eliminação"):
                df = df[df["Nome do Perfume"] != p_del]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.warning(f"'{p_del}' removido.")
                st.rerun()
                
