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
    # --- AQUI VOCÊ ORGANIZA A ORDEM DAS COLUNAS ---
    # Basta mudar a posição dos nomes nesta lista:
    cols = [
        "Nome do Perfume", 
        "Marca", 
        "Estações", 
        "Ocasiões de Uso", 
        "Família Olfativa", 
        "Notas Olfativas", 
        "Perfumista", 
        "Ano"
    ]
    
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            
            # Renomeia se ainda estiver com o nome antigo
            if 'Categoria' in df.columns:
                df = df.rename(columns={'Categoria': 'Estações'})
            
            # Cria colunas que faltem (como a nova 'Ocasiões de Uso')
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            
            # --- REORDENAÇÃO EFETIVA ---
            # Isto garante que a tabela aparece na ordem da lista 'cols'
            df = df[cols]
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
    search = st.text_input("Pesquisar (notas, marcas, ocasiões...)")
    
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
        
        # Converte para string para evitar erros no editor
        result_display = result.fillna("").astype(str).reset_index(drop=True)
        
        try:
            st.data_editor(
                result_display, 
                use_container_width=True, 
                hide_index=True,
                disabled=True, 
                key="editor_reorder",
                column_config={
                    "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width="large"),
                    "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium")
                }
            )
        except:
            st.dataframe(result_display, use_container_width=True, hide_index=True)
        
        if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados", csv, "pesquisa.csv", "text/csv")

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "OUTONO", "MEIA-ESTAÇÃO", "INVERNO", "GERAL"])
            ocasiao = st.text_input("Ocasião de Uso")
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            notas = st.text_area("Notas Olfativas")
            
        if st.form_submit_button("Guardar"):
            if nome:
                # Criar a linha seguindo exatamente a ordem da lista 'cols' do load_data
                new_data = {
                    "Nome do Perfume": nome,
                    "Marca": marca,
                    "Estações": est,
                    "Ocasiões de Uso": ocasiao,
                    "Família Olfativa": fam,
                    "Notas Olfativas": notas,
                    "Perfumista": perf,
                    "Ano": ano
                }
                new_row = pd.DataFrame([new_data])
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
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                e_est = st.text_input("Estação", value=str(df.loc[idx, "Estações"]))
                e_ocasiao = st.text_input("Ocasião", value=str(df.loc[idx, "Ocasiões de Uso"]))
            with c2:
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                e_ano = st.text_input("Ano", value=str(df.loc[idx, "Ano"]))
                e_notas = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            
            if st.form_submit_button("Atualizar"):
                # Atualização usando os nomes das colunas para evitar erros de posição
                df.at[idx, "Nome do Perfume"] = e_nome
                df.at[idx, "Marca"] = e_marca
                df.at[idx, "Estações"] = e_est
                df.at[idx, "Ocasiões de Uso"] = e_ocasiao
                df.at[idx, "Família Olfativa"] = e_fam
                df.at[idx, "Notas Olfativas"] = e_notas
                df.at[idx, "Perfumista"] = e_perf
                df.at[idx, "Ano"] = e_ano
                
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
        
