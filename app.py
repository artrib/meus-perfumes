import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# 1. Configuração de Layout
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

# 2. CSS Customizado: Menu Lateral Gigante, Botão Centralizado e Ajustes Visuais
st.markdown("""
    <style>
    /* Aumenta o título do menu lateral */
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #4F709C !important;
    }
    /* Aumenta as opções do rádio botão */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        font-size: 22px !important;
        font-weight: 500 !important;
    }
    /* Espaçamento das opções */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        padding: 8px 0px !important;
    }
    /* Centralização do botão de download */
    .stDownloadButton {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Constantes e Configurações
DB_FILE = "perfumes_data.csv"
ESTACOES_LISTA = ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "Geral"]
OCASIOES_OPCOES = ["CASUAL DIA", "CASUAL NOITE", "TRABALHO", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"]

# 4. Funções de Suporte
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
            return df[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# 5. Interface Principal
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# --- ABA PESQUISAR ---
if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar por nome, nota, marca, perfumista...")
    
    if not df.empty:
        result = df.copy()
        if search:
            termos = search.split()
            for termo in termos:
                termo_norm = remover_acentos(termo)
                mask = result.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(termo_norm)).any(axis=1)
                result = result[mask]
        
        st.write(f"Encontrados **{len(result)}** perfumes.")
        st.data_editor(result.reset_index(drop=True), use_container_width=True, hide_index=True, disabled=True)
        
        if not result.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                csv = result.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Descarregar resultados (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")
        config_est = {'staticPlot': True}
        
        # --- GRÁFICOS (TODOS COMPLETOS) ---
        col1, col2 = st.columns(2)
        with col1:
            c_est = df["Estações do Ano"].value_counts().reset_index()
            st.plotly_chart(px.bar(c_est, x="Estações do Ano", y="count", text="count", title="Estações", color_discrete_sequence=['#D8C4B6']), use_container_width=True, config=config_est)
        
        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
            c_not = n_s[n_s != ""].value_counts().reset_index()
            st.plotly_chart(px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", title="Lista Completa de Notas", color_discrete_sequence=['#4F709C'], height=max(400, len(c_not)*25)), use_container_width=True, config=config_est)

        col3, col4 = st.columns(2)
        with col3:
            f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
            c_fam = f_s[f_s != ""].value_counts().reset_index()
            fig_p = px.pie(c_fam, values='count', names='Família Olfativa', color='Família Olfativa', 
                           color_discrete_map={"Cítrico aromática": "#D35400", "Cítrico aromático": "#D35400"},
                           color_discrete_sequence=['#8EACCD', '#94A684', '#F9F3CC', '#D2E0FB'])
            fig_p.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=22), itemsizing='constant'), height=480)
            st.plotly_chart(fig_p, use_container_width=True, config=config_est)

        with col4:
            c_perf = df["Perfumista"].replace("", "Desconhecido").value_counts().reset_index()
            st.plotly_chart(px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", title="Todos os Perfumistas", color_discrete_sequence=['#94A684'], height=max(400, len(c_perf)*25)), use_container_width=True, config=config_est)

        c_mar = df["Marca"].value_counts().reset_index()
        st.plotly_chart(px.bar(c_mar, x="Marca", y="count", text="count", title="Todas as Marcas", color_discrete_sequence=['#607274'], height=max(400, len(c_mar)*30)), use_container_width=True, config=config_est)

# --- ABA ADICIONAR ---
elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
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
                new_row = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": est, "Ocasiões de Uso": ", ".join(ocas), "Família Olfativa": fam, "Notas Olfativas": notas, "Marca": marca, "Perfumista": perf}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Adicionado!")
                st.rerun()

# --- ABA EDITAR ---
elif choice == "📝 Editar":
    st.subheader("Editar")
    if not df.empty:
        p_sel = st.selectbox("Escolha o perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == p_sel].index[0]
        ocas_atual = [x.strip() for x in str(df.loc[idx, "Ocasiões de Uso"]).split(",") if x.strip() in OCASIOES_OPCOES]
        est_idx = ESTACOES_LISTA.index(df.loc[idx, "Estações do Ano"]) if df.loc[idx, "Estações do Ano"] in ESTACOES_LISTA else 0

        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_nome = st.text_input("Nome", value=str(df.loc[idx, "Nome do Perfume"]))
                e_marca = st.text_input("Marca", value=str(df.loc[idx, "Marca"]))
                e_est = st.selectbox("Estação", ESTACOES_LISTA, index=est_idx)
                e_ocas = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=ocas_atual)
            with c2:
                e_fam = st.text_input("Família", value=str(df.loc[idx, "Família Olfativa"]))
                e_perf = st.text_input("Perfumista", value=str(df.loc[idx, "Perfumista"]))
                e_ano = st.text_input("Ano", value=str(df.loc[idx, "Ano"]))
                e_not = st.text_area("Notas", value=str(df.loc[idx, "Notas Olfativas"]))
            if st.form_submit_button("Atualizar"):
                df.loc[idx] = [e_ano, e_nome, e_est, ", ".join(e_ocas), e_fam, e_not, e_marca, e_perf]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!")
                st.rerun()

# --- ABA APAGAR ---
elif choice == "🗑️ Apagar":
    st.subheader("Eliminar")
    if not df.empty:
        p_del = st.selectbox("Perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação Permanente"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Eliminado.")
            st.rerun()
