import pandas as pd


def tranformar_tc(df):
    df[['project_name', 'name']] = df['project'].str.split(pat = ':', expand = True)
    df.drop(['project'], axis=1, inplace=True)
    df[['dominio','empresa','namespace','tipo','lenguaje']] = df['project_name'].str.split(pat = '.', n=4, expand = True)
    df.drop(['dominio','empresa','project_name'], axis=1, inplace=True)
    df['namespace'].fillna('None', inplace=True)
    df['lenguaje'].fillna('None', inplace=True)
    df['tipo'].fillna('None', inplace=True)
    df['name'].fillna('None', inplace=True)
    df[df['lenguaje'] != 'None']
    df[df['namespace'] != 'None']
    df[df['tipo'] != 'None']
    df[df['name'] != 'None']
    
    return df


def filtrar_solo_java(df):
    if 'lenguaje' not in df.columns:
        print("La columna 'lenguaje' no existe en el DataFrame.")
        return df
    
    num_filas = df.shape[0]
    df_extract = df[df['lenguaje'] == 'java' ]
    print(f'Se han eliminado {(num_filas - df_extract.shape[0])} filas por no ser java.')
    return df_extract


def filtrar_por_fecha(df, fecha_corte='2023-01-01'):
    num_filas = df.shape[0]
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    # filtered_df = df.loc[(df['commit_created_at'] >= '2023-01-01') & (df['commit_created_at'] < '2023-09-15')]
    filtered_df = df.loc[(df['date'] >= fecha_corte)]
    print(f'Se han eliminado {(num_filas - filtered_df.shape[0])} filas anteriores a {fecha_corte}.')
    return filtered_df

def eliminar_namespaces(df, namespace_to_exclude='tdccicdosp'):
    if 'namespace' not in df.columns:
        print("La columna 'namespace' no existe en el DataFrame.")
        return df

    num_filas = df.shape[0]
    df = df.drop(df[df['namespace'] == namespace_to_exclude].index)
    filas_eliminadas = num_filas - df.shape[0]
    print(f'Se han eliminado {filas_eliminadas} filas por namespace invalido.')
    return df, filas_eliminadas

def eliminar_namespaces(df, namespace_to_exclude):
    if 'namespace' not in df.columns:
        print("La columna 'namespace' no existe en el DataFrame.")
        return df

    num_filas = df.shape[0]
    df_filtrado = df[~df['namespace'].isin(namespace_to_exclude)]
    filas_eliminadas = num_filas - df_filtrado.shape[0]
    # print(f'Se han eliminado {filas_eliminadas} filas por namespace invalido.')
    return df_filtrado, filas_eliminadas


def eliminar_error_namespaces(df, namespace_to_exclude='error'):
    if 'namespace' not in df.columns:
        print("La columna 'namespace' no existe en el DataFrame.")
        return df

    num_filas = df.shape[0]
    df = df.drop(df[df['namespace'] == namespace_to_exclude].index)
    filas_eliminadas = num_filas - df.shape[0]
    # print(f'Se han eliminado {filas_eliminadas} filas por error en el namespace.')
    return df, filas_eliminadas


def contar_caracter(palabra, caracter):
    """
    Función para contar el número de veces que un carácter aparece en una palabra.

    Parámetros:
    palabra (str): La palabra en la que se buscará el carácter.
    caracter (str): El carácter a buscar en la palabra.

    Retorna:
    int: El número de veces que el carácter aparece en la palabra.
    """
    if len(caracter) != 1:
        raise ValueError("El segundo argumento debe ser un solo carácter")

    contador = 0
    for c in palabra:
        if c == caracter:
            contador += 1
    return contador

# com.orange.webmethods.differential.package:webmethods
# com.orange.peoplesoft.application.java:psclientes
def extraer_componentes(project):
    try:
        aplicacion, extension = project.split(sep=':')
        num_puntos = contar_caracter(aplicacion, '.')

        if num_puntos > 4:
            dominio, empresa, namespace, subtipo, tipo, lenguaje = aplicacion.split(sep='.')
        else:
            dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')

        return {
            'namespace': namespace,
            'tipo': tipo,
            'lenguaje': lenguaje
        }
    except ValueError as e:
        return {
            'namespace': "error",
            'tipo': "error tipo",
            'lenguaje': "no_languje"
        }

