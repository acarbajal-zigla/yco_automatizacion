from selenium.webdriver.support.select import Select
from scraper_yco import connect_sat, get_osc_data, check_exists
from selenium.common.exceptions import NoSuchElementException
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
        if check_exists("transparenciaDetForm:idSelectEjercicioFiscal", "id") == True:
            ejercicios_box = browser.find_element_by_id("transparenciaDetForm:idSelectEjercicioFiscal")
            ejercicios_disponibles = Select(ejercicios_box)
            ejercicios_disponibles = [opt.text for opt in ejercicios_disponibles.options if int(opt.text) >= 2014]
            ejercicios_disponibles.sort(reverse=True)
            break
        else:
            browser.quit()
            browser = connect_sat(rfc)
            if browser == None:
                continue
            i += 1

    for ejercicio in ejercicios_disponibles:
        if check_exists(f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]", "xpath") == True:
            browser.find_element_by_xpath(f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]").click()
            boton_consulta = browser.find_element_by_id("transparenciaDetForm:_idJsp22") # Boton Consultar
            boton_consulta.click()
        elif check_exists("_idJsp1:_idJsp6", "id") == True:
            boton_consulta = browser.find_element_by_id("_idJsp1:_idJsp6")
            boton_consulta.click()
        elif check_exists("/html/body/table[2]/tbody/tr/td/b", "xpath"):
            # "La Donataria Autorizada no ha capturado la información que desea consultar."
            browser.quit()
            browser = connect_sat(rfc)
            continue
        else:
            osc[ejercicio] = get_osc_data(browser)
            i = 0 

    else:
        browser.quit()
        print("Error desconocido, abortando...\n")
        raise
        
            
                
        

    data[rfc] = osc   

pd.DataFrame.from_dict(data).to_excel("test.xlsx")

print(data)