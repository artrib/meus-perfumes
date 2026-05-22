import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

from database import create_table, insert_perfume, update_perfume, delete_perfume, get_all_perfumes, get_perfume_by_name, import_csv_to_db
from utils import remover_acentos, padronizar_texto, processar_lista_tags, ESTACOES_LISTA, OCASIOES_OPCOES, get_all_unique_values, get_top_n_values

# =========================================================
# GESTÃO DE ESTADO
# =========================================================
if "edit_perfume" not in st.session_state:
    st.session_state.edit_perfume = None
if "menu_choice" not in st.session_state:
    st.session_state.menu_choice = " Pesquisar"

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
    opacity: 0.9;
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
# INICIALIZAÇÃO DO BANCO DE DADOS E CARREGAMENTO DE DADOS
# =========================================================
create_table()

# Verifica se o banco de dados está vazio e tenta importar de CSV se existir
if get_all_perfumes().empty and os.path.exists("perfumes_data.csv"):
    try:
        import_csv_to_db("perfumes_data.csv")
        st.toast("Dados importados do CSV com sucesso!", icon="✅")
    except Exception as e:
        st.error(f"Erro ao importar CSV para o banco de dados: {e}")

df = get_all_perfumes()

# =========================================================
# TÍTULO
# =========================================================
st.markdown("<h2 style='text-align:left; font-size:37px; color: var(--text-color);'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================
menu = [" Pesquisar", " Adicionar", " Editar", " Apagar"]
default_index = menu.index(st.session_state.menu_choice) if st.session_state.menu_choice in menu else 0

choice = st.sidebar.radio("", menu, index=default_index, key="main_menu")
st.session_state.menu_choice = choice # Atualiza o estado da sessão para manter a escolha do menu

# =========================================================
# 1. PESQUISAR E ESTATÍSTICAS
# =========================================================

if choice == " Pesquisar":
    col_busca, col_filtro = st.columns([3, 1])
    
    with col_busca:
        search = st.text_input("pesquisa", placeholder="🔍", key="search_input")
    
    with col_filtro:
        opcoes_busca = ["Tudo", "Notas Olfativas", "Família Olfativa", "Estações do Ano", "Ocasiões de Uso", "Perfumista", "Marca", "Nome do Perfume"]
        local_busca = st.selectbox("filtros", opcoes_busca, key="search_filter")
        
    result = df.copy()
    result.insert(0, "Editar", False)

    if search:
        termos = search.split()
        for termo in termos:
            t_norm = remover_acentos(termo)
            if local_busca == "Tudo":
                mask = result.apply(
                    lambda row: row.astype(str).map(remover_acentos).str.contains(t_norm, case=False, na=False).any(),
                    axis=1
                )
            else:
                mask = result[local_busca].astype(str).map(remover_acentos).str.contains(t_norm, case=False, na=False)
            result = result[mask].copy()

    # 1. Limpa linhas fantasma que tenham o nome do perfume em branco
    result = result[result["Nome do Perfume"].str.strip() != ""]
    
    # 2. Mostra o total real
    st.write(f"**{len(result)}** perfumes")

    if not df.empty:
        # 3. Cria uma cópia para visualização e força o índice a começar em 1
        df_visual = result.reset_index(drop=True)
        df_visual.index = df_visual.index + 1  
        
        edited_df = st.data_editor(
            df_visual, 
            use_container_width=True,
            hide_index=True, 
            column_config={
                "Editar": st.column_config.CheckboxColumn("edit", width=30, default=False),
                "Ano": st.column_config.TextColumn("Ano", width=55),
                "Nome do Perfume": st.column_config.TextColumn("Nome do Perfume", width="medium"),
                "Marca": st.column_config.TextColumn("Marca", width=120),
                "Notas Olfativas": st.column_config.TextColumn("Notas Olfativas", width=220),
                "Estações do Ano": st.column_config.TextColumn("Estações do Ano", width=120),
                "Ocasiões de Uso": st.column_config.TextColumn("Ocasiões de Uso", width=120)
            },
            disabled=[c for c in result.columns if c != "Editar"], key="data_editor_search"
        )

        check_click = edited_df[edited_df["Editar"] == True]
        if not check_click.empty:
            st.session_state.edit_perfume = check_click.iloc[0]["Nome do Perfume"]
            st.session_state.menu_choice = " Editar"
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
            c_est = get_top_n_values(df, "Estações do Ano", n=len(ESTACOES_LISTA))
            ordem_estacoes = [
                padronizar_texto(s) for s in ESTACOES_LISTA
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
            c_oc = get_top_n_values(df, "Ocasiões de Uso", n=len(OCASIOES_OPCOES))
            ordem_desejada = [
                s.upper() for s in OCASIOES_OPCOES
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

            # GRÁFICO: DIA E NOITE (Ying Yang)
            st.markdown("<br>", unsafe_allow_html=True)
            
            dia_tags = ["CASUAL DIA", "TRABALHO PRI/VER", "TRABALHO OUT/INV", "FORMAL DIA"]
            noite_tags = ["CASUAL NOITE", "FORMAL NOITE"]

            total_dia = 0
            total_noite = 0

            for _, row in df.iterrows():
                ocasioes = [o.strip().upper() for o in str(row["Ocasiões de Uso"]).split(",") if o.strip()]
                
                if any(tag in ocasioes for tag in dia_tags):
                    total_dia += 1
                
                if any(tag in ocasioes for tag in noite_tags):
                    total_noite += 1

            df_pie = pd.DataFrame({
                "Periodo": ["DIA", "NOITE"],
                "count": [total_dia, total_noite]
            })
            
            fig_yn = px.pie(
                df_pie, 
                values='count', 
                names='Periodo', 
                hole=0.55, 
                color_discrete_sequence=['#9cb7ba', '#141414']
            )
            
            fig_yn.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5), 
                margin=dict(t=10, b=50, l=10, r=10), 
                height=300 
            )
            
            col_left, col_donut, col_right = st.columns([1, 2, 1])
            with col_donut:
                st.plotly_chart(fig_yn, use_container_width=True, config=config_fixo)

        with col2:
            # GRÁFICO 2: NOTAS
            c_not = get_top_n_values(df, "Notas Olfativas", n=30)
            fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#94A684'])
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=750, margin=dict(t=20, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

        st.markdown("<br><br>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            # GRÁFICO 3: FAMÍLIA
            c_fam = get_top_n_values(df, "Família Olfativa", n=8)
            fig3 = px.pie(c_fam, values='count', names='Família Olfativa', color_discrete_sequence=paleta_minimalista)
            fig3.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), margin=dict(t=10, b=100), height=340)
            st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

        with col4:
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # GRÁFICO 4: PERFUMISTAS
            c_perf = get_top_n_values(df, "Perfumista", n=15)
            fig4 = px.bar(c_perf, x="count", y="Perfumista", orientation='h', text="count", color_discrete_sequence=['#607274'])
            fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True, config=config_fixo)

        # GRÁFICO 6: MARCAS
        st.markdown("---")
        c_marca = get_top_n_values(df, "Marca", n=20)
        fig6 = px.bar(c_marca, x="Marca", y="count", text="count", color_discrete_sequence=['#cfbd9f'])
        fig6.update_traces(width=0.6, textposition='outside')
        fig6.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=20, b=10), height=400)
        st.plotly_chart(fig6, use_container_width=True, config=config_fixo)

