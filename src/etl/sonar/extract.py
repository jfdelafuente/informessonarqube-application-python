#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Extracción ETL para SonarQube

Este módulo contiene las funciones de extracción de datos desde la API de SonarQube,
incluyendo proyectos, métricas históricas y análisis de versiones.

Funciones principales:
    - extract_proyectos: Extrae todos los proyectos de SonarQube
    - extract_historico_columnas: Extrae histórico completo de métricas
    - extract_historico_columnas_from: Extrae histórico incremental desde una fecha
    - extract_analisis: Extrae análisis de versiones de proyectos
"""

import json
import logging
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime

import requests
import pandas as pd

from etl.sonar.transform import extraer_componentes


# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================

# Definición de columnas del DataFrame de salida
COLUMNS = [
    'project', 'aplicacion', 'name', 'tipo', 'lenguaje', 'date',
    'complexity', 'coverage', 'ncloc', 'duplicated_lines_density',
    'code_smells', 'bugs', 'vulnerabilities', 'sqale_index',
    'sqale_rating', 'sqale_debt_ratio', 'reliability_rating',
    'security_rating', 'alert_status', 'quality_gate'
]

# Configuración de paginación
DEFAULT_PAGE_SIZE = 100
INITIAL_TOTAL = 5000


# =============================================================================
# CLASES AUXILIARES
# =============================================================================

class Colors:
    """Colores ANSI para salida en terminal"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


# =============================================================================
# FUNCIONES DE UTILIDAD PARA OUTPUT
# =============================================================================

def _print_progress(current: int, total: int, message: str = ""):
    """
    Imprime el progreso actual con barra visual

    Args:
        current: Número actual
        total: Total de elementos
        message: Mensaje adicional
    """
    if total > 0:
        percentage = (current / total) * 100
        bar_length = 30
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)

        msg = f"{Colors.CYAN}[{bar}] {current}/{total} ({percentage:.1f}%){Colors.END}"
        if message:
            msg += f" {Colors.YELLOW}{message}{Colors.END}"
        print(f"\r{msg}", end='', flush=True)


