#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Transformación ETL para SonarQube

Este módulo contiene funciones de transformación y limpieza de datos
extraídos de SonarQube.

Funciones principales:
    - extraer_componentes: Parsea claves de proyectos de SonarQube
    - eliminar_namespaces: Filtra proyectos por namespace
"""

import logging
from typing import Dict, Tuple
from functools import lru_cache
import pandas as pd


@lru_cache(maxsize=1024)
def extraer_componentes(project: str) -> Dict[str, str]:
    """
    Parsea la clave de un proyecto de SonarQube para extraer sus componentes

    Los proyectos de SonarQube tienen claves con formato:
    - Standard: "com.empresa.namespace.tipo.lenguaje:nombre_proyecto"
    - Extendido: "com.empresa.namespace.subtipo.tipo.lenguaje:nombre_proyecto"

    Args:
        project: Clave del proyecto de SonarQube

    Returns:
        Diccionario con claves:
            - namespace: Namespace/aplicación del proyecto
            - tipo: Tipo de proyecto (package, application, etc.)
            - lenguaje: Lenguaje de programación

    Example:
        >>> extraer_componentes("com.orange.webmethods.differential.package:webmethods")
        {'namespace': 'webmethods', 'tipo': 'package', 'lenguaje': 'differential'}

        >>> extraer_componentes("com.orange.peoplesoft.application.java:psclientes")
        {'namespace': 'peoplesoft', 'tipo': 'application', 'lenguaje': 'java'}

    Note:
        - Si el proyecto no puede parsearse, retorna valores de error:
          {'namespace': 'error', 'tipo': 'error tipo', 'lenguaje': 'no_languje'}
        - Esta función está cacheada (LRU cache de 1024 entradas) para evitar
          parsing redundante del mismo proyecto key
    """
    try:
        # Separar la parte de la aplicación del nombre del proyecto
        # Formato: "com.orange.namespace.tipo.lenguaje:nombre"
        aplicacion, extension = project.split(sep=':')

        # Contar puntos para determinar el formato
        num_puntos = _contar_caracter(aplicacion, '.')

        if num_puntos > 4:
            # Formato extendido: com.empresa.namespace.subtipo.tipo.lenguaje
            dominio, empresa, namespace, subtipo, tipo, lenguaje = aplicacion.split(sep='.')
            logging.debug(
                f"Proyecto extendido parseado: {project} -> "
                f"namespace={namespace}, tipo={tipo}, lenguaje={lenguaje}"
            )
        else:
            # Formato estándar: com.empresa.namespace.tipo.lenguaje
            dominio, empresa, namespace, tipo, lenguaje = aplicacion.split(sep='.')
            logging.debug(
                f"Proyecto estándar parseado: {project} -> "
                f"namespace={namespace}, tipo={tipo}, lenguaje={lenguaje}"
            )

        return {
            'namespace': namespace,
            'tipo': tipo,
            'lenguaje': lenguaje
        }

    except ValueError as e:
        # Error al parsear la clave del proyecto
        logging.warning(
            f"No se pudo parsear el proyecto '{project}': {e}. "
            f"Retornando valores de error."
        )
        return {
            'namespace': "error",
            'tipo': "error tipo",
            'lenguaje': "no_languje"
        }


def eliminar_namespaces(
    df: pd.DataFrame,
    namespace_to_exclude: list
) -> Tuple[pd.DataFrame, int]:
    """
    Elimina filas del DataFrame cuyos namespaces estén en la lista de exclusión

    Esta función filtra proyectos no deseados basándose en sus namespaces.
    Útil para excluir aplicaciones de prueba, desarrollo o sistemas internos.

    Args:
        df: DataFrame con columna 'namespace'
        namespace_to_exclude: Lista de namespaces a excluir

    Returns:
        Tupla (df_filtrado, filas_eliminadas):
            - df_filtrado: DataFrame sin los namespaces excluidos
            - filas_eliminadas: Número de filas eliminadas

    Raises:
        ValueError: Si la columna 'namespace' no existe en el DataFrame

    Example:
        >>> df = pd.DataFrame({
        ...     'namespace': ['app1', 'test', 'app2', 'dev'],
        ...     'name': ['Project 1', 'Test', 'Project 2', 'Dev']
        ... })
        >>> df_clean, eliminadas = eliminar_namespaces(df, ['test', 'dev'])
        >>> print(f"Eliminadas: {eliminadas}")
        Eliminadas: 2
        >>> print(df_clean['namespace'].tolist())
        ['app1', 'app2']
    """
    # Validar que existe la columna namespace
    if 'namespace' not in df.columns:
        error_msg = "La columna 'namespace' no existe en el DataFrame."
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Contar filas antes del filtrado
    num_filas_original = df.shape[0]

    # Filtrar: mantener solo las filas cuyo namespace NO esté en la lista de exclusión
    df_filtrado = df[~df['namespace'].isin(namespace_to_exclude)]

    # Calcular filas eliminadas
    filas_eliminadas = num_filas_original - df_filtrado.shape[0]

    # Log del resultado
    if filas_eliminadas > 0:
        logging.info(
            f"Eliminadas {filas_eliminadas} filas de {num_filas_original} "
            f"por namespace inválido. Namespaces excluidos: {namespace_to_exclude}"
        )
    else:
        logging.debug("No se eliminaron filas. Ningún namespace coincide con la lista de exclusión.")

    return df_filtrado, filas_eliminadas


# =============================================================================
# FUNCIONES AUXILIARES PRIVADAS
# =============================================================================

def _contar_caracter(palabra: str, caracter: str) -> int:
    """
    Cuenta el número de veces que un carácter aparece en una palabra

    Args:
        palabra: Texto en el que buscar
        caracter: Carácter a contar (debe ser un solo carácter)

    Returns:
        Número de apariciones del carácter

    Raises:
        ValueError: Si el segundo argumento no es un solo carácter

    Example:
        >>> _contar_caracter("com.orange.app", ".")
        2
    """
    if len(caracter) != 1:
        raise ValueError("El segundo argumento debe ser un solo carácter")

    contador = 0
    for c in palabra:
        if c == caracter:
            contador += 1

    return contador
