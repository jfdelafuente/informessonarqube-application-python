import json
import configSonar
import api.SonarAPIHandler as sonarAPIHandler
import datetime
from utils.utils import load_to_json

def leer_last_date():
    fecha = ""
    with open(configSonar.DIR_SONAR + 'last_date.txt', mode='r') as file:
        fecha = file.readline()
        
    return fecha

def main():
    
    # inicializamos Sonarqube
    print("Inicio")
    sonar = sonarAPIHandler.SonarAPIHandler()
    
    project_name = "com.orange.pangeaosp.spa.typescript:pdv"
    
    component_project, component_name = project_name.split(sep=':')
    origen, compania, app, aplication, lenguaje = component_project.split(sep='.')
    print(project_name)

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterdayD = yesterday.strftime("%Y-%m-%dT%H:%M:%S+0200")
    # d = datetime.datetime.strptime(leer_last_date(), "%Y-%m-%d %H:%M:%S")
    # yesterdayD = d.strftime("%Y-%m-%dT%H:%M:%S+0200")
    print("{time}".format(time=yesterdayD))
    
    
    # obtemos las métricas de cada proyecto
    measures = sonar.get_measures_history_from(project_name, yesterdayD)
    # measures = sonar.get_measures_history(project_name)
    datos_json = json.loads(measures.text)
    if datos_json['paging']['total'] == 0:
        print("no hay datos")
        exit()
    
    nombre_fichero = app + "_" + lenguaje + "_" + component_name + "_history.json"
    load_to_json(nombre_fichero, datos_json)

    print("Fin")
        
if __name__ == '__main__':
    main()