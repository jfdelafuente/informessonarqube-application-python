# Uso Práctico del Sistema de Benchmarking

**Documento:** Guía práctica para medir y validar mejoras de rendimiento
**Fecha:** 2025-12-10
**Audiencia:** Desarrolladores implementando optimizaciones

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Workflow Completo](#workflow-completo)
3. [Comandos de Benchmarking](#comandos-de-benchmarking)
4. [Escenarios de Uso](#escenarios-de-uso)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Comparación de Baselines](#comparación-de-baselines)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El sistema de benchmarking permite:
- ✅ Establecer líneas base de rendimiento
- ✅ Medir impacto real de optimizaciones
- ✅ Comparar resultados antes/después
- ✅ Validar que las mejoras cumplen objetivos

### Ubicación de Scripts

```
scripts/
└── benchmarking/
    └── benchmark_baseline.py    # Script principal
```

### Archivos Generados

```
.benchmark/                      # Histórico de benchmarks (JSON)
├── baseline_2025-12-10_10-00-00.json
├── baseline_2025-12-10_15-00-00.json
└── ...

docs/
└── PERFORMANCE_BASELINE.md      # Documentación actualizada
```

---

## 🔄 Workflow Completo

### Escenario: Implementar y Validar Optimizaciones de Fase 1

```bash
# ═══════════════════════════════════════════════════════════════
# PASO 1: Establecer Baseline (ANTES de optimizaciones)
# ═══════════════════════════════════════════════════════════════

# 1.1 - Checkout a la rama de baseline (Fase 0)
git checkout feature/performance-optimization-phase-0

# 1.2 - Ejecutar benchmark completo
python scripts/benchmarking/benchmark_baseline.py all

# 1.3 - Resultados generados:
# ✅ .benchmark/baseline_2025-12-10_10-00-00.json
# ✅ docs/PERFORMANCE_BASELINE.md

# Ejemplo de salida:
# ═══════════════════════════════════════════════════════════════
# 🔍 Starting benchmark: SonarQube ETL
# Start time: 2025-12-10 10:00:00
# Initial memory: 150.23 MB
#
# [OK] Benchmark completed: SonarQube ETL
# Duration: 1234.56 seconds (20.58 minutes)
# Final memory: 450.67 MB
# Memory increase: 300.44 MB
# ═══════════════════════════════════════════════════════════════

# 1.4 - Anotar métricas baseline
echo "Baseline establecido:"
echo "  SonarQube ETL: 20.58 min, 300.44 MB"
echo "  GitLab ETL: 5.30 min, 80.12 MB"


# ═══════════════════════════════════════════════════════════════
# PASO 2: Implementar Optimizaciones (Fase 1)
# ═══════════════════════════════════════════════════════════════

# 2.1 - Crear rama de feature
git checkout -b feature/performance-optimization-phase-1

# 2.2 - Implementar optimizaciones
# - Issue #1: Año dinámico
# - Issue #2: Eliminar logging en loops
# - Issue #3: Vectorizar iterrows()
# - Issue #4: Caché LRU
# - Issue #5: DataFrame construcción

# 2.3 - Ejecutar tests para validar
pytest tests/test_sonar_transform.py -v
pytest tests/test_gitlab_transform.py -v
pytest tests/test_regression.py -v

# 2.4 - Commit de cambios
git add .
git commit -m "perf: implementar optimizaciones Fase 1"
git push origin feature/performance-optimization-phase-1


# ═══════════════════════════════════════════════════════════════
# PASO 3: Medir Impacto (DESPUÉS de optimizaciones)
# ═══════════════════════════════════════════════════════════════

# 3.1 - Asegurar que estamos en la rama optimizada
git checkout feature/performance-optimization-phase-1

# 3.2 - Ejecutar benchmark post-optimización
python scripts/benchmarking/benchmark_baseline.py all

# 3.3 - Resultados generados:
# ✅ .benchmark/baseline_2025-12-10_15-00-00.json
# ✅ docs/PERFORMANCE_BASELINE.md (actualizado)

# Ejemplo de salida:
# ═══════════════════════════════════════════════════════════════
# [OK] Benchmark completed: SonarQube ETL
# Duration: 740.74 seconds (12.35 minutes)  ← 40% más rápido!
# Final memory: 420.23 MB
# Memory increase: 270.00 MB
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# PASO 4: Comparar Resultados
# ═══════════════════════════════════════════════════════════════

# 4.1 - Calcular mejora porcentual
echo "Mejora SonarQube ETL:"
echo "  Antes: 20.58 min"
echo "  Después: 12.35 min"
echo "  Mejora: (20.58 - 12.35) / 20.58 = 40.0% más rápido ✅"
echo ""
echo "Mejora GitLab ETL:"
echo "  Antes: 5.30 min"
echo "  Después: 3.20 min"
echo "  Mejora: (5.30 - 3.20) / 5.30 = 39.6% más rápido ✅"

# 4.2 - Validar contra objetivos
echo ""
echo "Objetivo Fase 1: 18-45% mejora"
echo "Resultado: 40% mejora ✅ CUMPLIDO"


# ═══════════════════════════════════════════════════════════════
# PASO 5: Documentar y Hacer PR
# ═══════════════════════════════════════════════════════════════

# 5.1 - Actualizar documentación con resultados reales
# (El script ya lo hace automáticamente en PERFORMANCE_BASELINE.md)

# 5.2 - Crear Pull Request
# Incluir los resultados del benchmark en la descripción del PR

# 5.3 - Merge a develop después de code review

```

---

## 🖥️ Comandos de Benchmarking

### Ejecutar Benchmark Completo (Todos los ETLs)

```bash
python scripts/benchmarking/benchmark_baseline.py all
```

**Cuándo usar:**
- Al establecer baseline inicial (Fase 0)
- Al validar optimizaciones completas (Fase 1, 2, etc.)
- Para comparaciones end-to-end

**Duración aproximada:**
- SonarQube ETL: ~15-25 minutos (depende de # proyectos)
- GitLab ETL: ~3-7 minutos
- **Total: ~20-30 minutos**

---

### Ejecutar Solo SonarQube ETL

```bash
python scripts/benchmarking/benchmark_baseline.py sonar
```

**Cuándo usar:**
- Optimizaciones específicas de SonarQube
- Debug de problemas de rendimiento en SonarQube
- Cuando no hay cambios en GitLab ETL

**Duración aproximada:** ~15-25 minutos

---

### Ejecutar Solo GitLab ETL

```bash
python scripts/benchmarking/benchmark_baseline.py gitlab
```

**Cuándo usar:**
- Optimizaciones específicas de GitLab
- Cuando no hay cambios en SonarQube ETL
- Testing rápido de cambios menores

**Duración aproximada:** ~3-7 minutos

---

## 📊 Escenarios de Uso

### Escenario 1: Primera Vez (Establecer Baseline)

```bash
# Situación: No hay baseline establecido
# Objetivo: Crear baseline inicial antes de cualquier optimización

# Paso 1: Asegurar rama limpia (sin optimizaciones)
git checkout develop
git pull origin develop

# Paso 2: Ejecutar benchmark
python scripts/benchmarking/benchmark_baseline.py all

# Paso 3: Verificar archivos generados
ls -lh .benchmark/
cat docs/PERFORMANCE_BASELINE.md

# Paso 4: Commit baseline a repositorio (opcional)
git add .benchmark/ docs/PERFORMANCE_BASELINE.md
git commit -m "docs: establecer baseline de rendimiento"
git push origin develop
```

---

### Escenario 2: Validar Optimización Específica

```bash
# Situación: Implementaste caché LRU, quieres medir impacto
# Objetivo: Comparar antes/después solo en SonarQube ETL

# Paso 1: Benchmark ANTES (rama sin caché)
git checkout develop
python scripts/benchmarking/benchmark_baseline.py sonar
# Resultado: 20.5 min
mv .benchmark/baseline_*.json .benchmark/before_cache.json

# Paso 2: Implementar caché
git checkout feature/add-lru-cache
# ... implementar caché ...

# Paso 3: Benchmark DESPUÉS (rama con caché)
python scripts/benchmarking/benchmark_baseline.py sonar
# Resultado: 19.8 min
mv .benchmark/baseline_*.json .benchmark/after_cache.json

# Paso 4: Comparar
echo "Mejora: (20.5 - 19.8) / 20.5 = 3.4%"
echo "Impacto de caché: 3.4% ✅"
```

---

### Escenario 3: Comparar Múltiples Versiones

```bash
# Situación: Tienes 3 ramas con diferentes optimizaciones
# Objetivo: Comparar cuál tiene mejor rendimiento

# Rama 1: Baseline
git checkout develop
python scripts/benchmarking/benchmark_baseline.py all
mv .benchmark/baseline_*.json .benchmark/version_baseline.json

# Rama 2: Vectorización
git checkout feature/vectorization
python scripts/benchmarking/benchmark_baseline.py all
mv .benchmark/baseline_*.json .benchmark/version_vectorization.json

# Rama 3: Paralelización
git checkout feature/parallelization
python scripts/benchmarking/benchmark_baseline.py all
mv .benchmark/baseline_*.json .benchmark/version_parallel.json

# Comparar manualmente los 3 JSON files
# O usar un script de comparación (ver sección siguiente)
```

---

### Escenario 4: Debugging de Regresión

```bash
# Situación: Los tests pasan pero el rendimiento empeoró
# Objetivo: Identificar qué commit causó la regresión

# Paso 1: Benchmark en rama actual (lenta)
git checkout feature/my-changes
python scripts/benchmarking/benchmark_baseline.py all
# Resultado: 35 min (¡más lento que antes!)

# Paso 2: Benchmark en commit anterior
git checkout HEAD~1
python scripts/benchmarking/benchmark_baseline.py all
# Resultado: 20 min (normal)

# Paso 3: Identificar commit problemático
git log --oneline -5
git diff HEAD HEAD~1

# Paso 4: Revertir o arreglar el commit problemático
```

---

## 📈 Interpretación de Resultados

### Salida de Consola

```
═══════════════════════════════════════════════════════════════
🔍 Starting benchmark: SonarQube ETL
═══════════════════════════════════════════════════════════════
Start time: 2025-12-10 10:00:00
Initial memory: 150.23 MB

[Aquí se ejecuta el ETL... verás logs del proceso]

═══════════════════════════════════════════════════════════════
[OK] Benchmark completed: SonarQube ETL
═══════════════════════════════════════════════════════════════
Duration: 1234.56 seconds (20.58 minutes)
Final memory: 450.67 MB
Memory increase: 300.44 MB
Peak memory: 450.67 MB
═══════════════════════════════════════════════════════════════
```

### Qué Significan las Métricas

| Métrica | Descripción | Qué Buscar |
|---------|-------------|------------|
| **Duration** | Tiempo total de ejecución | ⬇️ Menor es mejor. Meta: 50-70% reducción |
| **Initial memory** | Memoria al inicio | Baseline estable (~150 MB) |
| **Final memory** | Memoria al finalizar | Debe ser < 2 GB para 5000 proyectos |
| **Memory increase** | Aumento neto de memoria | ⬇️ Menor es mejor. Indica eficiencia |
| **Peak memory** | Pico de memoria usado | Crítico si se acerca al límite de RAM |

---

### Archivo JSON Generado

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
    }
  ]
}
```

**Campos importantes:**
- `duration_minutes`: Para reportes ejecutivos
- `memory_increase_mb`: Para detectar memory leaks
- `system_info`: Para contextualizar resultados (CPU/RAM afectan)

---

## 🔍 Comparación de Baselines

### Script de Comparación Manual

```bash
# Crear script de comparación (compare_benchmarks.sh)
cat > compare_benchmarks.sh << 'EOF'
#!/bin/bash

BEFORE=$1
AFTER=$2

echo "════════════════════════════════════════════"
echo "  Comparación de Benchmarks"
echo "════════════════════════════════════════════"

# Extraer duración con jq
BEFORE_TIME=$(jq '.benchmarks[0].duration_minutes' "$BEFORE")
AFTER_TIME=$(jq '.benchmarks[0].duration_minutes' "$AFTER")

# Calcular mejora
IMPROVEMENT=$(echo "scale=2; ($BEFORE_TIME - $AFTER_TIME) / $BEFORE_TIME * 100" | bc)

echo "Antes:   $BEFORE_TIME min"
echo "Después: $AFTER_TIME min"
echo "Mejora:  $IMPROVEMENT%"

if (( $(echo "$IMPROVEMENT > 0" | bc -l) )); then
    echo "✅ MEJORA DE RENDIMIENTO"
else
    echo "❌ REGRESIÓN DE RENDIMIENTO"
fi
EOF

chmod +x compare_benchmarks.sh

# Usar el script
./compare_benchmarks.sh \
    .benchmark/baseline_2025-12-10_10-00-00.json \
    .benchmark/baseline_2025-12-10_15-00-00.json

# Output:
# ════════════════════════════════════════════
#   Comparación de Benchmarks
# ════════════════════════════════════════════
# Antes:   20.58 min
# Después: 12.35 min
# Mejora:  40.00%
# ✅ MEJORA DE RENDIMIENTO
```

---

### Comparación Python (Más Sofisticada)

```python
# compare_benchmarks.py
import json
import sys
from pathlib import Path

def compare_benchmarks(before_file, after_file):
    with open(before_file) as f:
        before = json.load(f)

    with open(after_file) as f:
        after = json.load(f)

    print("="*60)
    print("  COMPARACIÓN DE BENCHMARKS")
    print("="*60)

    for i, bench_before in enumerate(before['benchmarks']):
        bench_after = after['benchmarks'][i]
        name = bench_before['name']

        time_before = bench_before['duration_minutes']
        time_after = bench_after['duration_minutes']
        time_improvement = ((time_before - time_after) / time_before) * 100

        mem_before = bench_before['memory_increase_mb']
        mem_after = bench_after['memory_increase_mb']
        mem_improvement = ((mem_before - mem_after) / mem_before) * 100

        print(f"\n{name}:")
        print(f"  Tiempo:")
        print(f"    Antes:   {time_before:.2f} min")
        print(f"    Después: {time_after:.2f} min")
        print(f"    Mejora:  {time_improvement:+.2f}%")

        print(f"  Memoria:")
        print(f"    Antes:   {mem_before:.2f} MB")
        print(f"    Después: {mem_after:.2f} MB")
        print(f"    Cambio:  {mem_improvement:+.2f}%")

        if time_improvement > 0:
            print("  ✅ MEJORA DE RENDIMIENTO")
        else:
            print("  ❌ REGRESIÓN DE RENDIMIENTO")

if __name__ == '__main__':
    compare_benchmarks(sys.argv[1], sys.argv[2])
```

**Uso:**
```bash
python compare_benchmarks.py \
    .benchmark/baseline_2025-12-10_10-00-00.json \
    .benchmark/baseline_2025-12-10_15-00-00.json
```

---

## ⚠️ Troubleshooting

### Problema 1: "ModuleNotFoundError: No module named 'src'"

**Causa:** Paths de Python incorrectos

**Solución:**
```bash
# Ejecutar desde la raíz del proyecto
cd /path/to/informessonarqube-application-python
python scripts/benchmarking/benchmark_baseline.py all

# NO ejecutar desde scripts/benchmarking/
```

---

### Problema 2: Benchmark se queda colgado

**Causa:** Conexión con API de SonarQube/GitLab lenta o timeout

**Solución:**
```bash
# 1. Verificar conectividad
ping sonarqube.tu-empresa.com
ping gitlab.tu-empresa.com

# 2. Verificar credenciales en .env
cat .env | grep -E "SONAR|GITLAB"

# 3. Ejecutar solo un ETL a la vez
python scripts/benchmarking/benchmark_baseline.py sonar  # Probar primero
```

---

### Problema 3: Memoria muy alta (> 2 GB)

**Causa:** Memory leak o DataFrames muy grandes

**Solución:**
```bash
# 1. Identificar dónde crece la memoria
# Agregar prints en el código:
# print(f"Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")

# 2. Verificar que DataFrames se liberan
# Agregar del df después de usarlos

# 3. Reducir batch size temporalmente para testing
```

---

### Problema 4: Resultados inconsistentes entre ejecuciones

**Causa:** Cache del sistema, carga de la red, procesos paralelos

**Solución:**
```bash
# 1. Ejecutar 3 veces y promediar
for i in {1..3}; do
    python scripts/benchmarking/benchmark_baseline.py all
    sleep 60  # Esperar 1 min entre ejecuciones
done

# 2. Cerrar otros procesos pesados antes de benchmark
# 3. Ejecutar en horarios de baja carga de red
```

---

## 📚 Referencias

- [FASE_0_PREPARACION.md](./FASE_0_PREPARACION.md) - Setup inicial de benchmarking
- [FASE_1_COMPLETADA.md](./FASE_1_COMPLETADA.md) - Ejemplo de uso en Fase 1
- [OPTIMIZACION_RENDIMIENTO.md](./OPTIMIZACION_RENDIMIENTO.md) - Técnicas de optimización

---

## 🎯 Checklist de Benchmarking

Antes de hacer PR de optimizaciones:

- [ ] Benchmark baseline ejecutado (antes de cambios)
- [ ] Benchmark post-optimización ejecutado (después de cambios)
- [ ] Mejora medida >= objetivo de la fase
- [ ] Memoria se mantiene < 2 GB
- [ ] Resultados documentados en PR description
- [ ] Archivos `.benchmark/*.json` guardados para histórico
- [ ] `docs/PERFORMANCE_BASELINE.md` actualizado

---

**Última actualización:** 2025-12-10
**Versión del documento:** 1.0
