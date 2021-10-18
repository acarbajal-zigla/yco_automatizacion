from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
from scraper_yco import connect_sat, get_osc_data, check_exists
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

file = open("rfcs.txt")
rfc_list = file.readlines()
data = dict()

import pandas as pd

for rfc in rfc_list:
    osc=dict()
    print(f"Obteniendo datos de {rfc}")
    
    browser = connect_sat(rfc)
    if browser == None:
        continue

    i=0
    while(i<2):
        if check_exists(browser, 'transparenciaDetForm:idSelectEjercicioFiscal', 'id') == True:
            ejercicios_box = browser.find_element_by_id("transparenciaDetForm:idSelectEjercicioFiscal")
            ejercicios_disponibles = Select(ejercicios_box)
            ejercicios_disponibles = [opt.text for opt in ejercicios_disponibles.options if int(opt.text) >= 2014 and int(opt.text) < 2020]
            ejercicios_disponibles.sort(reverse=True)
            break
        else:
            browser.quit()
            browser = connect_sat(rfc)
        i += 1

    for ejercicio in ejercicios_disponibles:
        if check_exists(browser, 'transparenciaDetForm:_idJsp22', 'id') == True:
            browser.find_element_by_xpath(f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]").click() # Selector de año
            boton_consulta = browser.find_element_by_id('transparenciaDetForm:_idJsp22') # Boton Consultar
            boton_consulta.click()
        while check_exists(browser, f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]", "xpath") == False:
            if check_exists(browser, '/html/body/table[2]/tbody/tr/td/b', 'xpath') == True:
                browser.quit()
                browser = connect_sat(rfc)
            elif check_exists(browser, "_idJsp1:_idJsp6", "id") == True:
                boton_consulta = browser.find_element_by_id("_idJsp1:_idJsp6") # Botón de continuar para DDJJs
                boton_consulta.click()
            else:
                browser.quit()
                print("Error desconocido, abortando...\n")
                raise
            try:
                wait = WebDriverWait(browser, 4)
                boton_RFC = wait.until(EC.element_to_be_clickable((By.ID, 'transparenciaDetForm:_idJsp22')))
            except TimeoutException:
                pass
        osc[ejercicio] = get_osc_data(browser)
    browser.quit()
    data[rfc] = osc   

pd.DataFrame.from_dict(data).to_excel("test.xlsx")

print(data)



###### LA SESSION HA CADUCADO

# "/html/body/table[2]/tbody/tr/td/b"
# Botón "Aceptar" (name = "Aceptar")