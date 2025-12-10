"""
Unit tests for SonarQube transform functions

Tests to verify transformation logic and caching behavior.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from etl.sonar.transform import extraer_componentes


class TestExtraerComponentes:
    """Tests for extraer_componentes function"""

    def test_extraer_componentes_standard_format(self):
        """Verify standard format project parsing"""
        project = "com.orange.peoplesoft.application.java:psclientes"
        result = extraer_componentes(project)

        assert result['namespace'] == 'peoplesoft'
        assert result['tipo'] == 'application'
        assert result['lenguaje'] == 'java'

    def test_extraer_componentes_extended_format(self):
        """Verify extended format project parsing"""
        project = "com.orange.webmethods.differential.package.java:webmethods"
        result = extraer_componentes(project)

        assert result['namespace'] == 'webmethods'
        assert result['tipo'] == 'package'
        assert result['lenguaje'] == 'java'

    def test_extraer_componentes_error_handling(self):
        """Verify error handling for invalid project keys"""
        invalid_project = "invalid_format"
        result = extraer_componentes(invalid_project)

        assert result['namespace'] == 'error'
        assert result['tipo'] == 'error tipo'
        assert result['lenguaje'] == 'no_languje'

    def test_extraer_componentes_caching(self):
        """Verify that LRU cache is working"""
        # Clear cache before test
        extraer_componentes.cache_clear()

        # First call - should be a cache miss
        project = "com.orange.peoplesoft.application.java:psclientes"
        result1 = extraer_componentes(project)

        # Check cache info
        cache_info = extraer_componentes.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 1
        assert cache_info.currsize == 1

        # Second call with same project - should be a cache hit
        result2 = extraer_componentes(project)

        # Verify results are identical
        assert result1 == result2

        # Check cache hit
        cache_info = extraer_componentes.cache_info()
        assert cache_info.hits == 1
        assert cache_info.misses == 1
        assert cache_info.currsize == 1

        # Third call with different project - should be another miss
        project2 = "com.orange.webmethods.differential.package.java:webmethods"
        result3 = extraer_componentes(project2)

        cache_info = extraer_componentes.cache_info()
        assert cache_info.hits == 1
        assert cache_info.misses == 2
        assert cache_info.currsize == 2

        # Clean up
        extraer_componentes.cache_clear()

    def test_extraer_componentes_cache_size(self):
        """Verify cache respects maxsize limit"""
        # Clear cache before test
        extraer_componentes.cache_clear()

        # Generate many unique project keys
        for i in range(10):
            project = f"com.orange.namespace{i}.application.java:project{i}"
            extraer_componentes(project)

        cache_info = extraer_componentes.cache_info()
        assert cache_info.currsize == 10
        assert cache_info.misses == 10
        assert cache_info.hits == 0

        # Clean up
        extraer_componentes.cache_clear()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
