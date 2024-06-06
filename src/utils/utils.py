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

def contar_caracter(palabra, caracter):
    """
    Función para contar el número de veces que un carácter aparece en una palabra.

    Parámetros:
    palabra (str): La palabra en la que se buscará el carácter.
    caracter (str): El carácter a buscar en la palabra.

    Retorna:
    int: El número de veces que el carácter aparece en la palabra.
    """
    if len(caracter) != 1:
        raise ValueError("El segundo argumento debe ser un solo carácter")

    contador = 0
    for c in palabra:
        if c == caracter:
            contador += 1
    return contador

# com.orange.webmethods.differential.package:webmethods
# com.orange.peoplesoft.application.java:psclientes
def extraer_componentes(project):
    try:
        aplicacion, extension = project.split(sep=':')
        num_puntos = contar_caracter(aplicacion, '.')

        if num_puntos > 4:
            dominio, empresa, namespace, subtipo, tipo, lenguaje = aplicacion.split(sep='.')
        else:
            dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')

        return {
            'namespace': namespace,
            'tipo': tipo,
            'lenguaje': lenguaje
        }
    except ValueError as e:
        return {
            'namespace': "error",
            'tipo': "error tipo",
            'lenguaje': "no_languje"
        }

