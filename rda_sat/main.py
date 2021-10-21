from ordenar_RDA import get_table_from_pdf

PDF_path = r'C:\Users\ZIGLA\Desktop\RDA_2020.pdf'

for rango in ['8-161', '316-467', '470-600']:
    df = get_table_from_pdf(PDF_path, rango)
    df.to_excel(f"C:/Users/ZIGLA/Desktop/Tabla_{rango}.xlsx", index=False)
# TODO: reemplazar los nombres de columnas

