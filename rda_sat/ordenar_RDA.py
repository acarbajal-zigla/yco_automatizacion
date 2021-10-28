import camelot
import pandas as pd
import numpy as np

def get_headers_from_dataframe(df: pd.DataFrame):
    for index, row in df.iterrows():
        if (row[0] == "RFC") and (row[1] == "DENOMINACION SOCIAL"):
            alto_header = 1
            while(df.iloc[index+alto_header, 0] == "RFC"):
                alto_header += 1
            for column in range(2, len(row.tolist())):
                for i in range(1, alto_header):
                    row[column] = f"{row[column]} - {df.iloc[index+i, column]}"
            return [a.replace("\n", "").strip() for a in row.tolist()]
        else:
            continue

def set_categorias(df: pd.DataFrame):
    df.loc[df[df.columns[0]] == df[df.columns[1]], "CATEGORIA"] = df.loc[df[df.columns[0]] == df[df.columns[1]],df.columns[0]]
    df["CATEGORIA"] = df["CATEGORIA"].ffill()

def set_entidades_federativas(df: pd.DataFrame):
    df.loc[df[df.columns[0]].str.startswith("TOTAL "),"ENTIDAD FEDERATIVA"] = df.loc[df[df.columns[0]].str.startswith("TOTAL "),df.columns[0]]
    df.loc[:,"ENTIDAD FEDERATIVA"] = df.loc[:,"ENTIDAD FEDERATIVA"].str.replace("TOTAL ", "")
    df["ENTIDAD FEDERATIVA"] = df["ENTIDAD FEDERATIVA"].bfill()

def set_entidades_federativas_viejo(df: pd.DataFrame):
    df.loc[df["RFC"] == df[df.columns[4]],"ENTIDAD FEDERATIVA"] = df[df["RFC"] == df[df.columns[4]]]["RFC"]
    df["ENTIDAD FEDERATIVA"] = df["ENTIDAD FEDERATIVA"].ffill()

def get_table_from_pdf(path, hojas):

    tables = camelot.read_pdf(path, pages=hojas, copy_text=['h', 'v'],  line_scale=80)

    # Concateno todas las tablas en un dataframe
    df = pd.concat([t.df for t in tables])
#   df[pd.notna(df[df.columns[-1]])] = df[pd.notna(df[df.columns[-1]])].shift(axis=1, periods=-1)
    if df[df.columns[-2]].equals(df[df.columns[-3]]):
        df = df[df.columns[:-2]] # en los datos viejos elimina la columna de datos inválidos

    # Obtengo y asigno headers
    headers = get_headers_from_dataframe(df)
    #headers = [header for header in headers if (header.startswith("nan") == False)] # en datos viejos no contabiliza la columna nan-nan
    df.columns = headers

    # Elimino las filas que son repetición de headers por cambio de entidad federativa
    df = df[df["RFC"] != "RFC"]
    #df = df[df["RFC"].str.startswith("TOTAL ") == False]

    # Elimino todas las filas vacias
    df = df.dropna()
    df = df[df["RFC"].astype(bool)]

    # Agrego las columnas de categoria y entidad federativa
    df["CATEGORIA"] = np.nan
    df["ENTIDAD FEDERATIVA"] = np.nan
    set_categorias(df)
    set_entidades_federativas(df)
    #set_entidades_federativas_viejo(df)

    df = df[df["RFC"] != df["CATEGORIA"]]
    df = df.replace("-","")
    return df