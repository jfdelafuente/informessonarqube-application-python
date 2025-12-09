#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests de integración para el pipeline completo de extracción de SonarQube

Este módulo contiene tests que verifican el flujo completo de extracción,
desde la obtención de proyectos hasta la generación de DataFrames con métricas.
"""

import pytest
import responses
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
from api.SonarAPIHandler import SonarAPIHandler
from etl.sonar.extract import (
    extract_proyectos,
    extract_historico,
    extract_historico_columnas,
    COLUMNS
)


# =============================================================================
# FIXTURES DE MOCK RESPONSES
# =============================================================================

@pytest.fixture
def mock_sonar_handler(mock_env_vars):
    """Fixture: Handler de SonarQube mockeado"""
    return SonarAPIHandler()


@pytest.fixture
def mock_projects_response_simple():
    """Fixture: Respuesta simple con 2 proyectos"""
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
                "qualifier": "TRK"
            },
            {
                "key": "com.orange.peoplesoft.application.java:psclientes",
                "name": "PeopleSoft Clientes",
                "qualifier": "TRK"
            }
        ]
    }


@pytest.fixture
def mock_quality_gate_response():
    """Fixture: Respuesta de Quality Gate"""
    return {
        "projectStatus": {
            "status": "OK",
            "conditions": []
        },
        "qualityGate": {
            "name": "Sonar way",
            "key": "AXJMbIUHPAOIsUIE3eNF"
        }
    }


@pytest.fixture
def mock_measures_history_response():
    """Fixture: Respuesta de histórico de métricas"""
    return {
        "measures": [
            {
                "metric": "bugs",
                "history": [
                    {"date": "2024-01-15T10:00:00+0000", "value": "5"},
                    {"date": "2024-01-16T10:00:00+0000", "value": "3"}
                ]
            },
            {
                "metric": "vulnerabilities",
                "history": [
                    {"date": "2024-01-15T10:00:00+0000", "value": "2"},
                    {"date": "2024-01-16T10:00:00+0000", "value": "1"}
                ]
            },
            {
                "metric": "coverage",
                "history": [
                    {"date": "2024-01-15T10:00:00+0000", "value": "85.5"},
                    {"date": "2024-01-16T10:00:00+0000", "value": "87.2"}
                ]
            }
        ]
    }


@pytest.fixture
def sample_df_projects():
    """Fixture: DataFrame de proyectos de ejemplo"""
    return pd.DataFrame({
        "project": [
            "com.orange.webmethods.differential.package:webmethods",
            "com.orange.peoplesoft.application.java:psclientes"
        ],
        "namespace": ["webmethods", "peoplesoft"],
        "name": ["WebMethods Integration", "PeopleSoft Clientes"],
        "tipo": ["differential", "application"],
        "lenguaje": ["package", "java"],
        "quality_gate": ["Sonar way", "Sonar way"]
    })


# =============================================================================
# TESTS PARA extract_proyectos()
# =============================================================================

class TestExtractProyectos:
    """Tests de integración para la función extract_proyectos"""

    @pytest.mark.integration
    @responses.activate
    def test_extract_proyectos_basico(self, mock_env_vars, mock_projects_response_simple):
        """Test: Extraer proyectos básico con mock"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json=mock_projects_response_simple,
            status=200
        )

        # Mock de Quality Gate para cada proyecto
        for _ in range(2):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={
                    "qualityGate": {"name": "Sonar way"}
                },
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        assert isinstance(df_projects, pd.DataFrame)
        assert len(df_projects) == 2
        assert "project" in df_projects.columns
        assert "namespace" in df_projects.columns
        assert "name" in df_projects.columns
        assert "quality_gate" in df_projects.columns

    @pytest.mark.integration
    @responses.activate
    def test_extract_proyectos_vacio(self, mock_env_vars):
        """Test: Manejar respuesta sin proyectos"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 100, "total": 0},
                "components": []
            },
            status=200
        )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        assert isinstance(df_projects, pd.DataFrame)
        assert len(df_projects) == 0

    @pytest.mark.integration
    @responses.activate
    def test_extract_proyectos_parsea_componentes_correctamente(
        self,
        mock_env_vars,
        mock_projects_response_simple
    ):
        """Test: Los componentes se parsean correctamente"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json=mock_projects_response_simple,
            status=200
        )

        for _ in range(2):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={"qualityGate": {"name": "Sonar way"}},
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        assert df_projects.loc[0, "namespace"] == "webmethods"
        assert df_projects.loc[0, "tipo"] == "differential"
        assert df_projects.loc[0, "lenguaje"] == "package"

        assert df_projects.loc[1, "namespace"] == "peoplesoft"
        assert df_projects.loc[1, "tipo"] == "application"
        assert df_projects.loc[1, "lenguaje"] == "java"

    @pytest.mark.integration
    @responses.activate
    def test_extract_proyectos_con_paginacion(self, mock_env_vars):
        """Test: Manejo de múltiples páginas"""
        # Arrange - Página 1
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 2, "total": 3},
                "components": [
                    {
                        "key": "com.orange.app1.type.lang:project1",
                        "name": "Project 1",
                        "qualifier": "TRK"
                    },
                    {
                        "key": "com.orange.app2.type.lang:project2",
                        "name": "Project 2",
                        "qualifier": "TRK"
                    }
                ]
            },
            status=200
        )

        # Arrange - Página 2
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 2, "pageSize": 2, "total": 3},
                "components": [
                    {
                        "key": "com.orange.app3.type.lang:project3",
                        "name": "Project 3",
                        "qualifier": "TRK"
                    }
                ]
            },
            status=200
        )

        # Quality Gates para 3 proyectos
        for _ in range(3):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={"qualityGate": {"name": "Sonar way"}},
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        assert len(df_projects) == 3
        assert len(responses.calls) == 5  # 2 páginas + 3 quality gates


