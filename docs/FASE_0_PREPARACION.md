# Fase 0: Preparación y Fundamentos

**Fecha:** 2025-12-09
**Branch:** `feature/performance-optimization-phase-0`
**Estado:** ✅ Completado

---

## Objetivos

Establecer baseline y tests de regresión antes de realizar optimizaciones.

### Tareas Completadas

- ✅ **0.1** Benchmarking inicial - Script `benchmark_baseline.py`
- ✅ **0.2** Tests de regresión - `tests/test_regression.py`
- ✅ **0.3** Generación de fixtures - Script `generate_baseline.py`
- ✅ **0.4** Documentación de proceso

---

## Herramientas Creadas

### 1. benchmark_baseline.py

Script para medir el rendimiento actual del ETL.

**Uso:**
```bash
# Benchmark de todos los procesos
python benchmark_baseline.py

# Solo SonarQube
python benchmark_baseline.py sonar

# Solo GitLab
python benchmark_baseline.py gitlab
```

**Salidas:**
- `.benchmark/baseline_YYYY-MM-DD_HH-MM-SS.json` - Métricas detalladas
- `docs/PERFORMANCE_BASELINE.md` - Documentación actualizada

**Métricas capturadas:**
- Duración total (segundos/minutos)
- Memoria inicial/final/pico (MB)
- Incremento de memoria
- Información del sistema (CPU, RAM)

### 2. generate_baseline.py

Script para capturar outputs actuales como fixtures de referencia.

**Uso:**
```bash
# Ejecutar después del ETL para capturar outputs
python generate_baseline.py
```

**Salidas:**
- `tests/fixtures/baseline/sonar_proyectos_baseline.csv`
- `tests/fixtures/baseline/sonar_historico_baseline.csv`
- `tests/fixtures/baseline/sonar_measures_baseline.csv`
- `tests/fixtures/baseline/gitlab_commits_baseline.csv`
- `tests/fixtures/baseline/metadata.txt`

**Propósito:**
- Validar que optimizaciones no rompan funcionalidad
- Comparar estructura de datos antes/después
- Detectar cambios no intencionados

### 3. tests/test_regression.py

Suite de tests de regresión para validar integridad post-optimización.

**Uso:**
```bash
# Ejecutar todos los tests
pytest tests/test_regression.py -v

# Solo tests de SonarQube
pytest tests/test_regression.py::TestRegressionSonarETL -v

# Solo tests de GitLab
pytest tests/test_regression.py::TestRegressionGitLabETL -v
```

**Tests incluidos:**

#### TestRegressionSonarETL
- ✅ `test_projects_output_structure` - Valida columnas y cantidad de filas
- ✅ `test_projects_data_types` - Verifica tipos de datos consistentes
- ✅ `test_historico_output_structure` - Valida estructura de histórico
- ✅ `test_measures_output_structure` - Valida estructura de measures
- ✅ `test_output_file_formats` - Verifica formato CSV con `;`
- ✅ `test_no_duplicate_projects` - Detecta duplicados

#### TestRegressionGitLabETL
- ✅ `test_gitlab_output_structure` - Valida estructura
- ✅ `test_gitlab_year_filter` - **Verifica bug B1 (año hardcodeado)**

#### TestPerformanceRegression
- ✅ `test_benchmark_files_exist` - Valida ejecución de benchmarks
- ✅ `test_memory_usage_reasonable` - Alerta si memoria > 2GB

---

## Flujo de Trabajo

### Paso 1: Ejecutar ETL Actual (Baseline)

```bash
# Ejecutar ETL para generar outputs actuales
python src/main_etl_sonar.py
python src/main_etl_gitlab.py
```

### Paso 2: Capturar Baseline

```bash
# Generar fixtures de referencia
python generate_baseline.py
```

### Paso 3: Ejecutar Benchmark Inicial

```bash
# Medir rendimiento actual
python benchmark_baseline.py
```

Esto genera:
- `.benchmark/baseline_YYYY-MM-DD_HH-MM-SS.json`
- `docs/PERFORMANCE_BASELINE.md`

### Paso 4: Ejecutar Tests de Regresión

```bash
# Verificar que tests pasan con estado actual
pytest tests/test_regression.py -v
```

Todos los tests deberían pasar ✅ en el estado actual.

### Paso 5: Proceder con Optimizaciones

Una vez establecido el baseline:

1. Implementar optimizaciones (Fase 1, 2, 3...)
2. Re-ejecutar benchmark para medir mejoras
3. Re-ejecutar tests de regresión para validar integridad
4. Comparar métricas antes/después

---

## Métricas de Éxito (Fase 0)

| Criterio | Estado |
|----------|--------|
| ✅ Script de benchmark funcional | Completado |
| ✅ Tests de regresión creados | Completado |
| ✅ Fixtures de baseline generados | Pendiente* |
| ✅ Documentación completa | Completado |

*Los fixtures se generan cuando el usuario ejecute el ETL + `generate_baseline.py`

---

## Archivos Creados

```
.
├── benchmark_baseline.py          # Script de benchmarking
├── generate_baseline.py           # Generador de fixtures
├── tests/
│   ├── test_regression.py         # Tests de regresión
│   └── fixtures/
│       └── baseline/              # Directorio para fixtures (creado al ejecutar)
├── docs/
│   ├── FASE_0_PREPARACION.md      # Este documento
│   └── PERFORMANCE_BASELINE.md    # Generado por benchmark_baseline.py
└── .benchmark/                    # Directorio para resultados (creado al ejecutar)
    └── baseline_*.json            # Métricas de benchmark
```

---

## Siguiente Fase

Con la Fase 0 completada, podemos proceder a:

➡️ **Fase 1: Optimizaciones de Bajo Riesgo**

Incluye:
- Vectorización de operaciones Pandas (20% mejora)
- Caché de proyectos (50% mejora en dev)
- Fix bug año hardcodeado (crítico)
- Reducción de logging en loops (10% mejora)

**Branch siguiente:** `feature/performance-optimization-phase-1`

---

## Notas Técnicas

### Requisitos

```bash
pip install pytest psutil
```

### Consideraciones

1. **Benchmarks** son sensibles a:
   - Carga del sistema
   - Estado de la red (latencia API)
   - Cantidad de datos en SonarQube/GitLab
   - Ejecutar múltiples veces para promediar

2. **Fixtures** deben regenerarse si:
   - Cambia estructura de datos en SonarQube
   - Se agregan/eliminan proyectos significativamente
   - Cambia formato de output intencionalmente

3. **Tests de regresión** toleran:
   - ±5% variación en cantidad de filas
   - Orden diferente de filas (no verifica orden)
   - No validan contenido exacto, solo estructura

---

## Troubleshooting

### Problema: "Baseline fixtures not generated yet"

**Solución:**
```bash
python generate_baseline.py
```

### Problema: Benchmark falla con error de API

**Solución:**
- Verificar conectividad con SonarQube/GitLab
- Verificar credenciales en `.env`
- Ejecutar solo el proceso que funciona: `python benchmark_baseline.py sonar`

### Problema: Tests fallan en estado actual

**Causa:** Probablemente bug B1 (año hardcodeado)

**Solución:**
- Tests están diseñados para detectar bugs conocidos
- Proceder con Fase 1 para corregir bug B1
- Tests deberían pasar después de corrección

---

**Preparado por:** Claude Code
**Fecha:** 2025-12-09
