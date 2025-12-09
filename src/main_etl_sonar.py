#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ETL Principal para SonarQube

Este script realiza el proceso completo de extracción, transformación y carga
de datos desde SonarQube, incluyendo proyectos, métricas e históricos.

Uso:
    python src/main_etl_sonar.py
"""

import os
import time
from datetime import datetime

import configSonar
import api.SonarAPIHandler as sonarAPIHandler
from etl.sonar.extract import (
    extract_proyectos,
    extract_historico_columnas,
    extract_historico_columnas_from,
    extract_analisis
)
from etl.sonar.transform import eliminar_namespaces
from utils.utils import load_to_csv
from utils.lastdate import leer_last_date, nombre_fichero, save_current_date


class Colors:
    """Colores para salida en terminal"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(text):
    """Imprime el paso actual del proceso"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}{text}{Colors.END}")


def format_duration(seconds):
    """Formatea la duración en segundos a un formato legible"""
    if seconds < 60:
        return f"{seconds:.2f} segundos"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutos ({seconds:.2f} segundos)"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} horas ({seconds:.2f} segundos)"


def setup_directories():
    """Crea los directorios necesarios si no existen"""
    print_info("Verificando estructura de directorios...")

    directories = [
        configSonar.DIR_SONAR_LOGS,
        configSonar.DIR_SONAR_XLSX
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_info(f"  - {directory}: OK")


def extract_projects(sonar_handler):
    """
    Extrae todos los proyectos de SonarQube

    Args:
        sonar_handler: Handler de la API de SonarQube

    Returns:
        DataFrame con los proyectos extraídos y ordenados
    """
    print_step("PASO 1: Extracción de Proyectos")
    start_time = time.time()

    # Extraer proyectos
    df_project = extract_proyectos(sonar_handler)
    df_project = df_project.sort_values('namespace')

    # Guardar resultado
    output_file = os.path.join(configSonar.DIR_SONAR_XLSX, "sonar_salida_projects_etl_tc.csv")
    load_to_csv(output_file, df_project)

    duration = time.time() - start_time
    print_success(f"Proyectos extraídos: {len(df_project)}")
    print_success(f"Archivo generado: {output_file}")
    print_info(f"Duración: {format_duration(duration)}\n")

    return df_project


def clean_projects(df_project):
    """
    Limpia los proyectos eliminando namespaces excluidos

    Args:
        df_project: DataFrame con los proyectos

    Returns:
        DataFrame limpio
    """
    print_step("PASO 2: Limpieza de Datos")
    start_time = time.time()

    initial_count = len(df_project)
    df_clean, filas_eliminadas = eliminar_namespaces(
        df_project,
        configSonar.APLICACIONES_EXCLUIDAS
    )

    duration = time.time() - start_time
    print_success(f"Filas eliminadas: {filas_eliminadas} de {initial_count}")
    print_success(f"Proyectos válidos: {len(df_clean)}")
    print_info(f"Aplicaciones excluidas: {', '.join(configSonar.APLICACIONES_EXCLUIDAS)}")
    print_info(f"Duración: {format_duration(duration)}\n")

    return df_clean


def extract_history(df_project, sonar_handler):
    """
    Extrae el histórico de métricas de SonarQube

    Args:
        df_project: DataFrame con los proyectos
        sonar_handler: Handler de la API de SonarQube
    """
    print_step("PASO 3: Extracción de Histórico y Métricas")
    start_time = time.time()

    # Leer última fecha de extracción
    last_date_file = os.path.join(configSonar.DIR_SONAR, 'last_date.txt')
    last_date = leer_last_date(last_date_file)

    # Determinar tipo de carga (inicial o incremental)
    if last_date == "":
        print_info("Tipo de carga: INICIAL (primera vez)")
        df_historico, df_measures = extract_historico_columnas(df_project, sonar_handler)
    else:
        print_info(f"Tipo de carga: INCREMENTAL (última extracción: {last_date})")
        d = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
        from_date = d.strftime("%Y-%m-%dT%H:%M:%S+0200")
        print_info(f"Extrayendo datos desde: {from_date}")
        df_historico, df_measures = extract_historico_columnas_from(
            df_project,
            from_date,
            sonar_handler
        )

    # Guardar histórico
    historico_file = os.path.join(
        configSonar.DIR_SONAR_XLSX,
        nombre_fichero("historico", last_date)
    )
    load_to_csv(historico_file, df_historico)

    # Guardar métricas
    measures_file = os.path.join(
        configSonar.DIR_SONAR_XLSX,
        "sonar_salida_measure_etl_tc.csv"
    )
    load_to_csv(measures_file, df_measures)

    # Actualizar fecha de última extracción
    save_current_date(last_date_file)

    duration = time.time() - start_time
    print_success(f"Registros históricos: {len(df_historico)}")
    print_success(f"Métricas extraídas: {len(df_measures)}")
    print_success(f"Archivo histórico: {historico_file}")
    print_success(f"Archivo métricas: {measures_file}")
    print_info(f"Duración: {format_duration(duration)}\n")


def extract_analysis(df_project, sonar_handler):
    """
    Extrae los análisis realizados por SonarQube (opcional)

    Args:
        df_project: DataFrame con los proyectos
        sonar_handler: Handler de la API de SonarQube
    """
    print_step("PASO 4: Extracción de Análisis (Opcional)")
    start_time = time.time()

    df_analisis = extract_analisis(df_project, sonar_handler)

    # Guardar análisis
    analysis_file = os.path.join(
        configSonar.DIR_SONAR_XLSX,
        "sonar_salida_project_analisis_etl_tc.csv"
    )
    load_to_csv(analysis_file, df_analisis)

    duration = time.time() - start_time
    print_success(f"Análisis extraídos: {len(df_analisis)}")
    print_success(f"Archivo generado: {analysis_file}")
    print_info(f"Duración: {format_duration(duration)}\n")


def print_summary(total_duration):
    """
    Imprime el resumen final del proceso

    Args:
        total_duration: Duración total del proceso en segundos
    """
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}PROCESO ETL SONARQUBE COMPLETADO{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"\n{Colors.CYAN}Duración total: {format_duration(total_duration)}{Colors.END}")
    print(f"{Colors.CYAN}Archivos generados en: {configSonar.DIR_SONAR_XLSX}{Colors.END}\n")


def main():
    """
    Función principal del ETL de SonarQube

    Proceso:
    1. Extracción de proyectos
    2. Limpieza de datos (eliminar namespaces excluidos)
    3. Extracción de histórico y métricas
    4. Extracción de análisis (solo si ONLY_DASHBOARD = True)
    """
    start_time_total = time.time()

    print(f"\n{Colors.BOLD}ETL SonarQube - Inicio{Colors.END}")
    print(f"{Colors.CYAN}Configuración:{Colors.END}")
    print(f"{Colors.CYAN}  - Host: {os.getenv('SONAR_DEFAULT_HOST', 'No configurado')}{Colors.END}")
    print(f"{Colors.CYAN}  - Directorio salida: {configSonar.DIR_SONAR_XLSX}{Colors.END}")
    print(f"{Colors.CYAN}  - Dashboard mode: {configSonar.ONLY_DASHBOARD}{Colors.END}\n")

    try:
        # Setup
        setup_directories()
        sonar_handler = sonarAPIHandler.SonarAPIHandler()

        # Paso 1: Extracción de proyectos
        df_project = extract_projects(sonar_handler)

        # Paso 2: Limpieza de datos
        df_project_clean = clean_projects(df_project)

        # Paso 3: Extracción de histórico y métricas
        extract_history(df_project_clean, sonar_handler)

        # Paso 4: Extracción de análisis (opcional)
        if configSonar.ONLY_DASHBOARD:
            extract_analysis(df_project_clean, sonar_handler)
        else:
            print_info("PASO 4: Extracción de Análisis - OMITIDO (ONLY_DASHBOARD = False)\n")

        # Resumen final
        total_duration = time.time() - start_time_total
        print_summary(total_duration)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Proceso interrumpido por el usuario{Colors.END}\n")
        return 1
    except Exception as e:
        print(f"\n\n{Colors.BOLD}ERROR: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
