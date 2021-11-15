from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import TableFuncs
from constantes import TABLAS, NAMES, ERRORES

import logging

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
        if data is None:
            logging.info(f"Error en {table_data['categoria']}")
        osc[table_data['categoria']].append(data)
    return osc

def cargar_sat(rfc, ejercicio):
    URL = "https://portalsat.plataforma.sat.gob.mx/TransparenciaDonaciones/faces/publica/frmCConsultaDona.jsp"
    ID_BOTON_RFC = 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20'
    ID_BOTON_DDJJ = '_idJsp1:_idJsp6'
    XPATH_TEXTO_ERROR = '/html/body/form/table[6]/tbody/tr/td/ul/li'
    XPATH_TEXTO_NO_HA_CAPTURADO = '/html/body/table[2]/tbody/tr/td/b'   # Tambien es texto de sesion caducada

    texto_error = ""

    flag_error = True  # False: no hay datos // True: hay datos // None: chequear error
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
        try:
            browser.quit()
        except:
            logging.error(f"[{rfc}] [cargar_sat] - Error al querer cerrar post carga basica de formulario.")
        return None

    if check_exists(browser, ID_BOTON_RFC, 'id') == True:
        boton_rfc = browser.find_element_by_id(ID_BOTON_RFC)
        clase_boton = boton_rfc.find_element_by_xpath(".//span").get_attribute("class")
        if  clase_boton == 'renglonCDecl':
            logging.info(f"[{rfc}] [cargar_sat]: posee datos para {ejercicio} - botón de RFC negro.")
            boton_rfc.click()
            if check_exists(browser, ID_BOTON_DDJJ, 'id') == True: # Caso DDJJ
                logging.info(f"[{rfc}] [cargar_sat]: posee ventana de DDJJ")
                browser.find_element_by_id(ID_BOTON_DDJJ).click() # Click en boton de DDJJs ("Consultar Registro")
            elif check_exists(browser, NAMES['Mision'], 'name') == True:
                logging.info(f"[{rfc}] [cargar_sat]: Ventana de datos alcanzada")
            else:
                logging.error(f"[{rfc}]")
                flag_error = None
        else: # Botón no es negro -> no hay datos => salgo
            logging.info(f"[{rfc}] [cargar_sat]: no posee datos para {ejercicio} - botón de RFC rojo.")
            flag_error = False # No existe el dato
    elif check_exists(browser, XPATH_TEXTO_ERROR, 'xpath') ==  True:
        texto_error = browser.find_element_by_xpath(XPATH_TEXTO_ERROR)
        texto_error = texto_error.get_attribute("innerHTML")
        if texto_error == ERRORES["AL_RECUPERAR"]: # Error estandar - error al recuperar los datos. Solo hay que intentar de nuevo.
            logging.info(f"[{rfc}] [cargar_sat]: - Error estandar")
            browser.find_element_by_id("publicaConsultaDonaForm:_idJsp24").click()
            if check_exists(browser, ID_BOTON_RFC, 'id') == True: # Click en boton de RFC que me lleva a los datos de la consulta
                boton_rfc = browser.find_element_by_id(ID_BOTON_RFC)
                clase_boton = boton_rfc.find_element_by_xpath(".//span").get_attribute("class")
                if  clase_boton == 'renglonCDecl':
                    logging.info(f"[{rfc}] [cargar_sat]: posee datos para {ejercicio} - botón de RFC negro. Post error estandar.")
                    boton_rfc.click()
                    if check_exists(browser, ID_BOTON_DDJJ, 'id') == True: # Caso DDJJ
                        logging.info(f"[{rfc}] [cargar_sat]: posee ventana de DDJJ. Post error estandar.")
                        browser.find_element_by_id(ID_BOTON_DDJJ).click() # Click en boton de DDJJs ("Consultar Registro")
                    elif check_exists(browser, NAMES['Mision'], 'name') == True:
                        logging.info(f"[{rfc}] [cargar_sat]: Ventana de datos alcanzada. Post error estandar.")
                    else:
                        logging.info(f"[{rfc}] [cargar_sat]:: Error extraño post error estandar y click de boton RFC.")
                        flag_error = None
        elif texto_error == ERRORES["NO_AUTORIZADO"]:
            logging.info(f"[{rfc}] [cargar_sat]: no posee datos para {ejercicio}.")
            flag_error = False
        else:
            logging.error(f"[{rfc}] [cargar_sat]:  Error al obtener los datos del {ejercicio} - texto de error extraño.")
            flag_error = None
    elif check_exists(browser, XPATH_TEXTO_NO_HA_CAPTURADO, 'xpath') == True:
        texto_error = browser.find_element_by_xpath(XPATH_TEXTO_NO_HA_CAPTURADO)
        texto_error = texto_error.get_attribute("innerHTML")
        if texto_error == ERRORES["NO_EXISTE_DATO"]:
            logging.info(f"[{rfc}] [cargar_sat]: no posee datos para {ejercicio}.")
            flag_error = False
        else:
            logging.error(f"[{rfc}] [cargar_sat]: error al obtener los datos de {ejercicio} - texto de error alternativo extraño.")
            flag_error = None
    else:
        logging.error(f"[{rfc}] [cargar_sat]: error al obtener datos de {ejercicio}. Situación no contemplada.")
        flag_error = None

    if flag_error is None:
        if check_exists(browser, XPATH_TEXTO_NO_HA_CAPTURADO, 'xpath') == True:
            texto_error = browser.find_element_by_xpath(XPATH_TEXTO_NO_HA_CAPTURADO)
            texto_error = texto_error.get_attribute("innerHTML")
            if texto_error != "LA SESSION HA CADUCADO":
                logging.error(f"[{rfc}] []: - Error no contemplado.")
            else:
                logging.info(f"[{rfc}] [cargar_sat]: - La sesion caducó.")
                browser.quit()
        else:
            inner_html = browser.find_element_by_tag_name('html').get_attribute('innerHTML')
            f = open(f"scraper_sat/unhandled_errors/{rfc}.html", 'w')
            f.write(inner_html)
            f.close()
    elif flag_error == False:
        browser.quit()
    else:
        return browser
    return flag_error

def submit_rfc_form(rfc: str, ejercicio: str):
    browser = None
    XPATH_TEXTO_SESION_CADUCO = '/html/body/table[2]/tbody/tr/td/b'
    while browser is None:
        browser = cargar_sat(rfc, ejercicio)
        if browser == False:
            return False
        elif browser is not None:
            # Devuelvo el browser si pude ingresar bien chequeando la existencia del campo "Misión" - else: None
            if check_exists(browser, NAMES['Mision'], 'name') == True:
                logging.info(f"[{rfc}] [submit_rfc_form]: Retornando browser correctamente - se encontró Mision.")
                return browser
            else:
                logging.error(f"[{rfc}] [submit_rfc_form]: No se encontró Mision.")
                if check_exists(browser, XPATH_TEXTO_SESION_CADUCO, 'xpath') == True:
                    texto_error = browser.find_element_by_xpath(XPATH_TEXTO_SESION_CADUCO)
                    texto_error = texto_error.get_attribute("innerHTML")
                    if texto_error != "LA SESSION HA CADUCADO":
                        logging.error(f"[{rfc}] [submit_rfc_form]: - Error no contemplado.")
                    else:
                        logging.info(f"[{rfc}] [submit_rfc_form]: - La sesion caducó.")
                browser.quit()
                browser = None
