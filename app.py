import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            # utf-8-sig resolve problemas de acentos (como o "ã" de Verão)
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            # Muda o nome da coluna para Estações
            df = df.rename(columns={'Categoria': 'Estações'})
            return df
        except:
            return pd.read_csv(DB_FILE, encoding='latin-1').rename(columns={'Categoria': 'Estações'})
    return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])

df = load_data()

st.title("👃 Minha Caixa de Perfumes")

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("Procurar perfume, nota ou marca...")
    if not df.empty:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        st.dataframe(df[mask] if search else df, use_container_width=True, hide_index=True)

# --- ADICIONAR ---
elif choice == "➕ Adicionar":
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "Geral"])
            nome = st.text_input("Nome *")
            marca = st.text_input("Marca")
        with c2:
            perf = st.text_input("Perfumista")
            fam = st.text_input("Família")
            notas = st.text_area("Notas (Fragrantica/Parfumo)")
        if st.form_submit_button("Guardar"):
            if nome:
                new_row = pd.DataFrame([[est, nome, "", marca, perf, fam, notas]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Adicionado!")
                st.rerun()

# --- EDITAR ---
elif choice == "📝 Editar":
    if not df.empty:
        perfume_sel = st.selectbox("Escolha o perfume para editar:", df["Nome do Perfume"].tolist())
        index = df[df["Nome do Perfume"] == perfume_sel].index[0]
        
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_est = st.text_input("Estação", value=df.at[index, "Estações"])
                new_nome = st.text_input("Nome", value=df.at[index, "Nome do Perfume"])
                new_marca = st.text_input("Marca", value=df.at[index, "Marca"])
            with c2:
                new_perf = st.text_input("Perfumista", value=df.at[index, "Perfumista"])
                new_fam = st.text_input("Família", value=df.at[index, "Família Olfativa"])
                new_notas = st.text_area("Notas", value=df.at[index, "Notas Olfativas"])
            
            if st.form_submit_button("Atualizar Dados"):
                df.at[index, "Estações"] = new_est
                df.at[index, "Nome do Perfume"] = new_nome
                df.at[index, "Marca"] = new_marca
                df.at[index, "Perfumista"] = new_perf
                df.at[index, "Família Olfativa"] = new_fam
                df.at[index, "Notas Olfativas"] = new_notas
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!")
                st.rerun()

# --- APAGAR ---
elif choice == "🗑️ Apagar":
    if not df.empty:
        perfume_del = st.selectbox("Escolha o perfume para APAGAR:", df["Nome do Perfume"].tolist())
        if st.button("❌ Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != perfume_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning(f"'{perfume_del}' foi removido.")
            st.rerun()
            
