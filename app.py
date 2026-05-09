import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            # Esta configuração ignora erros de vírgulas extras e deteta o formato correto
            return pd.read_csv(DB_FILE, encoding='latin-1', sep=',', on_bad_lines='skip')
        except:
            return pd.read_csv(DB_FILE, encoding='utf-8', sep=',', on_bad_lines='skip')
    return pd.DataFrame(columns=["Categoria", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas"])

df = load_data()

st.title("👃 Minha Caixa de Perfumes")

menu = ["🔍 Pesquisar Coleção", "➕ Adicionar Novo"]
choice = st.sidebar.radio("Navegação", menu)

if choice == "🔍 Pesquisar Coleção":
    st.subheader("Consultar Inventário")
    search = st.text_input("Pesquise por Nome, Nota, Perfumista ou Família...", placeholder="Ex: Alberto Morillas, Citrino, Zara...")
    
    if not df.empty:
        filtered_df = df.copy()
        if search:
            # Pesquisa em todas as colunas de forma segura
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        
        st.write(f"Encontrados {len(filtered_df)} perfumes.")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("A base de dados está vazia ou não foi encontrada.")

else:
    st.subheader("Registar Novo Perfume")
    st.info("Dica: Procure as notas no Fragrantica ou Parfumo antes de preencher.")
    with st.form("form_add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Categoria", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "Geral"])
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            ano = st.text_input("Ano")
        with col2:
            perf = st.text_input("Perfumista")
            fam = st.text_input("Família Olfativa")
            notas = st.text_area("Notas Olfativas (Topo, Coração, Base)")
        
        submit = st.form_submit_button("Guardar Perfume")
        if submit:
            if nome:
                new_row = pd.DataFrame([{"Categoria": cat, "Nome do Perfume": nome, "Ano": ano, "Marca": marca, "Perfumista": perf, "Família Olfativa": fam, "Notas": notas}])
                df = pd.concat([df, new_row], ignore_index=True)
                # Guarda garantindo compatibilidade futura
                df.to_csv(DB_FILE, index=False, encoding='utf-8')
                st.success(f"'{nome}' guardado com sucesso!")
                st.rerun()
            else:
                st.error("O nome do perfume é obrigatório.")
