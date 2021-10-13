from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import TableFuncs
from constantes import TABLAS, NAMES, ERRORES

def check_exists(path_or_id, mode):
    try:
        if mode == "xpath":
            webdriver.find_element_by_xpath(path_or_id)
        elif mode == "id":
            webdriver.find_element_by_id(path_or_id)
    except NoSuchElementException:
        return False
    return True

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
    except NoSuchElementException:
        return False
    return True

def connect_sat(rfc):
    options = Options()
    options.headless=True
    browser = webdriver.Chrome(options=options)

    XPATH_TEXTO_ERROR = "/html/body/form/table[6]/tbody/tr/td/ul/li/text()"

    j=0
    ejercicio = 2019
    flag_query = False

    while(j<2 and flag_query == False):
        flag_query = query_rfc(browser, rfc, str(ejercicio))
        if flag_query == True:
            break

        if check_exists(XPATH_TEXTO_ERROR, "xpath") ==  True:
            texto_error = browser.find_element_by_xpath(XPATH_TEXTO_ERROR, "xpath")
            if texto_error == ERRORES["NO_AUTORIZADO"]:
                ejercicio -= 1
                if ejercicio < 2014:
                    return None
                j = 0
            elif texto_error == ERRORES["AL_RECUPERAR"]:
                j += 1
            else:
                raise "Error"

    return browser
