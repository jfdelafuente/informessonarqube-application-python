import json
import requests
import api.SonarAPIHandler as sonarAPIHandler
import pandas as pd
from utils.utils import get_namespace, get_lenguaje, get_tipo
from datetime import datetime


columns = ['project', 'aplicacion', 'name', 'tipo', 'lenguaje', 'date', 'complexity', 'coverage', 'ncloc',	'duplicated_lines_density',
            'code_smells', 'bugs', 'vulnerabilities', 'sqale_index', 'sqale_rating', 'sqale_debt_ratio', 'reliability_rating',
            'security_rating', 'alert_status', 'quality_gate']


'''
    Función que realiza la extracción de componentes(repositorios) sobre el "host"
    de Sonar indicado y utilizando el API
'''
def extract_proyectos(sonar_handle):
    index = 1
    pageSize = 100
    total = 5000
    project_ids = []
    contador = 0
    
    def get_project_data(project):
        namespace = get_namespace(project["project"])
        tipo = get_tipo(project["project"])
        lenguaje = get_lenguaje(project["project"])
        quality_gate = sonar_handle.get_qualitygate_by_project(project["project"])
        quality_json = json.loads(quality_gate.text)
        return (
            project["project"],
            namespace,
            project["name"],
            tipo,
            lenguaje,
            quality_json["qualityGate"]["name"]
        )

    while index * pageSize < total + pageSize:
        project_response = sonar_handle.get_component(qualifiers="TRK", index=index)
        try:
            project_response.raise_for_status()
            datos_json = json.loads(project_response.text)
            index += 1
            total = datos_json["paging"]["total"]

            for project in datos_json["components"]:
                contador += 1
                project_ids.append(get_project_data(project))

        except requests.exceptions.HTTPError as err:
            print(f"Error en la solicitud: {err}")
            break

    print(f"Extraccion Proyectos: se han tratado {contador} proyectos")
    df_project = pd.DataFrame(project_ids, columns=["project", "namespace", "name", "tipo", "lenguaje", "quality_gate"])
    return df_project

'''
    Función que realiza la extracción del histórico de medidas de los projectos
    incluídos en el campo "project" del dataframe de entrada.
'''
def extract_historico(df_projects, sonar_handle):

    project_ids = []
    
    def get_value(history):
        try:
            return history["value"]
        except KeyError:
            return 0
    
    for i, row in df_projects.iterrows():
        measures = sonar_handle.get_measures_history(row["project"])
        datos_json = json.loads(measures.text)
        for component in datos_json["measures"]:
            for history in component["history"]:
                value = get_value(history)
                project_ids.append(
                    (
                        get_namespace(row["project"]),
                        row["name"],
                        get_lenguaje(row["project"]),
                        component["metric"],
                        datetime.fromisoformat(history["date"]).strftime(
                            "%Y-%m-%d %H:%M:%S"),
                        value
                    )
                )
    print("Extraccion Históricos: se han tratado %s proyectos" % i)
    df_project = pd.DataFrame(project_ids, columns=[
                "aplicacion", "proyecto", "lenguaje", "metric", "date", "value"])
    return df_project

