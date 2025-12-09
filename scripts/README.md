# Scripts Directory

Utility scripts organized by functionality.

---

## Directory Structure

```
scripts/
├── benchmarking/          # Performance measurement
│   ├── benchmark_baseline.py
│   └── generate_baseline.py
├── validation/            # Setup validation
│   ├── test_connection.py
│   └── validate_setup.py
└── testing/               # Test runners
    ├── run_tests.sh
    └── run_tests.bat
```

---

## Benchmarking Scripts

**Location:** `scripts/benchmarking/`

### benchmark_baseline.py

Measures ETL performance to establish baseline metrics.

**Usage:**
```bash
python scripts/benchmarking/benchmark_baseline.py [sonar|gitlab|all]
```

**Outputs:**
- `.benchmark/baseline_*.json` - Detailed metrics
- `docs/PERFORMANCE_BASELINE.md` - Documentation

### generate_baseline.py

Captures current ETL outputs as regression test fixtures.

**Usage:**
```bash
python scripts/benchmarking/generate_baseline.py
```

**Outputs:**
- `tests/fixtures/baseline/*.csv` - Reference data

---

## Validation Scripts

**Location:** `scripts/validation/`

### test_connection.py

Tests connectivity to SonarQube and GitLab APIs.

**Usage:**
```bash
python scripts/validation/test_connection.py
```

### validate_setup.py

Validates complete project setup and configuration.

**Usage:**
```bash
python scripts/validation/validate_setup.py
```

---

## Testing Scripts

**Location:** `scripts/testing/`

### run_tests.sh (Linux/Mac)

Runs the complete test suite.

**Usage:**
```bash
bash scripts/testing/run_tests.sh
```

### run_tests.bat (Windows)

Runs the complete test suite on Windows.

**Usage:**
```cmd
scripts\testing\run_tests.bat
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Benchmark SonarQube ETL** | `python scripts/benchmarking/benchmark_baseline.py sonar` |
| **Benchmark GitLab ETL** | `python scripts/benchmarking/benchmark_baseline.py gitlab` |
| **Generate test fixtures** | `python scripts/benchmarking/generate_baseline.py` |
| **Test API connections** | `python scripts/validation/test_connection.py` |
| **Validate setup** | `python scripts/validation/validate_setup.py` |
| **Run tests (Linux/Mac)** | `bash scripts/testing/run_tests.sh` |
| **Run tests (Windows)** | `scripts\testing\run_tests.bat` |

---

**For detailed documentation, see:**
- [docs/FASE_0_PREPARACION.md](../docs/FASE_0_PREPARACION.md) - Phase 0 preparation guide
- [tests/README.md](../tests/README.md) - Testing documentation
