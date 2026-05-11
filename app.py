import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

st.markdown("""
    <style>
    /* Maximiza o menu lateral para facilitar a leitura */
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #4F709C !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        font-size: 22px !important;
        font-weight: 500 !important;
    }
    /* Centraliza botões de download */
    .stDownloadButton {
        display: flex;
        justify-content: center;
    }
    /* Espaçamento uniforme entre blocos */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
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
            df = df.fillna("").astype(str)
            # Garante que as colunas existem
            for col in cols:
                if col not in df.columns: df[col] = ""
            return df[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# 3. INTERFACE PRINCIPAL
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar por nome, nota, marca, perfumista...")
    
    result = df.copy()
    if search:
        termos = search.split()
        for termo in termos:
            termo_norm = remover_acentos(termo)
            mask = result.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(termo_norm)).any(axis=1)
            result = result[mask]
    
    # Contador de Perfumes (Tamanho normal conforme solicitado)
    st.write(f"Total: {len(result)} Perfumes")
    
    if not df.empty:
        st.data_editor(result.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
        
        # Botão de Download
        if not result.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv")

        st.markdown("---")
        # Configuração para gráficos não interativos/estáticos se desejar, ou padrão
        config_est = {'displayModeBar': False}

        # --- LINHA 1: ESTAÇÕES E NOTAS (TOP 30) ---
        col1, col2 = st.columns(2)
        with col1:
            c_est = df["Estações do Ano"].value_counts().reset_index()
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#D8C4B6'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False, margin=dict(t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True, config=config_est)
        
        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            c_not = n_s[n_s != ""].value_counts().nlargest(30).reset_index()
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#4F709C'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title=None, yaxis_title=None, height=700, margin=dict(t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True, config=config_est)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- LINHA 2: PIZZA (TOP 6) E PERFUMISTAS (TOP 15) ---
        col3, col4 = st.columns(2)
        with col3:
            f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            c_fam = f_s[f_s != ""].value_counts().nlargest(6).reset_index()
            
            # Cores solicitadas e legenda normal (lateral)
            cores_map = {
                "Cítrico aromático": "#FFF59D",     # Amarelo claro
                "Amadeirado especiado": "#8B4513"   # Castanho
            }
            
            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', 
                          color='Família Olfativa', color_discrete_map=cores_map,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            
            # Gráfico Pizza um pouco menor e legenda normal
            fig3.update_layout(showlegend=True, height=400, margin=dict(t=30, b=30))
            st.plotly_chart(fig3, use_container_width=True, config=config_est)

        with col4:
            c_perf = df["Perfumista"].replace(["", "nan", "None"], "Desconhecido").value_counts().nlargest(15).reset_index()
            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title=None, yaxis_title=None, height=500, margin=dict(t=20, b=20))
            st.plotly_chart(fig4, use_container_width=True, config=config_est)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- LINHA 3: MARCAS (TOP 15) ---
        c_mar = df["Marca"].value_counts().nlargest(15).reset_index()
        fig5 = px.bar(c_mar, x="Marca", y="count", text="count", color_discrete_sequence=['#607274'])
        fig5.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=20))
        st.plotly_chart(fig5, use_container_width=True, config=config_est)

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("form_add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.selectbox("Estação do Ano", ESTACOES_LISTA)
            ocas = st.multiselect("Ocasiões de Uso", OCASIOES_OPCOES)
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            not_ol = st.text_area("Notas Olfativas (separadas por vírgula)")
        
        if st.form_submit_button("Guardar Perfume"):
            if nome:
                new_data = pd.DataFrame([{
                    "Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est,
                    "Ocasiões de Uso": ", ".join(ocas), "Família Olfativa": fam,
                    "Notas Olfativas": not_ol, "Marca": marca, "Perfumista": perf
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado com sucesso!")
                st.rerun()
            else:
                st.error("O campo 'Nome do Perfume' é obrigatório.")

# --- ABA EDITAR ---
elif choice == "📝 Editar":
    st.subheader("Editar")
    if not df.empty:
        lista_perfumes = sorted(df["Nome do Perfume"].unique().tolist())
        p_sel = st.selectbox("Selecione o perfume para editar:", lista_perfumes)
        idx = df[df["Nome do Perfume"] == p_sel].index[0]
        
        # Parse das ocasiões atuais para o multiselect
        ocas_at = [x.strip() for x in str(df.loc[idx, "Ocasiões de Uso"]).split(",") if x.strip() in OCASIOES_OPCOES]
        
        with st.form("form_edit"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=df.loc[idx, "Nome do Perfume"])
                e_marca = st.text_input("Marca", value=df.loc[idx, "Marca"])
                e_est = st.selectbox("Estação", ESTACOES_LISTA, index=ESTACOES_LISTA.index(df.loc[idx, "Estações do Ano"]) if df.loc[idx, "Estações do Ano"] in ESTACOES_LISTA else 0)
                e_ocas = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=ocas_at)
            with c2:
                e_fam = st.text_input("Família", value=df.loc[idx, "Família Olfativa"])
                e_perf = st.text_input("Perfumista", value=df.loc[idx, "Perfumista"])
                e_ano = st.text_input("Ano", value=df.loc[idx, "Ano"])
                e_not = st.text_area("Notas", value=df.loc[idx, "Notas Olfativas"])
            
            if st.form_submit_button("Atualizar Dados"):
                df.loc[idx, "Ano"] = e_ano
                df.loc[idx, "Nome do Perfume"] = e_nome
                df.loc[idx, "Estações do Ano"] = e_est
                df.loc[idx, "Ocasiões de Uso"] = ", ".join(e_ocas)
                df.loc[idx, "Família Olfativa"] = e_fam
                df.loc[idx, "Notas Olfativas"] = e_not
                df.loc[idx, "Marca"] = e_marca
                df.loc[idx, "Perfumista"] = e_perf
                
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Alterações gravadas!")
                st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Apagar")
    if not df.empty:
        lista_del = sorted(df["Nome do Perfume"].unique().tolist())
        p_del = st.selectbox("Selecione o perfume para remover:", lista_del)
        if st.button("Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning(f"'{p_del}' foi removido.")
            st.rerun()
