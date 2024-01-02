from etl.sonar.extract import extract_proyectos, extract_measure2
from etl.sonar.transform import eliminar_error_namespaces
from utils.utils import load_to_csv
import configSonar

'''
    Proceso para extraer todos los componentes de SONAR
'''  
def main():
    print("SONAR: Extraccion de proyectos ... ")
    df_project = extract_proyectos()
    
    # Solo datos para el dashboard
    if configSonar.ONLY_DASHBOARD:
        load_to_csv(configSonar.DIR_SONAR_XLSX +
            "sonar_salida_projects_etl_tc.csv", df_project)

    print("SONAR: Extraccion de proyectos ... Fin carga proyectos")
    df_project = df_project.sort_values('namespace')
    df_project = eliminar_error_namespaces(df_project)
    
    print("SONAR : Fin eliminar Errores")
    df_measures = extract_measure2(df_project)
    # df_measures = transformar_date(df_measures)
    file_measure = "sonar_salida_measure_etl_tc.csv"
    load_to_csv(configSonar.DIR_SONAR_XLSX +
        file_measure, df_measures)
    print("SONAR : Fin carga Métricas")


if __name__ == '__main__':
    main()
