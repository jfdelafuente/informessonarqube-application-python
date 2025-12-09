"""
Regression tests to ensure optimizations don't break functionality

These tests validate that ETL outputs remain consistent after optimizations.
"""

import os
import pytest
import pandas as pd
from pathlib import Path


class TestRegressionSonarETL:
    """Regression tests for SonarQube ETL"""

    BASELINE_DIR = Path("tests/fixtures/baseline")
    OUTPUT_DIR = Path("xlsx/SONAR")

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure baseline fixtures exist"""
        if not self.BASELINE_DIR.exists():
            pytest.skip("Baseline fixtures not generated yet. Run: python generate_baseline.py")

    def test_projects_output_structure(self):
        """Verify projects CSV has expected columns and structure"""
        baseline_file = self.BASELINE_DIR / "sonar_proyectos_baseline.csv"
        current_file = self.OUTPUT_DIR / "sonar_salida_projects_etl_tc.csv"

        if not baseline_file.exists():
            pytest.skip("Baseline projects file not found")

        if not current_file.exists():
            pytest.fail("Current projects file not generated")

        df_baseline = pd.read_csv(baseline_file, sep=';')
        df_current = pd.read_csv(current_file, sep=';')

        # Check columns match
        assert list(df_baseline.columns) == list(df_current.columns), \
            "Column structure has changed"

        # Check row count is similar (±5% tolerance)
        baseline_count = len(df_baseline)
        current_count = len(df_current)
        tolerance = 0.05

        assert abs(current_count - baseline_count) / baseline_count <= tolerance, \
            f"Row count differs significantly: {baseline_count} -> {current_count}"

    def test_projects_data_types(self):
        """Verify data types remain consistent"""
        current_file = self.OUTPUT_DIR / "sonar_salida_projects_etl_tc.csv"

        if not current_file.exists():
            pytest.skip("Current projects file not generated")

        df = pd.read_csv(current_file, sep=';')

        # Verify expected columns exist
        expected_columns = ['project', 'namespace', 'name', 'tipo', 'lenguaje', 'quality_gate']

        for col in expected_columns:
            assert col in df.columns, f"Expected column '{col}' not found"

        # Verify no null values in key columns
        assert not df['project'].isna().any(), "Project column has null values"
        assert not df['name'].isna().any(), "Name column has null values"

    def test_historico_output_structure(self):
        """Verify historico CSV has expected columns"""
        baseline_file = self.BASELINE_DIR / "sonar_historico_baseline.csv"
        current_file = self.OUTPUT_DIR / "sonar_salida_historico_etl_tc.csv"

        if not baseline_file.exists():
            pytest.skip("Baseline historico file not found")

        if not current_file.exists():
            pytest.fail("Current historico file not generated")

        df_baseline = pd.read_csv(baseline_file, sep=';')
        df_current = pd.read_csv(current_file, sep=';')

        # Check columns match
        assert list(df_baseline.columns) == list(df_current.columns), \
            "Historico column structure has changed"

    def test_measures_output_structure(self):
        """Verify measures CSV has expected structure"""
        baseline_file = self.BASELINE_DIR / "sonar_measures_baseline.csv"
        current_file = self.OUTPUT_DIR / "sonar_salida_measure_etl_tc.csv"

        if not baseline_file.exists():
            pytest.skip("Baseline measures file not found")

        if not current_file.exists():
            pytest.fail("Current measures file not generated")

        df_baseline = pd.read_csv(baseline_file, sep=';')
        df_current = pd.read_csv(current_file, sep=';')

        # Check columns match
        assert list(df_baseline.columns) == list(df_current.columns), \
            "Measures column structure has changed"

    def test_output_file_formats(self):
        """Verify all output files use consistent format (CSV with ';' separator)"""
        output_files = [
            self.OUTPUT_DIR / "sonar_salida_projects_etl_tc.csv",
            self.OUTPUT_DIR / "sonar_salida_historico_etl_tc.csv",
            self.OUTPUT_DIR / "sonar_salida_measure_etl_tc.csv"
        ]

        for file_path in output_files:
            if not file_path.exists():
                continue

            # Read first line to verify it's CSV with ';'
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                assert ';' in first_line, f"{file_path.name} doesn't use ';' separator"

    def test_no_duplicate_projects(self):
        """Verify no duplicate project entries"""
        current_file = self.OUTPUT_DIR / "sonar_salida_projects_etl_tc.csv"

        if not current_file.exists():
            pytest.skip("Current projects file not generated")

        df = pd.read_csv(current_file, sep=';')

        duplicates = df[df.duplicated(subset=['project'], keep=False)]

        assert len(duplicates) == 0, \
            f"Found {len(duplicates)} duplicate projects: {duplicates['project'].tolist()}"


class TestRegressionGitLabETL:
    """Regression tests for GitLab ETL"""

    BASELINE_DIR = Path("tests/fixtures/baseline")
    OUTPUT_DIR = Path("xlsx/GITLAB")

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure baseline fixtures exist"""
        if not self.BASELINE_DIR.exists():
            pytest.skip("Baseline fixtures not generated yet")

    def test_gitlab_output_structure(self):
        """Verify GitLab CSV has expected structure"""
        baseline_file = self.BASELINE_DIR / "gitlab_commits_baseline.csv"
        current_file = self.OUTPUT_DIR / "gitlab_salida_commits.csv"

        if not baseline_file.exists():
            pytest.skip("Baseline GitLab file not found")

        if not current_file.exists():
            pytest.fail("Current GitLab file not generated")

        df_baseline = pd.read_csv(baseline_file, sep=';')
        df_current = pd.read_csv(current_file, sep=';')

        # Check columns match
        assert list(df_baseline.columns) == list(df_current.columns), \
            "GitLab column structure has changed"

    def test_gitlab_year_filter(self):
        """Verify GitLab data is filtered to current year (not hardcoded 2023)"""
        current_file = self.OUTPUT_DIR / "gitlab_salida_commits.csv"

        if not current_file.exists():
            pytest.skip("Current GitLab file not generated")

        df = pd.read_csv(current_file, sep=';')

        if 'commit_created_at' not in df.columns:
            pytest.skip("commit_created_at column not found")

        # Extract years from commit_created_at
        from datetime import datetime
        current_year = datetime.now().year

        # Check that we have data from current year (not stuck on 2023)
        years_in_data = df['commit_created_at'].str[:4].unique()

        assert str(current_year) in years_in_data or len(df) == 0, \
            f"No commits from {current_year}. Bug B1 may still be present. Found years: {years_in_data}"


