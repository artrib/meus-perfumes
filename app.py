import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px
import re

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Gestão de Perfumes",
    layout="wide",
    page_icon="👃"
)

# =========================================================
# CSS PERSONALIZADO
# =========================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}
[data-testid="stWidgetLabel"] {
    display: none !important;
}
[data-testid="stVerticalBlock"] > div:has(input) {
    margin-bottom: -35px !important;
}
[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}
*:focus,
[data-baseweb="input"] > div:focus-within,
[data-testid="stDataEditor"] *:focus {
    outline: none !important;
    border-color: #dcdcdc !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stRadio label p {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #4F709C !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES E TRATAMENTO
# =========================================================

DB_FILE = "perfumes_data.csv"

ESTACOES_LISTA = ["COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "GERAL"]
OCASIOES_OPCOES = ["CASUAL DIA", "CASUAL NOITE", "TRABALHO", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"]

def remover_acentos(texto):
    if not isinstance(texto, str): texto = str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def padronizar_texto(texto):
    if not texto or not isinstance(texto, str): return ""
    t = remover_acentos(texto).strip()
    if t.endswith('s') and len(t) > 4: t = t[:-1]
    return t.capitalize()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            for col in cols:
                if col not in df.columns: df[col] = ""
            return df.fillna("").astype(str)[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# =========================================================
# INÍCIO DA APP
# =========================================================

df = load_data()
st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

if choice == "🔍 Pesquisar":
    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        search = st.text_input("pesquisa", placeholder="...")
    with col_filtro:
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", 'Ocasiões de Uso", "Estações do Ano", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca)

    result = df.copy()

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            
            # LÓGICA DE EXCLUSÃO PARA "ROSA"
            if t_norm == "rosa":
                # Procura 'rosa' mas garante que não tem 'pimenta' ou 'pimentas' antes
                padrao = r'(?<!pimenta)(?<!pimentas)\s?\brosa\b'
            else:
                padrao = rf'\b{t_norm}\b'

            if local_busca == "Tudo":
                mask = result.apply(
                    lambda row: row.astype(str).map(remover_acentos).str.contains(padrao, regex=True, flags=re.IGNORECASE).any(), axis=1
                )
            else:
                mask = result[local_busca].astype(str).map(remover_acentos).str.contains(padrao, regex=True, flags=re.IGNORECASE)
            result = result[mask].copy()

    st.caption(f"{len(result)} perfumes encontrados")

    if not df.empty:
        st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "Ano": st.column_config.TextColumn("Ano", width=55),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Marca": st.column_config.TextColumn("Marca", width=120),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220)
            }
        )

        st.markdown("---")
        config_fixo = {'staticPlot': True}
        paleta = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']

        col1, col2 = st.columns(2)
        with col1:
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            fig1 = px.bar(c_est, x=c_est.columns[0], y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)
            
            st.write("")
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc != ""].value_counts().reset_index(name="count")
            fig_oc = px.bar(c_oc, x="count", y=c_oc.columns[0], orientation='h', text="count", color_discrete_sequence=['#C08261'])
            fig_oc.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title=None, yaxis_title=None, height=350)
            st.plotly_chart(fig_oc, use_container_width=True, config=config_fixo)

        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            fig2 = px.bar(c_not, x="count", y=c_not.columns[0], orientation='h', text="count", color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=770, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            f_s = df["Família Olfativa"].str.replace('/', ',').str.split(',').explode().str.strip()
            c_fam = f_s[f_s != ""].apply(padronizar_texto).value_counts().nlargest(8).reset_index(name="count")
            fig3 = px.pie(c_fam, values='count', names=c_fam.columns[0], color_discrete_sequence=paleta)
            fig3.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), height=340)
            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        with col4:
            c_perf = df["Perfumista"].replace(["", "nan"], "Desconhecido")
            c_perf = c_perf.apply(lambda x: padronizar_texto(x) if x != "Desconhecido" else x)
            c_perf = c_perf.value_counts().nlargest(15).reset_index(name="count")
            fig4 = px.bar(c_perf, x="count", y=c_perf.columns[0], orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

        st.markdown("---")
        st.subheader("Distribuição por Marcas")
        c_marca = df["Marca"].replace(["", "nan"], "N/A").apply(padronizar_texto).value_counts().nlargest(20).reset_index(name="count")
        fig_m = px.bar(c_marca, x=c_marca.columns[0], y="count", text="count", color_discrete_sequence=['#607274'])
        fig_m.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
        st.plotly_chart(fig_m, use_container_width=True, config=config_fixo)

elif choice == "➕ Adicionar":
    st.subheader("Novo Registo")
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.multiselect("Estações", ESTACOES_LISTA)
            oc = st.multiselect("Ocasiões de Uso", OCASIOES_OPCOES)
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            notas = st.text_area("Notas Olfativas")

        if st.form_submit_button("Guardar"):
            if nome:
                f_c = ", ".join([padronizar_texto(i) for i in fam.replace('/', ',').split(',') if i.strip()])
                n_c = ", ".join([padronizar_texto(i) for i in notas.split(',') if i.strip()])
                new = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": ", ".join(est), "Ocasiões de Uso": ", ".join(oc), "Família Olfativa": f_c, "Notas Olfativas": n_c, "Marca": marca, "Perfumista": padronizar_texto(perf)}])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado!"); st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar Registo")
    if not df.empty:
        sel = st.selectbox("Selecione o perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        idx = df[df["Nome do Perfume"] == sel].index[0]
        at_oc = [x.strip() for x in str(df.at[idx, "Ocasiões de Uso"]).split(",") if x.strip() in OCASIOES_OPCOES]
        at_est = [x.strip() for x in str(df.at[idx, "Estações do Ano"]).split(",") if x.strip() in ESTACOES_LISTA]
        with st.form("edit"):
            c1, c2 = st.columns(2)
            with c1:
                e_n = st.text_input("Nome", value=df.at[idx, "Nome do Perfume"])
                e_m = st.text_input("Marca", value=df.at[idx, "Marca"])
                e_e = st.multiselect("Estações", ESTACOES_LISTA, default=at_est)
                e_oc = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=at_oc)
            with c2:
                e_f = st.text_input("Família", value=df.at[idx, "Família Olfativa"])
                e_p = st.text_input("Perfumista", value=df.at[idx, "Perfumista"])
                e_a = st.text_input("Ano", value=df.at[idx, "Ano"])
                e_not = st.text_area("Notas", value=df.at[idx, "Notas Olfativas"])
            if st.form_submit_button("Atualizar"):
                f_e = ", ".join([padronizar_texto(i) for i in e_f.replace('/', ',').split(',') if i.strip()])
                n_e = ", ".join([padronizar_texto(i) for i in e_not.split(',') if i.strip()])
                df.loc[idx] = [e_a, e_n, ", ".join(e_e), ", ".join(e_oc), f_e, n_e, e_m, padronizar_texto(e_p)]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Atualizado!"); st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Eliminar Registo")
    if not df.empty:
        p_del = st.selectbox("Perfume a eliminar:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar Eliminação"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Registo eliminado."); st.rerun()
            
