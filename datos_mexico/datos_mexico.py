import pandas as pd 
import requests 
data = requests.get("copie aquí la URL") 
df = pd.DataFrame(data.json()["data"])
