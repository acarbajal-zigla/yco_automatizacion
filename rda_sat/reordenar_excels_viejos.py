from os import listdir
import pandas as pd

df = pd.DataFrame()
for anio in range(2014,2018):
    path = f"C:/Users/Alen trabajo/OneDrive - Fundación ZIGLA LAB/YCO/Carga masiva/RDA_excels/{anio}/{anio}.xlsx"
    aux = pd.read_excel(path)
    aux['anio'] = anio
    df = pd.concat([df, aux])
df = df[~(df["RFC"].str.startswith("TOTAL "))]
df.to_excel(f"C:/Users/Alen trabajo/OneDrive - Fundación ZIGLA LAB/YCO/Carga masiva/RDA_excels/2014-2017.xlsx", index=False)

"""
df.loc[df["RFC"] == df[df.columns[4]], "ENTIDAD FEDERATIVA"] = df.loc[df["RFC"] == df[df.columns[5]], "RFC"]
df = df.drop(df[df["RFC"] == df[df.columns[1]]].index)
df.loc[:,"ENTIDAD FEDERATIVA"] = df["ENTIDAD FEDERATIVA"].ffill()
path = f"C:/Users/Alen trabajo/OneDrive - Fundación ZIGLA LAB/YCO/Carga masiva/RDA_excels/{anio}.xlsx"
anio+=1    
df.to_excel(path, index=False)
"""