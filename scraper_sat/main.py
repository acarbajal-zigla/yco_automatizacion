from scraper_yco import submit_rfc_form, get_osc_data
from threading import Thread
import pandas as pd

def scraper_rfc(rfc, data_rfcs):
    print(f"    Obteniendo datos de {rfc}")
    browser = submit_rfc_form(rfc, ejercicio)
    if browser != None:
        data_rfcs[rfc] = get_osc_data(browser)
        browser.quit()
    else:
        print("browser IS nONE")

file = open("rfcs.txt")
rfc_list = file.readlines()

ejercicio = 2019
print(f"Obteniendo datos de {ejercicio}")
data_rfcs = dict()

# Creo lista de threads
threads = []
for rfc in rfc_list:
    # Inicio un thread por rfc.
    process = Thread(target=scraper_rfc, args=[rfc, data_rfcs])
    process.start()
    threads.append(process)

# joineo los threads al main y los valores deberian estar guardados
for process in threads:
    process.join()
print(data_rfcs)
pd.DataFrame.from_dict(data_rfcs).to_excel("test3.xlsx")

###### LA SESSION HA CADUCADO

# "/html/body/table[2]/tbody/tr/td/b"
# Botón "Aceptar" (name = "Aceptar")