from scraper_yco import connect_sat, get_osc_data
from threading import Thread
from queue import Queue
import pandas as pd

def scraper_rfc(rfc, data_rfcs):
    print(f"    Obteniendo datos de {rfc}")
    browser = connect_sat(rfc, ejercicio)
    if browser != None:
        data_rfcs[rfc] = get_osc_data(browser)
        browser.quit()

file = open("rfcs.txt")
rfc_list = file.readlines()

data_final = dict()
for ejercicio in [2019,2018,2017,2016,2015,2014]:
    print(f"Obteniendo datos de {ejercicio}")
    data_rfcs = dict()
    # Creo lista de threads
    threads = []
    for ii in range(len(rfc_list)):
        # Inicio un thread por rfc.
        process = Thread(target=scraper_rfc, args=[rfc_list[ii], data_rfcs])
        process.start()
        threads.append(process)
    
    # joineo los threads al main y los valores deberian estar guardados
    for process in threads:
        process.join()

    data_final[ejercicio] = data_rfcs
pd.DataFrame.from_dict(data_final).to_excel("test.xlsx")



###### LA SESSION HA CADUCADO

# "/html/body/table[2]/tbody/tr/td/b"
# Botón "Aceptar" (name = "Aceptar")