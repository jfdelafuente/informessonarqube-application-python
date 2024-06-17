import pandas as pd
import json
from datetime import datetime


def limpiar_datos(file, proyectos, aplicaciones, languages, sheet_name):
    # fichero = nombre+ ".xlsx"
    df = pd.read_excel(file)

    # Remove duplicates
    df = df.drop_duplicates()

    # Filter data
    # df = df[df['aplicacion'] != 'tdccicdosp']
    for aplicacion in aplicaciones:
        df.drop(df[(df['aplicacion'] == aplicacion)].index, inplace=True)

    for proyecto in proyectos:
        df.drop(df[(df['aplicacion'] == proyecto[0] ) & (df['proyecto'] == proyecto[1])].index, inplace=True)
    
    for language in languages:
        df.drop(df[(df['lenguaje'] == language)].index, inplace=True)

    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

'''
    Parsea en un excel las métricas extraidas de un fichero json.
    NO utilizado ... ahora utilizamos "parsear_measure"
'''
def parsear_measure_deprecated(directorio, file_json):
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos = json.load(archivo)
        aplicacion, proyecto = datos["component"]["key"].split(sep=':')
        origen, compania, app, aplication, lenguaje = aplicacion.split(sep='.')
        # print(json.dumps(datos, indent=4, sort_keys=True))
        dict_metrics = {}
        dict_metrics["aplicacion"]  = app
        dict_metrics["proyecto"] = proyecto
        dict_metrics["lenguaje"] = lenguaje
        try:
            dict_metrics['date'] = datetime.fromisoformat(datos["periods"][0]["date"]).strftime("%Y-%m-%d %H:%M:%S")
            dict_metrics["version"] = datos["periods"][0]["parameter"]
        except Exception as err:
            print(f"No encontrado {err=} en %s" % (err))
            dict_metrics["date"] = ""
            dict_metrics["version"] = ""

        for component in datos["component"]["measures"]:
            dict_metrics[component["metric"]] =  component["value"]

        lista_sonar.append(dict_metrics)
    return lista_sonar

'''
    Parsea en un excel las métricas extraidas de un fichero json.
'''

def parsear_measures(directorio, file_json) :
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos_json = json.load(archivo)
        aplicacion, extension = file_json.split(sep='.')
        app, lenguaje, proyecto, history = aplicacion.split(sep='_')
        
        total = datos_json["paging"]["total"]
        ultimo = total - 1
        total_measures = len(datos_json["measures"])
        
        dict_metrics = {}
        dict_metrics["aplicacion"]  = app
        dict_metrics["proyecto"] = proyecto
        dict_metrics["lenguaje"] = lenguaje
            
        for i in range(total_measures):
            dict_metrics["date"] = datetime.fromisoformat(datos_json["measures"][i]["history"][ultimo]["date"]).strftime("%Y-%m-%d %H:%M:%S")
            try:
                dict_metrics[datos_json["measures"][i]["metric"]] = datos_json["measures"][i]["history"][ultimo]["value"]
            except Exception as err:
                print(f"No encontrado {err=} en %s %s %s" % (app, proyecto, lenguaje))
                dict_metrics[datos_json["measures"][i]["metric"]] = ""
                
        lista_sonar.append(dict_metrics)
    return lista_sonar

'''
    funcion que solo funciona para CFM.
    Parsea en un excel los análisis extraidas de un fichero json
'''
    
