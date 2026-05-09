import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Minha Caixa de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            # O motor 'python' com 'on_bad_lines' resolve o problema das vírgulas nos nomes
            df = pd.read_csv(DB_FILE, encoding='latin-1', sep=',', on_bad_lines='skip', engine='python')
            # Garante que a coluna Notas existe para não dar erro na pesquisa
            if 'Notas' not in df.columns:
                df['Notas'] = ""
            return df
        except Exception as e:
            st.error(f"Erro ao ler base de dados: {e}")
            return pd.DataFrame(columns=["Categoria", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas"])
    return pd.DataFrame(columns=["Categoria", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas"])

df = load_data()

st.title("👃 Minha Caixa de Perfumes")

menu = ["🔍 Pesquisar Coleção", "➕ Adicionar Novo"]
choice = st.sidebar.radio("Navegação", menu)

if choice == "🔍 Pesquisar Coleção":
    st.subheader("Consultar Inventário")
    search = st.text_input("Pesquise por Nome, Nota, Perfumista ou Família...", placeholder="Ex: Lavanda, Alberto Morillas, Zara...")
    
    if not df.empty:
        filtered_df = df.copy()
        if search:
            # Pesquisa inteligente em todas as colunas ao mesmo tempo
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        
        st.write(f"Encontrados {len(filtered_df)} perfumes.")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("A base de dados ainda não tem perfumes ou o ficheiro não foi lido.")

else:
    st.subheader("Registar Novo Perfume")
    st.info("Consulte as notas no Fragrantica ou Parfumo para completar o registo.")
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
            notas = st.text_area("Notas Olfativas (Copie do Fragrantica)")
        
        submit = st.form_submit_button("Guardar no Inventário")
        if submit:
            if nome:
                new_row = pd.DataFrame([{"Categoria": cat, "Nome do Perfume": nome, "Ano": ano, "Marca": marca, "Perfumista": perf, "Família Olfativa": fam, "Notas": notas}])
                df = pd.concat([df, new_row], ignore_index=True)
                # Guarda em UTF-8 para evitar problemas futuros de acentuação
                df.to_csv(DB_FILE, index=False, encoding='utf-8')
                st.success(f"'{nome}' adicionado! A página vai atualizar...")
                st.rerun()
            else:
                st.error("O nome do perfume é obrigatório.")
