from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import TableFuncs
from constantes import TABLAS, NAMES, ERRORES

def check_exists(browser, path_or_id, mode):
    ret = True
    try:
        if mode == 'xpath':
            browser.find_element_by_xpath(path_or_id)
        elif mode == 'id':
            browser.find_element_by_id(path_or_id)
    except NoSuchElementException:
        ret = False
    return ret

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

    boton_buscar = browser.find_element_by_id("publicaConsultaDonaForm:_idJsp24")
    boton_buscar.click()
    
    if check_exists(browser, 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20', 'id') == True:
        boton_RFC = browser.find_element_by_id('publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20') # Boton de RFC que lleva a datos
        boton_RFC.click()
    if check_exists(browser, '_idJsp1:_idJsp6', 'id') == True:
        boton_Consultar_Registro = browser.find_element_by_id('_idJsp1:_idJsp6') # Boton de DDJJs
        boton_Consultar_Registro.click()
    
    if check_exists(browser, 'transparenciaDetForm:_idJsp22', 'id') == True:
        return True
    else:
        return False

def connect_sat(rfc):
    options = Options()
    options.headless=False
    browser = webdriver.Chrome(options=options)

    XPATH_TEXTO_ERROR = '/html/body/form/table[6]/tbody/tr/td/ul/li'
    XPATH_ALTERNATIVO = '/html/body/table[2]/tbody/tr/td/b'

    i=0
    ejercicio = 2019
    flag_query = False

    while(i<2 and flag_query == False):
        flag_query = query_rfc(browser, rfc, str(ejercicio))
        if flag_query == True:
            break

        if check_exists(browser, XPATH_TEXTO_ERROR, 'xpath') ==  True:
            texto_error = browser.find_element_by_xpath(XPATH_TEXTO_ERROR)
            texto_error = texto_error.get_attribute("innerHTML")
            if texto_error == ERRORES["NO_AUTORIZADO"]:
                ejercicio -= 1
                if ejercicio < 2014:
                    return None
                i = 0
            elif texto_error == ERRORES["AL_RECUPERAR"]:
                i += 1
            else:
                raise "Error"
        elif check_exists(browser, XPATH_ALTERNATIVO, 'xpath') ==  True:
                texto_error = browser.find_element_by_xpath(XPATH_ALTERNATIVO)
                texto_error = texto_error.get_attribute("innerHTML")
                if texto_error == ERRORES["NO_EXISTE_DATO"]:
                    ejercicio -= 1
                    if ejercicio < 2014:
                        return None
                    i = 0
        else:
            i+=1
    if i == 2:
        return None
    return browser
