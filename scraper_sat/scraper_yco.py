from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import TableFuncs
from constantes import TABLAS, NAMES

def get_osc_field(browser, dict_osc, field_name):
    field = browser.find_element_by_name(NAMES[field_name])
    aux = ''
    if field.tag_name == 'input':
        aux = field.get_attribute('value')
    elif field.tag_name == 'textarea':
        aux = field.text.replace('\t', ' ')
    elif field.tag_name == 'a':
        aux = field.get_attribute('innerHTML')
    dict_osc[field_name] = aux.replace('\n',' ').replace('\t', ' ').strip()
# Funcion que scrapea todos los datos devueltos por la consulta
def get_osc_data(browser):
    osc = dict()

    for key, value in NAMES.items():
        get_osc_field(browser, osc, key)
    
    # Rubros autorizados
    rubro_aut = browser.find_element_by_id(NAMES['Rubros autorizados'])
    rubro_aut = Select(rubro_aut)
    rubros = [opt.text.replace('\n',' ').replace('\t', ' ').strip() for opt in rubro_aut.options]
    osc['Rubros autorizados'] = rubros

    # Tablas
    for table_data in TABLAS:
        osc[table_data['categoria']] = []

    for table_data in TABLAS:
        data = TableFuncs.get_datos_tabla(browser, table_data)
        osc[table_data['categoria']].append(data)
    
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

def connect_sat(rfc):
    options = Options()
    #options.headless=True
    """
    options.add_argument('--no-sandbox')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
"""
    browser = webdriver.Chrome(options=options)
    flag_query = False
    j=0
    while(j<2 and flag_query == False):
        flag_query = query_rfc(browser, rfc, "2019")
        j += 1
    return browser