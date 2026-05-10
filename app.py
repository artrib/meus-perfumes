import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px
import plotly.graph_objects as go

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
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Estações' in df.columns: df = df.rename(columns={'Estações': 'Estações do Ano'})
            df = df.fillna("").astype(str)
            return df[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# --- INTERFACE ---
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar na coleção...")
    
    if not df.empty:
        # Lógica de Pesquisa
        if search:
            termos = search.split()
            result = df.copy()
            for termo in termos:
                termo_norm = remover_acentos(termo)
                mask = result.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(termo_norm)).any(axis=1)
                result = result[mask]
        else:
            result = df
            
        st.write(f"Encontrados **{len(result)}** perfumes.")
        
        # TABELA DE DADOS
        st.data_editor(
            result.reset_index(drop=True), 
            use_container_width=True, hide_index=True, disabled=True,
            column_config={"Ano": st.column_config.TextColumn("Ano", width=50)}
        )
        
        # --- BOTÃO DE DESCARREGAR (REPOSTO AQUI) ---
        if not result.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Descarregar resultados (CSV)", 
                data=csv, 
                file_name="meus_perfumes.csv", 
                mime="text/csv",
                key="download_btn"
            )

        # --- ZONA DE GRÁFICOS (FIXOS VISUALMENTE E ESTÁTICOS) ---
        st.markdown("---")
        
        # Configuração para os gráficos não reagirem ao toque/dedo
        config_estatico = {'staticPlot': True}

        # Linha 1: Estações e Notas (Sempre baseados na coleção total 'df')
        col1, col2 = st.columns(2)
        with col1:
            c_est = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color="Estações do Ano", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig1, use_container_width=True, config=config_estatico)

        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            c_not = n_s[n_s != ""].value_counts().nlargest(10).reset_index()
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color="count", color_continuous_scale="Viridis")
            fig2.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig2, use_container_width=True, config=config_estatico)

        # Linha 2: Marcas e Família (Aranha Simplificado)
        col3, col4 = st.columns(2)
        with col3:
            c_mar = df["Marca"].value_counts().nlargest(10).reset_index()
            fig3 = px.bar(c_mar, x="count", y="Marca", orientation='h', text="count", color_discrete_sequence=['#636EFA'])
            fig3.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig3, use_container_width=True, config=config_estatico)

        with col4:
            f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            c_fam = f_s[f_s != ""].value_counts().reset_index()
            if not c_fam.empty:
                fig4 = go.Figure(data=go.Scatterpolar(r=c_fam['count'], theta=c_fam['Família Olfativa'], fill='toself', line_color='teal'))
                fig4.update_layout(
                    polar=dict(radialaxis=dict(visible=False), angularaxis=dict(gridcolor="lightgrey", rotation=90)),
                    showlegend=False, margin=dict(t=30, b=30, l=50, r=50), height=300
                )
                st.plotly_chart(fig4, use_container_width=True, config=config_estatico)

# --- ABAS DE GESTÃO (ADICIONAR / EDITAR / APAGAR) ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV","MEIA-ESTAÇÃO", "Geral"])
            ocasiao = st.text_input("Ocasiões")
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            notas = st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            if nome:
                new_row = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est, "Ocasiões de Uso": ocasiao, "Família Olfativa": fam, "Notas Olfativas": notas, "Marca": marca, "Perfumista": perf}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Adicionado!")
                st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar")
    if not df.empty:
        p_sel = st.selectbox("Escolha:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == p_sel].index[0]
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                e_est = st.text_input("Estação", value=str(df.loc[idx, "Estações do Ano"]))
            with c2:
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_ano = st.text_input("Ano", value=str(df.loc[idx, "Ano"]))
                e_notas = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            if st.form_submit_button("Atualizar"):
                df.loc[idx, ["Nome do Perfume","Marca","Estações do Ano","Família Olfativa","Ano","Notas Olfativas"]] = [e_nome, e_marca, e_est, e_fam, e_ano, e_notas]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!")
                st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Apagar")
    if not df.empty:
        p_del = st.selectbox("Perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success("Removido.")
            st.rerun()