class TestPerformanceRegression:
    """Tests to detect performance regressions"""

    BENCHMARK_DIR = Path(".benchmark")

    def test_benchmark_files_exist(self):
        """Verify benchmark files are being generated"""
        if not self.BENCHMARK_DIR.exists():
            pytest.skip("No benchmarks run yet")

        benchmark_files = list(self.BENCHMARK_DIR.glob("baseline_*.json"))

        assert len(benchmark_files) > 0, \
            "No benchmark files found. Run: python benchmark_baseline.py"

    def test_memory_usage_reasonable(self):
        """Verify memory usage doesn't exceed reasonable limits"""
        import json

        if not self.BENCHMARK_DIR.exists():
            pytest.skip("No benchmarks run yet")

        benchmark_files = sorted(self.BENCHMARK_DIR.glob("baseline_*.json"))

        if not benchmark_files:
            pytest.skip("No benchmark files found")

        # Load latest benchmark
        with open(benchmark_files[-1], 'r') as f:
            data = json.load(f)

        # Check memory usage for each benchmark
        for benchmark in data.get('benchmarks', []):
            memory_mb = benchmark.get('end_memory_mb', 0)

            # Alert if memory usage exceeds 2GB
            assert memory_mb < 2000, \
                f"{benchmark['name']} uses {memory_mb:.2f} MB (> 2GB limit)"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
