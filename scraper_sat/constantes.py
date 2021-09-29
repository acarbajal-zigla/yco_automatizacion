import re

# Constantes
HEAD = 'transparenciaDetForm'
#REGEX_WEB = re.compile(r"window\.open\(\'<web>\', \'popupWindowName\', \'menubar=no, toolbar=no, status=yes\'\); return false;")

NAMES = {
    # Datos generales
    'Mision':HEAD+':idGralesRegistro:_idJsp31',
    'Vision':HEAD+':idGralesRegistro:_idJsp36',
    'Pagina web':HEAD+':idGralesRegistro:_idJsp41',
    'Anio de autorizacion':HEAD+':_idJsp26',
    'Socios o Asociados':HEAD+':idGralesRegistro:_idJsp67',
    'Rubros autorizados':HEAD+':idGralesRegistro:idRubro2',
    # Plantillas de personal
    'Plantilla laboral': HEAD+':idGralesRegistro:_idJsp78',
    'Plantilla voluntariado': HEAD+':idGralesRegistro:_idJsp79',
    'Monto total plantilla laboral': HEAD+':idEgresosRegistro:_idJsp166',
    # Patrimonio
    'Activo': HEAD+':idIngresosRegistro:_idJsp107',
    'Pasivo': HEAD+':idIngresosRegistro:_idJsp108',
    'Capital': HEAD+':idIngresosRegistro:_idJsp109',
    # Gastos
    'Gastos administracion': HEAD+':idEgresosRegistro:_idJsp200',
    'Gastos operacion': HEAD+':idEgresosRegistro:_idJsp201',
    'Gastos representacion': HEAD+':idEgresosRegistro:_idJsp202'
}

TABLAS = [
        {'categoria':'Ingresos',
        'subcategoria':'Ingresos'},
        {'categoria':'Ingresos', 
        'subcategoria':'OtrosIngresos'},
        {'categoria':'Egresos', 
        'subcategoria':'Egresos'},
        {'categoria':'Egresos', 
        'subcategoria':'MontosConceptos'},
        {'categoria':'Egresos', 
        'subcategoria':'Donativos'},
        {'categoria':'Actividades', 
        'subcategoria':'Actividades'}
    ]