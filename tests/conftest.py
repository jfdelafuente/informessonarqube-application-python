#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuración compartida de pytest para todos los tests

Este archivo contiene fixtures y configuraciones que están disponibles
para todos los archivos de test del proyecto.
"""

import os
import sys
import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, List

# Agregar el directorio src al path para poder importar módulos
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# =============================================================================
# FIXTURES DE CONFIGURACIÓN
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Retorna la ruta raíz del proyecto"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Retorna la ruta del directorio de datos de prueba"""
    return project_root / "tests" / "fixtures"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """
    Crea un directorio temporal para archivos de salida de tests

    Se limpia automáticamente al finalizar el test
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


# =============================================================================
# FIXTURES DE DATOS DE PRUEBA - PROYECTOS
# =============================================================================

@pytest.fixture
def sample_project_keys() -> List[str]:
    """Lista de claves de proyectos de SonarQube para testing"""
    return [
        "com.orange.webmethods.differential.package:webmethods",
        "com.orange.peoplesoft.application.java:psclientes",
        "com.orange.sap.integration.abap:sapfi",
        "com.orange.sharepoint.extra.library.javascript:sp_portal"
    ]


@pytest.fixture
def sample_project_data() -> List[Dict]:
    """Datos de ejemplo de proyectos de SonarQube"""
    return [
        {
            "key": "com.orange.webmethods.differential.package:webmethods",
            "name": "WebMethods Integration",
            "qualifier": "TRK",
            "visibility": "private"
        },
        {
            "key": "com.orange.peoplesoft.application.java:psclientes",
            "name": "PeopleSoft Clientes",
            "qualifier": "TRK",
            "visibility": "private"
        }
    ]


@pytest.fixture
def sample_measures_data() -> List[Dict]:
    """Datos de ejemplo de métricas de SonarQube"""
    return [
        {
            "component": "com.orange.webmethods.differential.package:webmethods",
            "metric": "bugs",
            "value": "5"
        },
        {
            "component": "com.orange.webmethods.differential.package:webmethods",
            "metric": "vulnerabilities",
            "value": "2"
        },
        {
            "component": "com.orange.peoplesoft.application.java:psclientes",
            "metric": "bugs",
            "value": "0"
        }
    ]


# =============================================================================
# FIXTURES DE DATAFRAMES
# =============================================================================

@pytest.fixture
def sample_df_projects(sample_project_data: List[Dict]) -> pd.DataFrame:
    """DataFrame de ejemplo con proyectos"""
    return pd.DataFrame(sample_project_data)


@pytest.fixture
def sample_df_with_namespaces() -> pd.DataFrame:
    """DataFrame con columna namespace para testing de filtros"""
    return pd.DataFrame({
        'namespace': ['app1', 'test', 'app2', 'dev', 'app3'],
        'name': ['Project 1', 'Test Project', 'Project 2', 'Dev Env', 'Project 3'],
        'bugs': [5, 0, 3, 1, 2]
    })


# =============================================================================
# FIXTURES DE ARCHIVOS TEMPORALES
# =============================================================================

@pytest.fixture
def temp_csv_file(tmp_path: Path) -> Path:
    """Crea un archivo CSV temporal para testing"""
    csv_file = tmp_path / "test_data.csv"

    # Crear CSV con datos de prueba
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    df.to_csv(csv_file, sep=';', encoding='utf-8', index=False)

    return csv_file


@pytest.fixture
def temp_lastdate_file(tmp_path: Path) -> Path:
    """Crea un archivo temporal para last_date"""
    return tmp_path / "last_date.txt"


# =============================================================================
# FIXTURES DE CONFIGURACIÓN DE ENTORNO
# =============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Configura variables de entorno mock para testing"""
    monkeypatch.setenv("SONAR_DEFAULT_HOST", "https://sonar.test.com")
    monkeypatch.setenv("SONAR_DEFAULT_TOKEN", "test_token_12345")
    monkeypatch.setenv("GITLAB_DEFAULT_HOST", "https://gitlab.test.com")
    monkeypatch.setenv("GITLAB_DEFAULT_TOKEN", "gitlab_token_12345")


# =============================================================================
# FIXTURES DE MOCK DE RESPUESTAS HTTP
# =============================================================================

@pytest.fixture
def mock_sonar_projects_response() -> Dict:
    """Respuesta mock de la API de SonarQube para listado de proyectos"""
    return {
        "paging": {
            "pageIndex": 1,
            "pageSize": 100,
            "total": 2
        },
        "components": [
            {
                "key": "com.orange.webmethods.differential.package:webmethods",
                "name": "WebMethods Integration",
                "qualifier": "TRK",
                "visibility": "private"
            },
            {
                "key": "com.orange.peoplesoft.application.java:psclientes",
                "name": "PeopleSoft Clientes",
                "qualifier": "TRK",
                "visibility": "private"
            }
        ]
    }


@pytest.fixture
def mock_sonar_measures_response() -> Dict:
    """Respuesta mock de la API de SonarQube para métricas"""
    return {
        "component": {
            "key": "com.orange.webmethods.differential.package:webmethods",
            "measures": [
                {"metric": "bugs", "value": "5"},
                {"metric": "vulnerabilities", "value": "2"},
                {"metric": "code_smells", "value": "15"}
            ]
        }
    }


# =============================================================================
# HOOKS DE PYTEST
# =============================================================================

def pytest_configure(config):
    """Configuración inicial de pytest"""
    config.addinivalue_line(
        "markers", "unit: Tests unitarios de funciones individuales"
    )
    config.addinivalue_line(
        "markers", "integration: Tests de integración con APIs externas"
    )
    config.addinivalue_line(
        "markers", "slow: Tests que tardan más de 5 segundos"
    )
    config.addinivalue_line(
        "markers", "api: Tests que requieren conexión a SonarQube/GitLab"
    )
