"""
Unit tests for GitLab transform functions

Tests to verify that GitLab transformation logic works correctly,
especially the year filter fix (Issue #1).
"""

import pytest
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from etl.gitlab.transform import transformar_created_at


class TestGitLabTransform:
    """Tests for GitLab ETL transform functions"""

    def test_transformar_created_at_uses_current_year(self):
        """Verify that transformar_created_at filters by current year (not hardcoded 2023)"""
        # Create sample data with various years
        current_year = datetime.now().year
        previous_year = current_year - 1

        test_data = {
            'commit_id': ['abc123', 'def456', 'ghi789', 'jkl012'],
            'commit_created_at': [
                f'{current_year}-06-15 10:30:00',
                f'{current_year}-01-01 00:00:00',
                f'{previous_year}-12-31 23:59:59',
                f'{previous_year}-06-15 12:00:00'
            ]
        }

        df = pd.DataFrame(test_data)

        # Apply transformation
        result_df = transformar_created_at(df)

        # Verify only current year data is included
        assert len(result_df) == 2, f"Expected 2 commits from {current_year}, got {len(result_df)}"

        # Verify the correct commits are kept
        result_years = result_df['commit_created_at'].dt.year.unique()
        assert current_year in result_years, f"Expected {current_year} in results"
        assert previous_year not in result_years, f"Previous year {previous_year} should be filtered out"

    def test_transformar_created_at_converts_to_datetime(self):
        """Verify that commit_created_at is converted to datetime type"""
        test_data = {
            'commit_id': ['abc123'],
            'commit_created_at': [f'{datetime.now().year}-01-15 10:30:00']
        }

        df = pd.DataFrame(test_data)
        result_df = transformar_created_at(df)

        # Verify datetime conversion
        assert pd.api.types.is_datetime64_any_dtype(result_df['commit_created_at']), \
            "commit_created_at should be datetime type"

    def test_transformar_created_at_handles_empty_dataframe(self):
        """Verify that function handles empty DataFrame gracefully"""
        df = pd.DataFrame(columns=['commit_id', 'commit_created_at'])

        result_df = transformar_created_at(df)

        assert len(result_df) == 0, "Empty DataFrame should return empty result"
        assert list(result_df.columns) == ['commit_id', 'commit_created_at'], \
            "Columns should be preserved"

    def test_transformar_created_at_boundary_conditions(self):
        """Verify exact start of year boundary is included"""
        current_year = datetime.now().year

        test_data = {
            'commit_id': ['boundary1', 'boundary2'],
            'commit_created_at': [
                f'{current_year}-01-01 00:00:00',  # Exactly start of year
                f'{current_year}-01-01 00:00:01'   # One second after start
            ]
        }

        df = pd.DataFrame(test_data)
        result_df = transformar_created_at(df)

        # Both should be included
        assert len(result_df) == 2, "Start of year boundary should be included"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
