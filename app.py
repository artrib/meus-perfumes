import streamlit as st
import pandas as pd
import os
import unicodedata

# 1. Configuração de Layout
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

DB_FILE = "perfumes_data.csv"

# --- FUNÇÕES DE SUPORTE ---
def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

def load_data():
    df_empty = pd.DataFrame(columns=["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"])
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Categoria' in df.columns:
                df = df.rename(columns={'Categoria': 'Estações'})
            for col in df_empty.columns:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return df_empty
    return df_empty

df = load_data()

# --- INTERFACE ---
st.markdown("<h2 style='text-align: left; font-size: 32px;'>Caixa de Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- ABA PESQUISAR (COM SUPORTE A MÚLTIPLAS NOTAS) ---
if choice == "🔍 Pesquisar":
    search = st.text_input("Pesquisar (ex: 'baunilha ambar' para encontrar ambos)")
    
    if not df.empty:
        if search:
            # Separa os termos por espaço para pesquisa simultânea
            termos = search.split()
            result = df.copy()
            
            for termo in termos:
                termo_norm = remover_acentos(termo)
                # Filtra a tabela sucessivamente para cada palavra
                mask = result.astype(str).apply(
                    lambda col: col.map(remover_acentos).str.contains(termo_norm)
                ).any(axis=1)
                result = result[mask]
        else:
            result = df
            
        st.write(f"Encontrados {len(result)} perfumes.")
        st.dataframe(result, use_container_width=True, hide_index=True)

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "INVERNO", "MEIA-ESTAÇÃO", "GERAL"])
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

# --- ABA EDITAR (LÓGICA SEGURA .LOC) ---
elif choice == "📝 Editar":
    st.subheader("Editar Perfume")
    if not df.empty:
        perfume_sel = st.selectbox("Escolha o perfume para editar:", df["Nome do Perfume"].unique())
        idx = df[df["Nome do Perfume"] == perfume_sel].index[0]
        
        with st.form("edit_form_total"):
            c1, c2 = st.columns(2)
            with c1:
                new_est = st.text_input("Estação", value=str(df.loc[idx, "Estações"]))
                new_nome = st.text_input("Nome do Perfume", value=str(df.loc[idx, "Nome do Perfume"]))
                new_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
            with c2:
                new_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                new_fam = st.text_input("Família Olfativa", value=str(df.loc[idx, "Família Olfativa"]))
                new_notas = st.text_area("Notas Olfativas", value=str(df.loc[idx, "Notas Olfativas"]))
            
            if st.form_submit_button("Atualizar Todos os Campos"):
                df.loc[idx, "Estações"] = new_est
                df.loc[idx, "Nome do Perfume"] = new_nome
                df.loc[idx, "Marca"] = new_marca
                df.loc[idx, "Perfumista"] = new_perf
                df.loc[idx, "Família Olfativa"] = new_fam
                df.loc[idx, "Notas Olfativas"] = new_notas
                
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ Dados de '{new_nome}' atualizados!")
                st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Remover Perfume")
    if not df.empty:
        perfume_del = st.selectbox("Escolha o perfume para APAGAR:", df["Nome do Perfume"].tolist())
        if st.button("❌ Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != perfume_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning(f"'{perfume_del}' foi removido.")
            st.rerun()
                    
