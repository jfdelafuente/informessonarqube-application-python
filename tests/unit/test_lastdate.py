#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitarios para el módulo utils.lastdate

Tests para funciones de manejo de fechas de extracción incremental.
"""

import pytest
from pathlib import Path
from datetime import datetime
from utils.lastdate import leer_last_date, save_current_date, nombre_fichero


# =============================================================================
# TESTS PARA leer_last_date()
# =============================================================================

class TestLeerLastDate:
    """Tests para la función leer_last_date"""

    @pytest.mark.unit
    def test_leer_fecha_existente(self, temp_lastdate_file):
        """Test: Leer fecha de archivo existente"""
        # Arrange
        fecha_esperada = "2024-01-15 10:30:45"
        with open(temp_lastdate_file, 'w') as f:
            f.write(fecha_esperada)

        # Act
        fecha_leida = leer_last_date(str(temp_lastdate_file))

        # Assert
        assert fecha_leida == fecha_esperada

    @pytest.mark.unit
    def test_leer_archivo_inexistente(self, temp_output_dir):
        """Test: Retornar cadena vacía si archivo no existe"""
        # Arrange
        archivo_inexistente = temp_output_dir / "no_existe.txt"

        # Act
        fecha_leida = leer_last_date(str(archivo_inexistente))

        # Assert
        assert fecha_leida == ""

    @pytest.mark.unit
    def test_leer_archivo_vacio(self, temp_lastdate_file):
        """Test: Retornar cadena vacía si archivo está vacío"""
        # Arrange: crear archivo vacío
        temp_lastdate_file.touch()

        # Act
        fecha_leida = leer_last_date(str(temp_lastdate_file))

        # Assert
        assert fecha_leida == ""

    @pytest.mark.unit
    def test_leer_fecha_con_espacios_alrededor(self, temp_lastdate_file):
        """Test: Eliminar espacios en blanco alrededor de la fecha"""
        # Arrange
        with open(temp_lastdate_file, 'w') as f:
            f.write("  2024-01-15 10:30:45  \n")

        # Act
        fecha_leida = leer_last_date(str(temp_lastdate_file))

        # Assert
        assert fecha_leida == "2024-01-15 10:30:45"

    @pytest.mark.unit
    def test_leer_solo_primera_linea(self, temp_lastdate_file):
        """Test: Leer solo la primera línea del archivo"""
        # Arrange
        with open(temp_lastdate_file, 'w') as f:
            f.write("2024-01-15 10:30:45\n")
            f.write("2024-01-16 11:00:00\n")  # Línea extra

        # Act
        fecha_leida = leer_last_date(str(temp_lastdate_file))

        # Assert
        assert fecha_leida == "2024-01-15 10:30:45"


# =============================================================================
# TESTS PARA save_current_date()
# =============================================================================

class TestSaveCurrentDate:
    """Tests para la función save_current_date"""

    @pytest.mark.unit
    def test_guardar_fecha_actual(self, temp_lastdate_file):
        """Test: Guardar la fecha actual en el archivo"""
        # Act
        save_current_date(str(temp_lastdate_file))

        # Assert
        assert temp_lastdate_file.exists()

        # Leer y verificar formato
        with open(temp_lastdate_file, 'r') as f:
            fecha_guardada = f.read().strip()

        # Verificar que tiene formato "YYYY-MM-DD HH:MM:SS"
        datetime.strptime(fecha_guardada, "%Y-%m-%d %H:%M:%S")

    @pytest.mark.unit
    def test_formato_fecha_correcto(self, temp_lastdate_file):
        """Test: Verificar que la fecha tiene el formato correcto"""
        # Act
        save_current_date(str(temp_lastdate_file))

        # Assert
        with open(temp_lastdate_file, 'r') as f:
            fecha_guardada = f.read().strip()

        # Verificar componentes de la fecha
        assert len(fecha_guardada) == 19  # "YYYY-MM-DD HH:MM:SS" = 19 caracteres
        assert fecha_guardada[4] == '-'
        assert fecha_guardada[7] == '-'
        assert fecha_guardada[10] == ' '
        assert fecha_guardada[13] == ':'
        assert fecha_guardada[16] == ':'

    @pytest.mark.unit
    def test_crear_directorio_si_no_existe(self, temp_output_dir):
        """Test: Crear directorio padre si no existe"""
        # Arrange
        archivo_en_subdir = temp_output_dir / "subdir" / "nueva_carpeta" / "last_date.txt"

        # Act
        save_current_date(str(archivo_en_subdir))

        # Assert
        assert archivo_en_subdir.exists()
        assert archivo_en_subdir.parent.exists()

    @pytest.mark.unit
    def test_sobrescribir_fecha_anterior(self, temp_lastdate_file):
        """Test: Sobrescribir fecha anterior al guardar nueva"""
        # Arrange: guardar fecha antigua
        with open(temp_lastdate_file, 'w') as f:
            f.write("2020-01-01 00:00:00")

        # Act: guardar nueva fecha
        save_current_date(str(temp_lastdate_file))

        # Assert: la nueva fecha debe ser posterior a 2020
        with open(temp_lastdate_file, 'r') as f:
            fecha_nueva = f.read().strip()

        assert fecha_nueva.startswith("20")  # Siglo 21
        assert not fecha_nueva.startswith("2020-01-01")  # No es la fecha antigua


# =============================================================================
# TESTS PARA nombre_fichero()
# =============================================================================

class TestNombreFichero:
    """Tests para la función nombre_fichero"""

    @pytest.mark.unit
    def test_nombre_sin_fecha(self):
        """Test: Nombre de archivo cuando no hay fecha (primera extracción)"""
        # Act
        nombre = nombre_fichero("historico", "")

        # Assert
        assert nombre == "sonar_salida_historico_etl_tc.csv"

    @pytest.mark.unit
    def test_nombre_con_fecha(self):
        """Test: Nombre de archivo con timestamp cuando hay fecha"""
        # Arrange
        fecha = "2024-01-15 10:30:45"

        # Act
        nombre = nombre_fichero("measure", fecha)

        # Assert
        assert nombre == "sonar_salida_measure_etl_2024_01_15_10_30_45_tc.csv"

    @pytest.mark.unit
    @pytest.mark.parametrize("tipo,fecha,esperado", [
        ("historico", "", "sonar_salida_historico_etl_tc.csv"),
        ("measure", "", "sonar_salida_measure_etl_tc.csv"),
        ("analisis", "", "sonar_salida_analisis_etl_tc.csv"),
        ("project", "", "sonar_salida_project_etl_tc.csv"),
    ])
    def test_diferentes_tipos_sin_fecha(self, tipo, fecha, esperado):
        """Test parametrizado: Diferentes tipos de archivo sin fecha"""
        # Act
        nombre = nombre_fichero(tipo, fecha)

        # Assert
        assert nombre == esperado

    @pytest.mark.unit
    def test_conversion_caracteres_especiales(self):
        """Test: Conversión de caracteres especiales a guiones bajos"""
        # Arrange
        fecha = "2024-01-15 10:30:45"

        # Act
        nombre = nombre_fichero("historico", fecha)

        # Assert
        # Espacios, dos puntos y guiones deben convertirse a '_'
        assert " " not in nombre
        assert ":" not in nombre
        assert "-" not in nombre[len("sonar_salida_historico_etl_"):]  # Después del tipo

    @pytest.mark.unit
    def test_formato_csv(self):
        """Test: Todos los nombres deben terminar en .csv"""
        # Act
        nombre1 = nombre_fichero("historico", "")
        nombre2 = nombre_fichero("measure", "2024-01-15 10:30:45")

        # Assert
        assert nombre1.endswith(".csv")
        assert nombre2.endswith(".csv")

    @pytest.mark.unit
    def test_sufijo_tc_presente(self):
        """Test: Todos los nombres deben contener sufijo '_tc'"""
        # Act
        nombre1 = nombre_fichero("historico", "")
        nombre2 = nombre_fichero("measure", "2024-01-15 10:30:45")

        # Assert
        assert "_tc.csv" in nombre1
        assert "_tc.csv" in nombre2
