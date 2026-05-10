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
            if 'Ocasiões do Ano' in df.columns: df = df.rename(columns={'Ocasiões do Ano': 'Ocasiões de Uso'})
            for col in cols:
                if col not in df.columns: df[col] = ""
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
    search = st.text_input("", placeholder="Pesquisar...")
    
    if not df.empty:
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
        
        st.data_editor(
            result.reset_index(drop=True), 
            use_container_width=True, 
            hide_index=True,
            disabled=True, 
            key="editor_final",
            column_config={
                "Ano": st.column_config.TextColumn("Ano", width=50),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=200),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=110),
            }
        )
        
        if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados (CSV)", csv, "meus_perfumes.csv", "text/csv")

            # --- ZONA DE ESTATÍSTICAS ---
            st.markdown("---")
            
            # MÉTRICAS RÁPIDAS
            m1, m2, m3 = st.columns(3)
            m1.metric("Frascos", len(result))
            m2.metric("Marcas", result["Marca"].nunique())
            anos_v = pd.to_numeric(result["Ano"], errors='coerce').dropna()
            if not anos_v.empty:
                m3.metric("Ano mais antigo", int(anos_v.min()))
            
            st.markdown("<br>", unsafe_allow_html=True)

            # LINHA 1: Estações e Notas
            col1, col2 = st.columns(2)
            with col1:
                c_est = result["Estações do Ano"].value_counts().reset_index()
                c_est.columns = ["Estação", "Qtd"]
                fig1 = px.bar(c_est, x="Estação", y="Qtd", text="Qtd", color="Estação", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig1.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10, l=0, r=0), height=300)
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                n_s = result["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
                n_s = n_s[n_s != ""]
                c_not = n_s.value_counts().nlargest(10).reset_index()
                c_not.columns = ["Nota", "Frequência"]
                fig2 = px.bar(c_not, x="Frequência", y="Nota", orientation='h', text="Frequência", color="Frequência", color_continuous_scale="Viridis")
                fig2.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=0, r=0), height=300)
                st.plotly_chart(fig2, use_container_width=True)

            # LINHA 2: Marcas e Aranha Simplificado
            col3, col4 = st.columns(2)
            with col3:
                c_mar = result["Marca"].value_counts().nlargest(10).reset_index()
                c_mar.columns = ["Marca", "Qtd"]
                fig3 = px.bar(c_mar, x="Qtd", y="Marca", orientation='h', text="Qtd", color_discrete_sequence=['#636EFA'])
                fig3.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=0, r=0), height=300)
                st.plotly_chart(fig3, use_container_width=True)

            with col4:
                # GRÁFICO ARANHA SIMPLIFICADO
                f_s = result["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
                f_s = f_s[f_s != ""]
                c_fam = f_s.value_counts().reset_index()
                c_fam.columns = ["Família", "Qtd"]
                if not c_fam.empty:
                    fig4 = go.Figure(data=go.Scatterpolar(r=c_fam['Qtd'], theta=c_fam['Família'], fill='toself', line_color='teal'))
                    fig4.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=False), # Esconde números radiais
                            angularaxis=dict(gridcolor="lightgrey", rotation=90) # Limpa visual
                        ),
                        showlegend=False, margin=dict(t=30, b=30, l=50, r=50), height=300
                    )
                    st.plotly_chart(fig4, use_container_width=True)

# --- ABAS ADICIONAR / EDITAR / APAGAR ---
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
