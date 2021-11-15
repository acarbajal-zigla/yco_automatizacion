from ordenar_RDA import get_table_from_pdf

dict_entidades_fed = {"AGUASCALIENTES":"Aguascalientes",
"BAJA CALIFORNIA":"Baja California",
"BAJA CALIFORNIA SUR":"Baja California Sur",
"CAMPECHE":"Campeche",
"CHIAPAS":"Chiapas",
"CHIHUAHUA":"Chihuahua",
"CIUDAD DE MÉXICO":"CDMX",
"COAHUILA":"Coahuila de Zaragoza",
"COLIMA":"Colima",
"DURANGO":"Durango",
"GUANAJUATO":"Guanajuato",
"GUERRERO":"Guerrero",
"HIDALGO":"Hidalgo",
"JALISCO":"Jalisco",
"MÉXICO":"México",
"MICHOACÁN":"Michoacán de Ocampo",
"MORELOS":"Morelos",
"NAYARIT":"Nayarit",
"NUEVO LEÓN":"Nuevo León",
"OAXACA":"Oaxaca",
"PUEBLA":"Puebla",
"QUERÉTARO":"Querétaro",
"QUINTANA ROO":"Quintana Roo",
"SAN LUIS POTOSÍ":"San Luis Potosí",
"SINALOA":"Sinaloa",
"SONORA":"Sonora",
"TABASCO":"Tabasco",
"TAMAULIPAS":"Tamaulipas",
"TLAXCALA":"Tlaxcala",
"VERACRUZ":"Veracruz de Ignacio de la Llave",
"YUCATÁN":"Yucatán",
"ZACATECAS":"Zacatecas"}

# rangos = {'2014':['7-141'], '2015':['6-155'], '2016':['6-168'], '2017': ['6-171']}
#{'2019': ['233']}#['173-312']} #7', '150-287', '291-434']}#2021:['8-180',]
rangos_por_anio = {'2021':['183-379','383-566', '8-180']}

for anio, rangos in rangos_por_anio.items():
    for rango in rangos:
        PDF_path = f"C:/Users/Alen trabajo/OneDrive - Fundación ZIGLA LAB/YCO/Informes RDA/RDA_{anio}.pdf"
        df = get_table_from_pdf(PDF_path, rango)
        for entidad_RDA, entidad_correcta in dict_entidades_fed.items():
            df.loc[df["ENTIDAD FEDERATIVA"] == entidad_RDA, "ENTIDAD FEDERATIVA"] = entidad_correcta
        df.to_excel(f"C:/Users/Alen trabajo/OneDrive - Fundación ZIGLA LAB/YCO/Carga masiva/RDA_excels/{anio}/Tabla_{rango}.xlsx", index=False)
        print(f"\nTERMINADO {anio} - {rango}\n")

