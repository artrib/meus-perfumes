import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração de Layout
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

# CSS para MAXIMIZAR o Menu Lateral e Centralizar Botões
st.markdown("""
    <style>
    /* Aumenta o título do menu lateral */
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #4F709C !important;
    }
    /* Aumenta as opções (labels) do rádio botão */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        padding: 10px 0px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        font-size: 22px !important;
        font-weight: 500 !important;
    }
    /* Aumenta o tamanho do círculo do rádio botão */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        margin-bottom: 20px !important;
    }
    /* Estilo para centralizar o botão de download */
    .stDownloadButton {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- INTERFACE PRINCIPAL ---
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar na coleção...")
    
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
            use_container_width=True, hide_index=True, disabled=True,
            column_config={"Ano": st.column_config.TextColumn("Ano", width=50)}
        )
        
        if not result.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                csv = result.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Descarregar resultados (CSV)",
                    data=csv,
                    file_name="meus_perfumes.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.markdown("---")
        config_estatico = {'staticPlot': True}

        # --- LINHA 1: TODAS AS ESTAÇÕES E TODAS AS NOTAS ---
        col1, col2 = st.columns(2)
        with col1:
            # Gráfico de Estações Completo
            c_est = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#D8C4B6'])
            fig1.update_traces(textangle=0, textposition='outside') 
            fig1.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=40, b=0, l=0, r=0), height=400)
            st.plotly_chart(fig1, use_container_width=True, config=config_estatico)

        with col2:
            # Lista de Notas Completa (removido o nlargest)
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            c_not = n_s[n_s != ""].value_counts().reset_index()
            alt_notas = max(400, len(c_not) * 25) # Altura dinâmica para caber tudo
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#4F709C']) 
            fig2.update_traces(textangle=0, textposition='outside') 
            fig2.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=40, b=0, l=0, r=0), height=alt_notas)
            st.plotly_chart(fig2, use_container_width=True, config=config_estatico)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- LINHA 2: FAMÍLIAS (PIZZA) E TODOS OS PERFUMISTAS ---
        col3, col4 = st.columns(2)
        with col3:
            f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            c_fam = f_s[f_s != ""].value_counts().nlargest(6).reset_index()
            color_map = {"Cítrico aromática": "#D35400", "Cítrico aromático": "#D35400"}
            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', color='Família Olfativa', color_discrete_map=color_map, color_discrete_sequence=['#8EACCD', '#94A684', '#F9F3CC', '#D2E0FB', '#B0A695'])
            fig3.update_traces(textinfo='percent', hoverinfo='label+percent')
            fig3.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=22), itemsizing='constant'),
                margin=dict(t=40, b=80, l=10, r=10), 
                height=480 
            )
            st.plotly_chart(fig3, use_container_width=True, config=config_estatico)

        with col4:
            # Gráfico de Perfumistas Completo (removido o nlargest)
            c_perf = df["Perfumista"].replace("", "Desconhecido").value_counts().reset_index()
            alt_perf = max(400, len(c_perf) * 25) # Altura dinâmica
            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_traces(textangle=0, textposition='outside')
            fig4.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, yaxis={'categoryorder':'total ascending'}, margin=dict(t=40, b=0, l=0, r=0), height=alt_perf)
            st.plotly_chart(fig4, use_container_width=True, config=config_estatico)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- LINHA 3: MARCAS ---
        c_mar = df["Marca"].value_counts().reset_index()
        fig5 = px.bar(c_mar, x="Marca", y="count", text="count", color_discrete_sequence=['#607274'])
        fig5.update_traces(textangle=0, textposition='outside')
        fig5.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=40, b=0, l=0, r=0), height=450)
        st.plotly_chart(fig5, use_container_width=True, config=config_estatico)

# --- ABAS DE GESTÃO ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação", ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV","MEIA-ESTAÇÃO", "Geral"])
            ocasiao = st.text_input("Ocasião de Uso")
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
    st.subheader("Editar Perfume")
    if not df.empty:
        p_sel = st.selectbox("Selecione o perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == p_sel].index[0]
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                e_est = st.text_input("Estação", value=str(df.loc[idx, "Estações do Ano"]))
                e_ocas = st.text_input("Ocasião", value=str(df.loc[idx, "Ocasiões de Uso"]))
            with c2:
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                e_ano = st.text_input("Ano", value=str(df.loc[idx, "Ano"]))
                e_notas = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            if st.form_submit_button("Atualizar Dados"):
                df.at[idx, "Ano"] = e_ano
                df.at[idx, "Nome do Perfume"] = e_nome
                df.at[idx, "Estações do Ano"] = e_est
                df.at[idx, "Ocasiões de Uso"] = e_ocas
                df.at[idx, "Família Olfativa"] = e_fam
                df.at[idx, "Notas Olfativas"] = e_notas
                df.at[idx, "Marca"] = e_marca
                df.at[idx, "Perfumista"] = e_perf
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"'{e_nome}' atualizado!")
                st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Eliminar Registo")
    if not df.empty:
        p_del = st.selectbox("Escolha o perfume a apagar:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação Permanente"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning(f"'{p_del}' foi removido.")
            st.rerun()
