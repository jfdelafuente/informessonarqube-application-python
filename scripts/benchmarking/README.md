# Scripts de Benchmarking

Scripts para medir y comparar el rendimiento del ETL antes/después de optimizaciones.

## 📁 Contenido

| Script | Descripción | Plataforma |
|--------|-------------|------------|
| `benchmark_baseline.py` | Ejecuta benchmarks y mide rendimiento | Todas |
| `compare_benchmarks.py` | Compara dos benchmarks (Python) | Todas |
| `compare_benchmarks.sh` | Compara dos benchmarks (Bash) | Linux/Mac |

---

## 🚀 Uso Rápido

### 1. Ejecutar Benchmark

```bash
# Benchmark completo (SonarQube + GitLab)
python scripts/benchmarking/benchmark_baseline.py all

# Solo SonarQube ETL
python scripts/benchmarking/benchmark_baseline.py sonar

# Solo GitLab ETL
python scripts/benchmarking/benchmark_baseline.py gitlab
```

**Archivos generados:**
- `.benchmark/baseline_YYYY-MM-DD_HH-MM-SS.json` - Datos crudos
- `docs/PERFORMANCE_BASELINE.md` - Documentación actualizada

---

### 2. Comparar Benchmarks

#### Opción A: Script Python (Recomendado - Multiplataforma)

```bash
python scripts/benchmarking/compare_benchmarks.py \
    .benchmark/baseline_2025-12-09_10-00-00.json \
    .benchmark/baseline_2025-12-10_15-00-00.json
```

**Ventajas:**
- ✅ Funciona en Windows, Linux, Mac
- ✅ Output colorizado
- ✅ No requiere dependencias externas
- ✅ Muestra detalles adicionales

#### Opción B: Script Bash (Linux/Mac)

```bash
# Dar permisos de ejecución (solo primera vez)
chmod +x scripts/benchmarking/compare_benchmarks.sh

# Ejecutar comparación
./scripts/benchmarking/compare_benchmarks.sh \
    .benchmark/baseline_2025-12-09_10-00-00.json \
    .benchmark/baseline_2025-12-10_15-00-00.json
```

**Requisitos:**
- `jq` instalado: `sudo apt-get install jq` (Linux) o `brew install jq` (Mac)

---

## 📊 Ejemplo de Output

### benchmark_baseline.py

```
═══════════════════════════════════════════════════════════════
[BENCHMARK] ETL Performance Baseline Benchmark
═══════════════════════════════════════════════════════════════
Target: all
Timestamp: 2025-12-10 10:00:00
═══════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════
🔍 Starting benchmark: SonarQube ETL
═══════════════════════════════════════════════════════════════
Start time: 2025-12-10 10:00:00
Initial memory: 150.23 MB

[... Ejecución del ETL ...]

═══════════════════════════════════════════════════════════════
✓ Benchmark completed: SonarQube ETL
═══════════════════════════════════════════════════════════════
Duration: 1234.56 seconds (20.58 minutes)
Final memory: 450.67 MB
Memory increase: 300.44 MB
Peak memory: 450.67 MB
═══════════════════════════════════════════════════════════════

💾 Benchmark results saved to: .benchmark/baseline_2025-12-10_10-00-00.json
📄 Documentation updated: docs/PERFORMANCE_BASELINE.md
```

---

### compare_benchmarks.py

```
════════════════════════════════════════════════════════════════
  COMPARACIÓN DE BENCHMARKS
════════════════════════════════════════════════════════════════

Archivos comparados:
  Antes:   .benchmark/baseline_2025-12-09_10-00-00.json
           (2025-12-09)
  Después: .benchmark/baseline_2025-12-10_15-00-00.json
           (2025-12-10)

Sistema:
  CPU: 8 cores (16 lógicos)
  RAM: 32.0 GB

════════════════════════════════════════════════════════════════

SonarQube ETL
────────────────────────────────────────────────────────────────
⏱️  Tiempo de Ejecución:
  Antes:   20.58 min
  Después: 12.35 min
  Cambio:  -8.23 min
  ✅ Mejora: 40.00%

💾 Uso de Memoria:
  Antes:   300.44 MB
  Después: 270.00 MB
  Cambio:  -30.44 MB
  ✅ Reducción: 10.13%

ℹ️  Detalles Adicionales:
  Duración (segundos): 1234.56s → 740.74s
  Memoria final: 450.67 MB → 420.23 MB
  Pico memoria: 450.67 MB → 420.23 MB
────────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════════
  RESUMEN TOTAL
════════════════════════════════════════════════════════════════

⏱️  Tiempo Total:
  Antes:   25.88 min
  Después: 15.55 min
  ✅ Mejora: 39.91%

💾 Memoria Total:
  Antes:   380.56 MB
  Después: 350.12 MB
  ✅ Reducción: 8.00%

════════════════════════════════════════════════════════════════

🎉 EXCELENTE MEJORA DE RENDIMIENTO
```

