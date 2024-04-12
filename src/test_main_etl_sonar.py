from etl.sonar.extract import extract_proyectos, extract_historico_columnas, extract_analisis, extract_historico_columnas_from, extract_measure_mod
from etl.sonar.transform import eliminar_error_namespaces
from utils.utils import load_to_csv, extract_from_csv
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

    # file_measure = "prueba_project.csv"
    file_measure = "sonar_salida_projects_etl_tc_test.csv"
    df_project = extract_from_csv(configSonar.DIR_SONAR_XLSX + file_measure)
    


    print("SONAR : Eliminar errores")
    # start_time = time.time()
    df_project = df_project.sort_values('namespace')
    df_project, filas_eliminadas = eliminar_error_namespaces(df_project)
    print(f'Se han eliminado {filas_eliminadas} filas por error en el namespace.')
    # df_project = transformar_java(df_project)

    print("SONAR : Fin eliminar Errores")
    print("----------\n")


    print("SONAR : Inicio Extracción MÉTRICAS")
    # start_time = time.time()
    df_measures = extract_measure_mod(df_project, sonar_handler)
    # df_measures = transformar_date(df_measures)
    file_measure = "sonar_salida_measure_etl_tc_test_test.csv"
    # load_to_csv(configSonar.DIR_SONAR_XLSX +
    #     file_measure, df_measures)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        nombre_fichero("measure_test", ""), df_measures)

    print("SONAR : Fin carga Métricas")
    print("----------\n")


    # # Extraemos la extracción de histórico
    # print("SONAR : Inicio Extracción historico")
    # # start_time = time.time()
    # last_date = leer_last_date(configSonar.DIR_SONAR + 'last_date.txt')
    # if last_date=="":
    #     print("Cargando historico inicial")
    #     df_historico = extract_historico_columnas(df_project, sonar_handler)
    # else:
    #     d = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
    #     yesterdayD = d.strftime("%Y-%m-%dT%H:%M:%S+0200")
    #     print("Cargando historico desde ... {time}".format(time=yesterdayD))
    #     df_historico = extract_historico_columnas_from(df_project, yesterdayD, sonar_handler)
    # # df_historico = transformar_date(df_historico)
    # load_to_csv(configSonar.DIR_SONAR_XLSX +
    #     nombre_fichero("historico_test_test", last_date), df_historico)

    # print("SONAR : Fin carga Historico")
    # print("----------\n")

    # Extraemos loa análisis realizados por sonar
    # No es necesaria esta extracción para el Dashboard
    if configSonar.ONLY_DASHBOARD:
        print("SONAR: Inicio Extraccion analisis")
        # start_time = time.time()
        df_analisis = extract_analisis(df_project, sonar_handler)
        # df_analisis = transformar_date(df_analisis)
        # load_to_csv(configSonar.DIR_SONAR_XLSX +
        #     "sonar_salida_project_analisis_etl_tc_test.csv", df_analisis)
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            nombre_fichero("analisis_test", ""), df_analisis)

        print("SONAR : Fin carga Analisis")
        print("----------\n")


    # finalizamos
    print("")
    # save_current_date(configSonar.DIR_SONAR + 'last_date.txt')



if __name__ == '__main__':
    main()
