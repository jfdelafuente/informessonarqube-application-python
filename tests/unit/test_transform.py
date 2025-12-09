#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitarios para el módulo etl.sonar.transform

Tests para las funciones de transformación y parsing de datos de SonarQube.
"""

import pytest
import pandas as pd
from etl.sonar.transform import extraer_componentes, eliminar_namespaces


# =============================================================================
# TESTS PARA extraer_componentes()
# =============================================================================

class TestExtraerComponentes:
    """Tests para la función extraer_componentes"""

    @pytest.mark.unit
    def test_formato_estandar_correcto(self):
        """Test: Parsear proyecto con formato estándar (5 componentes)"""
        # Arrange
        project = "com.orange.webmethods.differential.package:webmethods"

        # Act
        result = extraer_componentes(project)

        # Assert
        assert result['namespace'] == 'webmethods'
        assert result['tipo'] == 'differential'
        assert result['lenguaje'] == 'package'

    @pytest.mark.unit
    def test_formato_extendido_correcto(self):
        """Test: Parsear proyecto con formato extendido (6+ componentes)"""
        # Arrange
        project = "com.orange.sharepoint.extra.library.javascript:sp_portal"

        # Act
        result = extraer_componentes(project)

        # Assert
        assert result['namespace'] == 'sharepoint'
        assert result['tipo'] == 'library'
        assert result['lenguaje'] == 'javascript'

    @pytest.mark.unit
    def test_proyecto_sin_dos_puntos(self):
        """Test: Proyecto sin separador ':' debe retornar error"""
        # Arrange
        project = "com.orange.webmethods.differential.package"

        # Act
        result = extraer_componentes(project)

        # Assert
        assert result['namespace'] == 'error'
        assert result['tipo'] == 'error tipo'
        assert result['lenguaje'] == 'no_languje'

    @pytest.mark.unit
    def test_proyecto_con_formato_invalido(self):
        """Test: Proyecto con formato inválido retorna error"""
        # Arrange
        project = "invalid_project_key"

        # Act
        result = extraer_componentes(project)

        # Assert
        assert result['namespace'] == 'error'
        assert result['tipo'] == 'error tipo'
        assert result['lenguaje'] == 'no_languje'

    @pytest.mark.unit
    @pytest.mark.parametrize("project,expected_namespace,expected_tipo,expected_lenguaje", [
        (
            "com.orange.peoplesoft.application.java:psclientes",
            "peoplesoft",
            "application",
            "java"
        ),
        (
            "com.orange.sap.integration.abap:sapfi",
            "sap",
            "integration",
            "abap"
        ),
        (
            "com.orange.webmethods.differential.package:wm_core",
            "webmethods",
            "differential",
            "package"
        ),
    ])
    def test_multiples_proyectos_validos(
        self,
        project: str,
        expected_namespace: str,
        expected_tipo: str,
        expected_lenguaje: str
    ):
        """Test parametrizado: Múltiples proyectos válidos"""
        # Act
        result = extraer_componentes(project)

        # Assert
        assert result['namespace'] == expected_namespace
        assert result['tipo'] == expected_tipo
        assert result['lenguaje'] == expected_lenguaje


# =============================================================================
# TESTS PARA eliminar_namespaces()
# =============================================================================

class TestEliminarNamespaces:
    """Tests para la función eliminar_namespaces"""

    @pytest.mark.unit
    def test_eliminar_namespaces_basico(self, sample_df_with_namespaces):
        """Test: Eliminar namespaces de la lista de exclusión"""
        # Arrange
        namespaces_excluir = ['test', 'dev']

        # Act
        df_result, eliminadas = eliminar_namespaces(
            sample_df_with_namespaces,
            namespaces_excluir
        )

        # Assert
        assert eliminadas == 2
        assert len(df_result) == 3
        assert 'test' not in df_result['namespace'].values
        assert 'dev' not in df_result['namespace'].values
        assert 'app1' in df_result['namespace'].values
        assert 'app2' in df_result['namespace'].values
        assert 'app3' in df_result['namespace'].values

    @pytest.mark.unit
    def test_eliminar_sin_coincidencias(self, sample_df_with_namespaces):
        """Test: No eliminar filas si no hay coincidencias"""
        # Arrange
        namespaces_excluir = ['inexistente', 'otro_inexistente']

        # Act
        df_result, eliminadas = eliminar_namespaces(
            sample_df_with_namespaces,
            namespaces_excluir
        )

        # Assert
        assert eliminadas == 0
        assert len(df_result) == len(sample_df_with_namespaces)

    @pytest.mark.unit
    def test_eliminar_todos_los_namespaces(self, sample_df_with_namespaces):
        """Test: Eliminar todos los namespaces resulta en DataFrame vacío"""
        # Arrange
        todos_namespaces = sample_df_with_namespaces['namespace'].unique().tolist()

        # Act
        df_result, eliminadas = eliminar_namespaces(
            sample_df_with_namespaces,
            todos_namespaces
        )

        # Assert
        assert eliminadas == len(sample_df_with_namespaces)
        assert len(df_result) == 0

    @pytest.mark.unit
    def test_eliminar_con_lista_vacia(self, sample_df_with_namespaces):
        """Test: Lista de exclusión vacía no elimina nada"""
        # Arrange
        namespaces_excluir = []

        # Act
        df_result, eliminadas = eliminar_namespaces(
            sample_df_with_namespaces,
            namespaces_excluir
        )

        # Assert
        assert eliminadas == 0
        assert len(df_result) == len(sample_df_with_namespaces)

    @pytest.mark.unit
    def test_error_sin_columna_namespace(self):
        """Test: Error si el DataFrame no tiene columna 'namespace'"""
        # Arrange
        df_sin_namespace = pd.DataFrame({
            'name': ['Project 1', 'Project 2'],
            'bugs': [5, 3]
        })
        namespaces_excluir = ['test']

        # Act & Assert
        with pytest.raises(ValueError, match="La columna 'namespace' no existe"):
            eliminar_namespaces(df_sin_namespace, namespaces_excluir)

    @pytest.mark.unit
    def test_dataframe_original_no_modificado(self, sample_df_with_namespaces):
        """Test: El DataFrame original no debe ser modificado"""
        # Arrange
        df_original_len = len(sample_df_with_namespaces)
        namespaces_excluir = ['test', 'dev']

        # Act
        df_result, eliminadas = eliminar_namespaces(
            sample_df_with_namespaces,
            namespaces_excluir
        )

        # Assert
        assert len(sample_df_with_namespaces) == df_original_len  # Original intacto
        assert len(df_result) < df_original_len  # Resultado filtrado
