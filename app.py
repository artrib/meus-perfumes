import streamlit as st
import pandas as pd
import os
import unicodedata

st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

def load_data():
    if os.path.exists(DB_FILE):
        try:
            # Tenta ler com utf-8-sig para acentos
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Categoria' in df.columns:
                df = df.rename(columns={'Categoria': 'Estações'})
            return df
        except:
            try:
                df = pd.read_csv(DB_FILE, encoding='latin-1').rename(columns={'Categoria': 'Estações'})
                return df
            except:
                return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])
    return pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])

df = load_data()

st.markdown("<h2 style='text-align: left; font-size: 32px;'>Caixa de Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

if choice == "🔍 Pesquisar":
    st.subheader("")
    search = st.text_input("Pesquisar")
    
    if not df.empty:
        if search:
            search_norm = remover_acentos(search)
            mask = df.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(search_norm)).any(axis=1)
            result = df[mask]
        else:
            result = df
        st.write(f"Encontrados {len(result)} perfumes.")
        st.dataframe(result, use_container_width=True, hide_index=True)

elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "Geral"])
            nome = st.text_input("Nome *")
            marca = st.text_input("Marca")
        with c2:
            perf = st.text_input("Perfumista")
            fam = st.text_input("Família")
            notas = st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            if nome:
                new_row = pd.DataFrame([[est, nome, "", marca, perf, fam, notas]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Adicionado!")
                st.rerun()

elif choice == "⚙️ Editar":
    tab1, tab2 = st.tabs(["📝 Editar Perfume", "🗑️ Apagar Perfume"])
    
    with tab1:
        if not df.empty:
            # 1. Selecionar o perfume
            perfume_sel = st.selectbox("Escolha o perfume para editar:", df["Nome do Perfume"].unique())
            
            # 2. Localizar o índice da linha
            idx = df[df["Nome do Perfume"] == perfume_sel].index[0]
            
            with st.form("form_editar_total"):
                st.write(f"A editar: **{perfume_sel}**")
                
                # Criar campos para todos os dados atuais
                col_ed1, col_ed2 = st.columns(2)
                
                with col_ed1:
                    novo_nome = st.text_input("Nome do Perfume", value=str(df.loc[idx, "Nome do Perfume"]))
                    nova_est = st.text_input("Estação (Estações)", value=str(df.loc[idx, "Estações"]))
                    nova_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                
                with col_ed2:
                    novo_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                    nova_fam = st.text_input("Família Olfativa", value=str(df.loc[idx, "Família Olfativa"]))
                    novas_notas = st.text_area("Notas Olfativas", value=str(df.loc[idx, "Notas Olfativas"]))

                if st.form_submit_button("Gravar Alterações"):
                    # ATUALIZAÇÃO SEGURA (Cria uma cópia para evitar o TypeError)
                    df.loc[idx, "Nome do Perfume"] = novo_nome
                    df.loc[idx, "Estações"] = nova_est
                    df.loc[idx, "Marca"] = nova_marca
                    df.loc[idx, "Perfumista"] = novo_perf
                    df.loc[idx, "Família Olfativa"] = nova_fam
                    df.loc[idx, "Notas Olfativas"] = novas_notas
                    
                    # Guardar no ficheiro
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ Todos os campos foram atualizados com sucesso!")
                    st.rerun()
        else:
            st.warning("A lista está vazia, não há nada para editar.")

elif choice == "🗑️ Apagar":
    st.subheader("Remover Perfume")
    if not df.empty:
        perfume_del = st.selectbox("Escolha o perfume para APAGAR:", df["Nome do Perfume"].tolist())
        if st.button("❌ Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != perfume_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning(f"'{perfume_del}' foi removido.")
            st.rerun()
                
