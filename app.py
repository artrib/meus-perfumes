import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px
import time

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
# CSS PERSONALIZADO (Adaptável a Light/Dark Mode)
# =========================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 1rem !important;
}

/* Remove outlines genéricos e sombras ao focar */
*:focus,
[data-baseweb="input"] > div:focus-within,
[data-testid="stDataEditor"] *:focus {
    outline: none !important;
    border-color: #dcdcdc !important;
    box-shadow: none !important;
}

/* --- CUSTOMIZAÇÃO DO RADIO MENU (SIDEBAR) --- */

/* 1. Altera o texto das opções (Tamanho e Cor dinâmica do tema) */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] .stRadio label p {
    font-size: 23px !important; /* Ajuste aqui o tamanho se quiser maior/menor */
    font-weight: 600 !important;
    color: var(--text-color) !important; /* Branco no Dark, Preto no Light automaticamente */
}

/* 2. Círculo não selecionado (Borda externa) */
[data-testid="stSidebar"] [data-fieldname="stRadio"] div[role="radiogroup"] div[data-id="stRadioOption"] div:first-child {
    border-color: var(--text-color) !important;
    opacity: 0.2;
}

/* 3. Círculo quando selecionado (Borda externa e a "bolinha" interior) */
[data-testid="stSidebar"] [data-fieldname="stRadio"] div[role="radiogroup"] div[data-id="stRadioOption"] input:checked + div {
    border-color: var(--text-color) !important;
}

[data-testid="stSidebar"] [data-fieldname="stRadio"] div[role="radiogroup"] div[data-id="stRadioOption"] input:checked + div ::before {
    background-color: var(--text-color) !important; /* Bolinha interna segue a cor do texto do tema */
}

