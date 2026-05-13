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
.block-container { padding-top: 2.5rem !important; }
*:focus { outline: none !important; border-color: #dcdcdc !important; box-shadow: none !important; }
[data-testid="stSidebar"] .stRadio label p {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #4F709C !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES E AUXILIARES
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
    if not isinstance(texto, str): return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def padronizar_texto(texto):
    if not texto or not isinstance(texto, str): return ""
    texto_limpo = remover_acentos(texto).strip()
    if texto_limpo.endswith('s') and len(texto_limpo) > 4: texto_limpo = texto_limpo[:-1]
    return texto_limpo.capitalize()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", 
            "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            for col in cols:
                if col not in df.columns: df[col] = ""
            df["Ano"] = pd.to_numeric(df["Ano"], errors='coerce').fillna(0).astype(int).astype(str).replace("0", "")
            return df.fillna("").astype(str)[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# =========================================================
# CARREGAR E EXIBIR
# =========================================================

df = load_data()
st.markdown("<h2 style='text-align:left; font-size:37px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("MENU DE GESTÃO", menu, index=2 if st.session_state.edit_perfume else 0)

# =========================================================
# 1. PESQUISAR E DASHBOARD
# =========================================================

if choice == "🔍 Pesquisar":
    c_busca, c_filtro = st.columns([3, 1])
    with c_busca: search = st.text_input("pesquisa", placeholder="🔍")
    with c_filtro: local_busca = st.selectbox("filtros", ["Tudo", "Notas Olfativas", "Família Olfativa", "Marca", "Perfumista"])
        
    result = df.copy()
    result.insert(0, "Editar", False)

    if search:
        t_norm = remover_acentos(search)
        if local_busca == "Tudo":
            mask = result.apply(lambda r: r.astype(str).map(remover_acentos).str.contains(t_norm).any(), axis=1)
        else:
            mask = result[local_busca].astype(str).map(remover_acentos).str.contains(t_norm)
        result = result[mask]

    st.write(f"{len(result)} perfumes encontrados")
    
    if not df.empty:
        # Tabela de Dados
        edited_df = st.data_editor(
            result.reset_index(drop=True),
            use_container_width=True, hide_index=True,
            column_config={"Editar": st.column_config.CheckboxColumn("", default=False), "Ano": st.column_config.TextColumn("Ano", width=55)},
            disabled=[c for c in result.columns if c != "Editar"]
        )

        if edited_df["Editar"].any():
            st.session_state.edit_perfume = edited_df[edited_df["Editar"]]["Nome do Perfume"].values[0]
            st.rerun()

        st.markdown("---")
        
        # --- DASHBOARD COM GRÁFICO ARANHA ---
        col1, col2 = st.columns(2)
        config_fixo = {'staticPlot': True}
        
        with col1:
            # 1. Estações (Barras)
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index()
            fig1 = px.bar(c_est, x=c_est.columns[0], y='count', text='count', color_discrete_sequence=['#B0A695'])
            fig1.update_layout(xaxis_title=None, yaxis_title=None, height=300, margin=dict(t=20, b=0))
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            # 2. Perfil de Uso (GRÁFICO ARANHA)
            st.write("**Perfil de Ocasiões**")
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc.isin(OCASIOES_OPCOES)].value_counts().reindex(OCASIOES_OPCOES, fill_value=0).reset_index()
            c_oc.columns = ["Ocasião", "Qtd"]
            
            fig_spider = px.line_polar(c_oc, r='Qtd', theta='Ocasião', line_close=True)
            fig_spider.update_traces(fill='toself', line_color='#C08261', fillcolor='rgba(192, 130, 97, 0.3)')
            fig_spider.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False)), height=380, margin=dict(t=30, b=30))
            st.plotly_chart(fig_spider, use_container_width=True)

        with col2:
            # 3. Notas (Ranking Horizontal)
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(25).reset_index()
            fig2 = px.bar(c_not, x='count', y=c_not.columns[0], orientation='h', text='count', color_discrete_sequence=['#8EACCD'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=750, margin=dict(t=20, b=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR / EDITAR / APAGAR (Lógica Simplificada)
# =========================================================

elif choice == "➕ Adicionar":
    with st.form("add"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *")
            marca = st.text_input("Marca")
            est = st.multiselect("Estações", ESTACOES_LISTA)
            oc = st.multiselect("Ocasiões", OCASIOES_OPCOES)
        with c2:
            fam = st.text_input("Família Olfativa")
            perf = st.text_input("Perfumista")
            ano = st.text_input("Ano")
            not_ol = st.text_area("Notas (separadas por vírgula)")
        
        if st.form_submit_button("Guardar"):
            if nome:
                new_row = pd.DataFrame([[ano, nome, ", ".join(est), ", ".join(oc), fam, not_ol, marca, perf]], columns=df.columns)
                pd.concat([df, new_row]).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success("Adicionado!")
                st.rerun()

elif choice == "📝 Editar":
    if not df.empty:
        sel = st.selectbox("Escolha o perfume:", sorted(df["Nome do
            
