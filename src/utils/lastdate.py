#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilidades para manejo de fechas de extracción incremental

Este módulo proporciona funciones para gestionar la fecha de última extracción,
permitiendo realizar cargas incrementales en el ETL de SonarQube.

El sistema guarda la fecha de la última extracción exitosa en un archivo de texto,
y la utiliza en ejecuciones posteriores para extraer solo datos nuevos.

Funciones principales:
    - leer_last_date: Lee la fecha de última extracción
    - save_current_date: Guarda la fecha actual
    - nombre_fichero: Genera nombres de archivo con timestamp
"""

import os
from datetime import datetime
from typing import Optional


def leer_last_date(file: str) -> str:
    """
    Lee la fecha de última extracción desde un archivo

    Args:
        file: Ruta del archivo que contiene la fecha

    Returns:
        Fecha en formato "YYYY-MM-DD HH:MM:SS" o cadena vacía si el archivo
        no existe o está vacío

    Example:
        >>> fecha = leer_last_date('last_date.txt')
        >>> print(fecha)
        '2024-01-15 10:30:45'

    Note:
        Si el archivo no existe, retorna una cadena vacía, lo que indica
        que es la primera extracción (carga completa).
    """
    try:
        with open(file, mode='r') as f:
            fecha = f.readline().strip()
        return fecha
    except FileNotFoundError:
        # Primera ejecución - no existe archivo de fecha
        return ""
    except Exception as e:
        # Error inesperado al leer el archivo
        print(f"Advertencia: Error al leer {file}: {e}. Usando fecha vacía.")
        return ""


def save_current_date(file: str) -> None:
    """
    Guarda la fecha y hora actual en un archivo

    La fecha se guarda en formato "YYYY-MM-DD HH:MM:SS" para ser utilizada
    en la próxima ejecución como punto de partida para carga incremental.

    Args:
        file: Ruta del archivo donde guardar la fecha

    Example:
        >>> save_current_date('last_date.txt')
        # El archivo contendrá algo como: "2024-01-15 10:30:45"

    Note:
        Esta función debe llamarse DESPUÉS de que la extracción se complete
        exitosamente para evitar perder datos en caso de error.
    """
    # Crear directorio si no existe
    directory = os.path.dirname(file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(file, mode='w') as f:
        now = datetime.now()
        f.write(now.strftime("%Y-%m-%d %H:%M:%S"))


def nombre_fichero(tipo: str, fecha: str) -> str:
    """
    Genera un nombre de archivo con timestamp opcional

    Args:
        tipo: Tipo de archivo (ej: "historico", "measure", "analisis")
        fecha: Fecha en formato "YYYY-MM-DD HH:MM:SS" o cadena vacía

    Returns:
        Nombre de archivo con el formato:
        - Si fecha está vacía: "sonar_salida_{tipo}_etl_tc.csv"
        - Si hay fecha: "sonar_salida_{tipo}_etl_{timestamp}_tc.csv"

    Example:
        >>> nombre_fichero("historico", "")
        'sonar_salida_historico_etl_tc.csv'

        >>> nombre_fichero("historico", "2024-01-15 10:30:45")
        'sonar_salida_historico_etl_2024_01_15_10_30_45_tc.csv'

    Note:
        Los caracteres especiales (espacios, dos puntos, guiones) se reemplazan
        por guiones bajos para compatibilidad con sistemas de archivos.
    """
    if fecha == "":
        # Primera extracción o extracción completa
        return f"sonar_salida_{tipo}_etl_tc.csv"

    # Convertir fecha a formato seguro para nombres de archivo
    # "2024-01-15 10:30:45" -> "2024_01_15_10_30_45"
    timestamp = fecha.replace(" ", "_").replace(":", "_").replace("-", "_")

    return f"sonar_salida_{tipo}_etl_{timestamp}_tc.csv"
