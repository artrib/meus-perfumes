import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def load_data():
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            # Limpa espaços e renomeia com segurança
            df.columns = df.columns.str.strip()
            if 'Categoria' in df.columns:
                df = df.rename(columns={'Categoria': 'Estações'})
            return df
        except:
            # Caso o ficheiro esteja vazio ou corrompido
            return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])
    return pd.DataFrame()

df = load_data()

st.title("Caixa de Perfumes")

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- PESQUISAR ---
# 1. Importe esta biblioteca no topo do arquivo (se não tiver)
import unicodedata

# 2. Função para remover acentos e facilitar a busca
def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

# 3. Na parte da pesquisa, use este bloco:
st.subheader("")
search = st.text_input("Pesquisar (não precisa de acentos ou maiúsculas):")

if not df.empty:
    if search:
        # Normaliza o termo pesquisado pelo usuário
        search_norm = remover_acentos(search)
        
        # Cria uma versão da tabela "sem acentos" apenas para a busca
        mask = df.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(search_norm)).any(axis=1)
        result = df[mask]
    else:
        result = df
        
    st.write(f"Encontrados {len(result)} perfumes.")
    st.dataframe(result, use_container_width=True, hide_index=True)

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
                new_est = st.text_input("Estações", value=df.at[index, "Estações"])
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
            
