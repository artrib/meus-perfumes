import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px

# =========================================================
# GESTÃO DE ESTADO
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
# CONSTANTES E TRATAMENTO
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
            return df.fillna("").astype(str)[cols]
        except Exception as e:
            st.error(f"Erro ao carregar CSV: {e}")
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# =========================================================
# INTERFACE PRINCIPAL
# =========================================================

df = load_data()

st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
default_index = 2 if st.session_state.edit_perfume else 0
choice = st.sidebar.radio("MENU DE GESTÃO", menu, index=default_index)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == "🔍 Pesquisar":
    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        search = st.text_input("pesquisa", placeholder="...")
    with col_filtro:
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", "Estações do Ano", "Ocasiões de Uso", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca)
        
    result = df.copy()
    result.insert(0, "Editar", False)

    if search:
        if local_busca == "Notas Olfativas":
            t_padronizado = padronizar_texto(search)
            mask = result["Notas Olfativas"].apply(lambda cell: t_padronizado in [padronizar_texto(n) for n in str(cell).split(",")])
            result = result[mask].copy()
        else:
            termos = search.split()
            for termo in termos:
                t_norm = remover_acentos(termo)
                if local_busca == "Tudo":
                    mask = result.apply(lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm).any(), axis=1)
                else:
                    mask = result[local_busca].astype(str).map(remover_acentos).str.contains(t_norm)
                result = result[mask].copy()

    st.write(f"{len(result)} perfumes")

    if not df.empty:
        edited_df = st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={"Editar": st.column_config.CheckboxColumn("", default=False), "Ano": st.column_config.TextColumn("Ano", width=55)},
            disabled=[c for c in result.columns if c != "Editar"]
        )

        check_click = edited_df[edited_df["Editar"] == True]
        if not check_click.empty:
            st.session_state.edit_perfume = check_click.iloc[0]["Nome do Perfume"]
            st.rerun()

        st.markdown("---")
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']
        
        col1, col2 = st.columns(2)

        with col1:
            # ESTAÇÕES
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=350)
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            # OCASIÕES DE USO
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc != ""].apply(lambda x: x.upper()).value_counts().reset_index(name="count")
            fig5 = px.bar(c_oc, x="Ocasiões", y="count", text="count", color_discrete_sequence=['#C08261'])
            fig5.update_traces(width=0.45, textposition='outside')
            fig5.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=40, b=10), height=350)
            st.plotly_chart(fig5, use_container_width=True, config=config_fixo)

        with col2:
            # NOTAS
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=750, margin=dict(t=20, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- MAPA DE GAPS (HEATMAP) ---
        st.write("Análise de Gaps (Estação vs Ocasião)")
        # Lógica para cruzar Estações e Ocasiões
        df_heatmap = df.copy()
        df_heatmap['Estação'] = df_heatmap['Estações do Ano'].str.split(',')
        df_heatmap = df_heatmap.explode('Estação')
        df_heatmap['Ocasião'] = df_heatmap['Ocasiões de Uso'].str.split(',')
        df_heatmap = df_heatmap.explode('Ocasião')
        df_heatmap['Estação'] = df_heatmap['Estação'].str.strip().apply(lambda x: x.upper() if x else "")
        df_heatmap['Ocasião'] = df_heatmap['Ocasião'].str.strip().apply(lambda x: x.upper() if x else "")
        df_heatmap = df_heatmap[(df_heatmap['Estação'] != "") & (df_heatmap['Ocasião'] != "")]
        
        # Criar matriz de contagem
        matrix = df_heatmap.groupby(['Estação', 'Ocasião']).size().reset_index(name='Quantidade')
        matrix_pivot = matrix.pivot(index='Estação', columns='Ocasião', values='Quantidade').fillna(0)
        
        fig_heat = px.imshow(
            matrix_pivot,
            labels=dict(x="Ocasião", y="Estação", color="Qtd"),
            color_continuous_scale='Blues',
            text_auto=True
        )
        fig_heat.update_layout(margin=dict(t=10, b=10), height=450, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_heat, use_container_width=True, config=config_fixo)

        col3, col4 = st.columns(2)
        with col3:
            # FAMÍLIA
            f_s = df["Família Olfativa"].str.replace('/', ',').str.split(',').explode().str.strip()
            c_fam = f_s[f_s != ""].apply(padronizar_texto).value_counts().nlargest(8).reset_index(name="count")
            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', color_discrete_sequence=paleta_minimalista)
            fig3.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), margin=dict(t=10, b=100), height=340)
            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        with col4:
            # PERFUMISTAS
            c_perf = df[df["Perfumista"].str.strip() != ""]["Perfumista"]
            c_perf = c_perf.apply(padronizar_texto).value_counts().nlargest(15).reset_index(name="count")
            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

        # MARCAS (Final)
        st.markdown("---")
        c_marca = df[df["Marca"].str.strip() != ""]["Marca"]
        c_marca = c_marca.apply(lambda x: x.upper().strip()).value_counts().nlargest(20).reset_index(name="count")
        fig6 = px.bar(c_marca, x="Marca", y="count", text="count", color_discrete_sequence=['#607274'])
        fig6.update_traces(width=0.6, textposition='outside')
        fig6.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
        st.plotly_chart(fig6, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR / EDITAR / APAGAR (Logica inalterada)
# =========================================================

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
                fam_clean = ", ".join([padronizar_texto(f) for f in fam.replace('/', ',').split(',') if f.strip()])
                notas_clean = ", ".join([padronizar_texto(n) for n in notas.split(',') if n.strip()])
                new = pd.DataFrame([{"Ano": ano, "Nome do Perfume": nome, "Estações do Ano": ", ".join(est), "Ocasiões de Uso": ", ".join(oc), "Família Olfativa": fam_clean, "Notas Olfativas": notas_clean, "Marca": marca, "Perfumista": padronizar_texto(perf)}])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado!")
                st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar")
    if not df.empty:
        lista_perfumes = sorted(df["Nome do Perfume"].unique().tolist())
        idx_default = lista_perfumes.index(st.session_state.edit_perfume) if st.session_state.edit_perfume in lista_perfumes else 0
        sel = st.selectbox("Selecione:", lista_perfumes, index=idx_default)
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
                fam_edit = ", ".join([padronizar_texto(f) for f in e_f.replace('/', ',').split(',') if f.strip()])
                notas_edit = ", ".join([padronizar_texto(n) for n in e_not.split(',') if n.strip()])
                df.loc[idx] = [e_a, e_n, ", ".join(e_e), ", ".join(e_oc), fam_edit, notas_edit, e_m, padronizar_texto(e_p)]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.session_state.edit_perfume = None
                st.success("Atualizado!")
                st.rerun()

elif choice == "🗑️ Apagar":
    st.subheader("Eliminar")
    if not df.empty:
        p_del = st.selectbox("Perfume:", sorted(df["Nome do Perfume"].unique().tolist()))
        if st.button("Confirmar"):
            df = df[df["Nome do Perfume"] != p_del]
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.warning("Eliminado.")
            st.rerun()
