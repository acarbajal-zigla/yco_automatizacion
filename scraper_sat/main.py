from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper_yco import submit_rfc_form, get_osc_data
from threading import Thread
import pandas as pd

import logging
logging.basicConfig(filename='rfc_con_erroes.log', encoding='utf-8', level=logging.DEBUG)

def scraper_rfc(rfc, data_rfcs):
    browser = submit_rfc_form(rfc, ejercicio)
    if browser != None:
        while(True):
            try:
                data_rfcs[rfc] = get_osc_data(browser)
                browser.quit()
                break
            except (TimeoutException, NoSuchElementException):
                browser = submit_rfc_form(rfc, ejercicio)
    else:
        logging.info(f"Error en {rfc} - browser == None\n")

file = open("rfcs.txt")
rfc_list = list(set(file.readlines()))
print(len(rfc_list))

ejercicio = 2019
data_rfcs = dict()

# Creo lista de threads
threads = []
for i in range(0,len(rfc_list),3):
    if(i+3<len(rfc_list)):
        aux = rfc_list[i:i+3]
    else:
        aux = rfc_list[i:]

    for rfc in aux:
        # Inicio un thread por rfc.
        process = Thread(target=scraper_rfc, args=[rfc, data_rfcs])
        process.start()
        threads.append(process)

    # joineo los threads al main y los valores deberian estar guardados
    for process in threads:
        process.join()

pd.DataFrame.from_dict(data_rfcs).to_excel("out.xlsx")

###### LA SESSION HA CADUCADO

# "/html/body/table[2]/tbody/tr/td/b"
# Botón "Aceptar" (name = "Aceptar")