import pandas as pd

'''
    Funcion que elimina las filas del DataFrame anteriores a 2023
'''

def transformar_created_at(df):
    df['commit_created_at'] = pd.to_datetime(df['commit_created_at'], 
                                             format='%Y-%m-%d %H:%M:%S')
    # filtered_df = df.loc[(df['commit_created_at'] >= '2023-01-01') & (df['commit_created_at'] < '2023-09-15')]
    filtered_df = df.loc[(df['commit_created_at'] >= '2023-01-01')]
    return filtered_df

'''
    Funcion que elimina las filas con los "namespaces" indicados
'''
def eliminar_namespaces(df):

    df = df.drop(df[df['namespace'] == 'Arquitectura y Estrategia'].index)
    df = df.drop(df[df['namespace'] == 'viveorangeosp'].index)
    
    return df
    

def eliminar_duplicados(df_tags, df_commits):
    valores = []
    for i in range(len(df_commits)):
        if df_commits.iloc[i]['commit_id'] in df_tags.commit_id.values:
            # print("Valor descartado: %s" % df_commits.iloc[i]['commit_id'])
            valores.append(df_commits.iloc[i]['commit_id'])
            
    for valor in valores:
        df_commits.drop(df_commits[(df_commits['commit_id'] == valor) ].index, inplace=True)
        
    return df_commits

        


    