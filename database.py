import sqlite3
import pandas as pd

DATABASE_NAME = "perfumes.db"
TABLE_NAME = "perfumes"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Ano TEXT,
            "Nome do Perfume" TEXT UNIQUE NOT NULL,
            "Estações do Ano" TEXT,
            "Ocasiões de Uso" TEXT,
            "Família Olfativa" TEXT,
            "Notas Olfativas" TEXT,
            Marca TEXT,
            Perfumista TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_perfume(perfume_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} (
                Ano, "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso",
                "Família Olfativa", "Notas Olfativas", Marca, Perfumista
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            perfume_data["Ano"],
            perfume_data["Nome do Perfume"],
            perfume_data["Estações do Ano"],
            perfume_data["Ocasiões de Uso"],
            perfume_data["Família Olfativa"],
            perfume_data["Notas Olfativas"],
            perfume_data["Marca"],
            perfume_data["Perfumista"]
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Perfume com o mesmo nome já existe
    finally:
        conn.close()

def update_perfume(perfume_name, perfume_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {TABLE_NAME} SET
            Ano = ?,
            "Estações do Ano" = ?,
            "Ocasiões de Uso" = ?,
            "Família Olfativa" = ?,
            "Notas Olfativas" = ?,
            Marca = ?,
            Perfumista = ?
        WHERE "Nome do Perfume" = ?
    """, (
        perfume_data["Ano"],
        perfume_data["Estações do Ano"],
        perfume_data["Ocasiões de Uso"],
        perfume_data["Família Olfativa"],
        perfume_data["Notas Olfativas"],
        perfume_data["Marca"],
        perfume_data["Perfumista"],
        perfume_name
    ))
    conn.commit()
    conn.close()

def delete_perfume(perfume_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {TABLE_NAME} WHERE "Nome do Perfume" = ?', (perfume_name,))
    conn.commit()
    conn.close()

def get_all_perfumes():
    conn = get_db_connection()
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    return df

def get_perfume_by_name(perfume_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {TABLE_NAME} WHERE "Nome do Perfume" = ?', (perfume_name,))
    perfume = cursor.fetchone()
    conn.close()
    return perfume

def import_csv_to_db(csv_file_path):
    df = pd.read_csv(csv_file_path, encoding='utf-8-sig', sep=None, engine='python')
    df.columns = df.columns.str.strip()
    
    # Garante que todas as colunas necessárias existam
    cols = ["Ano", "Nome do Perfume", "Estações do Ano", "Ocasiões de Uso", 
            "Família Olfativa", "Notas Olfativas", "Marca", "Perfumista"]
    for col in cols:
        if col not in df.columns:
            df[col] = ""
            
    df["Ano"] = pd.to_numeric(df["Ano"], errors='coerce').fillna(0).astype(int).astype(str)
    df = df.drop_duplicates(subset=["Nome do Perfume"], keep='first')
    df = df.fillna("")[cols]

    conn = get_db_connection()
    df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Dados importados de {csv_file_path} para o banco de dados SQLite.")

# Inicializa o banco de dados e a tabela se não existirem
create_table()
