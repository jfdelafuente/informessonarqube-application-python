import pandas as pd
import logging
import os
import time
import configGitlab
from etl.gitlab.extract import extract_proyectos, extract_tags, extract_commits, extract_pipelines
from etl.gitlab.transform import transformar_created_at, eliminar_namespaces, eliminar_duplicados
from utils.utils import load_to_csv, extract_from_csv

''' 
    Script ETL para repositorios "java" y "c" subidos a GitLab
    
    Extract :   Consultar proyectos, commits, tags y pipeline de GitLab
    Transform:  Filtramos para proyectos (namespace) y para 
                commits, tags y pipeline (fecha año 2023)
    Load :  volcamos los datos en los correspondientes ficheros 'csv'

'''
def main():

    print("Lanzando etl gitlab")
    logging.basicConfig(filename=configGitlab.DIR_GITLAB_LOGS + 'main_etl_gitlab.log',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    start_time_total = time.time()
    logging.info("")
    logging.info("GitLab: Extraccion los proyectos ...")
    if os.path.isfile(configGitlab.DIR_GITLAB_XLSX + "gitlab_salida_proyectos.csv"):
        print("Ficheros encontrados en local. Cargamos los ficheros de proyectos.")
        start_time = time.time()
        df_extract = extract_from_csv(
            configGitlab.DIR_GITLAB_XLSX + "gitlab_salida_proyectos.csv")
        # df_extract = eliminar_namespaces(df_extract)
        logging.info("EXTRACCION PROYECT FROM CSV duration: {} seconds".format(
            time.time() - start_time))
    else:
        start_time = time.time()
        # extraemos los proyectos de Gitlab
        df_extract = extract_proyectos()
        df_extract = df_extract.sort_values('namespace')
        logging.info("Filtramos los proyectos no necesarios.")
        df_extract = eliminar_namespaces(df_extract)
        logging.info("TX PROYECT duration: {} seconds".format(
            time.time() - start_time))
        load_to_csv(configGitlab.DIR_GITLAB_XLSX +
                    "gitlab_salida_proyectos.csv", df_extract)
        logging.info("Volcamos PROYECT a cvs duration: {} seconds".format(
            time.time() - start_time))

    try:
        logging.info("")
        logging.info("GitLab: Extraccion de tags ...")
        start_time = time.time()
        df_tags = extract_tags(df_project=df_extract)
        logging.info("EXTRACCION TAGS duration: {} seconds".format(
            time.time() - start_time))
        logging.info("Nos quedamos con los TAGS de este año")
        df_tags = transformar_created_at(df_tags)
        logging.info("TX TAGS duration: {} seconds".format(
            time.time() - start_time))
        load_to_csv(configGitlab.DIR_GITLAB_XLSX +
                    "gitlab_salida_tags.csv", df_tags)
        logging.info("Volcamos TAGS a cvs duration: {} seconds".format(
            time.time() - start_time))
    except Exception as err:
        print(
            f"GitLab: Extraccion de tags ... Encontrado {err=} en %s" % (err))

    try:
        logging.info("")
        logging.info("GitLab: Extraccion de commits ...")
        start_time = time.time()
        df_commits = extract_commits(df_project=df_extract)
        logging.info("EXTRACCION COMMITS duration: {} seconds".format(
            time.time() - start_time))
        logging.info("Nos quedamos con los COMMITS de este año")
        df_commits = transformar_created_at(df_commits)
        logging.info("TX COMMITS duration: {} seconds".format(
            time.time() - start_time))
        load_to_csv(configGitlab.DIR_GITLAB_XLSX +
                    "gitlab_salida_commits.csv", df_commits)
        logging.info("Volcamos COMMITS a cvs duration: {} seconds".format(
            time.time() - start_time))
    except Exception as err:
        print(
            f"GitLab: Extraccion de commits ... Encontrado {err=} en %s" % (err))

    try:
        logging.info("")
        logging.info("Elimiar duplicados en TAGs y COMMITs ...")
        df_commits = eliminar_duplicados(df_tags=df_tags, df_commits=df_commits)
        logging.info("Concatenando TAGs y COMMITs y creando fichero de salida ...")
        start_time = time.time()
        df_total = pd.concat([df_tags, df_commits])
        df_total.to_excel(configGitlab.DIR_GITLAB_XLSX + configGitlab.fich_salida_gitlab, index=False)
        logging.info("Concatenación duration: {} seconds".format(
            time.time() - start_time))
    except Exception as err:
        print(
            f"Concatenando TAGs y COMMITs y creando fichero de salida ... Encontrado {err=} en %s" % (err))

    try:
        logging.info("")
        logging.info("GitLab: Extraccion de pipelines ...")
        start_time = time.time()
        df_pipelines = extract_pipelines(df_project=df_extract)
        logging.info("EXTRACCION PIPELINES duration: {} seconds".format(
            time.time() - start_time))
        logging.info("Nos quedamos con los PIPELINES de este año")
        df_pipelines = transformar_created_at(df_pipelines)
        df_pipelines.sort_values(by='commit_created_at', ascending=False)
        logging.info("TX PIPELINES duration: {} seconds".format(
            time.time() - start_time))
        load_to_csv(configGitlab.DIR_GITLAB_XLSX +
                    "gitlab_salida_pipelines.csv", df_pipelines)
        logging.info("Volcamos PIPELINES a cvs duration: {} seconds".format(
            time.time() - start_time))
    except Exception as err:
        print(
            f"GitLab: Extraccion de pipelines ... Encontrado {err=} en %s" % (err))
    
    
    logging.info("")    
    logging.info("TOTAL duration: {} seconds".format(
            time.time() - start_time_total))


if __name__ == '__main__':
    main()
