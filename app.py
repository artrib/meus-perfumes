import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, encoding='latin-1', sep=None, engine='python', on_bad_lines='skip')
    return pd.DataFrame(columns=["Categoria", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas"])

df = load_data()

st.title("👃 Base de Dados de Perfumes")

menu = ["🔍 Pesquisar", "➕ Adicionar Novo"]
choice = st.sidebar.radio("Navegação", menu)

if choice == "🔍 Pesquisar":
    st.subheader("O Meu Inventário")
    search = st.text_input("Pesquisar por nome, notas, perfumista ou família...")
    
    filtered_df = df.copy()
    if search:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        filtered_df = filtered_df[mask]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

else:
    st.subheader("Adicionar Novo Perfume")
    with st.form("form_add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            ano = st.text_input("Ano")
        with col2:
            perfumista = st.text_input("Perfumista")
            familia = st.text_input("Família Olfativa")
            notas = st.text_area("Notas Olfativas (Fragrantica/Parfumo)")
        
        submit = st.form_submit_button("Guardar Perfume")
        if submit:
            if nome:
                new_row = pd.DataFrame([{"Categoria": "Geral", "Nome do Perfume": nome, "Ano": ano, "Marca": marca, "Perfumista": perfumista, "Família Olfativa": familia, "Notas": notas}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"'{nome}' guardado!")
                st.rerun()
            else:
                st.error("Nome é obrigatório.")
