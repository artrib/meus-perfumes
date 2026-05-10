import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Caixa de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            # quotechar='"' resolve o erro das vírgulas dentro dos nomes dos perfumistas
            df = pd.read_csv(DB_FILE, encoding='utf-8')
            # Limpar espaços em branco extras nos nomes das colunas
            df.columns = df.columns.str.strip()
            
            # Garantir que a coluna de Notas existe para a pesquisa funcionar
            if 'Notas Olfativas' not in df.columns:
                df['Notas Olfativas'] = ""
            return df
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

st.title("👃 Caixa de Perfumes")

menu = ["🔍 Pesquisar", "➕ Adicionar Novo"]
choice = st.sidebar.radio("Menu", menu)

if choice == "🔍 Pesquisar":
    st.subheader("Consultar Inventário")
    search = st.text_input("Procure por perfume, nota, perfumista ou marca...", placeholder="Ex: Guerlain, Íris, Morillas...")
    
    if not df.empty:
        if search:
            # Pesquisa em todas as colunas ao mesmo tempo
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            result = df[mask]
        else:
            result = df
            
        st.write(f"A mostrar {len(result)} perfumes.")
        st.dataframe(result, use_container_width=True, hide_index=True)
    else:
        st.info("A base de dados está vazia ou o ficheiro não foi carregado corretamente.")

else:
    st.subheader("Adicionar Novo Perfume")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cat = st.text_input("Categoria (Ex: Inverno)")
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            ano = st.text_input("Ano")
        with col2:
            perf = st.text_input("Perfumista")
            fam = st.text_input("Família Olfativa")
            notas = st.text_area("Notas Olfativas (Copie do Fragrantica/Parfumo)")
            
        if st.form_submit_button("Guardar"):
            if nome:
                new_data = pd.DataFrame([[cat, nome, ano, marca, perf, fam, notas]], columns=df.columns)
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8')
                st.success("Guardado com sucesso!")
                st.rerun()
            else:
                st.error("O nome é obrigatório.")
                
