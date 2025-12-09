#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitarios para el módulo utils.utils

Tests para funciones de lectura y escritura de archivos CSV.
"""

import pytest
import pandas as pd
from pathlib import Path
from utils.utils import load_to_csv, extract_from_csv


# =============================================================================
# TESTS PARA load_to_csv()
# =============================================================================

class TestLoadToCsv:
    """Tests para la función load_to_csv"""

    @pytest.mark.unit
    def test_guardar_dataframe_simple(self, temp_output_dir):
        """Test: Guardar DataFrame simple en CSV"""
        # Arrange
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        output_file = temp_output_dir / "test_output.csv"

        # Act
        load_to_csv(str(output_file), df)

        # Assert
        assert output_file.exists()

        # Verificar contenido
        df_leido = pd.read_csv(output_file, sep=';', encoding='utf-8')
        pd.testing.assert_frame_equal(df, df_leido)

    @pytest.mark.unit
    def test_guardar_con_caracteres_especiales(self, temp_output_dir):
        """Test: Guardar DataFrame con caracteres especiales UTF-8"""
        # Arrange
        df = pd.DataFrame({
            'nombre': ['José', 'María', 'Ñoño'],
            'descripción': ['Código', 'Métrica', 'Análisis']
        })
        output_file = temp_output_dir / "test_utf8.csv"

        # Act
        load_to_csv(str(output_file), df)

        # Assert
        assert output_file.exists()

        # Verificar que UTF-8 funciona correctamente
        df_leido = pd.read_csv(output_file, sep=';', encoding='utf-8')
        assert df_leido.loc[0, 'nombre'] == 'José'
        assert df_leido.loc[2, 'nombre'] == 'Ñoño'

    @pytest.mark.unit
    def test_sobrescribir_archivo_existente(self, temp_output_dir):
        """Test: Sobrescribir archivo CSV existente"""
        # Arrange
        output_file = temp_output_dir / "test_overwrite.csv"

        df1 = pd.DataFrame({'col': [1, 2]})
        df2 = pd.DataFrame({'col': [10, 20, 30]})

        # Act
        load_to_csv(str(output_file), df1)
        load_to_csv(str(output_file), df2)  # Sobrescribir

        # Assert
        df_leido = pd.read_csv(output_file, sep=';', encoding='utf-8')
        assert len(df_leido) == 3  # Debe tener 3 filas (df2), no 2 (df1)
        assert df_leido.loc[0, 'col'] == 10

    @pytest.mark.unit
    def test_guardar_dataframe_vacio(self, temp_output_dir):
        """Test: Guardar DataFrame vacío"""
        # Arrange
        df = pd.DataFrame(columns=['col1', 'col2'])
        output_file = temp_output_dir / "test_empty.csv"

        # Act
        load_to_csv(str(output_file), df)

        # Assert
        assert output_file.exists()

        df_leido = pd.read_csv(output_file, sep=';', encoding='utf-8')
        assert len(df_leido) == 0
        assert list(df_leido.columns) == ['col1', 'col2']

    @pytest.mark.unit
    def test_sin_indice_en_archivo(self, temp_output_dir):
        """Test: El CSV no debe contener columna de índice"""
        # Arrange
        df = pd.DataFrame({'col1': [1, 2]})
        output_file = temp_output_dir / "test_no_index.csv"

        # Act
        load_to_csv(str(output_file), df)

        # Assert
        with open(output_file, 'r', encoding='utf-8') as f:
            primera_linea = f.readline()

        # No debe empezar con "Unnamed" o números de índice
        assert not primera_linea.startswith('0')
        assert 'col1' in primera_linea


# =============================================================================
# TESTS PARA extract_from_csv()
# =============================================================================

class TestExtractFromCsv:
    """Tests para la función extract_from_csv"""

    @pytest.mark.unit
    def test_leer_csv_existente(self, temp_csv_file):
        """Test: Leer archivo CSV existente"""
        # Act
        df = extract_from_csv(str(temp_csv_file))

        # Assert
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'col1' in df.columns
        assert 'col2' in df.columns
        assert df.loc[0, 'col1'] == 1

    @pytest.mark.unit
    def test_leer_csv_inexistente(self, temp_output_dir):
        """Test: Error al leer archivo que no existe"""
        # Arrange
        archivo_inexistente = temp_output_dir / "no_existe.csv"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            extract_from_csv(str(archivo_inexistente))

    @pytest.mark.unit
    def test_leer_csv_con_utf8(self, temp_output_dir):
        """Test: Leer CSV con caracteres UTF-8"""
        # Arrange
        df_original = pd.DataFrame({
            'nombre': ['José', 'María'],
            'edad': [30, 25]
        })
        csv_file = temp_output_dir / "test_utf8.csv"
        df_original.to_csv(csv_file, sep=';', encoding='utf-8', index=False)

        # Act
        df_leido = extract_from_csv(str(csv_file))

        # Assert
        assert df_leido.loc[0, 'nombre'] == 'José'
        assert df_leido.loc[1, 'nombre'] == 'María'

    @pytest.mark.unit
    def test_leer_csv_vacio(self, temp_output_dir):
        """Test: Leer CSV vacío (solo headers)"""
        # Arrange
        df_vacio = pd.DataFrame(columns=['col1', 'col2'])
        csv_file = temp_output_dir / "test_empty.csv"
        df_vacio.to_csv(csv_file, sep=';', encoding='utf-8', index=False)

        # Act
        df_leido = extract_from_csv(str(csv_file))

        # Assert
        assert len(df_leido) == 0
        assert list(df_leido.columns) == ['col1', 'col2']

    @pytest.mark.unit
    def test_lectura_escritura_roundtrip(self, temp_output_dir):
        """Test: Guardar y leer debe preservar los datos exactamente"""
        # Arrange
        df_original = pd.DataFrame({
            'project': ['app1', 'app2'],
            'bugs': [5, 3],
            'coverage': [85.5, 92.3]
        })
        csv_file = temp_output_dir / "test_roundtrip.csv"

        # Act
        load_to_csv(str(csv_file), df_original)
        df_leido = extract_from_csv(str(csv_file))

        # Assert
        pd.testing.assert_frame_equal(df_original, df_leido)
