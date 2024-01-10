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


def transformar_java(df):
    num_filas = df.shape[0]
    df_extract = df[df['lenguaje'] == 'java' ]
    print(f'Se han eliminado {(num_filas - df_extract.shape[0])} filas por no ser java.')
    return df_extract

def transformar_date(df):
    num_filas = df.shape[0]
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    # filtered_df = df.loc[(df['commit_created_at'] >= '2023-01-01') & (df['commit_created_at'] < '2023-09-15')]
    filtered_df = df.loc[(df['date'] >= '2023-01-01')]
    print(f'Se han eliminado {(num_filas - filtered_df.shape[0])} filas anteriores a 2023.')
    return filtered_df

def eliminar_namespaces(df):
    num_filas = df.shape[0]
    df = df.drop(df[df['namespace'] == 'tdccicdosp'].index)
    print(f'Se han eliminado {(num_filas - df.shape[0])} filas por namespace invalido.')
    return df

def eliminar_error_namespaces(df):
    num_filas = df.shape[0]
    df = df.drop(df[df['namespace'] == 'error'].index)
    print(f'Se han eliminado {(num_filas - df.shape[0])} filas por error namespace.')
    return df

