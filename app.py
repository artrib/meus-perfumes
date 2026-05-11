import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

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
    padding-top: 2.5rem !important;
    padding-bottom: 1rem !important;
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
# CONSTANTES
# =========================================================

DB_FILE = "perfumes_data.csv"

ESTACOES_LISTA = [
    "COLÓNIAS",
    "PRIMAVERA",
    "VERÃO",
    "PRI/VER",
    "OUTONO",
    "INVERNO",
    "OUT/INV",
    "MEIA-ESTAÇÃO",
    "GERAL"
]

OCASIOES_OPCOES = [
    "CASUAL DIA",
    "CASUAL NOITE",
    "TRABALHO",
    "FORMAL DIA",
    "FORMAL NOITE",
    "ESPECIAL"
]

# =========================================================
# FUNÇÕES
# =========================================================

def remover_acentos(texto):

    if not isinstance(texto, str):
        texto = str(texto)

    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def padronizar_texto(texto):
    """Transforma termos como 'Cítricos' e 'cítrico' em 'Citrico'."""
    if not isinstance(texto, str) or texto == "":
        return ""
    
    # Remove acentos e converte para minúsculas
    texto = remover_acentos(texto).strip()
    
    # Normalização simples de plural (remove 's' final se a palavra for longa)
    if texto.endswith('s') and len(texto) > 3:
        texto = texto[:-1]
        
    return texto.upper() # Mantemos em maiúsculas para os gráficos de categorias fixas

def load_data():

    cols = [
        "Ano",
        "Nome do Perfume",
        "Estações do Ano",
        "Ocasiões de Uso",
        "Família Olfativa",
        "Notas Olfativas",
        "Marca",
        "Perfumista"
    ]

    if os.path.exists(DB_FILE):

        try:

            df = pd.read_csv(
                DB_FILE,
                encoding='utf-8-sig'
            )

            df.columns = df.columns.str.strip()

            # GARANTIR TODAS AS COLUNAS
            for col in cols:

                if col not in df.columns:
                    df[col] = ""

            return df.fillna("").astype(str)[cols]

        except Exception as e:

            st.error(f"Erro ao carregar CSV: {e}")

            return pd.DataFrame(columns=cols)

    return pd.DataFrame(columns=cols)

# =========================================================
# CARREGAR DADOS
# =========================================================

df = load_data()

# =========================================================
# TÍTULO
# =========================================================

st.markdown(
    "<h2 style='text-align:left; font-size:34px;'>Caixa dos Perfumes</h2>",
    unsafe_allow_html=True
)

# =========================================================
# MENU
# =========================================================

menu = [
    "🔍 Pesquisar",
    "➕ Adicionar",
    "📝 Editar",
    "🗑️ Apagar"
]

choice = st.sidebar.radio(
    "MENU DE GESTÃO",
    menu
)

# =========================================================
# PESQUISAR
# =========================================================

