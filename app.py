import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# =========================================================
# GESTÃO DE ESTADO (Para Edição Direta)
# =========================================================
if "edit_perfume" not in st.session_state:
    st.session_state.edit_perfume = None

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
    "CASUAL DIA", "CASUAL NOITE", "TRABALHO PRI/VER", 
    "TRABALHO OUT/INV", "FORMAL DIA", "FORMAL NOITE", "ESPECIAL", "GERAL"
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
    if not texto or not isinstance(texto, str):
        return ""
    texto_limpo = remover_acentos(texto).strip()
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
            
            df["Ano"] = pd.to_numeric(df["Ano"], errors='coerce')
            df["Ano"] = df["Ano"].apply(lambda x: str(int(x)) if pd.notnull(x) else "")
            
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

st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
default_index = 2 if st.session_state.edit_perfume else 0
choice = st.sidebar.radio("MENU DE GESTÃO", menu, index=default_index)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == "🔍 Pesquisar":
    col_busca, col_filtro = st.columns([3, 1])
    
    with col_busca:
        search = st.text_input("pesquisa", placeholder="🔍")
    
    with col_filtro:
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", "Estações do Ano", "Ocasiões de Uso", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca)
        
    result = df.copy()
    result.insert(0, "Editar", False)

    if search:
        if local_busca == "Notas Olfativas":
            t_padronizado = padronizar_texto(search)
            def match_exact_note(cell_value):
                if not cell_value: return False
                notas_no_banco = [padronizar_texto(n) for n in str(cell_value).split(",")]
                return t_padronizado in notas_no_banco
            mask = result["Notas Olfativas"].apply(match_exact_note)
            result = result[mask].copy()
        else:
            termos = search.split()
            for termo in termos:
                t_norm = remover_acentos(termo)
                if local_busca == "Tudo":
                    mask = result.apply(
                        lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(),
                        axis=1
                    )
                else:
                    mask = result[local_busca].astype(str).map(remover_acentos).str.contains(t_norm)
                result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

    if not df.empty:
        edited_df = st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Editar": st.column_config.CheckboxColumn("", default=False),
                "Ano": st.column_config.TextColumn("Ano", width=55),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Marca": st.column_config.TextColumn("Marca", width=120),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=120),
                "Ocasiões de Uso": st.column_config.TextColumn("Ocasiões de Uso", width=120)
            },
            disabled=[c for c in result.columns if c != "Editar"]
        )

        check_click = edited_df[edited_df["Editar"] == True]
        if not check_click.empty:
            st.session_state.edit_perfume = check_click.iloc[0]["Nome do Perfume"]
            st.rerun()

        if not result.empty:
            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:
                csv = result.drop(columns=["Editar"]).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download (CSV)", data=csv, file_name="meus_perfumes.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']
        col1, col2 = st.columns(2)

        with col1:
            # GRÁFICO 1: ESTAÇÕES
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            c_est.columns = ["Estações do Ano", "count"]
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=350)
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            # GRÁFICO 5: OCASIÕES DE USO
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc != ""].apply(lambda x: x.upper()).value_counts().reset_index(name="count")
            c_oc.columns = ["Ocasiões", "count"]
            fig5 = px.bar(c_oc, x="Ocasiões", y="count", text="count", color_discrete_sequence=['#C08261'])
            fig5.update_traces(width=0.45, textposition='outside')
            fig5.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=40, b=10), height=350)
            st.plotly_chart(fig5, use_container_width=True, config=config_fixo)

            # MAPA DE CALOR DIA/NOITE
            h_df = df.copy()
            h_df["Estações do Ano"] = h_df["Estações do Ano"].astype(str).str.split(',')
            h_df["Ocasiões de Uso"] = h_df["Ocasiões de Uso"].astype(str).str.split(',')
            h_df = h_df.explode("Estações do Ano").explode("Ocasiões de Uso")
            
            h_df["Estação"] = h_df["Estações do Ano"].astype(str).str.strip().apply(padronizar_texto)
            h_df["Oc_Limpa"] = h_df["Ocasiões de Uso"].astype(str).str.strip().str.upper()
            
            map_p = {
                "CASUAL DIA": "DIA", "TRABALHO PRI/VER": "DIA", "TRABALHO OUT/INV": "DIA", "FORMAL DIA": "DIA",
                "CASUAL NOITE": "NOITE", "FORMAL NOITE": "NOITE"
            }
            h_df["Período"] = h_df["Oc_Limpa"].map(map_p)
            h_df = h_df.dropna(subset=["Período"])
            h_df = h_df[h_df["Estação"] != ""]
            
            if not h_df.empty:
                h_pv = h_df.groupby(["Período", "Estação"]).size().unstack(fill_value=0)
                e_ordem = [padronizar_texto(e) for e in ESTACOES_LISTA if padronizar_texto(e) in h_pv.columns]
                h_pv = h_pv.reindex(columns=e_ordem)
                # Garante ordem DIA -> NOITE no eixo Y
                p_ordem = [p for p in ["DIA", "NOITE"] if p in h_pv.index]
                h_pv = h_pv.reindex(index=p_ordem)
                
                fig_h = px.imshow(h_pv, text_auto=True, color_continuous_scale=[[0, '#fdfbf7'], [1, '#8EACCD']])
                fig_h.update_layout(height=180, margin=dict(t=30, b=10, l=5, r=5), xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
                st.plotly_chart(fig_h, use_container_width=True, config=config_fixo)

        with col2:
            # GRÁFICO 2: NOTAS
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            c_not.columns = ["Notas Olfativas", "count"]
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=910, margin=dict(t=20, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        col3, col4 = st.columns(2)
        with col3:
            # GRÁFICO 3: FAMÍLIA
            f_s = df["Família Olfativa"].str.replace('/', ',').str.split(',').explode().str.strip()
            c_fam = f_s[f_s != ""].apply(padronizar_texto).value_counts().nlargest(8).reset_index(name="count")
            c_fam.columns = ["Família Olfativa", "count"]
            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', color_discrete_sequence=paleta_minimalista)
            fig3.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), margin=dict(t=10, b=100), height=340)
            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        with col4:
            # GRÁFICO 4: PERFUMISTAS
            c_perf = df[df["Perfumista"].str.strip() != ""]["Perfumista"]
            c_perf = c_perf.apply(padronizar_texto).value
                
