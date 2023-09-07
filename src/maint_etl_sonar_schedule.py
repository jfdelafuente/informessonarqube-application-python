from etl.sonar.extract import extract_proyectos, extract_measure, extract_historico_columnas, extract_analisis
from etl.sonar.transform import eliminar_error_namespaces, transformar_java, transformar_date
from utils.utils import load_to_csv, extract_from_csv
import configSonar
import os
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler

'''
    Proceso para extraer todos los componentes de SONAR
'''

def etl_job():
    print("")
    print("SONAR: Extraccion de proyectos ...")
    df_project = extract_proyectos()
    load_to_csv(configSonar.DIR_SONAR_XLSX +
                "sonar_salida_projects_etl_tc.csv", df_project)  
    print("SONAR: Extraccion de proyectos ... Fin carga proyectos")

    print("SONAR : Eliminar errores")
    df_project = df_project.sort_values('namespace')
    df_project = eliminar_error_namespaces(df_project)
    # df_project = transformar_java(df_project)
    print("SONAR : Fin eliminar Errores")

    print("SONAR : Inicio Extracción MÉTRICAS")
    df_measures = extract_measure(df_project)
    # df_measures = transformar_date(df_measures)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
                "sonar_salida_measure_etl_tc.csv", df_measures)
    print("SONAR : Fin carga Métricas")

    print("SONAR : Inicio Extracción historico")
    df_historico = extract_historico_columnas(df_project)
    # df_historico = transformar_date(df_historico)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
                "sonar_salida_historico_etl_tc.csv", df_historico)
    print("SONAR : Fin carga Historico")

    print("SONAR: Inicio Extraccion analisis")
    df_analisis = extract_analisis(df_project)
    # df_analisis = transformar_date(df_analisis)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
                "sonar_salida_project_analisis_etl_tc.csv", df_analisis)
    print("SONAR : Fin carga Analisis")

    print("")



if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(etl_job, 'interval', minutes=10)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()