# =========================================================
# ADICIONAR
# =========================================================
elif choice == " Adicionar":
    st.subheader("Novo Registo")
    with st.form("add_perfume_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Perfume *", key="add_nome")
            marca = st.text_input("Marca", key="add_marca")
            est = st.multiselect("Estações", ESTACOES_LISTA, key="add_estacoes")
            oc = st.multiselect("Ocasiões de Uso", OCASIOES_OPCOES, key="add_ocasioes")
        with c2:
            fam = st.text_input("Família Olfativa", key="add_familia")
            perf = st.text_input("Perfumista", key="add_perfumista")
            ano = st.text_input("Ano", key="add_ano")
            notas = st.text_area("Notas Olfativas", key="add_notas")

        if st.form_submit_button("Guardar"):
            if not nome:
                st.warning("O nome do perfume é obrigatório!")
            elif get_perfume_by_name(nome):
                st.warning(f"Já existe um perfume com o nome '{nome}'. Por favor, escolha um nome diferente ou edite o existente.")
            else:
                try:
                    # Validação do ano
                    if ano and not ano.isdigit():
                        st.warning("O Ano deve ser um número válido.")
                        st.stop()
                    
                    perfume_data = {
                        "Ano": ano,
                        "Nome do Perfume": nome,
                        "Estações do Ano": processar_lista_tags(", ".join(est), ESTACOES_LISTA),
                        "Ocasiões de Uso": processar_lista_tags(", ".join(oc), OCASIOES_OPCOES),
                        "Família Olfativa": processar_lista_tags(fam),
                        "Notas Olfativas": processar_lista_tags(notas),
                        "Marca": padronizar_texto(marca),
                        "Perfumista": padronizar_texto(perf)
                    }
                    insert_perfume(perfume_data)
                    st.toast("PERFUME SALVO COM SUCESSO", icon="✅")
                    st.session_state.edit_perfume = None # Limpa qualquer estado de edição
                    st.session_state.menu_choice = " Pesquisar"
                    time.sleep(1) 
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar perfume: {e}")

