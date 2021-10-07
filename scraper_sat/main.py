from selenium.webdriver.support.select import Select
from scraper_yco import connect_sat, get_osc_data
from selenium.common.exceptions import NoSuchElementException
file = open("rfcs.txt")
rfc_list = file.readlines()
data = dict()

import pandas as pd

for rfc in rfc_list:
    osc=dict()
    print(f"Obteniendo datos de {rfc}")
    i=0
    browser = connect_sat(rfc)
    while(i<2):
        try:
            ejercicios_box = browser.find_element_by_id("transparenciaDetForm:idSelectEjercicioFiscal")
            ejercicios_disponibles = Select(ejercicios_box)
            ejercicios_disponibles = [opt.text for opt in ejercicios_disponibles.options]
            ejercicios_disponibles.sort(reverse=True)
        except NoSuchElementException:
            try:
                boton_consulta = browser.find_element_by_id("_idJsp1:_idJsp6")
                boton_consulta.click()
                continue
            except:
                browser.quit()
                print("Error desconocido, abortando...\n")
                exit()
        for ejercicio in ejercicios_disponibles:
            if int(ejercicio) >= 2014:
                try:
                    browser.find_element_by_xpath(f"//select[@name='transparenciaDetForm:idSelectEjercicioFiscal']/option[text()={ejercicio}]").click()
                    boton_consulta = browser.find_element_by_id("transparenciaDetForm:_idJsp22")
                    boton_consulta.click()
                except NoSuchElementException:
                    try:
                        boton_consulta = browser.find_element_by_id("_idJsp1:_idJsp6")
                        boton_consulta.click()
                    except:
                        browser.quit()
                        print("Error desconocido, abortando...\n")
                        raise
                    browser.quit()
                    browser = connect_sat(rfc)
                    continue
                try:
                    browser.find_element_by_xpath("/html/body/table[2]/tbody/tr/td/b")
                    browser.quit()
                    browser = connect_sat(rfc)
                    continue
                except NoSuchElementException:
                    osc[ejercicio] = get_osc_data(browser)
                    i = 0
            else:
                break
        i += 1
        browser.quit()
        break
    data[rfc] = osc   

pd.DataFrame.from_dict(data).to_excel("test.xlsx")

print(data)