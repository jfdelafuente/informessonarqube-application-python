# Generacion Informes

## Instalación

python.exe -m pip install --upgrade pip
pip install -r requirements.txt

## Descripción Sonar

### 1. Realizaremos las consultas a SONAR para obtener los resultados en distintos ficheros JSON.

  1.1 Editaremos el fichero **'./configSonar.py'** con los parametros siguientes parámetros.

    - DIR_SONAR = './'
    - DIR_SONAR_LOGS = DIR_SONAR + 'logs/'
    - DIR_SONAR_XLSX = DIR_SONAR + 'xlsx/SONAR/'

  [!IMPORTANT]
  1.2 Creamos los directoriso "logs/" y "xlsx/SONAR/"
  
  1.3 Ejecutaremos el ejecutable **'./main_etl_sonar.py'**.

  > $python ./src/main_etl_sonar.py
  
    Se ejecutarán 4 procesos:

    - SONAR: Extraccion de proyectos: Se genera un fichero '{DIR_SONAR_XLSX}/sonar_salida_proyects_etl_tc.csv'

    - SONAR : Eliminar errores

    - SONAR : Extracción MÉTRICAS: Se genera un fichero '{DIR_SONAR_XLSX}/sonar_salida_measure_etl_tc.csv'

    - SONAR : Extracción historico: Se genera un fichero '{DIR_SONAR_XLSX}/sonar_salida_historico_etl_tc.csv'

    - SONAR : Extraccion analisis: Se genera un fichero '{DIR_SONAR_XLSX}/sonar_salida_project_analisis_etl_tc.csv'


## Descripción GitLab

### 1. Realizaremos las consultas a GITLAB para obtener los resultados en distintos ficheros JSON.

  1.1 Editaremos el fichero **'./configGitlab.py'** con los parametros siguientes parámetros.

    - DIR_GITLAB = './'
    - DIR_GITLAB_LOGS = DIR_GITLAB + 'logs/'
    - DIR_GITLAB_XLSX = DIR_GITLAB + 'xlsx/GITLAB/'

  [!IMPORTANT]
  1.2 Creamos los directoriso "logs/" y "xlsx/GITLAB/"
  
  1.3 Ejecutaremos el ejecutable **'./main_etl_gitlab.py'**.

  > $python ./src/main_etl_gitlab.py
  
    Se ejecutarán 4 procesos:

    - GITLAB: Extraccion de proyectos con tecnología "java" y "C": Se genera un fichero '{DIR_GITLAB_XLSX}/gitlab_salida_proyectos.csv'

    - GITLAB: Extracción de tags: Se genera un fichero '{DIR_GITLAB_XLSX}/gitlab_salida_tags.csv'

    - GITLAB: Extracción de commits : Se genera un fichero '{DIR_GITLAB_XLSX}/gitlab_salida_commits.csv'

    - GITLAB: Concatenamos TAGs Y COMMITs, eliminando duplicados y se genera un fichoro  '{DIR_GITLAB_XLSX}/gitlab_data.xlsx'

    - GITLAB: Extraccion pipeline: Se genera un fichero '{DIR_GITLAB_XLSX}/gitlab_salida_pipelines.csv'


