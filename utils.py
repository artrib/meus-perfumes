import unicodedata
import pandas as pd

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
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    ).lower()

def padronizar_texto(texto):
    if not texto or not isinstance(texto, str):
        return ""
    texto_limpo = remover_acentos(texto).strip()
    # Removendo o 's' final apenas se a palavra tiver mais de 4 caracteres
    if texto_limpo.endswith("s") and len(texto_limpo) > 4:
        texto_limpo = texto_limpo[:-1]
    return texto_limpo.capitalize()

def processar_lista_tags(tags_str, lista_referencia=None):
    if not tags_str:
        return ""
    tags = [t.strip() for t in tags_str.replace("/", ",").split(",") if t.strip()]
    if lista_referencia:
        # Filtra e padroniza apenas as tags que estão na lista de referência
        processed_tags = [tag for tag in tags if tag.upper() in [s.upper() for s in lista_referencia]]
    else:
        # Apenas padroniza se não houver lista de referência
        processed_tags = [padronizar_texto(tag) for tag in tags]
    return ", ".join(processed_tags)

def get_all_unique_values(df, column_name):
    if column_name not in df.columns or df.empty:
        return []
    
    # Explode a coluna se for uma string separada por vírgulas
    if df[column_name].dtype == 'object': # Assume que é string
        series = df[column_name].astype(str).str.split(',').explode().str.strip()
    else:
        series = df[column_name].astype(str).str.strip()
        
    # Remove valores vazios e retorna únicos
    return sorted(series[series != ''].unique().tolist())

def get_top_n_values(df, column_name, n=10):
    if column_name not in df.columns or df.empty:
        return pd.DataFrame()
    
    series = df[column_name].astype(str).str.split(',').explode().str.strip()
    counts = series[series != ''].apply(padronizar_texto).value_counts().nlargest(n).reset_index(name="count")
    counts.columns = [column_name, "count"]
    return counts
