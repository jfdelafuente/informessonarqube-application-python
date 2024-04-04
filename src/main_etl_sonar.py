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
    
    start_time_total = time.time()
    print("")
    print("SONAR: Extraccion de proyectos ...")
    # if os.path.isfile(configSonar.DIR_SONAR_XLSX + 'sonar_salida_projects_etl_tc.csv'):
    #     print("SONAR: Extraccion de proyectos ... Ficheros encontrados en local. Cargamos los ficheros de proyectos.")
    #     start_time = time.time()
    #     df_project = extract_from_csv(
    #         configSonar.DIR_SONAR_XLSX + 'sonar_salida_projects_etl_tc.csv')
    #     print("...EXTRACCION proyectos from CSV duration : {} seconds".format(
    #         time.time() - start_time))
    # else:
    start_time = time.time()
    df_project = extract_proyectos(sonar_handler)
    
    # Solo datos para el dashboard
    if configSonar.ONLY_DASHBOARD:
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            "sonar_salida_projects_etl_tc.csv", df_project)
    
    print("EXTRACCION proyectos duration: {} seconds".format(time.time() - start_time))        
    print("SONAR: Extraccion de proyectos ... Fin carga proyectos")
    print("----------\n")


    print("SONAR : Eliminar errores")
    # start_time = time.time()
    df_project = df_project.sort_values('namespace')
    df_project, filas_eliminadas = eliminar_error_namespaces(df_project)
    print(f'Se han eliminado {filas_eliminadas} filas por error en el namespace.')
    # df_project = transformar_java(df_project)
    print("Limpiar Errores duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin eliminar Errores")
    print("----------\n")


    print("SONAR : Inicio Extracción MÉTRICAS")
    # start_time = time.time()
    df_measures = extract_measure(df_project, sonar_handler)
    # df_measures = transformar_date(df_measures)
    file_measure = "sonar_salida_measure_etl_tc.csv"
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        file_measure, df_measures)
    print("EXTRACCION Métricas duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin carga Métricas")
    print("----------\n")


    # Extraemos la extracción de histórico
    print("SONAR : Inicio Extracción historico")
    # start_time = time.time()
    last_date = leer_last_date(configSonar.DIR_SONAR + 'last_date.txt')
    if last_date=="":
        print("Cargando historico inicial")
        df_historico = extract_historico_columnas(df_project, sonar_handler)
    else:
        d = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
        yesterdayD = d.strftime("%Y-%m-%dT%H:%M:%S+0200")
        print("Cargando historico desde ... {time}".format(time=yesterdayD))
        df_historico = extract_historico_columnas_from(df_project, yesterdayD, sonar_handler)
    # df_historico = transformar_date(df_historico)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        nombre_fichero("historico", last_date), df_historico)
    print("EXTRACCION Histórico duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin carga Historico")
    print("----------\n")

    # Extraemos loa análisis realizados por sonar
    # No es necesaria esta extracción para el Dashboard
    if configSonar.ONLY_DASHBOARD:
        print("SONAR: Inicio Extraccion analisis")
        # start_time = time.time()
        df_analisis = extract_analisis(df_project, sonar_handler)
        # df_analisis = transformar_date(df_analisis)
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            "sonar_salida_project_analisis_etl_tc.csv", df_analisis)
        print("EXTRACCION Anális duration: {} seconds".format(
            time.time() - start_time))
        print("SONAR : Fin carga Analisis")
        print("----------\n")


    # finalizamos
    print("")
    # save_current_date(configSonar.DIR_SONAR + 'last_date.txt')
    print("TOTAL duration: {} seconds".format(
        time.time() - start_time_total))


if __name__ == '__main__':
    main()
