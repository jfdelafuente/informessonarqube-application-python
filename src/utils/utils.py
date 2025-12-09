#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilidades para operaciones con archivos CSV

Este módulo proporciona funciones para leer y escribir DataFrames en formato CSV,
utilizadas en los procesos ETL de SonarQube y GitLab.

Funciones principales:
    - load_to_csv: Guarda un DataFrame como archivo CSV
    - extract_from_csv: Lee un archivo CSV y retorna un DataFrame
"""

import pandas as pd


def load_to_csv(targetfile: str, data_to_load: pd.DataFrame) -> None:
    """
    Guarda un DataFrame en un archivo CSV

    El archivo se guarda con las siguientes características:
    - Separador: punto y coma (;)
    - Encoding: UTF-8
    - Sin índice de filas

    Args:
        targetfile: Ruta del archivo de destino
        data_to_load: DataFrame a guardar

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        >>> load_to_csv('output/data.csv', df)

    Note:
        Si el archivo ya existe, será sobrescrito sin advertencia.
    """
    data_to_load.to_csv(targetfile, sep=';', encoding='utf-8', index=False)


def extract_from_csv(file_to_process: str) -> pd.DataFrame:
    """
    Lee un archivo CSV y retorna un DataFrame

    Args:
        file_to_process: Ruta del archivo CSV a leer

    Returns:
        DataFrame con los datos del archivo CSV

    Raises:
        FileNotFoundError: Si el archivo no existe
        pd.errors.ParserError: Si el archivo no puede ser parseado

    Example:
        >>> df = extract_from_csv('input/data.csv')
        >>> print(df.head())

    Note:
        El archivo debe usar punto y coma (;) como separador.
    """
    dataframe = pd.read_csv(file_to_process, sep=';')
    return dataframe
