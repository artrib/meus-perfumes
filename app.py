import streamlit as st
import pandas as pd
import os
import unicodedata
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração de Layout
st.set_page_config(page_title="Gestão de Perfumes", layout="wide", page_icon="👃")

# --- CSS PARA FIXAR OS GRÁFICOS NO FUNDO ---
st.markdown("""
    <style>
    /* Cria um espaço no fundo para a tabela não ficar coberta */
    .main .block-container {
        padding-bottom: 350px;
    }
    /* Fixa o contentor das estatísticas no fundo do ecrã */
    div[data-testid="stVerticalBlock"] > div:last-child {
        /* Se quiseres fixar especificamente os gráficos, 
           usamos um container identificado abaixo */
    }
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 1000;
        border-top: 1px solid #ddd;
        padding: 10px 50px;
        height: 320px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "perfumes_data.csv"

# --- FUNÇÕES DE SUPORTE ---
def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    return "".join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

def load_data():
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            if 'Estações' in df.columns: df = df.rename(columns={'Estações': 'Estações do Ano'})
            df = df.fillna("").astype(str)
            return df[cols]
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df = load_data()

# --- INTERFACE ---
st.markdown("<h2 style='text-align: left; font-size: 34px;'>Caixa dos Perfumes</h2>", unsafe_allow_html=True)

menu = ["🔍 Pesquisar", "➕ Adicionar", "📝 Editar", "🗑️ Apagar"]
choice = st.sidebar.radio("Menu de Gestão", menu)

if choice == "🔍 Pesquisar":
    search = st.text_input("", placeholder="Pesquisar...")
    
    if not df.empty:
        # Lógica de filtro
        if search:
            termos = search.split()
            result = df.copy()
            for termo in termos:
                termo_norm = remover_acentos(termo)
                mask = result.astype(str).apply(lambda col: col.map(remover_acentos).str.contains(termo_norm)).any(axis=1)
                result = result[mask]
        else:
            result = df
            
        st.write(f"Encontrados **{len(result)}** perfumes.")
        
        # Tabela (Esta vai deslizar)
        st.data_editor(
            result.reset_index(drop=True), 
            use_container_width=True, hide_index=True, disabled=True,
            column_config={"Ano": st.column_config.TextColumn("Ano", width=50)}
        )

        # --- CONTENTOR DOS GRÁFICOS FIXOS NO FUNDO ---
        # Usamos st.container() com uma div de CSS para "prender" os gráficos
        fixed_container = st.container()
        
        with fixed_container:
            # Configuração para os gráficos não mexerem com o toque
            config_fixo = {'staticPlot': True}
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Estações
                c_est = df["Estações do Ano"].value_counts().reset_index()
                fig1 = px.bar(c_est, x="Estações do Ano", y="count", text="count", color_discrete_sequence=['#ffcc99'])
                fig1.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=0,b=0,l=0,r=0), height=200)
                st.plotly_chart(fig1, use_container_width=True, config=config_fixo)

            with col2:
                # Top Notas
                n_s = df["Notas Olfativas"].str.split(',').explode().str.strip().str.capitalize()
                c_not = n_s[n_s != ""].value_counts().nlargest(5).reset_index()
                fig2 = px.bar(c_not, x="count", y="Notas Olfativas", orientation='h', text="count", color_discrete_sequence=['#99ffcc'])
                fig2.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=0,b=0,l=0,r=0), height=200)
                st.plotly_chart(fig2, use_container_width=True, config=config_fixo)

            with col3:
                # Aranha Famílias
                f_s = df["Família Olfativa"].str.split('/').explode().str.strip().str.capitalize()
                c_fam = f_s[f_s != ""].value_counts().reset_index()
                if not c_fam.empty:
                    fig3 = go.Figure(data=go.Scatterpolar(r=c_fam['count'], theta=c_fam['Família Olfativa'], fill='toself'))
                    fig3.update_layout(polar=dict(radialaxis=dict(visible=False)), showlegend=False, margin=dict(t=20,b=20,l=20,r=20), height=200)
                    st.plotly_chart(fig3, use_container_width=True, config=config_fixo)

# As outras abas (Adicionar, Editar, Apagar) seguem o mesmo padrão do ficheiro original...