def parsear_project_analyses(directorio, file_json):
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos = json.load(archivo)
        aplicacion, extension = file_json.split(sep='.')
        app, lenguaje, proyecto, history = aplicacion.split(sep='_')
        
        total = datos["paging"]["total"]
        # print("Total : %s" % total)
        
        for i in range(total):
            dict_metrics = {}
            dict_metrics["aplicacion"]  = app
            dict_metrics["proyecto"] = proyecto
            dict_metrics["lenguaje"] = lenguaje
            dict_metrics["date"] = datetime.fromisoformat(datos["analyses"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
            dict_metrics["version"] = datos["analyses"][i]["projectVersion"]
            '''
            try:
                dict_metrics["version"] = datos["analyses"][i]["projectVersion"]
            except Exception as err:
                print(f"No encontrado {err=} en %s %s %s" % (app, proyecto, lenguaje))
                # print("tamaño : %s" % len(datos["analyses"][i]["events"]))
                if len(datos["analyses"][i]["events"]) > 0:
                    # print("dato : %s" % datos["analyses"][i]["events"][0]["name"])
                    dict_metrics["version"] = datos["analyses"][i]["events"][0]["name"]
            '''

            lista_sonar.append(dict_metrics)
    return lista_sonar

'''
    funcion para TC y CFM
    Parsea en un excel los análisis extraidas de un fichero json
    
'''
def parsear_project_analyses_last(directorio,file_json):
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos = json.load(archivo)
        aplicacion, extension = file_json.split(sep='.')
        app, lenguaje, proyecto, history = aplicacion.split(sep='_')
        
        total = datos["paging"]["total"]
        # print("Total : %s" % total)
        
        for i in range(total):
            dict_metrics = {}
            dict_metrics["aplicacion"]  = app
            dict_metrics["proyecto"] = proyecto
            dict_metrics["lenguaje"] = lenguaje
            dict_metrics["date"] = datetime.fromisoformat(datos["analyses"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
            # dict_metrics["version"] = datos["analyses"][i]["projectVersion"]
            if len(datos["analyses"][i]["events"]) > 0:
                # print("dato : %s" % datos["analyses"][i]["events"][0]["name"])
                dict_metrics["version"] = datos["analyses"][i]["events"][0]["name"]
            else:
                dict_metrics["version"] = ""

            lista_sonar.append(dict_metrics)
    return lista_sonar

'''
    Parsea en un excel en filas las métricas extraidas de un fichero json
    Deprecated
'''

def parsear_measures_history_filas(directorio, file_json) :
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos_json = json.load(archivo)
        aplicacion, extension = file_json.split(sep='.')
        app, lenguaje, proyecto, history = aplicacion.split(sep='_')
        
        total = datos_json["paging"]["total"]
                
        for measure in datos_json["measures"]:
            dict_metrics = {}
            dict_metrics["aplicacion"]  = app
            dict_metrics["proyecto"] = proyecto
            dict_metrics["lenguaje"] = lenguaje
            dict_metrics["metric"] = measure["metric"]
            for i in range(total):
                dict_metrics["date"] = datetime.fromisoformat(measure["history"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                if len(measure["history"][i]) > 1:
                    value = measure["history"][i]["value"]
                    dict_metrics["value"] = value
                else:
                    dict_metrics["value"] = 0
                lista_sonar.append(dict_metrics)
            
    return lista_sonar

'''
    Parsea en un excel en columnas las métricas extraidas de un fichero json
'''

def parsear_measures_history_columnas(directorio, file_json):
    lista_sonar = []
    with open(directorio + file_json) as archivo:
        datos_json = json.load(archivo)
        aplicacion, extension = file_json.split(sep='.')
        app, lenguaje, proyecto, history = aplicacion.split(sep='_')
        
        total = datos_json["paging"]["total"]
        total_measures = len(datos_json["measures"])
            
        for i in range(total):
            dict_metrics = {}
            dict_metrics["aplicacion"]  = app
            dict_metrics["proyecto"] = proyecto
            dict_metrics["lenguaje"] = lenguaje
            for j in range(total_measures):
                dict_metrics["date"] = datetime.fromisoformat(datos_json["measures"][j]["history"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                if len(datos_json["measures"][j]["history"][i]) > 1:
                    value = datos_json["measures"][j]["history"][i]["value"]
                    dict_metrics[datos_json["measures"][j]["metric"]] = value
                else:
                    dict_metrics[datos_json["measures"][j]["metric"]] = "0"
            lista_sonar.append(dict_metrics)
            
    return lista_sonar
