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
    cols = [
        "Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", 
        "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"
    ]
    
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            
            if 'Estações' in df.columns:
                df = df.rename(columns={'Estações': 'Estações do Ano'})
            if 'Ocasiões do Ano' in df.columns: # Correção de segurança
                df = df.rename(columns={'Ocasiões do Ano': 'Ocasiões de Uso'})
            
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            
            df = df.fillna("").astype(str)
            return df[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# --- INTERFACE ---
st.markdown("<h2 style='text-align: left; font-size: 32px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar...")
    
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
            
        st.write(f"Encontrados **{len(result)}** perfumes.")
        
        result_display = result.reset_index(drop=True)
        
        st.data_editor(
            result_display, 
            use_container_width=True, 
            hide_index=True,
            disabled=True, 
            key="editor_final",
            column_config={
                "Ano": st.column_config.TextColumn("Ano", width=50),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width="200"),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width="100"),
            }
        )
        
        if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados (CSV)", csv, "meus_perfumes.csv", "text/csv")

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação de Uso", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV","MEIA-ESTAÇÃO", "Geral"])
            ocasiao = st.text_input("Ocasiões de Uso") # Corrigido
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            notas = st.text_area("Notas Olfativas")
            
        if st.form_submit_button("Guardar Perfume"):
            if nome:
                new_data = {
                    "Ano": ano,
                    "Nome do Perfume": nome,
                    "Estações do Ano": est,
                    "Ocasiões de Uso": ocasiao,
                    "Família Olfativa": fam,
                    "Notas Olfativas": notas,
                    "Marca": marca,
                    "Perfumista": perf
                }
                new_row = pd.DataFrame([new_data])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"Perfume '{nome}' adicionado com sucesso!")
                st.rerun()
            else:
                st.error("O campo 'Nome do Perfume' é obrigatório.")

# --- ABA EDITAR ---
elif choice == "📝 Editar":
    st.subheader("Editar Perfume")
    if not df.empty:
        nomes_unicos = sorted(df["Nome do Perfume"].unique().tolist())
        perfume_sel = st.selectbox("Escolha o perfume para alterar:", nomes_unicos)
        idx = df[df["Nome do Perfume"] == perfume_sel].index[0]
        
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                e_est = st.text_input("Estação do Ano", value=str(df.loc[idx, "Estações do Ano"]))
                e_ocasiao = st.text_input("Ocasiões de Uso", value=str(df.loc[idx, "Ocasiões de Uso"]))
            with c2:
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                e_ano = st.text_input("Ano", value=str(df.loc[idx, "Ano"]))
                e_notas = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            
            if st.form_submit_button("Atualizar Dados"):
                df.loc[idx, "Nome do Perfume"] = e_nome
                df.loc[idx, "Marca"] = e_marca
                df.loc[idx, "Estações do Ano"] = e_est
                df.loc[idx, "Ocasiões de Uso"] = e_ocasiao
                df.loc[idx, "Família Olfativa"] = e_fam
                df.loc[idx, "Notas Olfativas"] = e_notas
                df.loc[idx, "Perfumista"] = e_perf
                df.loc[idx, "Ano"] = e_ano
                
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ Informação atualizada!")
                st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Remover Perfume")
    if not df.empty:
        p_del = st.selectbox("Escolha o perfume que deseja remover:", sorted(df["Nome do Perfume"].unique().tolist()))
        st.warning(f"Tem a certeza que deseja apagar '{p_del}'? Esta ação não pode ser desfeita.")
        if st.button("❌ Sim, Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success("Removido com sucesso.")
            st.rerun()
