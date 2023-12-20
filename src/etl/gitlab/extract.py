import gitlab
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

'''
    Funcion auxiliar para validar que el lenguanje del repositorio
    corresponde con las lista de lenguajes a validar
    
'''

def esJava(name):
    try:
        namespace, tipologia, lenguaje= name.split(sep='-')
    except ValueError:
        es_java = False
    else:
        es_java = True if lenguaje == "java" or lenguaje == "c" else False

    return es_java

'''
    Funcion que extrae todos los proyectos  y devuelve un DataFrame con 
    los siguientes valores: 'ID', 'NAME','ID_NAMESPACE','NAMESPACE' y 'WEB_URL'
'''
        
def extract_todos_proyectos():
    gl = gitlab.Gitlab(url=os.environ["GITLAB_DEFAULT_HOST"], private_token=os.environ['GITLAB_ACCESS_TOKEN'])
    project_ids = [] 
    i = 0
    projects = gl.projects.list(iterator=True)
    for project in projects:
        i = i + 1
        # print("Cargando ... %s" % project.attributes["name"])
        project_ids.append((project.id, 
                                project.name,
                                project.attributes["namespace"]["id"],
                                project.attributes["namespace"]["name"],
                                project.attributes["namespace"]["web_url"]
                                ))
        
    df_project = pd.DataFrame(project_ids, columns=["id", "name", "id_namespace", "namespace","web_url"]) 
    print("Extraccion Proyectos: se han extraído %s proyectos" % i)
    # print(df_project)
    return df_project

'''
    Funcion que extrae los proyectos 'JAVA' de Gitlab y devuelve un DataFrame con 
    los siguientes valores: 'ID', 'NAME','ID_NAMESPACE','NAMESPACE' y 'WEB_URL'
'''
        
def extract_proyectos():
    gl = gitlab.Gitlab(url=os.environ["GITLAB_DEFAULT_HOST"], private_token=os.environ['GITLAB_ACCESS_TOKEN'])
    project_ids = [] 
    i = 0
    j = 0
    projects = gl.projects.list(iterator=True)
    for project in projects:
        i = i + 1
        if esJava(project.attributes["name"]):
            j = j + 1
            # print("Cargando ... %s" % project.attributes["name"])
            project_ids.append((project.id, 
                                project.name,
                                project.attributes["namespace"]["id"],
                                project.attributes["namespace"]["name"],
                                project.attributes["namespace"]["web_url"]
                                ))
        
    df_project = pd.DataFrame(project_ids, columns=["id", "name", "id_namespace", "namespace","web_url"]) 
    print("Extraccion Proyectos: se han extraído %s proyectos y se han tratado %s proyectos" % (i,j))
    # print(df_project)
    return df_project

'''
    Funcion que consulta el "id" de proyectos de un dataframe de entrada y devuelve los tags asociados 
    a ese proyecto en otro dataframe con los siguientes valores añadidos:
    "tag_name", "commit_id" y "commit_created_id"
'''
    
def extract_tags(df_project):
    gl = gitlab.Gitlab(url=os.environ["GITLAB_DEFAULT_HOST"], private_token=os.environ['GITLAB_ACCESS_TOKEN'])
    
    # get all members 
    proyectos = []
    num_tags = 0
    for i, row in df_project.iterrows():
        proj_id = gl.projects.get(row["id"], all=True)
        # print(proj_id.to_json(sort_keys=True, indent=4))
        for tag in proj_id.tags.list(get_all=False):
            # print(tag.to_json(sort_keys=True, indent=4))
            num_tags = num_tags + 1
            proyectos.append(
                (
                    row["id"],
                    row["name"],
                    row["id_namespace"],
                    row["namespace"],
                    row["web_url"],
                    tag.attributes["name"],
                    str("'" +tag.attributes["commit"]["short_id"]+ ""),
                    datetime.fromisoformat(tag.attributes["commit"]["created_at"]).strftime("%Y-%m-%d %H:%M:%S")  
                )
            )

    df_commits = pd.DataFrame( proyectos, 
                              columns=[ "id",
                                        "name",
                                        "id_namespace",
                                        "namespace",
                                        "web_url",
                                        "tag_name",
                                        "commit_id",
                                        "commit_created_at"
                              ]).drop_duplicates()
    
    df_commits.sort_values("id", inplace=True)
    print("Extraccion Tags: se han tratado %s proyectos y %s tags" % (i+1, num_tags))
    return df_commits

