from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def get_headers_tabla(tabla:webdriver.WebElement):
    headers = [element.gett_attribute('innerHTML') for element in tabla.find_elements_by_class_name('tablaHeader')] 
    return headers

def get_valores_renglones(tabla:webdriver.WebElement):
    renglones = tabla.find_elements_by_xpath(".//tr[contains(@class,'renglon')]")
    valores=[]
    for renglon in renglones:
        valores.append(tuple([a for a in renglon.find_elements_by_xpath(".//*") if not(a.get_attribute('innerHTML').startsWith('<'))]))
    return valores

def get_datos_tabla(browser: webdriver.Chrome, table_data:dict):
    # table_data = {'categoria':CAT, 'subcategoria':SUBCAT}
    HEAD = 'transparenciaDetForm'

    ids = {'table':f"{HEAD}:id{table_data['categoria']}Registro:dataTable{table_data['subcategoria']}", 
            'scroll':f"{HEAD}:id{table_data['categoria']}Registro:scroll{table_data['subcategoria']}next"
            }

    # Encuentro la tabla y la guardo en la variable "tabla"
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, ids['table']+':tbody_element')))
    tabla = browser.find_element_by_id(ids['table'])

    # Guardo headers de la tabla
    headers = get_headers_tabla(tabla)
    button_next_scroller = browser.find_element_by_id(ids['scroll'])
    scroller = button_next_scroller.find_element_by_xpath('../..')
    paginas = len(scroller) - 5

    valores=[]
    
    if(paginas <= 1):
        paginas = 1

    for page in range(1, paginas + 1):
        wait.until(EC.presence_of_element_located((By.ID, ids['table']+':tbody_element')))
        valores = get_valores_renglones(tabla)
        if paginas > 1 and page < paginas:
            browser.find_element_by_id(ids['scroll'] + 'next').click()
    
    data_tabla = dict()
    for tupla in valores:
        for i in range(len(headers)):
            data_tabla[headers[i]] = tupla[i]
    return data_tabla