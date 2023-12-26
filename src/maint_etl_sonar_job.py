from etl.sonar.extract import extract_proyectos, extract_historico_columnas, extract_analisis, extract_historico_columnas_from, extract_measure
from etl.sonar.transform import eliminar_error_namespaces
from utils.utils import load_to_csv
from utils.lastdate import save_current_date, leer_last_date, nombre_fichero
from datetime import datetime
import configSonar
import schedule
import time

'''
    Proceso para extraer todos los componentes de SONAR
'''

def etl_job():
    print("SONAR: Extraccion de proyectos ... ")
    start_time = time.time()
    df_project = extract_proyectos()
    # Solo datos para el dashboard
    if not configSonar.ONLY_DASHBOARD:
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            "sonar_salida_projects_etl_tc.csv", df_project)
    
    print("SONAR: Extraccion de proyectos ... Fin carga proyectos")



    print("SONAR : Eliminar errores")
    start_time = time.time()
    df_project = df_project.sort_values('namespace')
    df_project = eliminar_error_namespaces(df_project)
    # df_project = transformar_java(df_project)
    print("Limpiar Errores duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin eliminar Errores")


    print("SONAR : Inicio Extracción MÉTRICAS")
    start_time = time.time()
    df_measures = extract_measure(df_project)
    # df_measures = transformar_date(df_measures)
    file_measure = "sonar_salida_measure_etl_tc.csv"
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        file_measure, df_measures)
    print("EXTRACCION Métricas duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin carga Métricas")


    # Extraemos la extracción de histórico
    print("SONAR : Inicio Extracción historico")
    start_time = time.time()
    last_date = leer_last_date(configSonar.DIR_SONAR + 'last_date.txt')
    if last_date=="":
        print("Cargando historico inicial")
        df_historico = extract_historico_columnas(df_project)
    else:
        d = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
        yesterdayD = d.strftime("%Y-%m-%dT%H:%M:%S+0200")
        print("Cargando historico desde ... {time}".format(time=yesterdayD))
        df_historico = extract_historico_columnas_from(df_project, yesterdayD)
    # df_historico = transformar_date(df_historico)
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        nombre_fichero("historico", last_date), df_historico)
    print("EXTRACCION Histórico duration: {} seconds".format(
        time.time() - start_time))
    print("SONAR : Fin carga Historico")


    # Extraemos loa análisis realizados por sonar
    # No es necesaria esta extracción para el Dashboard
    if not configSonar.ONLY_DASHBOARD:
        print("SONAR: Inicio Extraccion analisis")
        start_time = time.time()
        df_analisis = extract_analisis(df_project)
        # df_analisis = transformar_date(df_analisis)
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            "sonar_salida_project_analisis_etl_tc.csv", df_analisis)
        print("EXTRACCION Anális duration: {} seconds".format(
            time.time() - start_time))
        print("SONAR : Fin carga Analisis")

    # finalizamos
    print("")
    save_current_date(configSonar.DIR_SONAR + 'last_date.txt')


def main():
    # Schedule the job every hour
    print("Lanzamos la primera ejecución ...")
    etl_job()
    print("Planificamos cada 60 minutos la ejecución.")
    schedule.every(60).minutes.do(etl_job)

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()