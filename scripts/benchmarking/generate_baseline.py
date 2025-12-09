"""
Generate baseline fixtures for regression testing

This script captures the current ETL outputs as baseline references.
Run this BEFORE making any optimizations.

Usage:
    python scripts/benchmarking/generate_baseline.py
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def generate_baseline_fixtures():
    """Copy current ETL outputs to baseline fixtures directory"""

    baseline_dir = Path("tests/fixtures/baseline")
    sonar_dir = Path("xlsx/SONAR")
    gitlab_dir = Path("xlsx/GITLAB")

    # Create baseline directory
    baseline_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("[BASELINE] Generating Baseline Fixtures")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Define file mappings (source directory, source file, target file)
    file_mappings = [
        # SonarQube files
        (sonar_dir, "sonar_salida_projects_etl_tc.csv", "sonar_proyectos_baseline.csv"),
        (sonar_dir, "sonar_salida_historico_etl_tc.csv", "sonar_historico_baseline.csv"),
        (sonar_dir, "sonar_salida_measure_etl_tc.csv", "sonar_measures_baseline.csv"),

        # GitLab files
        (gitlab_dir, "gitlab_salida_commits.csv", "gitlab_commits_baseline.csv"),
    ]

    copied_files = 0
    skipped_files = 0

    for source_dir, source_name, target_name in file_mappings:
        source_path = source_dir / source_name
        target_path = baseline_dir / target_name

        if not source_path.exists():
            print(f"[SKIP] {source_name} (not found in {source_dir})")
            skipped_files += 1
            continue

        # Copy file
        shutil.copy2(source_path, target_path)

        # Get file size
        size_mb = os.path.getsize(target_path) / 1024 / 1024

        print(f"[OK] Copied {source_name} -> {target_name} ({size_mb:.2f} MB)")
        copied_files += 1

    # Create metadata file
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "purpose": "Regression testing baseline",
        "branch": "feature/performance-optimization-phase-0",
        "files_count": copied_files
    }

    metadata_file = baseline_dir / "metadata.txt"
    with open(metadata_file, 'w') as f:
        f.write(f"Baseline Generated: {metadata['generated_at']}\n")
        f.write(f"Branch: {metadata['branch']}\n")
        f.write(f"Files: {metadata['files_count']}\n")
        f.write("\nThese files represent the BEFORE state (pre-optimization).\n")
        f.write("Use them to verify that optimizations don't break functionality.\n")

    print(f"\n[INFO] Metadata saved to: {metadata_file}")

    print("\n" + "="*60)
    print("[OK] Baseline Generation Complete")
    print("="*60)
    print(f"Files copied: {copied_files}")
    print(f"Files skipped: {skipped_files}")
    print(f"\nBaseline location: {baseline_dir}")
    print("\nNext steps:")
    print("  1. Run regression tests: pytest tests/test_regression.py")
    print("  2. Proceed with optimizations")
    print("  3. Re-run tests to ensure no regressions")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Cambiar al directorio raíz del proyecto (2 niveles arriba desde scripts/benchmarking/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)

    generate_baseline_fixtures()
