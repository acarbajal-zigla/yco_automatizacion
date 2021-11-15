from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper_yco import submit_rfc_form, get_osc_data
from threading import Thread
import pandas as pd

import logging

import datetime
from os import getcwd
from os import mkdir

import time

start_time = time.time()
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
try:
    mkdir(getcwd() + f"/scraper_sat/run_{timestamp}/")
    mkdir(getcwd() + f"/scraper_sat/run_{timestamp}/output/")
    mkdir(getcwd() + f"/scraper_sat/run_{timestamp}/unhandled_errors/")
except:
    exit()
logger_filename = getcwd() + f"/scraper_sat/run_{timestamp}/log_scraper.log"
f = open(logger_filename, mode='w')
f.close()
logging.basicConfig(filename=logger_filename, encoding='utf-8', level=logging.INFO)

def scraper_rfc(rfc, data_rfcs):
    logging.info(f"[{rfc}]: Proceso iniciado.")
    browser = submit_rfc_form(rfc, ejercicio)
    i = 1
    if browser == False:
        logging.info(f"[{rfc}]: Cerrando sin obtención de datos.")
    elif browser is None:
        logging.error(f"[{rfc}] [scraper_rfc]: browser is None")
    else:
        while(True):
            try:
                data_rfcs[rfc] = get_osc_data(browser)
                browser.quit()
                logging.info(f"[{rfc}]: Informacion conseguida al intento {i}.")
                break
            except (TimeoutException, NoSuchElementException):
                browser.quit()
                browser = submit_rfc_form(rfc, ejercicio)
            i += 1

file = open("rfcs.txt") 
logging.info(f"Número de registros (RFCs): {len(rfc_list)}")

ejercicio = 2019
MAX_THREADS = 30

# Creo lista de threads
threads = []
total_obtenidos = 0
for i in range(0,len(rfc_list),MAX_THREADS):
    start_time_of_batch = time.time()
    data_rfcs = dict()
    logging.info(f"\n---------------------Iniciando set de rfcs #{i//MAX_THREADS}---------------------\n")
    if(i+MAX_THREADS<len(rfc_list)):
        aux = rfc_list[i:i+MAX_THREADS]
    else:
        aux = rfc_list[i:]

    for rfc in aux:
        # Inicio un thread por rfc.
        process = Thread(target=scraper_rfc, args=[rfc.replace("\n", ''), data_rfcs])
        process.start()
        threads.append(process)

    # joineo los threads al main y los valores deberian estar guardados
    for process in threads:
        process.join()

    logging.info(f"-------Información obtenida para {len(data_rfcs)} organizaciones en {round(time.time() - start_time_of_batch, 3)} segundos-------")
    total_obtenidos += len(data_rfcs)
    if len(data_rfcs)>0:
        pd.DataFrame.from_dict(data_rfcs, orient='index').to_excel(f"{getcwd()}/scraper_sat/run_{timestamp}/output/out_{i//MAX_THREADS}.xlsx")
logging.info(f"-------Información obtenida para un total de {total_obtenidos} organizaciones en {round(time.time() - start_time, 3)} segundos-------")
logging.shutdown()