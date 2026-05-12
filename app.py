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

st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == "🔍 Pesquisar":
    # Adicionamos uma linha com dois elementos: o campo de busca e o seletor de coluna
    col_busca, col_filtro = st.columns([3, 1])
    
    with col_busca:
        search = st.text_input("pesquisa", placeholder="...")
    
    with col_filtro:
        # Permite escolher onde pesquisar
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", "Estações do Ano", "Ocasiões de Uso", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca)
        
    result = df.copy()

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            
            # Criamos um padrão que procura a palavra exata (isolada por espaços ou vírgulas)
            # \b garante que "Rosa" não coincida com "Pimenta Rosa" ou "Rosário"
            padrao_exato = rf'\b{t_norm}\b'
            
            if local_busca == "Tudo":
                mask = result.apply(
                    lambda row: row.astype(str).map(remover_acentos).str.contains(padrao_exato, regex=True).any(), 
                    axis=1
                )
            else:
                mask = result[local_busca].astype(str).map(remover_acentos).str.contains(padrao_exato, regex=True)
            
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

        # CONFIG GRÁFICOS
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']

        col1, col2 = st.columns(2)

        # 1. ESTAÇÕES DO ANO
        with col1:
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            c_est.columns = ["Estações do Ano", "count"]

            fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#B0A695'])
            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=420)
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

        # 2. NOTAS OLFATIVAS (Com Unificação)
        with col2:
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            c_not.columns = ["Notas Olfativas", "count"]

            altura_notas = max(400, len(c_not) * 22)
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=altura_notas, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        col3, col4 = st.columns(2)

        # 3. FAMÍLIA OLFATIVA (Com Unificação)
        with col3:
            # Tratando tanto '/' quanto ',' como separadores
            f_s = df["Família Olfativa"].str.replace('/', ',').str.split(',').explode().str.strip()
            c_fam = f_s[f_s != ""].apply(padronizar_texto).value_counts().nlargest(8).reset_index(name="count")
            c_fam.columns = ["Família Olfativa", "count"]

            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', color_discrete_sequence=paleta_minimalista)
            fig3.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), margin=dict(t=10, b=100), height=340)
            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        # 4. PERFUMISTAS (Com Unificação)
        with col4:
            c_perf = df["Perfumista"].replace(["", "nan"], "Desconhecido")
            c_perf = c_perf.apply(lambda x: padronizar_texto(x) if x != "Desconhecido" else x)
            c_perf = c_perf.value_counts().nlargest(15).reset_index(name="count")
            c_perf.columns = ["Perfumista", "count"]

            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR / EDITAR (Lógica de salvamento com padronização)
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
                # Padronizar as entradas de texto livre antes de guardar
                fam_clean = ", ".join([padronizar_texto(f) for f in fam.replace('/', ',').split(',') if f.strip()])
                notas_clean = ", ".join([padronizar_texto(n) for n in notas.split(',') if n.strip()])
                perf_clean = padronizar_texto(perf)

                new = pd.DataFrame([{
                    "Ano": ano,
                    "Nome do Perfume": nome,
                    "Estações do Ano": ", ".join(est),
                    "Ocasiões de Uso": ", ".join(oc),
                    "Família Olfativa": fam_clean,
                    "Notas Olfativas": notas_clean,
                    "Marca": marca,
                    "Perfumista": perf_clean
                }])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Guardado com sucesso!")
                st.rerun()

elif choice == "📝 Editar":
    st.subheader("Editar")
    if not df.empty:
        sel = st.selectbox("Selecione:", sorted(df["Nome do Perfume"].unique().tolist()))
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
                # Padronizar ao atualizar
                fam_edit = ", ".join([padronizar_texto(f) for f in e_f.replace('/', ',').split(',') if f.strip()])
                notas_edit = ", ".join([padronizar_texto(n) for n in e_not.split(',') if n.strip()])
                perf_edit = padronizar_texto(e_p)

                df.loc[idx] = [e_a, e_n, ", ".join(e_e), ", ".join(e_oc), fam_edit, notas_edit, e_m, perf_edit]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
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
            