'''
    Funcion que consulta el "id" de proyectos de un dataframe de entrada y devuelve los COMMITS asociados 
    a ese proyecto en otro dataframe con los siguientes valores añadidos:
    "tag_name", "commit_id" y "commit_created_id"
'''

def extract_commits(df_project):
    gl = gitlab.Gitlab(url=os.environ["GITLAB_DEFAULT_HOST"], private_token=os.environ['GITLAB_ACCESS_TOKEN'])
    
    # get all members 
    proyectos = []
    num_commits = 0
    for i, row in df_project.iterrows():
        proj_id = gl.projects.get(row["id"], all=True)
        # print(proj_id.to_json(sort_keys=True, indent=4))
        for commit in proj_id.commits.list(get_all=False):
            # print(tag.to_json(sort_keys=True, indent=4))
            num_commits = num_commits + 1
            proyectos.append(
                (
                    row["id"],
                    row["name"],
                    row["id_namespace"],
                    row["namespace"],
                    row["web_url"],
                    "",
                    str("'" +commit.attributes["short_id"]+ ""),
                    datetime.fromisoformat(commit.attributes["created_at"]).strftime("%Y-%m-%d %H:%M:%S")  
                )
            )

    df_commits = pd.DataFrame( proyectos, 
                              columns=[ "id",
                                                   "name",
                                                   "id_namespace",
                                                   "namespace",
                                                   "web_url",
                                                   "tag_name",
                                                   "commit_id",
                                                   "commit_created_at"
                              ]).drop_duplicates()
    
    df_commits.sort_values("id", inplace=True)
    print("Extraccion Commits: se han tratado %s proyectos y %s commits" % (i+1, num_commits))
    return df_commits

'''
    Funcion que consulta el "id" de proyectos de un dataframe de entrada y devuelve los PIPELINES asociados 
    a ese proyecto en otro dataframe con los siguientes valores:

    "sha", "status", "ref"(branch), "fihished_at", "id_pipeline" y "web_url"(jenkins)
'''

def extract_pipelines(df_project):
    gl = gitlab.Gitlab(url=os.environ["GITLAB_DEFAULT_HOST"], private_token=os.environ['GITLAB_ACCESS_TOKEN'])
    
    # get all members 
    proyectos = []
    num_pipeline = 0
    for i, row in df_project.iterrows():
        project = gl.projects.get(row["id"], all=True)
        # print("project ok: %s - % s" % (project.attributes["id"], project.attributes["name"]))
        try:
            pipelines = project.pipelines.list(get_all=False)
        except gitlab.exceptions.GitlabListError as msg_error:
                print(f"{msg_error} El {row['id']} no tiene PIPELINE valido!")
        else:
            for pipeline in pipelines:
                # print("pipeline: %s" % pipeline.attributes["id"])
                try:
                    id = pipeline.attributes["id"]
                    pipe = project.pipelines.get(id)          
                except gitlab.exceptions.GitlabListError as msg_error:
                    print(f"{msg_error} - {id} no es un PIPELINE valido!")
                else:
                    if pipe.attributes["finished_at"] is not None:
                        num_pipeline = num_pipeline + 1
                        proyectos.append(
                            (
                            str("'"+pipe.attributes["sha"][:8]+""),
                            pipe.attributes["status"],
                            pipe.attributes["ref"],
                            datetime.fromisoformat(pipe.attributes["finished_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                            pipe.attributes["id"],
                            pipe.attributes["web_url"]
                            )
                        )

    df_commits = pd.DataFrame( proyectos, 
                              columns=[ "sha",
                                        "status",
                                        "ref",
                                        "commit_created_at",
                                        "id_pipeline",
                                        "web_url"
                              ]).drop_duplicates()
    
    df_commits.sort_values("id_pipeline", inplace=True)
    print("Extraccion Pipelines: se han tratado %s proyectos y %s pipelines" % (i+1, num_pipeline))
    
    return df_commits

