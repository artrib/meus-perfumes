import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

st.markdown("""
    <style>
    /* Ajuste do topo para evitar cortes e garantir visibilidade */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* REMOVER CONTORNO VERMELHO E ESTILIZAR FOCO NEUTRO */
    *:focus, [data-baseweb="input"] > div:focus-within, [data-testid="stDataEditor"] *:focus {
        outline: none !important;
        border-color: #dcdcdc !important;
        box-shadow: none !important;
    }

    /* ESTILIZAÇÃO DO MENU LATERAL (SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #f8f9fb;
    }
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #4F709C !important;
    }
    
    /* CENTRALIZAÇÃO DO BOTÃO DESCARREGAR */
    .stDownloadButton {
        display: flex;
        justify-content: center;
        width: 100%;
        padding: 20px 0;
    }
    .stDownloadButton button {
        margin: 0 auto;
        display: block;
    }

    /* Espaçamento entre gráficos */
    [data-testid="column"] {
        padding: 0 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONSTANTES E BASE DE DADOS
DB_FILE = "perfumes_data.csv"
ESTACOES_LISTA = ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "Geral"]
OCASIOES_OPCOES = ["CASUAL DIA", "CASUAL NOITE", "TRABALHO", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"]

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

# 3. INTERFACE - TÍTULO
st.markdown("<h1 style='text-align: left; font-size: 34px; margin-top: -20px;'>Caixa dos Perfumes</h1>", unsafe_allow_html=True)

# MENU DE GESTÃO NA BARRA LATERAL
with st.sidebar:
    st.markdown("### Navegação")
    menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
    choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquise por marca, nome ou notas... (Ex: 'Dio Fah')")
    
    result = df.copy()
    if search:
        # Pesquisa Relacional (AND)
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            mask = result.apply(lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(), axis=1)
            result = result[mask]
    
    st.write(f"**Total Encontrado:** {len(result)} Perfumes")
    
    if not df.empty:
        st.data_editor(result.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
        
        # Botão Descarregar Centralizado
        if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv")

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # GRÁFICOS COM CORES MINIMALISTAS E ALTO CONTRASTE
        config_f = {'staticPlot': True}
        paleta_minimalista = ['#2E4374', '#7C9070', '#A45D5D', '#E4C988', '#435B66', '#9BABB8']
        
        mapa_cores = {
            "Cítrico aromático": "#7C9070", 
            "Aromático fougère": "#2E4374",
            "Amadeirado": "#435B66"
        }

        # Linha 1
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Distribuição por Estação")
            e_counts = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(e_counts, x="Estações do Ano", y="count", color_discrete_sequence=['#9BABB8'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=0, b=0), height=300)
            st.plotly_chart(fig1, use_container_width=True, config=config_f)
            
        with c2:
            st.markdown("##### Top Notas Olfativas")
            notas = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            n_counts = notas[notas != ""].value_counts().nlargest(20).reset_index()
            fig2 = px.bar(n_counts, x="count", y="Notas Olfativas", orientation='h', color_discrete_sequence=['#435B66'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=450, margin=dict(t=0, b=0))
            st.plotly_chart(fig2, use_container_width=True, config=config_f)

        # Linha 2
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### Famílias Olfativas (Principais)")
            fams = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            f_counts = fams[fams != ""].value_counts().nlargest(6).reset_index()
            fig3 = px.pie(f_counts, values='count', names='Família Olfativa', color='Família Olfativa', 
                          color_discrete_map=mapa_cores, color_discrete_sequence=paleta_minimalista)
            fig3.update_layout(
                showlegend=True,
                legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(size=18), itemsizing='constant'),
                margin=dict(t=0, b=50), height=400
            )
            st.plotly_chart(fig3, use_container_width=True, config=config_f)

        with c4:
            st.markdown("##### Perfumistas")
            perfs = df["Perfumista"].replace(["", "nan"], "Desconhecido").value_counts().nlargest(10).reset_index()
            fig4 = px.bar(perfs, x="count", y="Perfumista", orientation='h', color_discrete_sequence=['#7C9070'])
            fig4.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, margin=dict(t=0, b=0))
            st.plotly_chart(fig4, use_container_width=True, config=config_f)

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação", ESTACOES_LISTA)
            oc = st.multiselect("Ocasiões", OCASIOES_OPCOES)
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            not_ol = st.text_area("Notas Olfativas")
        if st.form_submit_button("Gravar Perfume"):
            if nome:
                new = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est, "Ocasiões de Uso": ", ".join(oc), "Família Olfativa": fam, "Notas Olfativas": not_ol, "Marca": marca, "Perfumista": perf}])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado com sucesso!"); st.rerun()

# --- ABA EDITAR ---
elif choice == "📝 Editar":
    st.subheader("Editar Perfume Existente")
    if not df.empty:
        p_sel = st.selectbox("Selecione o perfume para editar:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == p_sel].index[0]
        at_oc = [x.strip() for x in str(df.at[idx, "Ocasiões de Uso"]).split(",") if x.strip() in OCASIOES_OPCOES]
        with st.form("edit"):
            c1, c2 = st.columns(2)
            with c1:
                e_n = st.text_input("Nome", value=df.at[idx, "Nome do Perfume"])
                e_m = st.text_input("Marca", value=df.at[idx, "Marca"])
                e_e = st.selectbox("Estação", ESTACOES_LISTA, index=ESTACOES_LISTA.index(df.at[idx, "Estações do Ano"]) if df.at[idx, "Estações do Ano"] in ESTACOES_LISTA else 0)
                e_oc = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=at_oc)
            with c2:
                e_f = st.text_input("Família", value=df.at[idx, "Família Olfativa"])
                e_p = st.text_input("Perfumista", value=df.at[idx, "Perfumista"])
                e_a = st.text_input("Ano", value=df.at[idx, "Ano"])
                e_not = st.text_area("Notas", value=df.at[idx, "Notas Olfativas"])
            if st.form_submit_button("Atualizar Dados"):
                df.loc[idx] = [e_a, e_n, e_e, ", ".join(e_oc), e_f, e_not, e_m, e_p]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Dados atualizados!"); st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Eliminar Registo")
    if not df.empty:
        p_del = st.selectbox("Perfume a eliminar:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação Permanente"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Perfume eliminado da base de dados."); st.rerun()