if choice == "🔍 Pesquisar":

    search = st.text_input(
        "",
        placeholder="Pesquisar..."
    )

    result = df.copy()

    # -----------------------------------------------------
    # FILTRO DE PESQUISA
    # -----------------------------------------------------

    if search:

        termos = search.split()

        for termo in termos:

            t_norm = remover_acentos(termo)

            mask = result.apply(
                lambda row:
                row.astype(str)
                .map(remover_acentos)
                .str.contains(t_norm)
                .any(),
                axis=1
            )

            result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

    # -----------------------------------------------------
    # TABELA
    # -----------------------------------------------------

    if not df.empty:

        st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            disabled=True,

            column_config={

                "Ano":
                st.column_config.TextColumn(
                    "Ano",
                    width=55
                ),

                "Nome do Perfume":
                st.column_config.TextColumn(
                    "Nome do Perfume",
                    width="medium"
                ),

                "Marca":
                st.column_config.TextColumn(
                    "Marca",
                    width=120
                ),

                "Notas Olfativas":
                st.column_config.TextColumn(
                    "Notas Olfativas",
                    width=220
                ),

                "Estações do Ano":
                st.column_config.TextColumn(
                    "Estações do Ano",
                    width=120
                ),

                "Ocasiões de Uso":
                st.column_config.TextColumn(
                    "Ocasiões de Uso",
                    width=120
                )
            }
        )

        # -------------------------------------------------
        # DOWNLOAD CSV
        # -------------------------------------------------

        if not result.empty:

            _, col_center, _ = st.columns([1, 2, 1])

            with col_center:

                csv = result.to_csv(
                    index=False
                ).encode('utf-8-sig')

                st.download_button(
                    "📥 Download (CSV)",
                    data=csv,
                    file_name="meus_perfumes.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.markdown("---")

        # -------------------------------------------------
        # CONFIG GRÁFICOS
        # -------------------------------------------------

        config_fixo = {
            'staticPlot': True
        }

        paleta_minimalista = [
            '#8EACCD',
            '#94A684',
            '#B0A695',
            '#C08261',
            '#607274',
            '#E5BA73'
        ]

        # =================================================
        # PRIMEIRA LINHA DE GRÁFICOS
        # =================================================

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # ESTAÇÕES DO ANO
        # -------------------------------------------------

        with col1:

            c_est = (
                df["Estações do Ano"]
                .astype(str)
                .str.split(',')
                .explode()
                .str.strip()
                .map(padronizar_texto)
            )

            c_est = (
                c_est[c_est != ""]
                .value_counts()
                .reset_index(name="count")
                .rename(columns={
                    "index": "Estações do Ano"
                })
            )

            fig1 = px.bar(
                c_est,
                x="Estações do Ano",
                y="count",
                text="count",
                color_discrete_sequence=['#B0A695']
            )

            fig1.update_traces(
                width=0.45,
                textposition='outside'
            )

            fig1.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(t=20, b=10),
                height=420
            )

            st.plotly_chart(
                fig1,
                use_container_width=True,
                config=config_fixo
            )

        # -------------------------------------------------
        # NOTAS OLFATIVAS
        # -------------------------------------------------

        with col2:

            n_s = (
                df["Notas Olfativas"]
                .astype(str)
                .str.split(',')
                .explode()
                .str.strip()
                .map(padronizar_texto)
            )

            c_not = (
                n_s[n_s != ""]
                .value_counts()
                .nlargest(30)
                .reset_index(name="count")
                .rename(columns={
                    "index": "Notas Olfativas"
                })
            )

            altura_notas = max(
                400,
                len(c_not) * 22
            )

            fig2 = px.bar(
                c_not,
                x="count",
                y="Notas Olfativas",
                orientation='h',
                text="count",
                color_discrete_sequence=['#8EACCD']
            )

            fig2.update_layout(
                yaxis={
                    'categoryorder': 'total ascending'
                },
                height=altura_notas,
                margin=dict(t=10, b=10),
                xaxis_title=None,
                yaxis_title=None
            )

            st.plotly_chart(
                fig2,
                use_container_width=True,
                config=config_fixo
            )

        # =================================================
        # SEGUNDA LINHA DE GRÁFICOS
        # =================================================

        col3, col4 = st.columns(2)

        # -------------------------------------------------
        # OCASIÕES DE USO (ABAIXO DAS ESTAÇÕES)
        # -------------------------------------------------

        with col3:

            o_s = (
                df["Ocasiões de Uso"]
                .astype(str)
                .str.split(',')
                .explode()
                .str.strip()
                .map(padronizar_texto)
            )

            c_oc = (
                o_s[o_s != ""]
                .value_counts()
                .reset_index(name="count")
                .rename(columns={
                    "index": "Ocasiões"
                })
            )

            fig_oc = px.bar(
                c_oc,
                x="Ocasiões",
                y="count",
                text="count",
                color_discrete_sequence=['#C08261']
            )

            fig_oc.update_traces(
                width=0.45,
                textposition='outside'
            )

            fig_oc.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(t=20, b=10),
                height=420
            )

            st.plotly_chart(
                fig_oc,
                use_container_width=True,
                config=config_fixo
            )

        # -------------------------------------------------
        # FAMÍLIA OLFATIVA
        # -------------------------------------------------

        with col4:

            f_s = (
                df["Família Olfativa"]
                .astype(str)
                .str.split('/')
                .explode()
                .str.strip()
                .map(padronizar_texto)
            )

            c_fam = (
                f_s[f_s != ""]
                .value_counts()
                .nlargest(6)
                .reset_index(name="count")
                .rename(columns={
                    "index": "Família Olfativa"
                })
            )

            fig3 = px.pie(
                c_fam,
                values='count',
                names='Família Olfativa',
                color_discrete_sequence=paleta_minimalista
            )

            fig3.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.15,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=10, b=100),
                height=340
            )

            st.plotly_chart(
                fig3,
                use_container_width=True,
                config=config_fixo
            )

        # =================================================
        # TERCEIRA LINHA DE GRÁFICOS
        # =================================================

        col5, col6 = st.columns(2)

        # -------------------------------------------------
        # PERFUMISTAS
        # -------------------------------------------------

        with col5:

            c_perf = (
                df["Perfumista"]
                .replace(["", "nan"], "Desconhecido")
                .map(padronizar_texto)
                .value_counts()
                .nlargest(15)
                .reset_index(name="count")
                .rename(columns={
                    "index": "Perfumista"
                })
            )

            fig4 = px.bar(
                c_perf,
                x="count",
                y="Perfumista",
                orientation='h',
                text="count",
                color_discrete_sequence=['#94A684']
            )

            fig4.update_layout(
                yaxis={
                    'categoryorder': 'total ascending'
                },
                height=450,
                margin=dict(t=10, b=10),
                xaxis_title=None,
                yaxis_title=None
            )

            st.plotly_chart(
                fig4,
                use_container_width=True,
                config=config_fixo
            )

        # -------------------------------------------------
        # MARCAS (FINAL DE TUDO)
        # -------------------------------------------------

        with col6:

            c_marca = (
                df["Marca"]
                .replace(["", "nan"], "Desconhecido")
                .map(padronizar_texto)
                .value_counts()
                .nlargest(15)
                .reset_index(name="count")
                .rename(columns={
                    "index": "Marca"
                })
            )

            fig_marca = px.bar(
                c_marca,
                x="count",
                y="Marca",
                orientation='h',
                text="count",
                color_discrete_sequence=['#607274']
            )

            fig_marca.update_layout(
                yaxis={
                    'categoryorder': 'total ascending'
                },
                height=450,
                margin=dict(t=10, b=10),
                xaxis_title=None,
                yaxis_title=None
            )

            st.plotly_chart(
                fig_marca,
                use_container_width=True,
                config=config_fixo
            )

