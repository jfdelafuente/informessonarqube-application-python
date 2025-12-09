#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitarios para el módulo etl.sonar.extract

Tests para funciones auxiliares y de utilidad del módulo de extracción.
Los tests de las funciones principales de extracción están en integration/.
"""

import pytest
from datetime import datetime
import pandas as pd
from etl.sonar.extract import (
    _get_metric_value,
    _format_datetime,
    _create_metrics_dict,
    COLUMNS
)


# =============================================================================
# TESTS PARA _get_metric_value()
# =============================================================================

class TestGetMetricValue:
    """Tests para la función _get_metric_value"""

    @pytest.mark.unit
    def test_extraer_valor_existente(self):
        """Test: Extraer valor cuando existe en el diccionario"""
        # Arrange
        history_entry = {
            "date": "2024-01-15T10:30:00+0000",
            "value": "42"
        }

        # Act
        result = _get_metric_value(history_entry, "bugs")

        # Assert
        assert result == "42"

    @pytest.mark.unit
    def test_extraer_valor_cero_cuando_falta(self):
        """Test: Retornar "0" cuando el valor no existe"""
        # Arrange
        history_entry = {
            "date": "2024-01-15T10:30:00+0000"
        }

        # Act
        result = _get_metric_value(history_entry, "bugs")

        # Assert
        assert result == "0"

    @pytest.mark.unit
    def test_extraer_valor_entrada_vacia(self):
        """Test: Manejar entrada vacía (solo un elemento)"""
        # Arrange
        history_entry = {"date": "2024-01-15T10:30:00+0000"}

        # Act
        result = _get_metric_value(history_entry, "bugs")

        # Assert
        assert result == "0"

    @pytest.mark.unit
    def test_valor_numerico_como_string(self):
        """Test: Convertir valores numéricos a string"""
        # Arrange
        history_entry = {
            "date": "2024-01-15T10:30:00+0000",
            "value": 123
        }

        # Act
        result = _get_metric_value(history_entry, "coverage")

        # Assert
        assert result == "123"
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_valor_float_como_string(self):
        """Test: Convertir valores float a string"""
        # Arrange
        history_entry = {
            "date": "2024-01-15T10:30:00+0000",
            "value": 85.5
        }

        # Act
        result = _get_metric_value(history_entry, "coverage")

        # Assert
        assert result == "85.5"

    @pytest.mark.unit
    @pytest.mark.parametrize("value,expected", [
        ("0", "0"),
        ("100", "100"),
        ("", ""),
        ("N/A", "N/A"),
        (0, "0"),
        (None, "None"),
    ])
    def test_diferentes_tipos_de_valores(self, value, expected):
        """Test parametrizado: Diferentes tipos de valores"""
        # Arrange
        history_entry = {
            "date": "2024-01-15T10:30:00+0000",
            "value": value
        }

        # Act
        result = _get_metric_value(history_entry, "metric")

        # Assert
        assert result == expected


# =============================================================================
# TESTS PARA _format_datetime()
# =============================================================================

class TestFormatDatetime:
    """Tests para la función _format_datetime"""

    @pytest.mark.unit
    def test_formatear_fecha_iso_correcta(self):
        """Test: Formatear fecha ISO estándar"""
        # Arrange
        date_iso = "2024-01-15T10:30:45+0000"

        # Act
        result = _format_datetime(date_iso)

        # Assert
        assert result == "2024-01-15 10:30:45"

    @pytest.mark.unit
    def test_formatear_fecha_iso_sin_timezone(self):
        """Test: Formatear fecha ISO sin timezone"""
        # Arrange
        date_iso = "2024-01-15T10:30:45"

        # Act
        result = _format_datetime(date_iso)

        # Assert
        assert result == "2024-01-15 10:30:45"

    @pytest.mark.unit
    def test_formatear_fecha_invalida_retorna_original(self):
        """Test: Retornar fecha original si no se puede formatear"""
        # Arrange
        date_invalid = "invalid-date-format"

        # Act
        result = _format_datetime(date_invalid)

        # Assert
        assert result == date_invalid

    @pytest.mark.unit
    def test_formatear_fecha_vacia(self):
        """Test: Manejar string vacío"""
        # Arrange
        date_empty = ""

        # Act
        result = _format_datetime(date_empty)

        # Assert
        assert result == ""

    @pytest.mark.unit
    def test_formatear_fecha_con_microsegundos(self):
        """Test: Formatear fecha con microsegundos"""
        # Arrange
        date_iso = "2024-01-15T10:30:45.123456"

        # Act
        result = _format_datetime(date_iso)

        # Assert
        assert result.startswith("2024-01-15 10:30:45")

    @pytest.mark.unit
    @pytest.mark.parametrize("date_input,expected", [
        ("2024-01-01T00:00:00", "2024-01-01 00:00:00"),
        ("2024-12-31T23:59:59", "2024-12-31 23:59:59"),
        ("2024-06-15T12:00:00+0200", "2024-06-15 12:00:00"),
    ])
    def test_multiples_fechas_validas(self, date_input, expected):
        """Test parametrizado: Múltiples formatos de fecha válidos"""
        # Act
        result = _format_datetime(date_input)

        # Assert
        assert result == expected


# =============================================================================
# TESTS PARA _create_metrics_dict()
# =============================================================================

class TestCreateMetricsDict:
    """Tests para la función _create_metrics_dict"""

    @pytest.fixture
    def sample_row(self):
        """Fixture: Fila de ejemplo de un DataFrame de proyectos"""
        return pd.Series({
            "project": "com.orange.app.type.lang:project_name",
            "namespace": "app",
            "name": "Project Name",
            "tipo": "type",
            "lenguaje": "java",
            "quality_gate": "Sonar way"
        })

    @pytest.mark.unit
    def test_crear_diccionario_basico(self, sample_row):
        """Test: Crear diccionario de métricas con datos básicos"""
        # Arrange
        base_data = {"date": "2024-01-15 10:30:45"}

        # Act
        result = _create_metrics_dict(sample_row, base_data)

        # Assert
        assert result["project"] == "com.orange.app.type.lang:project_name"
        assert result["aplicacion"] == "app"
        assert result["name"] == "Project Name"
        assert result["tipo"] == "type"
        assert result["lenguaje"] == "java"
        assert result["quality_gate"] == "Sonar way"
        assert result["date"] == "2024-01-15 10:30:45"

    @pytest.mark.unit
    def test_diccionario_con_multiples_base_data(self, sample_row):
        """Test: Crear diccionario con múltiples campos en base_data"""
        # Arrange
        base_data = {
            "date": "2024-01-15 10:30:45",
            "bugs": "5",
            "coverage": "85.5"
        }

        # Act
        result = _create_metrics_dict(sample_row, base_data)

        # Assert
        assert result["date"] == "2024-01-15 10:30:45"
        assert result["bugs"] == "5"
        assert result["coverage"] == "85.5"

    @pytest.mark.unit
    def test_diccionario_con_base_data_vacio(self, sample_row):
        """Test: Crear diccionario con base_data vacío"""
        # Arrange
        base_data = {}

        # Act
        result = _create_metrics_dict(sample_row, base_data)

        # Assert
        assert "project" in result
        assert "aplicacion" in result
        assert "name" in result
        assert "tipo" in result
        assert "lenguaje" in result
        assert "quality_gate" in result
        assert len(result) == 6  # Solo los 6 campos base

    @pytest.mark.unit
    def test_no_modifica_fila_original(self, sample_row):
        """Test: No modificar la fila original"""
        # Arrange
        base_data = {"date": "2024-01-15 10:30:45"}
        original_values = sample_row.copy()

        # Act
        result = _create_metrics_dict(sample_row, base_data)

        # Assert
        pd.testing.assert_series_equal(sample_row, original_values)

    @pytest.mark.unit
    def test_estructura_correcta_para_dataframe(self, sample_row):
        """Test: El diccionario tiene la estructura correcta para crear DataFrame"""
        # Arrange
        base_data = {
            "date": "2024-01-15 10:30:45",
            "bugs": "0",
            "vulnerabilities": "0"
        }

        # Act
        result = _create_metrics_dict(sample_row, base_data)

        # Assert
        # Verificar que todas las claves requeridas están presentes
        required_keys = ["project", "aplicacion", "name", "tipo", "lenguaje", "quality_gate"]
        for key in required_keys:
            assert key in result

        # Verificar que se agregaron los datos base
        assert "date" in result
        assert "bugs" in result
        assert "vulnerabilities" in result


# =============================================================================
# TESTS PARA CONSTANTES
# =============================================================================

class TestConstants:
    """Tests para constantes del módulo"""

    @pytest.mark.unit
    def test_columns_definidas(self):
        """Test: Verificar que COLUMNS está definida"""
        # Assert
        assert COLUMNS is not None
        assert isinstance(COLUMNS, list)

    @pytest.mark.unit
    def test_columns_contiene_campos_esperados(self):
        """Test: COLUMNS contiene todos los campos esperados"""
        # Arrange
        expected_fields = [
            'project', 'aplicacion', 'name', 'tipo', 'lenguaje', 'date',
            'bugs', 'vulnerabilities', 'code_smells'
        ]

        # Assert
        for field in expected_fields:
            assert field in COLUMNS, f"Campo '{field}' no encontrado en COLUMNS"

    @pytest.mark.unit
    def test_columns_no_duplicados(self):
        """Test: COLUMNS no tiene elementos duplicados"""
        # Assert
        assert len(COLUMNS) == len(set(COLUMNS))

    @pytest.mark.unit
    def test_columns_longitud_correcta(self):
        """Test: COLUMNS tiene la longitud esperada"""
        # Assert
        assert len(COLUMNS) == 20  # Verificar cantidad de columnas


# =============================================================================
# TESTS DE INTEGRACIÓN DE FUNCIONES AUXILIARES
# =============================================================================

class TestAuxiliarFunctionsIntegration:
    """Tests de integración entre funciones auxiliares"""

    @pytest.fixture
    def sample_project_row(self):
        """Fixture: Fila de proyecto de ejemplo"""
        return pd.Series({
            "project": "com.orange.webmethods.differential.package:webmethods",
            "namespace": "webmethods",
            "name": "WebMethods Integration",
            "tipo": "differential",
            "lenguaje": "package",
            "quality_gate": "Sonar way"
        })

    @pytest.fixture
    def sample_history_entry(self):
        """Fixture: Entrada de histórico de ejemplo"""
        return {
            "date": "2024-01-15T10:30:45+0000",
            "value": "42"
        }

    @pytest.mark.unit
    def test_pipeline_completo_creacion_metrica(
        self,
        sample_project_row,
        sample_history_entry
    ):
        """Test: Pipeline completo de creación de una métrica"""
        # Arrange
        metric_name = "bugs"

        # Act - Paso 1: Formatear fecha
        formatted_date = _format_datetime(sample_history_entry["date"])

        # Act - Paso 2: Obtener valor de métrica
        metric_value = _get_metric_value(sample_history_entry, metric_name)

        # Act - Paso 3: Crear diccionario de métricas
        base_data = {
            "date": formatted_date,
            metric_name: metric_value
        }
        metrics_dict = _create_metrics_dict(sample_project_row, base_data)

        # Assert
        assert metrics_dict["date"] == "2024-01-15 10:30:45"
        assert metrics_dict["bugs"] == "42"
        assert metrics_dict["project"] == "com.orange.webmethods.differential.package:webmethods"
        assert metrics_dict["namespace"] == "webmethods"

    @pytest.mark.unit
    def test_crear_dataframe_desde_funciones_auxiliares(
        self,
        sample_project_row
    ):
        """Test: Crear DataFrame usando las funciones auxiliares"""
        # Arrange
        history_entries = [
            {"date": "2024-01-15T10:00:00", "value": "10"},
            {"date": "2024-01-16T10:00:00", "value": "8"},
            {"date": "2024-01-17T10:00:00", "value": "5"},
        ]

        # Act
        metrics_list = []
        for entry in history_entries:
            formatted_date = _format_datetime(entry["date"])
            metric_value = _get_metric_value(entry, "bugs")

            base_data = {
                "date": formatted_date,
                "bugs": metric_value
            }
            metrics_dict = _create_metrics_dict(sample_project_row, base_data)
            metrics_list.append(metrics_dict)

        df = pd.DataFrame(metrics_list)

        # Assert
        assert len(df) == 3
        assert "date" in df.columns
        assert "bugs" in df.columns
        assert "project" in df.columns
        assert df["bugs"].tolist() == ["10", "8", "5"]

    @pytest.mark.unit
    def test_manejo_de_datos_faltantes_en_pipeline(self, sample_project_row):
        """Test: Pipeline maneja correctamente datos faltantes"""
        # Arrange
        incomplete_entry = {
            "date": "2024-01-15T10:00:00"
            # Sin campo "value"
        }

        # Act
        formatted_date = _format_datetime(incomplete_entry.get("date", ""))
        metric_value = _get_metric_value(incomplete_entry, "bugs")

        base_data = {
            "date": formatted_date,
            "bugs": metric_value
        }
        metrics_dict = _create_metrics_dict(sample_project_row, base_data)

        # Assert
        assert metrics_dict["date"] == "2024-01-15 10:00:00"
        assert metrics_dict["bugs"] == "0"  # Valor por defecto

    @pytest.mark.unit
    def test_multiples_metricas_en_mismo_diccionario(self, sample_project_row):
        """Test: Crear diccionario con múltiples métricas"""
        # Arrange
        metrics_data = {
            "bugs": {"date": "2024-01-15T10:00:00", "value": "5"},
            "vulnerabilities": {"date": "2024-01-15T10:00:00", "value": "2"},
            "code_smells": {"date": "2024-01-15T10:00:00", "value": "15"}
        }

        # Act
        base_data = {"date": _format_datetime(metrics_data["bugs"]["date"])}

        for metric_name, entry in metrics_data.items():
            base_data[metric_name] = _get_metric_value(entry, metric_name)

        metrics_dict = _create_metrics_dict(sample_project_row, base_data)

        # Assert
        assert metrics_dict["bugs"] == "5"
        assert metrics_dict["vulnerabilities"] == "2"
        assert metrics_dict["code_smells"] == "15"
        assert metrics_dict["date"] == "2024-01-15 10:00:00"
