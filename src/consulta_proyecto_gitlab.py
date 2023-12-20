from etl.gitlab.extract import extract_todos_proyectos
from etl.gitlab.transform import eliminar_namespaces
from utils.utils import load_to_csv
import configGitlab

def main():
        # extraemos los proyectos de Gitlab
        print("Iniciamos la consulta de proyectos de GitLab")
        df_extract = extract_todos_proyectos()
        df_extract = df_extract.sort_values('namespace')
        # df_extract = eliminar_namespaces(df_extract)
        load_to_csv(configGitlab.DIR_GITLAB_XLSX +
                    "gitlab_salida_todos_proyectos.csv", df_extract)
        print("Fin consulta proyecto GitLab")
        
if __name__ == '__main__':
    main()