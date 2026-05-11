import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. CONFIGURAÇÃO DE LAYOUT E TEMA NEUTRO
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

# Injeção de CSS Robusto para eliminar o vermelho e ajustar o topo
st.markdown("""
    <style>
    /* Esconde o header nativo para evitar corte no título */
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* REMOVER CONTORNO VERMELHO (PRIMARY COLOR) E SUBSTITUIR POR BRANCO/NEUTRO */
    input:focus, textarea:focus, div:focus, .st-at:focus {
        border-color: #dcdcdc !important;
        box-shadow: 0 0 0 1px #dcdcdc !important;
        outline: none !important;
    }
    
    /* Estilo para a Tabela (DataEditor) */
    [data-testid="stDataEditor"] {
        border: 1px solid #eeeeee !important;
    }

    /* Menu Lateral */
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #4F709C !important;
    }

    /* Centralização do Botão de Download */
    .stDownloadButton {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONSTANTES E CARREGAMENTO
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

# 3. INTERFACE PRINCIPAL
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquise por qualquer termo...")
    
    res = df.copy()
    if search:
        t = remover_acentos(search)
        mask = res.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(t)).any(axis=1)
        res = res[mask]
    
    st.write(f"Total: {len(res)} Perfumes")
    
    st.data_editor(res.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
    
    if not res.empty:
        csv = res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv")

    st.markdown("---")
    
    if not df.empty:
        config_f = {'staticPlot': True}
        
        # DEFINIÇÃO DE CORES (Inversão solicitada)
        mapa_cores = {
            "Cítrico aromático": "#94A684",  # Cor Sálvia (era do Fougere)
            "Aromático fougère": "#8EACCD",  # Cor Azul Acinzentado
            "Amadeirado": "#B0A695"          # Areia
        }

        # Gráficos de cima
        c1, c2 = st.columns(2)
        with c1:
            e_counts = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(e_counts, x="Estações do Ano", y="count", color_discrete_sequence=['#B0A695'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True, config=config_f)
            
        with c2:
            notas = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            n_counts = notas[notas != ""].value_counts().nlargest(30).reset_index()
            fig2 = px.bar(n_counts, x="count", y="Notas Olfativas", orientation='h', color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=700, margin=dict(t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True, config=config_f)

        # Gráficos de baixo
        c3, c4 = st.columns(2)
        with c3:
            fams = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            f_counts = fams[fams != ""].value_counts().nlargest(6).reset_index()
            
            fig3 = px.pie(f_counts, values='count', names='Família Olfativa',
                          color='Família Olfativa', color_discrete_map=mapa_cores)
            
            fig3.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h", y=-0.2, x=0.5, xanchor="center",
                    font=dict(size=20), # Fonte maior
                    itemsizing='constant' # Símbolos da legenda grandes e fixos
                ),
                margin=dict(t=0, b=100), height=500
            )
            st.plotly_chart(fig3, use_container_width=True, config=config_f)

        with c4:
            perfs = df["Perfumista"].replace(["", "nan"], "Desconhecido").value_counts().nlargest(15).reset_index()
            fig4 = px.bar(perfs, x="count", y="Perfumista", orientation='h', color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10))
            st.plotly_chart(fig4, use_container_width=True, config=config_f)

        # Marca (Final)
        marcas = df["Marca"].value_counts().nlargest(15).reset_index()
        fig5 = px.bar(marcas, x="Marca", y="count", color_discrete_sequence=['#607274'])
        fig5.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig5, use_container_width=True, config=config_f)

# (Abas Adicionar, Editar e Apagar permanecem com a mesma lógica funcional, mas agora herdam o CSS sem o contorno vermelho)
elif choice == "➕ Adicionar":
    st.subheader("Novo Perfume")
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
        if st.form_submit_button("Gravar"):
            if nome:
                new = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est, "Ocasiões de Uso": ", ".join(oc), "Família Olfativa": fam, "Notas Olfativas": not_ol, "Marca": marca, "Perfumista": perf}])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado!"); st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar Registo")
    if not df.empty:
        p_sel = st.selectbox("Escolha:", sorted(df["Nome do Perfume"].unique().tolist()))
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
            if st.form_submit_button("Atualizar"):
                df.loc[idx] = [e_a, e_n, e_e, ", ".join(e_oc), e_f, e_not, e_m, e_p]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!"); st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Eliminar")
    if not df.empty:
        p_del = st.selectbox("Perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Eliminar"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Removido."); st.rerun()
