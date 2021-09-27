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

