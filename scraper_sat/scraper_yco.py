from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import TableFuncs
from constantes import TABLAS, NAMES

def get_osc_field(browser, dict_osc, field_name):
    print('Procesando {}'.format(field_name))
    field = browser.find_element_by_name(NAMES[field_name])

    if field.tag_name == 'input':
        dict_osc[field_name] = field.get_attribute('value')
    elif field.tag_name == 'textarea':
        dict_osc[field_name] = field.text
    elif field.tag_name == 'a':
        dict_osc[field_name] = field.get_attribute('innerHTML')

# Funcion que scrapea todos los datos devueltos por la consulta
def get_osc_data(browser):
    osc = dict()

    for key, value in NAMES.items():
        get_osc_field(browser, osc, key)
    
    # Rubros autorizados
    rubro_aut = browser.find_element_by_id(NAMES['Rubros autorizados'])
    rubro_aut = Select(rubro_aut)
    rubros = [opt.text for opt in rubro_aut.options]
    osc['rubros_autorizados'] = rubros

    # Tablas
    for table_data in TABLAS:
        data = TableFuncs.get_datos_tabla(browser, table_data)
        print(f"TABLA: {table_data['categoria']} - {table_data['subcategoria']}\n")
        print(data)
        print('\n')

# Ejercicio Fiscal
    # Selector --> transparenciaDetForm:idSelectEjercicioFiscal (childs -> anios disponibles)
    # Boton para consulta de anio --> transparenciaDetForm:_idJsp22

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
    
RFC = "CRM050218MCA"
ejercicio = '2019'

options = Options()
#options.headless=True

browser = webdriver.Chrome(options=options)
osc={}

i=0
flag_query = False
while(i<2 and flag_query == False):
    flag_query = query_rfc(browser, RFC, ejercicio)
    if flag_query == True:
        osc = get_osc_data(browser)
        break
    else:
        print("Error, al consultar datos...\n")
    i += 1

browser.close()
browser.quit()
print(osc)