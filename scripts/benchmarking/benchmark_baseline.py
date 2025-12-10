"""
Benchmark script for SonarQube ETL Performance Baseline

This script measures the current performance of the ETL process to establish
a baseline for future optimizations.

Usage:
    python scripts/benchmarking/benchmark_baseline.py [sonar|gitlab|all]

Output:
    - Console: Summary of performance metrics
    - File: docs/PERFORMANCE_BASELINE.md (updated with results)
    - File: .benchmark/baseline_YYYY-MM-DD_HH-MM-SS.json (detailed metrics)
"""

import sys
import time
import psutil
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python
# Este script está en scripts/benchmarking/, así que subimos 2 niveles
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
# También agregar src/ para que los imports relativos funcionen
sys.path.insert(0, str(project_root / 'src'))


class PerformanceBenchmark:
    """Benchmark runner for ETL processes"""

    def __init__(self, name: str):
        self.name = name
        self.process = psutil.Process()
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = None

    def __enter__(self):
        """Start benchmarking"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        print(f"\n{'='*60}")
        print(f"🔍 Starting benchmark: {self.name}")
        print(f"{'='*60}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Initial memory: {self.start_memory:.2f} MB")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End benchmarking and collect metrics"""
        self.end_time = time.time()
        self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        if exc_type is not None:
            print(f"\n[ERROR] Benchmark failed with error: {exc_val}")
            return False

        duration = self.end_time - self.start_time
        memory_increase = self.end_memory - self.start_memory

        print(f"\n{'='*60}")
        print(f"[OK] Benchmark completed: {self.name}")
        print(f"{'='*60}")
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"Final memory: {self.end_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"Peak memory: {self.peak_memory:.2f} MB")
        print(f"{'='*60}\n")

        return True

    def get_metrics(self) -> dict:
        """Get benchmark metrics as dictionary"""
        if self.start_time is None or self.end_time is None:
            return {}

        duration = self.end_time - self.start_time

        return {
            'name': self.name,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': round(duration, 2),
            'duration_minutes': round(duration / 60, 2),
            'start_memory_mb': round(self.start_memory, 2),
            'end_memory_mb': round(self.end_memory, 2),
            'memory_increase_mb': round(self.end_memory - self.start_memory, 2),
            'peak_memory_mb': round(self.peak_memory, 2)
        }


def benchmark_sonar_etl() -> dict:
    """Benchmark SonarQube ETL process"""
    with PerformanceBenchmark("SonarQube ETL") as bench:
        from src.main_etl_sonar import main as sonar_main

        try:
            sonar_main()
        except Exception as e:
            print(f"[WARNING] ETL completed with warnings/errors: {e}")

    return bench.get_metrics()


def benchmark_gitlab_etl() -> dict:
    """Benchmark GitLab ETL process"""
    with PerformanceBenchmark("GitLab ETL") as bench:
        from src.main_etl_gitlab import main as gitlab_main

        try:
            gitlab_main()
        except Exception as e:
            print(f"[WARNING] ETL completed with warnings/errors: {e}")

    return bench.get_metrics()


def save_benchmark_results(results: list, output_dir: str = ".benchmark"):
    """Save benchmark results to JSON file"""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"baseline_{timestamp}.json")

    benchmark_data = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory_gb': round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2)
        },
        'benchmarks': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Benchmark results saved to: {output_file}")
    return output_file


def update_baseline_documentation(results: list):
    """Update PERFORMANCE_BASELINE.md with latest results"""
    doc_file = "docs/PERFORMANCE_BASELINE.md"

    # Calculate totals
    total_duration = sum(r['duration_seconds'] for r in results)
    total_memory = sum(r['memory_increase_mb'] for r in results)

    content = f"""# Performance Baseline

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Branch:** feature/performance-optimization-phase-0
**Purpose:** Establish baseline metrics before optimizations

---

## System Information

- **CPU Cores (Physical):** {psutil.cpu_count(logical=False)}
- **CPU Cores (Logical):** {psutil.cpu_count(logical=True)}
- **Total RAM:** {round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2)} GB

---

## Baseline Metrics

### Summary

| Metric | Value |
|--------|-------|
| **Total Duration** | {total_duration:.2f}s ({total_duration/60:.2f} min) |
| **Total Memory Increase** | {total_memory:.2f} MB |

### Detailed Results

"""

    for result in results:
        content += f"""
#### {result['name']}

| Metric | Value |
|--------|-------|
| Duration | {result['duration_seconds']:.2f}s ({result['duration_minutes']:.2f} min) |
| Start Memory | {result['start_memory_mb']:.2f} MB |
| End Memory | {result['end_memory_mb']:.2f} MB |
| Memory Increase | {result['memory_increase_mb']:.2f} MB |
| Peak Memory | {result['peak_memory_mb']:.2f} MB |

"""

    baseline_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    content += f"""
---

## Interpretation

These metrics represent the **current state (before optimization)** of the ETL processes.

### Expected Improvements (Post-Optimization)

Based on the improvement plan:

- **Phase 1 (Low-risk optimizations):** 30-40% improvement
- **Phase 2 (Concurrency):** 50-70% total improvement
- **Combined:** Target 50-70% faster execution

### Key Performance Indicators (KPIs)

After optimizations, we should see:

1. **Duration:** Reduction of 50%+ in total time
2. **API Calls:** Reduction of 40%+ in sequential calls
3. **Memory:** Should remain < 2GB for 5000 projects

---

## Next Steps

1. Implement Phase 1 optimizations (vectorization, caching, logging)
2. Re-run benchmarks to measure improvement
3. Proceed to Phase 2 if targets are met

---

**Baseline established on:** {baseline_timestamp}
"""

    os.makedirs("docs", exist_ok=True)
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"📄 Documentation updated: {doc_file}")


def main():
    """Main benchmark runner"""
    parser = argparse.ArgumentParser(
        description='Benchmark ETL processes to establish performance baseline'
    )
    parser.add_argument(
        'target',
        nargs='?',
        default='all',
        choices=['sonar', 'gitlab', 'all'],
        help='Which ETL process to benchmark (default: all)'
    )

    args = parser.parse_args()

    # Cambiar al directorio raíz del proyecto
    os.chdir(project_root)

    print("\n" + "="*60)
    print("[BENCHMARK] ETL Performance Baseline Benchmark")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = []

    if args.target in ['sonar', 'all']:
        results.append(benchmark_sonar_etl())

    if args.target in ['gitlab', 'all']:
        results.append(benchmark_gitlab_etl())

    # Save results
    output_file = save_benchmark_results(results)
    update_baseline_documentation(results)

    print("\n" + "="*60)
    print("[OK] Benchmarking Complete")
    print("="*60)
    print(f"\nResults saved to:")
    print(f"  - JSON: {output_file}")
    print(f"  - Docs: docs/PERFORMANCE_BASELINE.md")
    print("\nNext steps:")
    print("  1. Review baseline metrics in documentation")
    print("  2. Proceed with Phase 1 optimizations")
    print("  3. Re-run benchmark to measure improvements")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
