from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Funcion que scrapea todos los datos devueltos por la consulta
def get_osc_data(browser):
    osc = {}
    mision = browser.find_element_by_name("transparenciaDetForm:idGralesRegistro:_idJsp31").text
    osc["Mision"] = mision

    rubro_aut = browser.find_element_by_name("transparenciaDetForm:idGralesRegistro:idRubro2")
    rubro_aut = Select(rubro_aut)
    rubros = [opt.text for opt in rubro_aut.options]
    osc["rubros_autorizados"] = rubros

    pagina_web = browser.find_element_by_name("transparenciaDetForm:idGralesRegistro:_idJsp41").text
    osc["pagina_web"] = pagina_web

    # Tabla ingresos --> 'transparenciaDetForm:idIngresosRegistro:dataTableIngresos'
    # Obtener todos los elementos de la tabla --> tabla.find_elements_by_css_selector("*")

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
    
    try:
        wait = WebDriverWait(browser, 10)
        boton_RFC = wait.until(EC.element_to_be_clickable((By.ID, 'publicaConDonaDetalleForm:dataTableDonatarias:0:_idJsp20')))
        boton_RFC.click()
    except:
        return False
    return True
    
RFC = "FLA080707KE7"
ejercicio = '2019'

options = Options()
#options.headless=True
browser = webdriver.Chrome(options=options)

if query_rfc(browser, RFC, ejercicio) == False:
    print("Error, saliendo...\n")
else:
    osc = get_osc_data(browser)

browser.close()
browser.quit()
print(osc)