# =========================================================
# ADICIONAR
# =========================================================

elif choice == "➕ Adicionar":

    st.subheader("Novo Registo")

    with st.form("add"):

        c1, c2 = st.columns(2)

        with c1:

            nome = st.text_input(
                "Nome do Perfume *"
            )

            marca = st.text_input(
                "Marca"
            )

            est = st.multiselect(
                "Estações",
                ESTACOES_LISTA
            )

            oc = st.multiselect(
                "Ocasiões de Uso",
                OCASIOES_OPCOES
            )

        with c2:

            fam = st.text_input(
                "Família Olfativa"
            )

            perf = st.text_input(
                "Perfumista"
            )

            ano = st.text_input(
                "Ano"
            )

            notas = st.text_area(
                "Notas Olfativas"
            )

        if st.form_submit_button("Guardar"):

            if nome:

                new = pd.DataFrame([{
                    "Ano": ano,
                    "Nome do Perfume": nome,
                    "Estações do Ano": ", ".join(est),
                    "Ocasiões de Uso": ", ".join(oc),
                    "Família Olfativa": fam,
                    "Notas Olfativas": notas,
                    "Marca": marca,
                    "Perfumista": perf
                }])

                df = pd.concat(
                    [df, new],
                    ignore_index=True
                )

                df.to_csv(
                    DB_FILE,
                    index=False,
                    encoding='utf-8-sig'
                )

                st.success("Guardado!")

                st.rerun()

# =========================================================
# EDITAR
# =========================================================

elif choice == "📝 Editar":

    st.subheader("Editar")

    if not df.empty:

        sel = st.selectbox(
            "Selecione:",
            sorted(
                df["Nome do Perfume"]
                .unique()
                .tolist()
            )
        )

        idx = df[
            df["Nome do Perfume"] == sel
        ].index[0]

        at_oc = [
            x.strip()
            for x in str(
                df.at[idx, "Ocasiões de Uso"]
            ).split(",")
            if x.strip() in OCASIOES_OPCOES
        ]

        at_est = [
            x.strip()
            for x in str(
                df.at[idx, "Estações do Ano"]
            ).split(",")
            if x.strip() in ESTACOES_LISTA
        ]

        with st.form("edit"):

            c1, c2 = st.columns(2)

            with c1:

                e_n = st.text_input(
                    "Nome",
                    value=df.at[
                        idx,
                        "Nome do Perfume"
                    ]
                )

                e_m = st.text_input(
                    "Marca",
                    value=df.at[
                        idx,
                        "Marca"
                    ]
                )

                e_e = st.multiselect(
                    "Estações",
                    ESTACOES_LISTA,
                    default=at_est
                )

                e_oc = st.multiselect(
                    "Ocasiões",
                    OCASIOES_OPCOES,
                    default=at_oc
                )

            with c2:

                e_f = st.text_input(
                    "Família",
                    value=df.at[
                        idx,
                        "Família Olfativa"
                    ]
                )

                e_p = st.text_input(
                    "Perfumista",
                    value=df.at[
                        idx,
                        "Perfumista"
                    ]
                )

                e_a = st.text_input(
                    "Ano",
                    value=df.at[
                        idx,
                        "Ano"
                    ]
                )

                e_not = st.text_area(
                    "Notas",
                    value=df.at[
                        idx,
                        "Notas Olfativas"
                    ]
                )

            if st.form_submit_button("Atualizar"):

                df.loc[idx] = [
                    e_a,
                    e_n,
                    ", ".join(e_e),
                    ", ".join(e_oc),
                    e_f,
                    e_not,
                    e_m,
                    e_p
                ]

                df.to_csv(
                    DB_FILE,
                    index=False,
                    encoding='utf-8-sig'
                )

                st.success("Atualizado!")

                st.rerun()

# =========================================================
# APAGAR
# =========================================================

elif choice == "🗑️ Apagar":

    st.subheader("Eliminar")

    if not df.empty:

        p_del = st.selectbox(
            "Perfume:",
            sorted(
                df["Nome do Perfume"]
                .unique()
                .tolist()
            )
        )

        if st.button("Confirmar"):

            df = df[
                df["Nome do Perfume"] != p_del
            ]

            df.to_csv(
                DB_FILE,
                index=False,
                encoding='utf-8-sig'
            )

            st.warning("Eliminado.")

            st.rerun()
