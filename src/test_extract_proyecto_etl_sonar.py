from etl.sonar.extract import extract_proyectos, extract_historico_columnas, extract_analisis, extract_historico_columnas_from, extract_measure
from etl.sonar.transform import eliminar_error_namespaces
from utils.utils import load_to_csv
from utils.lastdate import save_current_date, leer_last_date, nombre_fichero
from datetime import datetime
import configSonar
import logging
import time
import api.SonarAPIHandler as sonarAPIHandler

'''
    Proceso para extraer todos los componentes de SONAR
'''  
def main():
    # logging.basicConfig(filename=configSonar.DIR_SONAR_LOGS + 'main_etl_sonar_tc.log',
    #                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=print)
    
    sonar_handler = sonarAPIHandler.SonarAPIHandler()
    
    print("")
    print("SONAR: Extraccion de proyectos ...")
    df_project = extract_proyectos(sonar_handler)
    df_project = df_project.sort_values('namespace')

    # Solo datos para el dashboard
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        "test_sonar_salida_projects_etl_tc.csv", df_project)

    print("SONAR: Extraccion de proyectos ... Fin carga proyectos")
    print("----------\n")


    print("SONAR : Eliminar errores")
    # start_time = time.time()
    df_project, filas_eliminadas = eliminar_error_namespaces(df_project)
    print(f'Se han eliminado {filas_eliminadas} filas por error en el namespace.')
    # df_project = transformar_java(df_project)
    print("SONAR : Fin eliminar Errores")
    print("----------\n")

if __name__ == '__main__':
    main()
