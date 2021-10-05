from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import TableFuncs
from constantes import TABLAS, NAMES

import pandas as pd

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
    osc[NAMES['rubros_autorizados']] = rubros

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
        ejercicios_box = browser.find_element_by_id("transparenciaDetForm:idSelectEjercicioFiscal")
        ejercicios_disponibles = Select(ejercicios_box)
        ejercicios_disponibles = [opt.text for opt in ejercicios_disponibles.options]
        for ejercicio in ejercicios_disponibles:
            print(ejercicio)
            browser.find_element_by_xpath(f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]").click()
            boton_consulta = browser.find_element_by_id("transparenciaDetForm:_idJsp22")
            boton_consulta.click()
            osc[ejercicio] = get_osc_data(browser)
        break
    else:
        print("Error, al consultar datos...\n")
    i += 1

browser.close()
browser.quit()
print(osc)

df = pd.DataFrame.from_dict(osc)
df.to_excel('C:/Users/ZIGLA/Documents/TEST_YCO.xlsx')