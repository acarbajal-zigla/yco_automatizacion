from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

NAMES = {
    # Datos generales
    'Mision':'transparenciaDetForm:idGralesRegistro:_idJsp31',
    'Vision':'transparenciaDetForm:idGralesRegistro:_idJsp36',
    # TODO: AGREGAR LINK TAG <a>"window.open('{LINK_RELEVANTE}', 'popupWindowName', 'menubar=no, 
    # toolbar=no, status=yes'); return false; "</a>'Pagina web':
    # 'transparenciaDetForm:idGralesRegistro:_idJsp41',
    'Anio de autorizacion':'transparenciaDetForm:_idJsp26',
    # Plantillas de personal
    'Plantilla laboral': 'transparenciaDetForm:idGralesRegistro:_idJsp78',
    'Plantilla voluntariado': 'transparenciaDetForm:idGralesRegistro:_idJsp79',
    'Monto total plantilla laboral': 'transparenciaDetForm:idEgresosRegistro:_idJsp166',
    # Patrimonio
    'Activo': 'transparenciaDetForm:idIngresosRegistro:_idJsp107',
    'Pasivo': 'transparenciaDetForm:idIngresosRegistro:_idJsp108',
    'Capital': 'transparenciaDetForm:idIngresosRegistro:_idJsp109',
    # Gastos
    'Gastos administracion': 'transparenciaDetForm:idEgresosRegistro:_idJsp200',
    'Gastos operacion': 'transparenciaDetForm:idEgresosRegistro:_idJsp201',
    'Gastos representacion': 'transparenciaDetForm:idEgresosRegistro:_idJsp202'
}

def get_osc_field(browser, dict_osc, field_name):
    field = browser.find_element_by_name(NAMES[field_name])
    if field.tag_name == 'input':
        dict_osc[field_name] = field.get_attribute('value')
    elif field.tag_name == 'textarea':
        dict_osc[field_name] = field.text
    elif field.tag_name == 'a':
        pass
    #
    

# Funcion que scrapea todos los datos devueltos por la consulta
def get_osc_data(browser):
    osc = {}

    for key, value in NAMES.items():
        get_osc_field(browser, osc, key)
    
    # Rubros autorizados
    rubro_aut = browser.find_element_by_id("transparenciaDetForm:idGralesRegistro:idRubro2")
    rubro_aut = Select(rubro_aut)
    rubros = [opt.text for opt in rubro_aut.options]
    osc["rubros_autorizados"] = rubros

# Ejercicio Fiscal
    # Selector --> transparenciaDetForm:idSelectEjercicioFiscal (childs -> anios disponibles)
    # Boton para consulta de anio --> transparenciaDetForm:_idJsp22

# Ingresos
    # transparenciaDetForm:idIngresosRegistro:dataTableIngresos
    # |
    #  -> transparenciaDetForm:idIngresosRegistro:dataTableIngresos:tbody_element
    # Obtener todos los elementos de la tabla --> tabla_body.find_elements_by_css_selector("*")

    # Total --> class =piePaginaText

    return osc

def query_rfc(browser: webdriver.Chrome, rfc: str, ejercicio: str):
    URL = "https://portalsat.plataforma.sat.gob.mx/TransparenciaDonaciones/faces/publica/frmCConsultaDona.jsp"

    browser.get(URL)
    
    ejercicio_fiscal = browser.find_element_by_id('publicaConsultaDonaForm:idSelectEjercicioFiscal')
    ejercicio_fiscal.send_keys(ejercicio)

    rfc_box = browser.find_element_by_id("publicaConsultaDonaForm:idRfc")
    rfc_box.send_keys(rfc)
    
    # Agregar chequeo inicial
    boton_buscar = browser.find_element_by_id("publicaConsultaDonaForm:_idJsp24")
    boton_buscar.click()
    
    try:
        wait = WebDriverWait(browser, 4)
        boton_RFC = wait.until(EC.element_to_be_clickable((By.ID, 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20')))
        boton_RFC.click()
    except:
        return False
    return True
    
RFC = "FLA080707KE7"
ejercicio = '2019'

options = Options()
#options.headless=True
options.gpu
browser = webdriver.Chrome(options=options)
osc={}

flag_query = True
while(flag_query == True):
    flag_query = query_rfc(browser, RFC, ejercicio)
    print("Error, al consultar datos...\n")
else:
    osc = get_osc_data(browser)

browser.close()
browser.quit()
print(osc)