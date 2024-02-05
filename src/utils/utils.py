from datetime import datetime
import pandas as pd
import json

def extract_from_csv(file_to_process) -> pd.DataFrame: 
    dataframe = pd.read_csv(file_to_process, sep=';') 
    return dataframe

def extract_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe

def extract_from_excel(file_to_process) -> pd.DataFrame:
    dataframe = pd.read_excel(file_to_process) 
    return dataframe

def load_to_csv(targetfile, data_to_load):
    data_to_load.to_csv(targetfile, sep=';', encoding='utf-8', index=False)
    
def load_to_json(targetfile, data_to_load):
    with open(targetfile, 'w') as file:
        return json.dump(data_to_load, file)
      
def log(message):
    timestamp_format = '%H:%M:%S-%h-%d-%Y'
    #Hour-Minute-Second-MonthName-Day-Year
    now = datetime.now() # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open("dealership_logfile.txt","a") as f: f.write(timestamp + ',' + message + '\n')
    
def get_respuesta_json(response):
    return json.loads(response.content.decode("utf8"))

# com.orange.webmethods.differential.package:webmethods
# com.orange.peoplesoft.application.java:psclientes
def get_namespace(project):
    try:
        aplicacion, extension = project.split(sep=':')
        dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')
        return namespace
    except ValueError:
        return "error"

def get_tipo(project):
    try:
        aplicacion, extension = project.split(sep=':')
        dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')
        return tipo
    except ValueError:
        return "error tipo"
    
def get_lenguaje(project):
    try:
        aplicacion, extension = project.split(sep=':')
        dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')
        return lenguaje
    except ValueError:
        return "no_languje"