---

## 📝 Workflow Típico

### Escenario: Medir Impacto de Optimización

```bash
# 1. Establecer baseline ANTES de optimización
git checkout develop
python scripts/benchmarking/benchmark_baseline.py all
# Output: .benchmark/baseline_2025-12-09_10-00-00.json

# 2. Implementar optimizaciones
git checkout -b feature/my-optimization
# ... hacer cambios ...
git commit -m "perf: optimizar X"

# 3. Medir DESPUÉS de optimización
python scripts/benchmarking/benchmark_baseline.py all
# Output: .benchmark/baseline_2025-12-10_15-00-00.json

# 4. Comparar resultados
python scripts/benchmarking/compare_benchmarks.py \
    .benchmark/baseline_2025-12-09_10-00-00.json \
    .benchmark/baseline_2025-12-10_15-00-00.json

# 5. Si mejora >= objetivo → Crear PR
# Si mejora < objetivo → Iterar optimización
```

---

## 🔧 Requisitos

### benchmark_baseline.py

```bash
# Dependencias Python (ya en requirements.txt)
pip install psutil  # Para métricas de sistema
```

### compare_benchmarks.py

```bash
# Sin dependencias adicionales (usa stdlib)
# Solo requiere Python 3.6+
```

### compare_benchmarks.sh

```bash
# Requiere jq para parsear JSON
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS
```

---

## 📂 Estructura de Archivos

```
scripts/benchmarking/
├── benchmark_baseline.py      # Script principal de benchmarking
├── compare_benchmarks.py      # Comparación (Python)
├── compare_benchmarks.sh      # Comparación (Bash)
└── README.md                  # Este archivo

.benchmark/                    # Generado automáticamente
├── baseline_2025-12-09_10-00-00.json
├── baseline_2025-12-10_15-00-00.json
└── ...

docs/
└── PERFORMANCE_BASELINE.md    # Actualizado automáticamente
```

---

## 📊 Formato de Datos JSON

```json
{
  "timestamp": "2025-12-10T10:00:00.123456",
  "system_info": {
    "cpu_count": 8,
    "cpu_count_logical": 16,
    "total_memory_gb": 32.0
  },
  "benchmarks": [
    {
      "name": "SonarQube ETL",
      "timestamp": "2025-12-10T10:00:00.123456",
      "duration_seconds": 1234.56,
      "duration_minutes": 20.58,
      "start_memory_mb": 150.23,
      "end_memory_mb": 450.67,
      "memory_increase_mb": 300.44,
      "peak_memory_mb": 450.67
    },
    {
      "name": "GitLab ETL",
      "timestamp": "2025-12-10T10:25:00.123456",
      "duration_seconds": 318.00,
      "duration_minutes": 5.30,
      "start_memory_mb": 420.67,
      "end_memory_mb": 500.79,
      "memory_increase_mb": 80.12,
      "peak_memory_mb": 500.79
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'src'"

**Causa:** Ejecutando desde directorio incorrecto

**Solución:**
```bash
# Siempre ejecutar desde raíz del proyecto
cd /path/to/informessonarqube-application-python
python scripts/benchmarking/benchmark_baseline.py all
```

---

### Error: "jq: command not found" (compare_benchmarks.sh)

**Causa:** jq no está instalado

**Solución:**
```bash
# Linux
sudo apt-get install jq

# macOS
brew install jq

# O usar versión Python en su lugar
python scripts/benchmarking/compare_benchmarks.py ...
```

---

### Benchmark se queda colgado

**Causa:** Conexión lenta o timeout con APIs

**Solución:**
```bash
# 1. Verificar conectividad
ping sonarqube.tu-empresa.com

# 2. Verificar credenciales
cat .env | grep -E "SONAR|GITLAB"

# 3. Ejecutar ETLs individualmente
python scripts/benchmarking/benchmark_baseline.py sonar
python scripts/benchmarking/benchmark_baseline.py gitlab
```

---

## 📚 Documentación Relacionada

- [USO_PRACTICO_BENCHMARK.md](../../docs/USO_PRACTICO_BENCHMARK.md) - Guía detallada
- [FASE_0_PREPARACION.md](../../docs/FASE_0_PREPARACION.md) - Setup inicial
- [FASE_1_COMPLETADA.md](../../docs/FASE_1_COMPLETADA.md) - Ejemplo de uso

---

## 🎯 Objetivos de Rendimiento

| Fase | Objetivo | Métrica |
|------|----------|---------|
| Fase 0 | Baseline | Establecer métricas actuales |
| Fase 1 | Quick Wins | 18-45% mejora tiempo |
| Fase 2 | Concurrencia | 50-70% mejora total |
| Fase 3 | Mantenibilidad | Sin regresión |

---

**Última actualización:** 2025-12-10
**Mantenido por:** Equipo de Performance Optimization
