from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
            by = By.XPATH
        elif mode == 'id':
            by= By.ID
        elif mode == 'name':
            by = By.NAME

        wait.until(EC.presence_of_element_located((by, path_or_id)))
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
        if data == None:
            print(f"Error en {table_data['categoria']}")
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
    XPATH_TEXTO_NO_HA_CAPTURADO = '/html/body/table[2]/tbody/tr/td/b'
    ID_BOTON_RFC = 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20'
    ID_BOTON_DDJJ = '_idJsp1:_idJsp6'

    # Cargo el formulario y hago click en Buscar
    browser = None
    while browser == None:
        browser = cargar_sat(rfc, ejercicio)
    
        # Click en boton de RFC que me lleva a los datos de la consulta
        if check_exists(browser, ID_BOTON_RFC, 'id') == True:
            browser.find_element_by_id(ID_BOTON_RFC).click()

            if check_exists(browser, ID_BOTON_DDJJ, 'id') == True:
                browser.find_element_by_id(ID_BOTON_DDJJ).click() # Click en boton de DDJJs ("Consultar Registro")
            elif check_exists(browser, XPATH_TEXTO_NO_HA_CAPTURADO, 'xpath') == True:
                texto_error = browser.find_element_by_xpath(XPATH_TEXTO_NO_HA_CAPTURADO)
                texto_error = texto_error.get_attribute("innerHTML")
                if texto_error == ERRORES["NO_EXISTE_DATO"]:
                    browser.quit()
                    return None
        
        elif check_exists(browser, XPATH_TEXTO_ERROR, 'xpath') ==  True:
            texto_error = browser.find_element_by_xpath(XPATH_TEXTO_ERROR)
            texto_error = texto_error.get_attribute("innerHTML")
        
            if texto_error == ERRORES["AL_RECUPERAR"]:
                # Error estandar - error al recuperar los datos. Solo hay que intentar de nuevo.
                browser.find_element_by_id("publicaConsultaDonaForm:_idJsp24").click()
                if check_exists(browser, ID_BOTON_RFC, 'id') == True:
                    # Click en boton de RFC que me lleva a los datos de la consulta
                    browser.find_element_by_id(ID_BOTON_RFC).click()
            elif texto_error == ERRORES["NO_AUTORIZADO"]:
                # No hay datos para este ejercicio
                browser.quit()
                return None
        # No hay datos para este ejercicio
        elif check_exists(browser, XPATH_TEXTO_NO_HA_CAPTURADO, 'xpath') ==  True:
            browser.quit()
            return None

        # Devuelvo el browser si pude ingresar bien chequeando la existencia del campo "Misión" - else: False
        if check_exists(browser, NAMES['Mision'], 'name') == True:
            return browser
        else:
            print("No se encontró MISIÓN")
            return None
