from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import TableFuncs
from constantes import TABLAS, NAMES, ERRORES

def check_exists(browser, path_or_id, mode):
    ret = True
    wait = WebDriverWait(browser, 3)
    try:
        if mode == 'xpath':
            wait.until(EC.presence_of_element_located((By.XPATH, path_or_id)))
        elif mode == 'id':
            wait.until(EC.presence_of_element_located((By.ID, path_or_id)))
    except TimeoutException:
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
 
def get_osc_data(browser):
    """Funcion que scrapea todos los datos devueltos por la consulta"""
    osc = dict()

    for key in NAMES.keys():
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

def cargar_sat(rfc, ejercicio):
    URL = "https://portalsat.plataforma.sat.gob.mx/TransparenciaDonaciones/faces/publica/frmCConsultaDona.jsp"
    options = Options()
    options.headless=True
    browser = webdriver.Chrome(options=options)

    try:
        browser.get(URL)
        # Setteo el ejercicio y el RFC en el formulario
        browser.find_element_by_id('publicaConsultaDonaForm:idSelectEjercicioFiscal').send_keys(ejercicio)
        browser.find_element_by_id("publicaConsultaDonaForm:idRfc").send_keys(rfc)
        # Submit
        browser.find_element_by_id("publicaConsultaDonaForm:_idJsp24").click()
    except:
        return None
    return browser

def submit_rfc_form(rfc: str, ejercicio: str):
    XPATH_TEXTO_ERROR = '/html/body/form/table[6]/tbody/tr/td/ul/li'
    ID_BOTON_RFC = 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20'
    browser = None

    while browser == None:
        browser = cargar_sat(rfc, ejercicio)
    
    if check_exists(browser, ID_BOTON_RFC, 'id') == True:
        # Click en boton de RFC que me lleva a los datos de la consulta
        browser.find_element_by_id(ID_BOTON_RFC).click()
        # En caso de surgir una pantalla de DDJJ
        if check_exists(browser, '_idJsp1:_idJsp6', 'id') == True:
            browser.find_element_by_id('_idJsp1:_idJsp6').click() # Click en boton de DDJJs
    elif check_exists(browser, XPATH_TEXTO_ERROR, 'xpath') ==  True:
        texto_error = browser.find_element_by_xpath(XPATH_TEXTO_ERROR)
        texto_error = texto_error.get_attribute("innerHTML")
        # Error estandar - error al recuperar los datos. Solo hay que intentar de nuevo.
        if texto_error == ERRORES["AL_RECUPERAR"] or texto_error == ERRORES["SESION"]:
            browser.quit()
            browser = cargar_sat(rfc, ejercicio)
            """# No hay datos para este ejercicio
            elif texto_error == ERRORES["NO_AUTORIZADO"]:
                browser.quit()
                return None"""
        else:
            browser.quit()
            return None
    elif check_exists(browser, XPATH_TEXTO_ERROR, 'xpath') ==  True:
        browser.quit()
        return None

    # Devuelvo True si pude ingresar bien chequeando la existencia del botón "Consultar" - else: False
    if check_exists(browser, NAMES['Mision'], 'id') == True:
        return browser
    else:
        return None
