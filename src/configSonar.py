#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuración para ETL de SonarQube

Este archivo contiene las variables de configuración para el proceso ETL de SonarQube.
Modifica estas variables según las necesidades de tu proyecto.
"""

# =============================================================================
# FILTRADO DE PROYECTOS
# =============================================================================

# Lista de namespaces/aplicaciones a excluir del procesamiento
# Los proyectos que contengan estos prefijos en su namespace serán filtrados
APLICACIONES_EXCLUIDAS = [
    'tdccicdosp',
    'viveorangeosp',
    'altamenaosp',
    'error'
]

# =============================================================================
# MODO DE EXTRACCIÓN
# =============================================================================

# ONLY_DASHBOARD: Controla si se extraen análisis de versiones de proyectos
#
# False (Por defecto): Modo rápido - Extrae solo datos esenciales
#   - Proyectos y sus propiedades
#   - Métricas de calidad (bugs, vulnerabilities, code smells, etc.)
#   - Histórico de métricas
#   - NO extrae análisis de versiones
#   - Proceso más rápido, recomendado para reportes de calidad de código
#
# True: Modo completo - Extrae todos los datos incluyendo análisis
#   - Todo lo anterior +
#   - Análisis de versiones de proyectos
#   - Genera archivo adicional: sonar_salida_project_analisis_etl_tc.csv
#   - Proceso más lento pero con información completa para dashboards
#   - Recomendado cuando necesitas tracking de versiones
#
ONLY_DASHBOARD = False


# =============================================================================
# DIRECTORIOS DE SALIDA
# =============================================================================

# Directorio raíz del proyecto
DIR_SONAR = './'

# Directorio para archivos de log
DIR_SONAR_LOGS = DIR_SONAR + 'logs/'

# Directorio para archivos de salida (CSV, Excel)
DIR_SONAR_XLSX = DIR_SONAR + 'xlsx/SONAR/'

# Directorio para archivos de salida diarios (si se usa extracción programada)
DIR_SONAR_XLSX_DIARIO = DIR_SONAR_XLSX


# =============================================================================
# CONFIGURACIÓN ADICIONAL
# =============================================================================

# Lenguajes de programación a considerar (usado en algunas transformaciones)
languages = ['script', 'typescript', 'php']

# Lista de proyectos específicos (vacío = todos los proyectos)
# Si se especifican proyectos aquí, solo se procesarán estos
proyectos = []
