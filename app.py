import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. CONFIGURAÇÃO DE LAYOUT
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

# 2. CSS PARA INTERFACE (MENU LATERAL GRANDE E DESIGN)
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stRadio label p { font-size: 24px !important; font-weight: 800 !important; color: #4F709C !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { font-size: 22px !important; font-weight: 500 !important; }
    .stDownloadButton { display: flex; justify-content: center; }
    [data-testid="column"] { padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "perfumes_data.csv"
ESTACOES_LISTA = ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "Geral"]
OCASIOES_OPCOES = ["CASUAL DIA", "CASUAL NOITE", "TRABALHO", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"]

# --- FUNÇÕES DE LIMPEZA E DADOS ---
def remover_acentos(texto):
    if not isinstance(texto, str): return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            return df.fillna("").astype(str)[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# --- INTERFACE PRINCIPAL ---
st.markdown("<h2 style='font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)
menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar...")
    
    res = df.copy()
    if search:
        termo = remover_acentos(search)
        mask = res.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(termo)).any(axis=1)
        res = res[mask]
    
    # LINHA DO TOTAL
    st.markdown(f"### Total: {len(res)} Perfumes")
    
    st.data_editor(res.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
    
    if not res.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        csv = res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv")

    st.markdown("---")
    cfg = {'staticPlot': True}

    if not df.empty:
        # LINHA 1: ESTAÇÕES E NOTAS (TOP 30)
        c1, c2 = st.columns(2)
        with c1:
            df_est = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(df_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#D8C4B6'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True, config=cfg)
        
        with c2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            df_not = n_s[n_s != ""].value_counts().nlargest(30).reset_index()
            fig2 = px.bar(df_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#4F709C'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title=None, yaxis_title=None, height=700, margin=dict(t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True, config=cfg)

        st.markdown("<br>", unsafe_allow_html=True)

        # LINHA 2: PIZZA (TOP 6) E PERFUMISTAS (TOP 15)
        c3, c4 = st.columns(2)
        with c3:
            f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            df_fam = f_s[f_s != ""].value_counts().nlargest(6).reset_index()
            
            # Mapeamento rigoroso de cores
            cores_pizza = {"Cítrico aromático": "#FFF176", "Amadeirado especiado": "#8B4513"}
            
            fig3 = px.pie(df_fam, values='count', names='Família Olfativa', color='Família Olfativa',
                          color_discrete_map=cores_pizza, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig3.update_layout(showlegend=True, height=450,
                               legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(size=14), ncol=2),
                               margin=dict(t=10, b=100))
            st.plotly_chart(fig3, use_container_width=True, config=cfg)

        with c4:
            df_perf = df["Perfumista"].replace("", "Desconhecido").value_counts().nlargest(15).reset_index()
            fig4 = px.bar(df_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title=None, yaxis_title=None, height=500, margin=dict(t=10, b=10))
            st.plotly_chart(fig4, use_container_width=True, config=cfg)

        st.markdown("<br>", unsafe_allow_html=True)

        # LINHA 3: MARCAS (TOP 15)
        df_mar = df["Marca"].value_counts().nlargest(15).reset_index()
        fig5 = px.bar(df_mar, x="Marca", y="count", text="count", color_discrete_sequence=['#607274'])
        fig5.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10))
        st.plotly_chart(fig5, use_container_width=True, config=cfg)

elif choice == "➕ Adicionar":
    st.subheader("Novo Perfume")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação", ESTACOES_LISTA)
            ocas = st.multiselect("Ocasiões de Uso", OCASIOES_OPCOES)
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            notas = st.text_area("Notas Olfativas")
        if st.form_submit_button("Guardar"):
            if nome:
                nova_linha = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est, "Ocasiões de Uso": ", ".join(ocas), "Família Olfativa": fam, "Notas Olfativas": notas, "Marca": marca, "Perfumista": perf}])
                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Perfumado com sucesso!")
                st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar Perfume")
    if not df.empty:
        sel = st.selectbox("Escolha o perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == sel].index[0]
        at_ocas = [x.strip() for x in str(df.at[idx, "Ocasiões de Uso"]).split(",") if x.strip() in OCASIOES_OPCOES]
        
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=df.at[idx, "Nome do Perfume"])
                e_marca = st.text_input("Marca", value=df.at[idx, "Marca"])
                e_est = st.selectbox("Estação", ESTACOES_LISTA, index=ESTACOES_LISTA.index(df.at[idx, "Estações do Ano"]) if df.at[idx, "Estações do Ano"] in ESTACOES_LISTA else 0)
                e_ocas = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=at_ocas)
            with c2:
                e_fam = st.text_input("Família", value=df.at[idx, "Família Olfativa"])
                e_perf = st.text_input("Perfumista", value=df.at[idx, "Perfumista"])
                e_ano = st.text_input("Ano", value=df.at[idx, "Ano"])
                e_not = st.text_area("Notas", value=df.at[idx, "Notas Olfativas"])
            if st.form_submit_button("Atualizar"):
                df.loc[idx] = [e_ano, e_nome, e_est, ", ".join(e_ocas), e_fam, e_not, e_marca, e_perf]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Dados atualizados!")
                st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Remover da Coleção")
    if not df.empty:
        p_del = st.selectbox("Perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Removido.")
            st.rerun()