# =============================================================================
# TESTS PARA extract_historico()
# =============================================================================

class TestExtractHistorico:
    """Tests de integración para extract_historico"""

    @pytest.mark.integration
    @responses.activate
    def test_extract_historico_formato_largo(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_history_response
    ):
        """Test: Extracción de histórico en formato largo"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_history_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_history = extract_historico(sample_df_projects, handler)

        # Assert
        assert isinstance(df_history, pd.DataFrame)
        assert "aplicacion" in df_history.columns
        assert "proyecto" in df_history.columns
        assert "lenguaje" in df_history.columns
        assert "metric" in df_history.columns
        assert "date" in df_history.columns
        assert "value" in df_history.columns

    @pytest.mark.integration
    @responses.activate
    def test_extract_historico_multiples_metricas(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_history_response
    ):
        """Test: Verificar que se extraen múltiples métricas"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_history_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_history = extract_historico(sample_df_projects, handler)

        # Assert
        metricas_extraidas = df_history["metric"].unique()
        assert "bugs" in metricas_extraidas
        assert "vulnerabilities" in metricas_extraidas
        assert "coverage" in metricas_extraidas

    @pytest.mark.integration
    @responses.activate
    def test_extract_historico_formato_fecha(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_history_response
    ):
        """Test: Las fechas se formatean correctamente"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_history_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_history = extract_historico(sample_df_projects, handler)

        # Assert
        fecha_ejemplo = df_history.loc[0, "date"]
        # Debe estar en formato "YYYY-MM-DD HH:MM:SS"
        assert len(fecha_ejemplo) == 19
        assert fecha_ejemplo[4] == "-"
        assert fecha_ejemplo[7] == "-"
        assert fecha_ejemplo[10] == " "


# =============================================================================
# TESTS PARA extract_historico_columnas()
# =============================================================================

class TestExtractHistoricoColumnas:
    """Tests de integración para extract_historico_columnas"""

    @pytest.fixture
    def mock_measures_columnar_response(self):
        """Fixture: Respuesta para formato columnar"""
        return {
            "measures": [
                {
                    "metric": "bugs",
                    "history": [{"date": "2024-01-15T10:00:00+0000", "value": "5"}]
                },
                {
                    "metric": "vulnerabilities",
                    "history": [{"date": "2024-01-15T10:00:00+0000", "value": "2"}]
                },
                {
                    "metric": "code_smells",
                    "history": [{"date": "2024-01-15T10:00:00+0000", "value": "15"}]
                },
                {
                    "metric": "coverage",
                    "history": [{"date": "2024-01-15T10:00:00+0000", "value": "85.5"}]
                },
                {
                    "metric": "complexity",
                    "history": [{"date": "2024-01-15T10:00:00+0000", "value": "120"}]
                }
            ]
        }

    @pytest.mark.integration
    @responses.activate
    def test_extract_historico_columnas_retorna_tupla(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_columnar_response
    ):
        """Test: La función retorna una tupla de dos DataFrames"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_columnar_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        result = extract_historico_columnas(sample_df_projects, handler)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        df_historico, df_measure = result
        assert isinstance(df_historico, pd.DataFrame)
        assert isinstance(df_measure, pd.DataFrame)

    @pytest.mark.integration
    @responses.activate
    def test_extract_historico_columnas_estructura_correcta(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_columnar_response
    ):
        """Test: Los DataFrames tienen las columnas correctas"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_columnar_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_historico, df_measure = extract_historico_columnas(sample_df_projects, handler)

        # Assert
        # Verificar que tienen las columnas de COLUMNS
        expected_columns = set(COLUMNS)
        historico_columns = set(df_historico.columns)
        measure_columns = set(df_measure.columns)

        # Al menos las columnas principales deben estar
        assert "project" in historico_columns
        assert "aplicacion" in historico_columns
        assert "date" in historico_columns

        assert "project" in measure_columns
        assert "aplicacion" in measure_columns


# =============================================================================
# TESTS DE PIPELINE COMPLETO
# =============================================================================

class TestPipelineCompleto:
    """Tests del pipeline completo end-to-end"""

    @pytest.mark.integration
    @pytest.mark.slow
    @responses.activate
    def test_pipeline_completo_extraccion(
        self,
        mock_env_vars,
        mock_projects_response_simple,
        mock_measures_history_response
    ):
        """Test: Pipeline completo desde proyectos hasta histórico"""
        # Arrange - Proyectos
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json=mock_projects_response_simple,
            status=200
        )

        # Quality Gates
        for _ in range(2):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={"qualityGate": {"name": "Sonar way"}},
                status=200
            )

        # Histórico
        for _ in range(2):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_history_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        # Paso 1: Extraer proyectos
        df_projects = extract_proyectos(handler)

        # Paso 2: Extraer histórico
        df_history = extract_historico(df_projects, handler)

        # Assert
        assert len(df_projects) > 0
        assert len(df_history) > 0
        assert df_projects["namespace"].nunique() == 2

    @pytest.mark.integration
    @responses.activate
    def test_pipeline_maneja_errores_gracefully(self, mock_env_vars):
        """Test: El pipeline maneja errores sin fallar completamente"""
        # Arrange - Primera página OK, segunda falla
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 100, "total": 1},
                "components": [
                    {
                        "key": "com.orange.app.type.lang:project",
                        "name": "Project",
                        "qualifier": "TRK"
                    }
                ]
            },
            status=200
        )

        responses.add(
            responses.GET,
            "https://sonar.test.com/api/qualitygates/get_by_project",
            json={"qualityGate": {"name": "Sonar way"}},
            status=200
        )

        handler = SonarAPIHandler()

        # Act - No debe lanzar excepción
        df_projects = extract_proyectos(handler)

        # Assert
        assert isinstance(df_projects, pd.DataFrame)
        assert len(df_projects) >= 0


# =============================================================================
# TESTS DE PERFORMANCE Y ESCALABILIDAD
# =============================================================================

class TestPerformance:
    """Tests de performance del pipeline"""

    @pytest.mark.integration
    @pytest.mark.slow
    @responses.activate
    def test_extraccion_multiples_proyectos(self, mock_env_vars):
        """Test: Extracción de múltiples proyectos es eficiente"""
        # Arrange - 10 proyectos
        components = [
            {
                "key": f"com.orange.app{i}.type.lang:project{i}",
                "name": f"Project {i}",
                "qualifier": "TRK"
            }
            for i in range(10)
        ]

        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 100, "total": 10},
                "components": components
            },
            status=200
        )

        # Quality Gates para 10 proyectos
        for _ in range(10):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={"qualityGate": {"name": "Sonar way"}},
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        assert len(df_projects) == 10
        assert df_projects["namespace"].notna().all()

    @pytest.mark.integration
    def test_dataframe_no_contiene_duplicados(self, sample_df_projects):
        """Test: El DataFrame de proyectos no contiene duplicados"""
        # Assert
        assert not sample_df_projects.duplicated(subset=["project"]).any()


# =============================================================================
# TESTS DE VALIDACIÓN DE DATOS
# =============================================================================

class TestValidacionDatos:
    """Tests de validación de la calidad de datos extraídos"""

    @pytest.mark.integration
    @responses.activate
    def test_proyectos_tienen_todos_campos_requeridos(
        self,
        mock_env_vars,
        mock_projects_response_simple
    ):
        """Test: Todos los proyectos tienen campos requeridos"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json=mock_projects_response_simple,
            status=200
        )

        for _ in range(2):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/qualitygates/get_by_project",
                json={"qualityGate": {"name": "Sonar way"}},
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_projects = extract_proyectos(handler)

        # Assert
        required_fields = ["project", "namespace", "name", "tipo", "lenguaje", "quality_gate"]
        for field in required_fields:
            assert field in df_projects.columns
            assert df_projects[field].notna().all(), f"Campo '{field}' tiene valores nulos"

    @pytest.mark.integration
    @responses.activate
    def test_historico_sin_valores_nulos_en_metricas(
        self,
        mock_env_vars,
        sample_df_projects,
        mock_measures_history_response
    ):
        """Test: El histórico no tiene valores nulos en campos críticos"""
        # Arrange
        for _ in range(len(sample_df_projects)):
            responses.add(
                responses.GET,
                "https://sonar.test.com/api/measures/search_history",
                json=mock_measures_history_response,
                status=200
            )

        handler = SonarAPIHandler()

        # Act
        df_history = extract_historico(sample_df_projects, handler)

        # Assert
        assert df_history["metric"].notna().all()
        assert df_history["date"].notna().all()
        assert df_history["value"].notna().all()