/* Ajuste fino para garantir que o hover/foco do rádio não quebre as cores */
[data-testid="stSidebar"] [data-fieldname="stRadio"] div[role="radiogroup"] div[data-id="stRadioOption"]:hover div {
    border-color: var(--text-color) !important;
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
            # O 'sep=None' faz o pandas detectar se é vírgula ou ponto e vírgula
            # O 'engine=python' é necessário para usar a detecção automática
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig', sep=None, engine='python')
            
            df.columns = df.columns.str.strip()
            
            # Garante que todas as colunas necessárias existam
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            
            # --- CORREÇÃO DO ANO ---
            df["Ano"] = pd.to_numeric(df["Ano"], errors='coerce')
            df["Ano"] = df["Ano"].apply(lambda x: str(int(x)) if pd.notnull(x) else "")

            # REMOVE NOMES DE PERFUMES DIPLICADOS:
            df = df.drop_duplicates(subset=["Nome do Perfume"], keep='first')

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

st.markdown("<h2 style='text-align:left; font-size:37px; color: var(--text-color);'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================

menu = [" Pesquisar", " Adicionar", " Editar", " Apagar"]
default_index = 2 if st.session_state.edit_perfume else 0
choice = st.sidebar.radio("", menu, index=default_index)

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == " Pesquisar":
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

    # --- AQUI É ONDE ENTRA A CORREÇÃO DA CONTAGEM E DO INDEX ---
    
    # 1. Limpa linhas fantasma que tenham o nome do perfume em branco
    result = result[result["Nome do Perfume"].str.strip() != ""]
    
    # 2. Mostra o total real (vai passar a dizer 192 em vez de 193)
    st.write(f"**{len(result)}** perfumes")

    if not df.empty:
        # 3. Cria uma cópia para visualização e força o índice a começar em 1
        df_visual = result.reset_index(drop=True)
        df_visual.index = df_visual.index + 1  
        
        edited_df = st.data_editor(
            df_visual, # <--- Usamos o df com o índice corrigido aqui
            use_container_width=True,
            hide_index=True, # <--- Se queres ver os números de 1 a 192 na tabela, deixa False. Se não queres ver números nenhuns, muda para True.
            column_config={
                "Editar": st.column_config.CheckboxColumn("edit", width=30, default=False),
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
# =========================================================
# MODULO DE GRAFICOS 
# =========================================================
        st.markdown("---")
        config_fixo = {'staticPlot': True}
        paleta_minimalista = ['#8EACCD', '#94A684', '#B0A695', '#C08261', '#607274', '#E5BA73']
        col1, col2 = st.columns(2)

        with col1:
            # GRÁFICO 1: ESTAÇÕES
            c_est = df["Estações do Ano"].str.split(',').explode().str.strip()
            # Filtra vazios e padroniza para garantir que batam com a lista definida
            c_est = c_est[c_est != ""].apply(padronizar_texto).value_counts().reset_index(name="count")
            c_est.columns = ["Estações do Ano", "count"]
            
            # Define a ordem desejada das colunas conforme solicitado
            ordem_estacoes = [
                "Colonia", "Primavera", "Verao", "Pri/ver", 
                "Meia-estacao", "Outono", "Inverno", "Out/inv", "Geral"
            ]
            
            fig1 = px.bar(
                c_est, 
                x="Estações do Ano", 
                y="count", 
                text="count", 
                color_discrete_sequence=['#B0A695'],
                category_orders={"Estações do Ano": ordem_estacoes}
            )
            
            fig1.update_traces(width=0.45, textposition='outside')
            fig1.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                margin=dict(t=20, b=10), 
                height=350
            )
            st.plotly_chart(fig1, use_container_width=True, config=config_fixo)
            
            # GRÁFICO 5: OCASIÕES DE USO
            c_oc = df["Ocasiões de Uso"].str.split(',').explode().str.strip()
            c_oc = c_oc[c_oc != ""].value_counts().reset_index(name="count")
            c_oc.columns = ["Ocasiões", "count"]
            
            # Define a ordem desejada das colunas
            ordem_desejada = [
                "CASUAL DIA", "FORMAL DIA", "TRABALHO PRI/VER", 
                "TRABALHO OUT/INV", "FORMAL NOITE", "CASUAL NOITE", 
                "ESPECIAL", "GERAL"
            ]
            
            fig5 = px.bar(
                c_oc, 
                x="Ocasiões", 
                y="count", 
                text="count", 
                color_discrete_sequence=['#C08261'],
                category_orders={"Ocasiões": ordem_desejada}
            )
            
            fig5.update_traces(width=0.45, textposition='outside')
            fig5.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                margin=dict(t=40, b=10), 
                height=350
            )
            st.plotly_chart(fig5, use_container_width=True, config=config_fixo)

            # NOVO GRÁFICO: DIA E NOITE (Ying Yang)
            st.markdown("<br>", unsafe_allow_html=True)
            def classificar_periodo(row):
                oc = [o.strip().upper() for o in str(row["Ocasiões de Uso"]).split(',')]
                dia_tags = ["CASUAL DIA", "TRABALHO PRI/VER", "TRABALHO OUT/INV", "FORMAL DIA"]
                noite_tags = ["CASUAL NOITE", "FORMAL NOITE"]
                
                if any(tag in oc for tag in dia_tags): return "DIA"
                if any(tag in oc for tag in noite_tags): return "NOITE"
                return "OUTROS"

            df_temp = df.copy()
            df_temp["Periodo"] = df_temp.apply(classificar_periodo, axis=1)
            df_pie = df_temp[df_temp["Periodo"].isin(["DIA", "NOITE"])]["Periodo"].value_counts().reset_index()
            df_pie.columns = ["Periodo", "count"]
            
            # Ajuste de cores e tamanho
            fig_yn = px.pie(df_pie, values='count', names='Periodo', hole=0.55, color_discrete_sequence=['#9cb7ba', '#141414'])
            # Centralização via legenda abaixo e redução de tamanho
            fig_yn.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5), 
                margin=dict(t=10, b=50, l=10, r=10), 
                height=300 
            )
            # Coluna centralizada para o gráfico
            col_left, col_donut, col_right = st.columns([1, 2, 1])
            with col_donut:
                st.plotly_chart(fig_yn, use_container_width=True, config=config_fixo)

        with col2:
            # GRÁFICO 2: NOTAS
            n_s = df["Notas Olfativas"].str.split(',').explode().str.strip()
            c_not = n_s[n_s != ""].apply(padronizar_texto).value_counts().nlargest(30).reset_index(name="count")
            c_not.columns = ["Notas Olfativas", "count"]
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=750, margin=dict(t=20, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        # Espaçamento aumentado
        st.markdown("<br><br>", unsafe_allow_html=True)
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
            # Adiciona um espaçamento antes do gráfico dos Perfumistas
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # GRÁFICO 4: PERFUMISTAS
            c_perf = df[df["Perfumista"].str.strip() != ""]["Perfumista"]
            c_perf = c_perf.apply(padronizar_texto).value_counts().nlargest(15).reset_index(name="count")
            c_perf.columns = ["Perfumista", "count"]
            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#607274'])
            fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

        # GRÁFICO 6: MARCAS
        st.markdown("---")
        c_marca = df[df["Marca"].str.strip() != ""]["Marca"]
        c_marca = c_marca.apply(lambda x: x.upper().strip()).value_counts().nlargest(20).reset_index(name="count")
        c_marca.columns = ["Marca", "count"]
        fig6 = px.bar(c_marca, x="Marca", y="count", text="count", color_discrete_sequence=['#cfbd9f'])
        fig6.update_traces(width=0.6, textposition='outside')
        fig6.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
        st.plotly_chart(fig6, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR / EDITAR / APAGAR
# =========================================================

elif choice == " Adicionar":
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
            if not nome:
                st.warning("O nome do perfume é obrigatório!")
            else:
                # Lógica de processamento
                fam_clean = ", ".join([padronizar_texto(f) for f in fam.replace('/', ',').split(',') if f.strip()])
                notas_clean = ", ".join([padronizar_texto(n) for n in notas.split(',') if n.strip()])
                perf_clean = padronizar_texto(perf)
                
                new = pd.DataFrame([{
                    "Ano": ano, "Nome do Perfume": nome, "Estações do Ano": ", ".join(est),
                    "Ocasiões de Uso": ", ".join(oc), "Família Olfativa": fam_clean,
                    "Notas Olfativas": notas_clean, "Marca": marca, "Perfumista": perf_clean
                }])
                
                # Atualiza o CSV
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                
                # --- LOGICA DE RESET ---
                # Define a página de destino para o próximo carregamento
                st.session_state.menu_choice = "🔍 Pesquisar"
                
                # Feedback de sucesso
                st.toast("PERFUME SALVO COM SUCESSO", icon="✅")
                time.sleep(2) 
                
                # O rerun() forçará o Streamlit a ler o topo do código, 
                # onde o radio lerá o novo valor do session_state.menu_choice
                st.rerun()

elif choice == " Editar":
    st.subheader("Editar")
    if not df.empty:
        lista_perfumes = sorted(df["Nome do Perfume"].unique().tolist())
        idx_default = 0
        if st.session_state.edit_perfume in lista_perfumes:
            idx_default = lista_perfumes.index(st.session_state.edit_perfume)
        
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

elif choice == " Apagar":
    st.subheader("Eliminar")
    if not df.empty:
        p_del = st.selectbox("Selecione o perfume para eliminar:", sorted(df["Nome do Perfume"].unique().tolist()))
        
        # Cria um espaço para a confirmação
        if st.button("Eliminar este perfume"):
            st.session_state.confirmar_delete = p_del
        
        # Verifica se o pedido de delete foi feito
        if "confirmar_delete" in st.session_state and st.session_state.confirmar_delete == p_del:
            st.warning(f"Tem a certeza que deseja eliminar '{p_del}'? Esta ação é irreversível.")
            
            col_sim, col_nao = st.columns(2)
            if col_sim.button("Sim, eliminar"):
                # Realiza a exclusão
                df = df[df["Nome do Perfume"] != p_del]
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"'{p_del}' eliminado com sucesso.")
                # Limpa o estado
                del st.session_state.confirmar_delete
                st.rerun()
            
            if col_nao.button("Cancelar"):
                del st.session_state.confirmar_delete
                st.rerun()


    