# =========================================================
# EDITAR
# =========================================================
elif choice == " Editar":
    st.subheader("Editar Perfume")
    if df.empty:
        st.info("Não há perfumes para editar.")
    else:
        lista_perfumes = sorted(df["Nome do Perfume"].unique().tolist())
        idx_default = 0
        if st.session_state.edit_perfume and st.session_state.edit_perfume in lista_perfumes:
            idx_default = lista_perfumes.index(st.session_state.edit_perfume)
        
        sel_perfume_name = st.selectbox("Selecione o perfume para editar:", lista_perfumes, index=idx_default, key="edit_select_perfume")
        
        perfume_to_edit = get_perfume_by_name(sel_perfume_name)
        if perfume_to_edit:
            # Converte sqlite3.Row para dicionário para facilitar o acesso
            perfume_to_edit_dict = dict(perfume_to_edit)

            # Prepara os valores para multiselect
            at_oc = [x.strip() for x in str(perfume_to_edit_dict.get("Ocasiões de Uso", "")).split(",") if x.strip() in OCASIOES_OPCOES]
            at_est = [x.strip() for x in str(perfume_to_edit_dict.get("Estações do Ano", "")).split(",") if x.strip() in ESTACOES_LISTA]

            with st.form("edit_perfume_form"):
                c1, c2 = st.columns(2)
                with c1:
                    e_n = st.text_input("Nome do Perfume *", value=perfume_to_edit_dict.get("Nome do Perfume", ""), disabled=True, key="edit_nome") # Nome não editável para evitar duplicados
                    e_m = st.text_input("Marca", value=perfume_to_edit_dict.get("Marca", ""), key="edit_marca")
                    e_e = st.multiselect("Estações", ESTACOES_LISTA, default=at_est, key="edit_estacoes")
                    e_oc = st.multiselect("Ocasiões", OCASIOES_OPCOES, default=at_oc, key="edit_ocasioes")
                with c2:
                    e_f = st.text_input("Família", value=perfume_to_edit_dict.get("Família Olfativa", ""), key="edit_familia")
                    e_p = st.text_input("Perfumista", value=perfume_to_edit_dict.get("Perfumista", ""), key="edit_perfumista")
                    e_a = st.text_input("Ano", value=perfume_to_edit_dict.get("Ano", ""), key="edit_ano")
                    e_not = st.text_area("Notas", value=perfume_to_edit_dict.get("Notas Olfativas", ""), key="edit_notas")

                if st.form_submit_button("Atualizar"):
                    try:
                        if e_a and not e_a.isdigit():
                            st.warning("O Ano deve ser um número válido.")
                            st.stop()

                        updated_perfume_data = {
                            "Ano": e_a,
                            "Estações do Ano": processar_lista_tags(", ".join(e_e), ESTACOES_LISTA),
                            "Ocasiões de Uso": processar_lista_tags(", ".join(e_oc), OCASIOES_OPCOES),
                            "Família Olfativa": processar_lista_tags(e_f),
                            "Notas Olfativas": processar_lista_tags(e_not),
                            "Marca": padronizar_texto(e_m),
                            "Perfumista": padronizar_texto(e_p)
                        }
                        update_perfume(sel_perfume_name, updated_perfume_data)
                        st.toast(f"Perfume '{sel_perfume_name}' atualizado com sucesso!", icon="✅")
                        st.session_state.edit_perfume = None
                        st.session_state.menu_choice = " Pesquisar"
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar perfume: {e}")
        else:
            st.warning("Perfume selecionado não encontrado.")

# =========================================================
# APAGAR
# =========================================================
elif choice == " Apagar":
    st.subheader("Eliminar Perfume")
    if df.empty:
        st.info("Não há perfumes para eliminar.")
    else:
        lista_perfumes = sorted(df["Nome do Perfume"].unique().tolist())
        p_del = st.selectbox("Selecione o perfume para eliminar:", lista_perfumes, key="delete_select_perfume")
        
        if p_del:
            # Cria um espaço para a confirmação
            if st.button("Eliminar este perfume", key="delete_button"):
                st.session_state.confirmar_delete = p_del
            
            # Verifica se o pedido de delete foi feito
            if "confirmar_delete" in st.session_state and st.session_state.confirmar_delete == p_del:
                st.warning(f"Tem a certeza que deseja eliminar '{p_del}'? Esta ação é irreversível.")
                
                col_sim, col_nao = st.columns(2)
                with col_sim:
                    if st.button("Sim, eliminar", key="confirm_delete_button"):
                        try:
                            delete_perfume(p_del)
                            st.toast(f"'{p_del}' eliminado com sucesso.", icon="✅")
                            # Limpa o estado
                            del st.session_state.confirmar_delete
                            st.session_state.edit_perfume = None
                            st.session_state.menu_choice = " Pesquisar"
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao eliminar perfume: {e}")
                with col_nao:
                    if st.button("Cancelar", key="cancel_delete_button"):
                        del st.session_state.confirmar_delete
                        st.rerun()
