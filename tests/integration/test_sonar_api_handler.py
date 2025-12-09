#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests de integración para el módulo api.SonarAPIHandler

Tests que verifican la integración con la API de SonarQube usando mocks.
"""

import pytest
import responses
from api.SonarAPIHandler import SonarAPIHandler


# =============================================================================
# TESTS DE INTEGRACIÓN CON MOCK
# =============================================================================

class TestSonarAPIHandlerIntegration:
    """Tests de integración para SonarAPIHandler usando responses mock"""

    @pytest.mark.integration
    @responses.activate
    def test_get_proyectos_con_paginacion(self, mock_env_vars):
        """Test: Obtener proyectos con paginación"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 2, "total": 2},
                "components": [
                    {"key": "project1", "name": "Project 1"},
                    {"key": "project2", "name": "Project 2"}
                ]
            },
            status=200
        )

        handler = SonarAPIHandler()

        # Act
        proyectos = handler.get_proyectos()

        # Assert
        assert len(proyectos) == 2
        assert proyectos[0]['key'] == 'project1'
        assert proyectos[1]['key'] == 'project2'

    @pytest.mark.integration
    @responses.activate
    def test_get_measures_proyecto(self, mock_env_vars):
        """Test: Obtener métricas de un proyecto específico"""
        # Arrange
        project_key = "com.orange.test:app"
        metrics = ["bugs", "vulnerabilities"]

        responses.add(
            responses.GET,
            "https://sonar.test.com/api/measures/component",
            json={
                "component": {
                    "key": project_key,
                    "measures": [
                        {"metric": "bugs", "value": "5"},
                        {"metric": "vulnerabilities", "value": "2"}
                    ]
                }
            },
            status=200
        )

        handler = SonarAPIHandler()

        # Act
        measures = handler.get_measures(project_key, metrics)

        # Assert
        assert 'component' in measures
        assert len(measures['component']['measures']) == 2

    @pytest.mark.integration
    @responses.activate
    def test_timeout_configuracion(self, mock_env_vars):
        """Test: Verificar que el timeout se puede configurar"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={"components": []},
            status=200
        )

        # Act
        handler = SonarAPIHandler(timeout=60)

        # Assert
        assert handler._timeout == 60

    @pytest.mark.integration
    def test_error_sin_variable_entorno(self, monkeypatch):
        """Test: Error si no existe SONAR_DEFAULT_HOST"""
        # Arrange: eliminar variable de entorno
        monkeypatch.delenv("SONAR_DEFAULT_HOST", raising=False)

        # Act & Assert
        with pytest.raises(KeyError, match="SONAR_DEFAULT_HOST"):
            SonarAPIHandler()

    @pytest.mark.integration
    @responses.activate
    def test_headers_autorizacion(self, mock_env_vars):
        """Test: Verificar que se envían headers de autorización correctos"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={"components": []},
            status=200
        )

        handler = SonarAPIHandler()

        # Act
        handler.get_proyectos()

        # Assert
        assert len(responses.calls) == 1
        headers = responses.calls[0].request.headers

        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test_token_12345'
        assert headers['Accept'] == 'application/json'


# =============================================================================
# TESTS DE EDGE CASES
# =============================================================================

class TestSonarAPIHandlerEdgeCases:
    """Tests de casos extremos y manejo de errores"""

    @pytest.mark.integration
    @responses.activate
    def test_respuesta_vacia(self, mock_env_vars):
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
        proyectos = handler.get_proyectos()

        # Assert
        assert proyectos == []

    @pytest.mark.integration
    @responses.activate
    def test_error_http_500(self, mock_env_vars):
        """Test: Manejar error 500 del servidor"""
        # Arrange
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={"error": "Internal Server Error"},
            status=500
        )

        handler = SonarAPIHandler()

        # Act & Assert
        with pytest.raises(Exception):
            handler.get_proyectos()

    @pytest.mark.integration
    @responses.activate
    def test_multiples_paginas(self, mock_env_vars):
        """Test: Obtener proyectos de múltiples páginas"""
        # Arrange: simular 2 páginas
        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 1, "pageSize": 2, "total": 3},
                "components": [
                    {"key": "project1", "name": "Project 1"},
                    {"key": "project2", "name": "Project 2"}
                ]
            },
            status=200
        )

        responses.add(
            responses.GET,
            "https://sonar.test.com/api/components/search_projects",
            json={
                "paging": {"pageIndex": 2, "pageSize": 2, "total": 3},
                "components": [
                    {"key": "project3", "name": "Project 3"}
                ]
            },
            status=200
        )

        handler = SonarAPIHandler()

        # Act
        proyectos = handler.get_proyectos()

        # Assert
        assert len(proyectos) == 3
        assert len(responses.calls) == 2  # Debe hacer 2 llamadas
