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
    cols = ["Estações", "Nome do Perfume", "Ano", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Categoria' in df.columns:
                df = df.rename(columns={'Categoria': 'Estações'})
            # Garante que todas as colunas existem
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# --- INTERFACE ---
st.markdown("<h2 style='text-align: left; font-size: 32px;'>Caixa de Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("Pesquisar notas ou marcas (ex: 'baunilha ambar')")
    
    if not df.empty:
        if search:
            termos = search.split()
            result = df.copy()
            for termo in termos:
                termo_norm = remover_acentos(termo)
                mask = result.astype(str).apply(
                    lambda col: col.map(remover_acentos).str.contains(termo_norm)
                ).any(axis=1)
                result = result[mask]
        else:
            result = df
            
        st.write(f"Encontrados {len(result)} perfumes.")
        
        # --- CORREÇÃO PARA O ERRO DE TIPO (API EXCEPTION) ---
        # 1. Convertemos toda a tabela para String para evitar erros de compatibilidade
        # 2. Preenchemos valores vazios com texto vazio ""
        result_display = result.fillna("").astype(str).reset_index(drop=True)
        
        # Usamos o dataframe simples se o data_editor continuar a dar erro no Python 3.14
        try:
            st.data_editor(
                result_display, 
                use_container_width=True, 
                hide_index=True,
                disabled=True, 
                key="editor_fix",
                column_config={
                    "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width="large")
                }
            )
        except:
            # Caso o data_editor falhe pela versão do Python, usamos o dataframe normal
            st.dataframe(result_display, use_container_width=True, hide_index=True)
        
        st.info("💡 Dica: Clique duas vezes numa célula para copiar o texto.")
        
        if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados", csv, "pesquisa.csv", "text/csv")

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

# --- ABA EDITAR ---
elif choice == "📝 Editar":
    st.subheader("Editar Perfume")
    if not df.empty:
        nomes_unicos = sorted(df["Nome do Perfume"].unique().tolist())
        perfume_sel = st.selectbox("Escolha o perfume:", nomes_unicos)
        idx = df[df["Nome do Perfume"] == perfume_sel].index[0]
        
        with st.form("edit_total"):
            c1, c2 = st.columns(2)
            with c1:
                e_est = st.text_input("Estação", value=str(df.loc[idx, "Estações"]))
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
            with c2:
                e_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_notas = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            
            if st.form_submit_button("Atualizar"):
                df.loc[idx, ["Estações", "Nome do Perfume", "Marca", "Perfumista", "Família Olfativa", "Notas Olfativas"]] = [e_est, e_nome, e_marca, e_perf, e_fam, e_notas]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!")
                st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Remover Perfume")
    if not df.empty:
        p_del = st.selectbox("Escolha para apagar:", df["Nome do Perfume"].unique().tolist())
        if st.button("❌ Confirmar"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Removido.")
            st.rerun()
                
