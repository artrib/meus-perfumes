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
    "COLÓNIAS", "PRIMAVERA", "VERÃO", "PRI/VER", 
    "OUTONO", "INVERNO", "OUT/INV", "MEIA-ESTAÇÃO", "GERAL"
]

OCASIOES_OPCOES = [
    "CASUAL DIA", "CASUAL NOITE", "TRABALHO", 
    "FORMAL DIA", "FORMAL NOITE", "ESPECIAL"
]

# =========================================================
# FUNÇÕES DE TRATAMENTO DE TEXTO
# =========================================================

def remover_acentos(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def padronizar_texto(texto):
    """Transforma 'cítrico', 'CITRICO', 'Cítricos' em 'Citrico'"""
    if not texto or not isinstance(texto, str):
        return ""
    # Remove acentos e converte para minúsculas
    texto_limpo = remover_acentos(texto).strip()
    # Remove o 's' final para unificar singular/plural (opcional, mas útil para notas)
    if texto_limpo.endswith('s') and len(texto_limpo) > 4:
        texto_limpo = texto_limpo[:-1]
    return texto_limpo.capitalize()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", 
            "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
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

st.markdown("<h2 style='text-align:left; font-size:34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# =========================================================
# PESQUISAR
# =========================================================

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar...")
    result = df.copy()

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            mask = result.apply(
                lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(),
                axis=1
            )
            result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

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
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=120),
                "Ocasiões de Uso": st.column_config.TextColumn("Ocasiões de Uso", width=120)
            }
        )

        if not result.empty:
            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:
                csv = result.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")

        # =================================================
        # PRIMEIRA LINHA DE GRÁFICOS
        # =================================================

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # ESTAÇÕES DO ANO
        # -------------------------------------------------

        with col1:
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            c_est.columns = ["Estações do Ano", "count"]

            fig1 = px.bar(
                c_est,
                x="Estações do Ano",
                y="count",
                text="count",
                color_discrete_sequence=['#B0A695']
            )

            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(
                xaxis_title=None, yaxis_title=None,
                margin=dict(t=20, b=10), height=400
            )

            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            # -------------------------------------------------
            # NOVO: OCASIÕES DE USO (Logo abaixo das Estações)
            # -------------------------------------------------
            st.write("") # Espaçador
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc != ""].value_counts().reset_index(name="count")
            c_oc.columns = ["Ocasião", "count"]

            fig_oc = px.bar(
                c_oc,
                x="count",
                y="Ocasião",
                orientation='h',
                text="count",
                color_discrete_sequence=['#C08261']
            )

            fig_oc.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title=None, yaxis_title=None,
                margin=dict(t=20, b=10), height=350
            )
            st.plotly_chart(fig_oc, use_container_width=True, config=config_fixo)

        # -------------------------------------------------
        # NOTAS OLFATIVAS
        # -------------------------------------------------

        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            c_not.columns = ["Notas Olfativas", "count"]

            altura_notas = max(400, len(c_not) * 22)

            fig2 = px.bar(
                c_not,
                x="count",
                y="Notas Olfativas",
                orientation='h',
                text="count",
                color_discrete_sequence=['#8EACCD']
            )

            fig2.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=770, # Ajustado para alinhar com os dois gráficos da esquerda
                margin=dict(t=10, b=10),
                xaxis_title=None, yaxis_title=None
            )

            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        # =================================================
        # SEGUNDA LINHA DE GRÁFICOS
        # =================================================

        col3, col4 = st.columns(2)

        # -------------------------------------------------
        # FAMÍLIA OLFATIVA
        # -------------------------------------------------

        with col3:
            f_s = df["Família Olfativa"].str.replace('/', ',').str.split(',').explode().str.strip()
            c_fam = f_s[f_s != ""].apply(padronizar_texto).value_counts().nlargest(8).reset_index(name="count")
            c_fam.columns = ["Família Olfativa", "count"]

            fig3 = px.pie(
                c_fam,
                values='count',
                names='Família Olfativa',
                color_discrete_sequence=paleta_minimalista
            )

            fig3.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                margin=dict(t=10, b=100), height=340
            )

            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        # -------------------------------------------------
        # PERFUMISTAS
        # -------------------------------------------------

        with col4:
            c_perf = df["Perfumista"].replace(["", "nan"], "Desconhecido")
            c_perf = c_perf.apply(lambda x: padronizar_texto(x) if x != "Desconhecido" else x)
            c_perf = c_perf.value_counts().nlargest(15).reset_index(name="count")
            c_perf.columns = ["Perfumista", "count"]

            fig4 = px.bar(
                c_perf,
                x="count",
                y="Perfumista",
                orientation='h',
                text="count",
                color_discrete_sequence=['#94A684']
            )

            fig4.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=450,
                margin=dict(t=10, b=10),
                xaxis_title=None, yaxis_title=None
            )

            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

        # =================================================
        # LINHA FINAL: MARCAS
        # =================================================
        
        st.markdown("---")
        st.subheader("Distribuição por Marcas")
        
        c_marca = df["Marca"].replace(["", "nan"], "N/A")
        c_marca = c_marca.apply(padronizar_texto).value_counts().nlargest(20).reset_index(name="count")
        c_marca.columns = ["Marca", "count"]

        fig_marca = px.bar(
            c_marca,
            x="Marca",
            y="count",
            text="count",
            color_discrete_sequence=['#607274']
        )

        fig_marca.update_traces(textposition='outside')
        fig_marca.update_layout(
            xaxis_title=None, yaxis_title=None,
            margin=dict(t=20, b=10), height=400
        )
        st.plotly_chart(fig_marca, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR / EDITAR / APAGAR (Lógica permanece igual à anterior)
# =========================================================