'''
    Función que realiza la extracción en columnas del histórico de medidas de los projectos
    incluídos en el campo "project" del dataframe de entrada.
'''
def extract_historico_columnas(df_projects, sonar_handle):
    project_ids = []
    tratadas = 0
    evaluadas = 0
    total = df_projects.shape[0]
    print(f'Se van a tratar {total} filas')
    for t, row in df_projects.iterrows():
        # print(f'Tratando el proyecto {row["project"]}')
        measures = sonar_handle.get_measures_history(row["project"])
        if measures.status_code == 200:
            datos_json = json.loads(measures.text)
            # print(json.dumps(datos_json, indent=4, sort_keys=True)) 
            evaluadas += 1

            total_history = len(datos_json["measures"][0]["history"])
            total_measures = len(datos_json["measures"])
            # print(f'El proyecto {row["project"]} tiene {total_history} historico.')
            for i in range(total_history):
                tratadas += 1
                # print(f'Tratando {i+1}/{total_history} del proyecto {row["project"]}')
                dict_metrics = {}
                dict_metrics["project"] = row["project"]
                dict_metrics["aplicacion"] = row["namespace"]
                dict_metrics["name"] = row["name"]
                dict_metrics["tipo"] = row["tipo"]
                dict_metrics["lenguaje"] = row["lenguaje"]
                dict_metrics["quality_gate"] = row["quality_gate"]
                
                for j in range(total_measures):
                    dict_metrics["date"] = datetime.fromisoformat(
                        datos_json["measures"][j]["history"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                    if len(datos_json["measures"][j]["history"][i]) > 1:
                        value = datos_json["measures"][j]["history"][i]["value"]
                        dict_metrics[datos_json["measures"][j]["metric"]] = value
                    else:
                        dict_metrics[datos_json["measures"][j]["metric"]] = "0"

                project_ids.append(dict_metrics)
        else:
            print(f"Error en la solicitud HTTP para {row['project']}. Código: {measures.status_code}")

    print(f"Extraccion Histórico: de {total} filas se han evaluado {evaluadas} y tratados {tratadas} proyectos")
    df_project = pd.DataFrame(project_ids, columns=columns)
    return df_project

def extract_historico_columnas_from(df_projects, date_from, sonar_handle):
    # inicializamos Sonarqube
    project_ids = []
    tratadas = 0
    evaluadas = 0
    total = df_projects.shape[0]
    print(f'Se van a tratar {total} filas')
    for _, row in df_projects.iterrows():
        # print(f'Tratando el proyecto {row["project"]}')
        measures = sonar_handle.get_measures_history_from(row["project"], date_from)
        if measures.status_code == 200:
            datos_json = json.loads(measures.text)
            # print(json.dumps(datos_json, indent=4, sort_keys=True)) 
            evaluadas += 1

            total_history = len(datos_json["measures"][0]["history"])
            total_measures = len(datos_json["measures"])
            # print(f'El proyecto {row["project"]} tiene {total_history} historico.')
            for i in range(total_history):
                tratadas = tratadas + 1
                # print(f'Tratando {i+1}/{total_history} del proyecto {row["project"]}')
                dict_metrics = {}
                dict_metrics["project"] = row["project"]
                dict_metrics["aplicacion"] = row["namespace"]
                dict_metrics["name"] = row["name"]
                dict_metrics["tipo"] = row["tipo"]
                dict_metrics["lenguaje"] = row["lenguaje"]
                dict_metrics["quality_gate"] = row["quality_gate"]
                
                for j in range(total_measures):
                    dict_metrics["date"] = datetime.fromisoformat(
                        datos_json["measures"][j]["history"][i]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                    if len(datos_json["measures"][j]["history"][i]) > 1:
                        value = datos_json["measures"][j]["history"][i]["value"]
                        dict_metrics[datos_json["measures"][j]["metric"]] = value
                    else:
                        dict_metrics[datos_json["measures"][j]["metric"]] = "0"

                project_ids.append(dict_metrics)
        else:
            print(f"Error en la solicitud HTTP para {row['project']}. Código: {measures.status_code}")

    print(f"Extraccion Histórico: de {total} filas se han evaluado {evaluadas} y tratados {tratadas} proyectos")
    df_project = pd.DataFrame(project_ids, columns=columns)
    return df_project

def extract_measure(df_projects, sonar_handle):
    project_ids = []
    no_tratado = 0
    tratados = 0
    print(f'Se van a tratar {df_projects.shape[0]} filas')
    for _, row in df_projects.iterrows():
        measures = sonar_handle.get_measures_history(row["project"])
        datos_json = json.loads(measures.text)
        #print(json.dumps(datos_json, indent=4, sort_keys=True))
        if datos_json["paging"]["total"] > 0:
            tratados = tratados + 1
            # print(row["project"])
            dict_metrics = {}
            dict_metrics["project"] = row["project"]
            dict_metrics["aplicacion"] = row["namespace"]
            dict_metrics["name"] = row["name"]
            dict_metrics["tipo"] = row["tipo"]
            dict_metrics["lenguaje"] = row["lenguaje"]
            dict_metrics["quality_gate"] = row["quality_gate"]

            total_measures = len(datos_json["measures"])
            for i in range(total_measures):
                ultimo = len(datos_json["measures"][i]["history"]) - 1
                dict_metrics["date"] = datetime.fromisoformat(datos_json["measures"][i]["history"][ultimo]["date"]).strftime("%Y-%m-%d %H:%M:%S")
                try:
                    dict_metrics[datos_json["measures"][i]["metric"]
                                ] = datos_json["measures"][i]["history"][ultimo]["value"]
                except Exception as err:
                    # print(f"No encontrado {err=} en %s" % (err))
                    dict_metrics[datos_json["measures"][i]["metric"]] = ""

            project_ids.append(dict_metrics)
        else:
            no_tratado = no_tratado + 1

    print(f"Extraccion Métricas: se han tratado {tratados} proyectos y no tratados {no_tratado}")
    df_project = pd.DataFrame(project_ids, columns=columns)
    return df_project


def extract_analisis(df_projects, sonar_handle):
    project_ids = []
    tratados = 0
    evaluados = 0
    print(f'Se van a tratar {df_projects.shape[0]} filas')
    for i, row in df_projects.iterrows():
        evaluados += 1
        measures = sonar_handle.get_project_analyses(row["project"])
        # print(f'Tratando {row["project"]}')
        if measures.status_code == 200:
            datos_json = json.loads(measures.text)
            # print(json.dumps(datos_json, indent=4, sort_keys=True))
            for analisis in datos_json.get("analyses", []):
                for eventos in analisis.get("events", []):
                    if eventos.get("category") == "VERSION":
                        tratados += 1
                        project_ids.append(
                            (
                                get_namespace(row["project"]),
                                row["name"],
                                get_lenguaje(row["project"]),
                                datetime.fromisoformat(analisis["date"]).strftime("%Y-%m-%d %H:%M:%S"),
                                eventos["name"]
                            )
                        )
            print(f"Error en la solicitud HTTP para {row['project']}. Código: {measures.status_code}")            
                    
    print(f"Extraccion Análisis: se han evaluado {evaluados} proyectos y {tratados} tratados")
    df_project = pd.DataFrame(project_ids, columns=[
                "aplicacion", "name", "lenguaje", "date", "version"])
    return df_project
