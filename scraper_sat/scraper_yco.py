from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import get_table_data

NAMES = {
    # Datos generales
    'Mision':'transparenciaDetForm:idGralesRegistro:_idJsp31',
    'Vision':'transparenciaDetForm:idGralesRegistro:_idJsp36',
    'Pagina web':'transparenciaDetForm:idGralesRegistro:_idJsp41',
    'Anio de autorizacion':'transparenciaDetForm:_idJsp26',
    'Socios o Asociados':'transparenciaDetForm:idGralesRegistro:_idJsp67',
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
    
    REGEX_WEB = re.compile(r"window\.open\(\'<web>\', \'popupWindowName\', \'menubar=no, toolbar=no, status=yes\'\); return false;")
    
    field = browser.find_element_by_name(NAMES[field_name])
    if field.tag_name == 'input':
        dict_osc[field_name] = field.get_attribute('value')
    elif field.tag_name == 'textarea':
        dict_osc[field_name] = field.text
    elif field.tag_name == 'a':
        field = field.get_attribute('href')
        match = REGEX_WEB.match(field)
        dict_osc[field_name] = match.group('web')

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

# Egresos
    # Montos y conceptos desarrollo directo de la actividad
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'transparenciaDetForm:idEgresosRegistro:dataTableMontosConceptos:tbody_element')))
    tabla = browser.find_element_by_id("transparenciaDetForm:idEgresosRegistro:dataTableMontosConceptos:tbody_element")
    montos=[]
    aux=dict()
    
    body = tabla.find_element_by_xpath('../../../../../../../../tr[4]/td')
    scroller = body.find_elements_by_xpath(".//table[contains(@class,'scroller')]/tbody/tr/td")
    
    for page in range(1,len(scroller) - 4):
        browser.find_element_by_id(f"transparenciaDetForm:idEgresosRegistro:scrollMontosConceptosidx{page}").click()
        wait.until(EC.presence_of_element_located((By.ID, 'transparenciaDetForm:idEgresosRegistro:dataTableMontosConceptos:tbody_element')))
        tabla = browser.find_element_by_id("transparenciaDetForm:idEgresosRegistro:dataTableMontosConceptos:tbody_element")
        for renglon in tabla.find_elements_by_xpath(".//tr[contains(@class,'renglon')]"):
            for a in renglon.find_elements_by_xpath(".//*"):
                print(a.get_attribute('innerHTML'))
            aux={'monto':'', 'concepto':''}
            aux['monto'] = renglon.find_element_by_xpath(f"./td[1]/table/tbody/tr/td").text
            aux['concepto'] = renglon.find_element_by_xpath(f"./td[2]").text
            montos.append(aux)
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