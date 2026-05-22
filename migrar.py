import pandas as pd
import sqlite3

# 1. Ler o CSV antigo
df_csv = pd.read_csv("perfumes_data.csv", sep=None, engine='python')

# 2. Mapear para os nomes exatos das colunas da tabela SQL
df_csv.columns = df_csv.columns.str.strip()
df_sql = pd.DataFrame()
df_sql['ano'] = df_csv['Ano'].fillna('').astype(str)
df_sql['nome_perfume'] = df_csv['Nome do Perfume'].str.strip()
df_sql['estacoes'] = df_csv['Estações do Ano'].fillna('').astype(str)
df_sql['ocasioes'] = df_csv['Ocasiões de Uso'].fillna('').astype(str)
df_sql['familia'] = df_csv['Família Olfativa'].fillna('').astype(str)
df_sql['notas'] = df_csv['Notas Olfativas'].fillna('').astype(str)
df_sql['marca'] = df_csv['Marca'].fillna('').astype(str).str.strip()
df_sql['perfumista'] = df_csv['Perfumista'].fillna('').astype(str)

# Remover duplicados pelo nome antes de salvar
df_sql = df_sql.drop_duplicates(subset=['nome_perfume'])

# 3. Guardar no SQLite
conn = sqlite3.connect("perfumes.db")
df_sql.to_sql("perfumes", conn, if_exists="append", index=False)
conn.close()

print("Migração concluída com sucesso!")

