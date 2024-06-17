import json
import configSonar
import api.SonarAPIHandler as sonarAPIHandler
import datetime
from utils.utils import load_to_json



def main():
    
    # inicializamos Sonarqube
    print("Inicio")
    sonar = sonarAPIHandler.SonarAPIHandler()
    index = 1;
    pageSize = 100;
    total = 5000;
    
    # project_name = "com.orange.crm4telcoosp.application.java:crm4telco"
    project_name = "com.orange.autorggccosp.spa.typescript:autorbdmfront"
    
    component_project, component_name = project_name.split(sep=':')
    origen, compania, app, aplication, lenguaje = component_project.split(sep='.')
    print(project_name)
    
    while index * pageSize < total + pageSize:

        # obtemos las métricas de cada proyecto
        measures = sonar.get_measures_history(project_name, index)
        datos_json = json.loads(measures.text)
        
        # if datos_json['paging']['total'] == 0:
        #     print("no hay datos")
        #     exit()
    
        nombre_fichero = app + "_" + lenguaje + "_" + component_name + "_history_" + str(index) + ".json"
        load_to_json(nombre_fichero, datos_json)
        index += 1
        total = datos_json["paging"]["total"]

    print("Fin")
        
if __name__ == '__main__':
    main()