def _print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def _print_info(text: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def _print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def _print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def _print_step(step_number: int, total_steps: int, title: str):
    """Imprime encabezado de paso"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}[{step_number}/{total_steps}] {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")


# =============================================================================
# FUNCIONES AUXILIARES INTERNAS
# =============================================================================

def _get_metric_value(history_entry: Dict[str, Any], metric_name: str) -> str:
    """
    Extrae el valor de una métrica del histórico de forma segura

    Args:
        history_entry: Entrada del histórico de métricas
        metric_name: Nombre de la métrica a extraer

    Returns:
        Valor de la métrica como string, "0" si no existe
    """
    if len(history_entry) > 1:
        return str(history_entry.get("value", "0"))
    return "0"


def _format_datetime(date_str: str) -> str:
    """
    Formatea una fecha ISO a formato estándar

    Args:
        date_str: Fecha en formato ISO

    Returns:
        Fecha formateada como "YYYY-MM-DD HH:MM:SS"
    """
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError) as e:
        logging.warning(f"Error al formatear fecha '{date_str}': {e}")
        return date_str


def _create_metrics_dict(row: pd.Series, base_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Crea el diccionario base de métricas con información del proyecto

    Args:
        row: Fila del DataFrame de proyectos
        base_data: Datos base adicionales (por ejemplo, fecha)

    Returns:
        Diccionario con información base del proyecto
    """
    metrics = {
        "project": row["project"],
        "aplicacion": row["namespace"],
        "name": row["name"],
        "tipo": row["tipo"],
        "lenguaje": row["lenguaje"],
        "quality_gate": row["quality_gate"]
    }
    metrics.update(base_data)
    return metrics


# =============================================================================
# FUNCIONES DE EXTRACCIÓN PRINCIPALES
# =============================================================================

def extract_proyectos(sonar_handle) -> pd.DataFrame:
    """
    Extrae todos los proyectos de SonarQube con paginación

    Recorre todas las páginas de proyectos disponibles en SonarQube,
    extrayendo información básica y el Quality Gate de cada uno.

    Args:
        sonar_handle: Instancia de SonarAPIHandler

    Returns:
        DataFrame con columnas: project, namespace, name, tipo, lenguaje, quality_gate

    Example:
        df_projects = extract_proyectos(sonar_handler)
        print(f"Proyectos extraídos: {len(df_projects)}")
    """
    _print_info("Iniciando extracción de proyectos de SonarQube...")

    index = 1
    total = INITIAL_TOTAL
    project_ids = []
    contador = 0

    def get_project_data(project: Dict[str, str]) -> Tuple[str, str, str, str, str, str]:
        """Extrae datos completos de un proyecto individual"""
        project_key = project["project"]
        result = extraer_componentes(project_key)

        # Obtener Quality Gate
        quality_gate_response = sonar_handle.get_qualitygate_by_project(project_key)
        quality_json = json.loads(quality_gate_response.text)

        return (
            project_key,
            result['namespace'],
            project["name"],
            result['tipo'],
            result['lenguaje'],
            quality_json["qualityGate"]["name"]
        )

    # Paginación
    while index * DEFAULT_PAGE_SIZE < total + DEFAULT_PAGE_SIZE:
        project_response = sonar_handle.get_component(qualifiers="TRK", index=index)

        try:
            project_response.raise_for_status()
            datos_json = json.loads(project_response.text)

            # Actualizar total y avanzar índice
            total = datos_json["paging"]["total"]
            index += 1

            # Procesar proyectos de la página actual
            for project in datos_json["components"]:
                contador += 1

                # Mostrar progreso
                project_name = project.get('name', 'unknown')[:40]
                _print_progress(contador, total, f"Extrayendo: {project_name}")

                logging.debug(f"Procesando proyecto {contador}/{total}: {project.get('key', 'unknown')}")
                project_ids.append(get_project_data(project))

        except requests.exceptions.HTTPError as err:
            print()  # Nueva línea después de la barra de progreso
            _print_error(f"Error HTTP en extracción de proyectos: {err}")
            logging.error(f"Error HTTP en extracción de proyectos: {err}")
            break
        except json.JSONDecodeError as err:
            print()
            _print_error(f"Error al decodificar JSON: {err}")
            logging.error(f"Error al decodificar JSON: {err}")
            break
        except Exception as err:
            logging.error(f"Error inesperado procesando proyecto: {err}")
            continue

    print()  # Nueva línea después de la barra de progreso
    _print_success(f"Extracción completada: {contador} proyectos procesados")
    logging.info(f"Extracción de proyectos completada: {contador} proyectos procesados")

    df_project = pd.DataFrame(
        project_ids,
        columns=["project", "namespace", "name", "tipo", "lenguaje", "quality_gate"]
    )

    return df_project


def extract_historico(df_projects: pd.DataFrame, sonar_handle) -> pd.DataFrame:
    """
    Extrae el histórico de métricas en formato largo (una fila por métrica/fecha)

    NOTA: Esta función extrae datos en formato largo. Para formato columnar,
    usar extract_historico_columnas().

    Args:
        df_projects: DataFrame con proyectos a procesar
        sonar_handle: Instancia de SonarAPIHandler

    Returns:
        DataFrame con columnas: aplicacion, proyecto, lenguaje, metric, date, value
    """
    total_projects = len(df_projects)
    _print_info(f"Iniciando extracción de histórico para {total_projects} proyectos...")

    project_ids = []
    logging.info(f"Iniciando extracción de histórico para {total_projects} proyectos")

    def get_value(history: Dict[str, Any]) -> Any:
        """Extrae el valor de forma segura"""
        return history.get("value", 0)

    for i, row in df_projects.iterrows():
        project_key = row["project"]
        project_name = row["name"][:40]

        _print_progress(i + 1, total_projects, f"Procesando: {project_name}")
        logging.debug(f"Extrayendo histórico de {project_key}")

        try:
            measures = sonar_handle.get_measures_history(project_key, index=1)
            datos_json = json.loads(measures.text)

            result = extraer_componentes(project_key)

            for component in datos_json.get("measures", []):
                metric_name = component.get("metric")
                for history in component.get("history", []):
                    value = get_value(history)
                    date_formatted = _format_datetime(history["date"])

                    project_ids.append((
                        result['namespace'],
                        row["name"],
                        result['lenguaje'],
                        metric_name,
                        date_formatted,
                        value
                    ))

        except Exception as err:
            logging.error(f"Error extrayendo histórico de {project_key}: {err}")
            continue

    print()
    _print_success(f"Extracción de histórico completada: {i + 1} proyectos procesados")
    logging.info(f"Extracción de histórico completada: {i + 1} proyectos procesados")

    df_project = pd.DataFrame(
        project_ids,
        columns=["aplicacion", "proyecto", "lenguaje", "metric", "date", "value"]
    )

    return df_project


def extract_historico_columnas(
    df_projects: pd.DataFrame,
    sonar_handle
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrae el histórico completo de métricas en formato columnar

    Cada fila representa una fecha, con todas las métricas como columnas.
    Retorna tanto el histórico completo como las métricas más recientes.

    Args:
        df_projects: DataFrame con proyectos a procesar
        sonar_handle: Instancia de SonarAPIHandler

    Returns:
        Tupla (df_historico, df_metrics_latest):
            - df_historico: Histórico completo con todas las fechas
            - df_metrics_latest: Solo las métricas más recientes de cada proyecto

    Example:
        df_hist, df_latest = extract_historico_columnas(df_projects, sonar)
        print(f"Total registros históricos: {len(df_hist)}")
        print(f"Métricas actuales: {len(df_latest)}")
    """
    return _extract_historico_columnas_internal(df_projects, sonar_handle, date_from=None)


def extract_historico_columnas_from(
    df_projects: pd.DataFrame,
    date_from: str,
    sonar_handle
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrae el histórico de métricas desde una fecha específica (carga incremental)

    Similar a extract_historico_columnas pero solo extrae datos desde date_from.
    Útil para cargas incrementales.

    Args:
        df_projects: DataFrame con proyectos a procesar
        date_from: Fecha desde la que extraer (formato: YYYY-MM-DDTHH:MM:SS+0200)
        sonar_handle: Instancia de SonarAPIHandler

    Returns:
        Tupla (df_historico, df_metrics_latest)

    Example:
        df_hist, df_latest = extract_historico_columnas_from(
            df_projects,
            "2024-01-01T00:00:00+0200",
            sonar
        )
    """
    return _extract_historico_columnas_internal(df_projects, sonar_handle, date_from)


def _extract_historico_columnas_internal(
    df_projects: pd.DataFrame,
    sonar_handle,
    date_from: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función interna que realiza la extracción de histórico en formato columnar

    Args:
        df_projects: DataFrame con proyectos
        sonar_handle: Handler de SonarQube
        date_from: Fecha desde la que extraer (None = todo el histórico)

    Returns:
        Tupla (df_historico_completo, df_metricas_actuales)
    """
    project_ids = []
    metrics_ids = []
    no_tratado = 0
    tratados = df_projects.shape[0]

    extraction_type = "incremental" if date_from else "completa"

    _print_info(f"Iniciando extracción {extraction_type} de histórico para {tratados} proyectos...")
    if date_from:
        _print_info(f"Extrayendo desde: {date_from}")

    logging.info(f"Iniciando extracción {extraction_type} de histórico para {tratados} proyectos")

    for t, row in df_projects.iterrows():
        project_key = row["project"]
        project_name = row["name"][:40]
        index = 1
        total = 500
        acumulado = 0

        _print_progress(
            t + 1,
            tratados,
            f"Proyecto: {project_name} | Métricas: {acumulado}"
        )

        logging.debug(f"Procesando proyecto {t + 1}/{tratados}: {project_key}")

        while index * DEFAULT_PAGE_SIZE < total + DEFAULT_PAGE_SIZE:
            try:
                # Elegir método según si hay fecha o no
                if date_from:
                    measures = sonar_handle.get_measures_history_from(project_key, index, date_from)
                else:
                    measures = sonar_handle.get_measures_history(project_key, index)

                if measures.status_code != 200:
                    logging.warning(
                        f"Error HTTP {measures.status_code} para {project_key}. "
                        f"Saltando {DEFAULT_PAGE_SIZE} registros."
                    )
                    index += 10
                    no_tratado += 1
                    break

                datos_json = json.loads(measures.text)
                total = datos_json["paging"]["total"]

                if total == 0:
                    logging.debug(f"El proyecto {project_key} no tiene métricas históricas")
                    no_tratado += 1
                    break

                # Verificar que existan métricas
                if not datos_json.get("measures") or len(datos_json["measures"]) == 0:
                    logging.debug(f"No hay métricas en la respuesta para {project_key}")
                    break

                total_history = len(datos_json["measures"][0]["history"])
                acumulado += total_history

                # Actualizar barra de progreso con contador de métricas
                _print_progress(
                    t + 1,
                    tratados,
                    f"Proyecto: {project_name} | Métricas: {acumulado}/{total}"
                )

                # Procesar cada punto en el histórico
                for i in range(total_history):
                    dict_metrics = _create_metrics_dict(row, {})

                    total_measures = len(datos_json["measures"])

                    # Iterar sobre todas las métricas
                    for j in range(total_measures):
                        measure = datos_json["measures"][j]
                        history_entry = measure["history"][i]

                        # Establecer fecha
                        dict_metrics["date"] = _format_datetime(history_entry["date"])

                        # Establecer valor de la métrica
                        metric_name = measure["metric"]
                        dict_metrics[metric_name] = _get_metric_value(history_entry, metric_name)

                    # Determinar si es el último registro (métrica más reciente)
                    ultimo = len(datos_json["measures"][j]["history"]) - 1

                    if acumulado == total and ultimo == i:
                        # Esta es la métrica más reciente del proyecto
                        metrics_ids.append(dict_metrics)

                    project_ids.append(dict_metrics)

            except json.JSONDecodeError as err:
                logging.error(f"Error decodificando JSON para {project_key}: {err}")
                no_tratado += 1
                break
            except Exception as err:
                logging.error(f"Error inesperado procesando {project_key}: {err}")
                no_tratado += 1
                break

            index += 1

    print()  # Nueva línea después de la barra de progreso

    tratados_exitosos = tratados - no_tratado
    _print_success(f"Proyectos tratados exitosamente: {tratados_exitosos}")
    if no_tratado > 0:
        _print_warning(f"Proyectos no tratados: {no_tratado}")

    _print_info(f"Total registros históricos: {len(project_ids)}")
    _print_info(f"Métricas más recientes: {len(metrics_ids)}")

    logging.info(
        f"Extracción de histórico completada: "
        f"{tratados_exitosos} proyectos tratados, {no_tratado} no tratados"
    )

    df_project = pd.DataFrame(project_ids, columns=COLUMNS)
    df_metrics = pd.DataFrame(metrics_ids, columns=COLUMNS)

    return df_project, df_metrics


def extract_measure(df_projects: pd.DataFrame, sonar_handle) -> pd.DataFrame:
    """
    Extrae solo las métricas más recientes de cada proyecto

    NOTA: Esta función está marcada como obsoleta. Se recomienda usar
    extract_historico_columnas() que retorna tanto el histórico como las métricas actuales.

    Args:
        df_projects: DataFrame con proyectos
        sonar_handle: Handler de SonarQube

    Returns:
        DataFrame con las métricas más recientes
    """
    _print_warning(
        "extract_measure() está obsoleta. "
        "Usar extract_historico_columnas() que retorna histórico y métricas actuales."
    )

    logging.warning(
        "extract_measure() está obsoleta. "
        "Usar extract_historico_columnas() que retorna histórico y métricas actuales."
    )

    project_ids = []
    no_tratado = 0
    tratados = df_projects.shape[0]

    _print_info(f"Iniciando extracción de métricas actuales para {tratados} proyectos...")
    logging.info(f"Iniciando extracción de métricas actuales para {tratados} proyectos")

    for idx, row in df_projects.iterrows():
        project_key = row["project"]
        project_name = row["name"][:40]
        index = 1
        total = 500
        acumulado = 0

        _print_progress(idx + 1, tratados, f"Procesando: {project_name}")
        logging.debug(f"Procesando métricas de {project_key}")

        while index * DEFAULT_PAGE_SIZE < total + DEFAULT_PAGE_SIZE:
            try:
                measures = sonar_handle.get_measures_history(project_key, index)

                if measures.status_code != 200:
                    logging.warning(f"Error HTTP {measures.status_code} para {project_key}")
                    index += 10
                    no_tratado += 1
                    break

                datos_json = json.loads(measures.text)
                total = datos_json["paging"]["total"]
                total_history = len(datos_json["measures"][0]["history"])
                acumulado += total_history

                logging.debug(f"{project_key}: {total_history}/{total} histórico, acumulado: {acumulado}")

                # Solo procesar cuando tengamos todo el histórico
                if total == acumulado and total > 0:
                    dict_metrics = _create_metrics_dict(row, {})

                    total_measures = len(datos_json["measures"])

                    for i in range(total_measures):
                        measure = datos_json["measures"][i]
                        ultimo = len(measure["history"]) - 1

                        # Tomar el último valor del histórico
                        last_entry = measure["history"][ultimo]
                        dict_metrics["date"] = _format_datetime(last_entry["date"])

                        try:
                            dict_metrics[measure["metric"]] = last_entry.get("value", "")
                        except Exception:
                            dict_metrics[measure["metric"]] = ""

                    logging.debug(f"Métricas extraídas para {project_key}")
                    project_ids.append(dict_metrics)

                elif total <= 0:
                    logging.debug(f"{project_key} no tiene métricas")
                    no_tratado += 1

                index += 1

            except Exception as err:
                logging.error(f"Error procesando {project_key}: {err}")
                no_tratado += 1
                break

    print()
    _print_success(f"Métricas extraídas: {tratados - no_tratado}")
    if no_tratado > 0:
        _print_warning(f"Proyectos no tratados: {no_tratado}")

    logging.info(f"Extracción de métricas: {tratados - no_tratado} tratados, {no_tratado} no tratados")

    df_project = pd.DataFrame(project_ids, columns=COLUMNS)
    return df_project


def extract_analisis(df_projects: pd.DataFrame, sonar_handle) -> pd.DataFrame:
    """
    Extrae los análisis de versiones de los proyectos

    Busca eventos de tipo VERSION en los análisis de SonarQube para
    obtener el historial de versiones de cada proyecto.

    Args:
        df_projects: DataFrame con proyectos a procesar
        sonar_handle: Instancia de SonarAPIHandler

    Returns:
        DataFrame con columnas: aplicacion, name, lenguaje, date, version

    Example:
        df_analysis = extract_analisis(df_projects, sonar_handler)
        print(f"Versiones encontradas: {len(df_analysis)}")
    """
    project_ids = []
    tratados = 0
    evaluados = 0
    total_proyectos = df_projects.shape[0]

    _print_info(f"Iniciando extracción de análisis para {total_proyectos} proyectos...")
    logging.info(f"Iniciando extracción de análisis para {total_proyectos} proyectos")

    for i, row in df_projects.iterrows():
        project_key = row["project"]
        project_name = row["name"][:40]
        evaluados += 1

        _print_progress(evaluados, total_proyectos, f"Analizando: {project_name} | Versiones: {tratados}")
        logging.debug(f"Procesando análisis {evaluados}/{total_proyectos}: {project_key}")

        try:
            measures = sonar_handle.get_project_analyses(project_key)

            if measures.status_code != 200:
                logging.warning(f"Error HTTP {measures.status_code} para {project_key}")
                continue

            datos_json = json.loads(measures.text)
            result = extraer_componentes(project_key)

            # Buscar eventos de tipo VERSION en los análisis
            for analisis in datos_json.get("analyses", []):
                for eventos in analisis.get("events", []):
                    if eventos.get("category") == "VERSION":
                        tratados += 1
                        date_formatted = _format_datetime(analisis["date"])

                        project_ids.append((
                            result['namespace'],
                            row["name"],
                            result['lenguaje'],
                            date_formatted,
                            eventos["name"]
                        ))

                        # Actualizar progreso con contador de versiones
                        _print_progress(
                            evaluados,
                            total_proyectos,
                            f"Analizando: {project_name} | Versiones: {tratados}"
                        )

        except json.JSONDecodeError as err:
            logging.error(f"Error decodificando JSON para {project_key}: {err}")
        except Exception as err:
            logging.error(f"Error procesando análisis de {project_key}: {err}")

    print()
    _print_success(f"Proyectos evaluados: {evaluados}")
    _print_success(f"Versiones encontradas: {tratados}")

    logging.info(f"Extracción de análisis completada: {evaluados} evaluados, {tratados} versiones encontradas")

    df_project = pd.DataFrame(
        project_ids,
        columns=["aplicacion", "name", "lenguaje", "date", "version"]
    )

    return df_project
