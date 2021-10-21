import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import range_boundaries

import pandas as pd
import numpy as np

""" 
       if (row_[0] == row_[1]) and (row_[3] == None):      # Caso -> es una categoria
            categoria = row_[0]
            row.drop()
        elif (len(row_[0]) == 13) and (row_[0] != row_[1]): # Caso -> es un dato
            row["CATEGORIA"] = categoria
            row["ENTIDAD FEDERATIVA"] = entidad_federativa
        elif row_[0].startswith("TOTAL "):                  # Caso -> es el total y saco la entidad federativa
            entidad_federativa = re.search("TOTAL (.*)", row_[0]).group(1)
            df["ENTIDAD FEDERATIVA"] = entidad_federativa
"""
def get_header_from_dataframe(df: pd.DataFrame):
    for index, row in df.iterrows():
        if (row[0] == "RFC") and (row[1] == "DENOMINACIÓN O RAZÓN SOCIAL"):
            alto_header = 1
            while(df.iloc[index+alto_header, 0] == "RFC"):
                alto_header += 1

            for column in range(2, len(row.tolist())):
                for i in range(1, alto_header):
                    row[column] += f" - {df.iloc[index+i, column]}"
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

def get_header_row(ws:Worksheet):
    """
        Busca la fila en que aparecen los encabezados de la tabla.
        En caso de encontrarla, devuelve el número de fila (base 1)
        si no encuentra ningun header, devuelve False
    """
    for row in ws.iter_rows():
        if row[0].value == "ENTIDAD FEDERATIVA" or row[0].value == "RFC":
            return row[0].row
    return False

def get_headers(ws: Worksheet, row: int):
    headers = []
    alto_header = 1
    while ws.cell(row=row+alto_header, column=1).value == None:
        alto_header += 1
    row_data = row + alto_header
    
    i=1
    for columna in range(2, len(ws[row_data])+1):
        if ws.cell(row=row, column=columna+1).value == None:
            ws.cell(row=row, column=columna+1).value = ws.cell(row=row, column=columna).value

    i = 1
    while ws.cell(row=row_data+1, column=i).value:
        headers.append(ws.cell(row=row, column=i).value)
        print(headers)
        for row_header in range(1, alto_header):
            if ws.cell(row=row+row_header, column=i).value:
                headers[-1] += f" - {ws.cell(row=row+1, column=i).value}"
        i += 1

    return headers, row_data

def get_tabla_entidades_federativas(ws: Worksheet):
    header_row = get_header_row(ws)
    headers, first_data_row = get_headers(ws, header_row) 
    tabla_EF = pd.DataFrame(columns=headers)
    
    for row in ws.iter_rows(min_row=first_data_row):
        if row[0].value.startswith("TOTAL"):
            break
        else:
            tabla_EF.append([cell.value for cell in row])
    return tabla_EF

import camelot

path = r'C:\Users\ZIGLA\Desktop\RDA_2020.pdf'
tables = camelot.read_pdf(path, pages='316-321', copy_text=['h', 'v'],  line_scale=80)
  
# Concateno todas las tablas en un dataframe
df = pd.concat([t.df for t in tables])

# Obtengo y asigno headers
headers = get_header_from_dataframe(df)
df.columns = headers

# Elimino las filas que son repetición de headers por cambio de entidad federativa
df = df[df["RFC"] != "RFC"]
# Elimino todas las filas vacias
df = df.dropna()
df = df[df["RFC"].astype(bool)]

# Agrego las columnas de categoria y entidad federativa
df[["CATEGORIA", "ENTIDAD FEDERATIVA"]] = np.nan
    
set_categorias(df)
set_entidades_federativas(df)
df = df[df[df.columns[0]] != df["CATEGORIA"]]
df = df.replace("-","")
df.to_excel(r'C:\Users\ZIGLA\Desktop\foo.xlsx', index=False)
exit()

wb = openpyxl.load_workbook(path)
ws = wb.active

for cell_group in ws.merged_cells.ranges:
        min_col, min_row, max_col, max_row = range_boundaries(str(cell_group))
        top_left_cell_value = ws.cell(row=min_row, column=min_col).value
        ws.unmerge_cells(str(cell_group))
        for row in ws.iter_rows(min_col=min_col, min_row=min_row, max_col=max_col, max_row=max_row):
            for cell in row:
                cell.value = top_left_cell_value
wb.save(path)

df = get_tabla_entidades_federativas(ws)
print(df.head())

# Concateno todas las hojas

# Busco RFC	y DENOMINACIÓN O RAZÓN SOCIAL en columnas A y B --> inicio de tabla
# Alternativamente busco la fila que está vacía en todas sus columnas excepto A, 
# y en A dice "Total [Entidad Federativa]"

# A la derecha de RFC y RAZÓN SOCIAL(C, D, etcétera) están los encabezados. Si debajo de RFC no hay nada,
# considero que hay un subítem que extraigo simplemente como C, D, etc -> una fila 
# debajo de "RFC"

# Arriba de esos valores tiene que estar la Entidad Federativa
# Debajo arranca la primera de las categorías. Son [NOMBRE][VACIO]*N

	
# TODO: ver cómo obtengo el título (es una imagen --> OCR?)
# TODO: pensar cómo buscar "Cuadro X" --> puede ayudar

#########################################################################################################

