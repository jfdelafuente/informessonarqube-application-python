#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cliente HTTP para la API de SonarQube

Este módulo proporciona una interfaz simplificada para interactuar con la API REST
de SonarQube, incluyendo búsqueda de componentes, métricas e históricos.

Uso:
    from api.SonarAPIHandler import SonarAPIHandler

    sonar = SonarAPIHandler()
    response = sonar.get_component(qualifiers="TRK", index=1)
"""

import os
import logging
import requests
from typing import Optional, Dict
from dotenv import load_dotenv


class SonarAPIHandler:
    """
    Manejador de la API REST de SonarQube

    Proporciona métodos para interactuar con los principales endpoints de SonarQube:
    - Búsqueda de componentes y proyectos
    - Extracción de métricas actuales e históricas
    - Análisis de proyectos
    - Quality Gates

    Attributes:
        DEFAULT_PAGE_SIZE (int): Tamaño de página predeterminado para consultas paginadas
        METRICS (str): Lista de métricas de SonarQube a extraer por defecto
    """

    # Configuración
    DEFAULT_BASE_PATH = ''
    DEFAULT_PAGE_SIZE = 200
    DEFAULT_TIMEOUT = 30

    # Endpoints de la API de SonarQube
    COMPONENTS_SEARCH_ENDPOINT = '/api/components/search'
    MEASURES_SEARCH_ENDPOINT = '/api/measures/search'
    MEASURES_SEARCH_HISTORY_ENDPOINT = '/api/measures/search_history'
    MEASURES_COMPONENT_ENDPOINT = '/api/measures/component'
    PROJECT_ANALYSES_ENDPOINT = '/api/project_analyses/search'
    PROJECT_SEARCH_ENDPOINT = '/api/projects/search'
    QUALITYGATE_BYPROJECT_ENDPOINT = '/api/qualitygates/get_by_project'

    # Métricas predeterminadas a extraer
    METRICS = (
        "alert_status,complexity,duplicated_lines_density,code_smells,"
        "sqale_rating,sqale_index,sqale_debt_ratio,bugs,reliability_rating,"
        "vulnerabilities,security_rating,ncloc,coverage,tests"
    )

    def __init__(
        self,
        host: Optional[str] = None,
        base_path: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Inicializa el manejador de la API de SonarQube

        Args:
            host: URL del servidor SonarQube. Si no se proporciona, se lee de .env
            base_path: Ruta base para los endpoints. Por defecto ''
            timeout: Timeout para las peticiones HTTP en segundos. Por defecto 30

        Raises:
            KeyError: Si las variables de entorno SONAR_DEFAULT_HOST o
                     SONAR_ACCESS_TOKEN no están definidas
        """
        load_dotenv()

        self._host = host or os.getenv('SONAR_DEFAULT_HOST')
        self._base_path = base_path or self.DEFAULT_BASE_PATH
        self._timeout = timeout

        if not self._host:
            raise KeyError("SONAR_DEFAULT_HOST no está definido en variables de entorno")

        self.token = os.getenv('SONAR_ACCESS_TOKEN')
        if not self.token:
            raise KeyError("SONAR_ACCESS_TOKEN no está definido en variables de entorno")

        logging.debug(f"SonarAPIHandler inicializado para: {self._host}")

    def _get_url(self, endpoint: str) -> str:
        """
        Construye la URL completa para un endpoint

        Args:
            endpoint: Ruta relativa del endpoint (ej: '/api/components/search')

        Returns:
            URL completa incluyendo host, base_path y endpoint
        """
        return f"{self._host}{self._base_path}{endpoint}"

    def _get_headers(self) -> Dict[str, str]:
        """
        Genera los headers HTTP para las peticiones a SonarQube

        Returns:
            Diccionario con headers incluyendo autenticación Bearer
        """
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _make_call(
        self,
        endpoint: str,
        method: str = "GET",
        **query_args
    ) -> requests.Response:
        """
        Realiza una petición HTTP a la API de SonarQube

        Args:
            endpoint: Endpoint relativo de la API
            method: Método HTTP (GET, POST, etc.). Por defecto GET
            **query_args: Parámetros de query string

        Returns:
            Objeto Response de requests

        Raises:
            requests.exceptions.RequestException: Si hay error en la petición HTTP
        """
        url = self._get_url(endpoint)
        headers = self._get_headers()

        logging.debug(f"API Call: {method} {url}")
        logging.debug(f"Query args: {query_args}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=query_args,
                timeout=self._timeout
            )

            # Log de respuesta para debugging
            if response.status_code != 200:
                logging.warning(
                    f"API returned status {response.status_code}: {response.text[:200]}"
                )

            return response

        except requests.exceptions.Timeout:
            logging.error(f"Timeout al conectar con {url}")
            raise
        except requests.exceptions.ConnectionError:
            logging.error(f"Error de conexión con {url}")
            raise
        except Exception as e:
            logging.error(f"Error inesperado en petición HTTP: {e}")
            raise

    def get_component(
        self,
        qualifiers: str,
        index: int,
        page_size: Optional[int] = None
    ) -> requests.Response:
        """
        Busca componentes en SonarQube por tipo

        Args:
            qualifiers: Tipo de componente (TRK=proyectos, BRC=ramas, etc.)
            index: Número de página (empieza en 1)
            page_size: Tamaño de página. Por defecto DEFAULT_PAGE_SIZE

        Returns:
            Response con lista de componentes paginada

        Example:
            response = sonar.get_component(qualifiers="TRK", index=1)
            data = response.json()
            projects = data.get('components', [])
        """
        query_args = {
            'qualifiers': qualifiers,
            'p': index,
            'ps': page_size or self.DEFAULT_PAGE_SIZE
        }
        return self._make_call(self.COMPONENTS_SEARCH_ENDPOINT, **query_args)

    def get_project(
        self,
        componente_list: str,
        page_size: Optional[int] = None
    ) -> requests.Response:
        """
        Busca proyectos específicos por clave

        Args:
            componente_list: Lista de claves de componentes separadas por coma
            page_size: Tamaño de página. Por defecto DEFAULT_PAGE_SIZE

        Returns:
            Response con proyectos encontrados

        Example:
            response = sonar.get_project("project1,project2,project3")
        """
        query_args = {
            'projects': componente_list,
            'qualifiers': "TRK",
            'ps': page_size or self.DEFAULT_PAGE_SIZE
        }
        return self._make_call(self.PROJECT_SEARCH_ENDPOINT, **query_args)

    def get_qualitygate_by_project(self, component: str) -> requests.Response:
        """
        Obtiene el Quality Gate de un proyecto específico

        Args:
            component: Clave del componente/proyecto

        Returns:
            Response con información del Quality Gate

        Example:
            response = sonar.get_qualitygate_by_project("my-project-key")
            qg_data = response.json()
        """
        query_args = {
            'project': component
        }
        return self._make_call(self.QUALITYGATE_BYPROJECT_ENDPOINT, **query_args)

    def get_measures_component(
        self,
        component: str,
        metric_keys: Optional[str] = None,
        additional_fields: str = 'metrics,periods'
    ) -> requests.Response:
        """
        Obtiene las métricas actuales de un componente

        Args:
            component: Clave del componente
            metric_keys: Métricas a obtener. Por defecto usa self.METRICS
            additional_fields: Campos adicionales a incluir

        Returns:
            Response con métricas del componente

        Example:
            response = sonar.get_measures_component("my-project")
            measures = response.json().get('component', {}).get('measures', [])
        """
        query_args = {
            'component': component,
            'additionalFields': additional_fields,
            'metricKeys': metric_keys or self.METRICS
        }
        return self._make_call(self.MEASURES_COMPONENT_ENDPOINT, **query_args)

    def get_measures_history(
        self,
        component: str,
        index: int,
        metric_keys: Optional[str] = None
    ) -> requests.Response:
        """
        Obtiene el histórico completo de métricas de un componente

        Args:
            component: Clave del componente
            index: Número de página
            metric_keys: Métricas a obtener. Por defecto usa self.METRICS

        Returns:
            Response con histórico de métricas paginado

        Example:
            response = sonar.get_measures_history("my-project", index=1)
            history = response.json().get('measures', [])
        """
        query_args = {
            'component': component,
            'p': index,
            'metrics': metric_keys or self.METRICS
        }
        return self._make_call(self.MEASURES_SEARCH_HISTORY_ENDPOINT, **query_args)

    def get_measures_history_from(
        self,
        component: str,
        index: int,
        fecha: str,
        metric_keys: Optional[str] = None
    ) -> requests.Response:
        """
        Obtiene el histórico de métricas desde una fecha específica (carga incremental)

        Args:
            component: Clave del componente
            index: Número de página
            fecha: Fecha desde la cual extraer (formato: YYYY-MM-DDTHH:MM:SS+0200)
            metric_keys: Métricas a obtener. Por defecto usa self.METRICS

        Returns:
            Response con histórico de métricas desde la fecha indicada

        Example:
            response = sonar.get_measures_history_from(
                "my-project",
                index=1,
                fecha="2024-01-01T00:00:00+0200"
            )
        """
        query_args = {
            'component': component,
            'p': index,
            'metrics': metric_keys or self.METRICS,
            'from': fecha
        }
        return self._make_call(self.MEASURES_SEARCH_HISTORY_ENDPOINT, **query_args)

    def get_project_analyses(
        self,
        component: str,
        page: int = 1,
        page_size: int = 100
    ) -> requests.Response:
        """
        Obtiene los análisis realizados sobre un proyecto

        Args:
            component: Clave del proyecto
            page: Número de página. Por defecto 1
            page_size: Tamaño de página. Por defecto 100

        Returns:
            Response con lista de análisis del proyecto

        Example:
            response = sonar.get_project_analyses("my-project")
            analyses = response.json().get('analyses', [])
        """
        query_args = {
            'project': component,
            'p': page,
            'ps': page_size
        }
        return self._make_call(self.PROJECT_ANALYSES_ENDPOINT, **query_args)

    def get_project_analyses_from(
        self,
        component: str,
        fecha: str,
        page: int = 1,
        page_size: int = 100,
        category: str = 'VERSION'
    ) -> requests.Response:
        """
        Obtiene análisis de un proyecto desde una fecha específica

        Args:
            component: Clave del proyecto
            fecha: Fecha desde la cual extraer
            page: Número de página. Por defecto 1
            page_size: Tamaño de página. Por defecto 100
            category: Categoría de análisis. Por defecto 'VERSION'

        Returns:
            Response con análisis filtrados por fecha y categoría

        Example:
            response = sonar.get_project_analyses_from(
                "my-project",
                fecha="2024-01-01T00:00:00+0200"
            )
        """
        query_args = {
            'project': component,
            'category': category,
            'from': fecha,
            'p': page,
            'ps': page_size
        }
        return self._make_call(self.PROJECT_ANALYSES_ENDPOINT, **query_args)

    def __repr__(self) -> str:
        """Representación en string del objeto"""
        return f"SonarAPIHandler(host='{self._host}')"
