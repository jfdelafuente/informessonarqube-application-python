# Plan de Mejoras por Fases

**Fecha:** 2025-12-09
**Proyecto:** informessonarqube-application-python
**Objetivo:** Mejorar rendimiento (50-70%), mantenibilidad y claridad

---

## Resumen Ejecutivo

Este plan propone **5 fases incrementales** de mejoras:

| Fase | Enfoque | Impacto Rendimiento | Riesgo | Esfuerzo |
|------|---------|---------------------|--------|----------|
| **Fase 0** | Preparación y benchmarking | - | Muy Bajo | Bajo |
| **Fase 1** | Optimizaciones de bajo riesgo | 30-40% | Bajo | Medio |
| **Fase 2** | Concurrencia y paralelización | 50-70% | Medio | Alto |
| **Fase 3** | Refactorización mantenibilidad | - | Medio-Alto | Alto |
| **Fase 4** | Claridad y documentación | - | Bajo | Medio |
| **Fase 5** | Optimizaciones avanzadas (opcional) | 20-30% | Alto | Muy Alto |

---

## FASE 0: Preparación y Fundamentos

**Objetivo:** Establecer baseline y tests de regresión

### Tareas

#### 0.1 Benchmarking Inicial

Crear `benchmark_baseline.py`:

```python
import time
import psutil
from src.main_etl_sonar import main as sonar_main

def benchmark_sonar_etl():
    process = psutil.Process()

    start_time = time.time()
    start_mem = process.memory_info().rss / 1024 / 1024  # MB

    sonar_main()

    end_time = time.time()
    end_mem = process.memory_info().rss / 1024 / 1024

    print(f"Tiempo total: {end_time - start_time:.2f}s")
    print(f"Memoria pico: {end_mem:.2f} MB")
```

Documentar en `docs/PERFORMANCE_BASELINE.md`

#### 0.2 Tests de Regresión

- Guardar outputs de referencia en `tests/fixtures/baseline/`
- Crear tests que validen formato exacto de CSV
- Comparar cantidad de registros

#### 0.3 Documentación de Arquitectura

- Crear diagramas de flujo actuales ✅ (ya creado en ARQUITECTURA_ACTUAL.md)

---

## FASE 1: Optimizaciones de Rendimiento de Bajo Riesgo

**Impacto esperado:** 30-40% mejora
**Riesgo:** Bajo

### 1.1 Vectorización de Operaciones Pandas

**Archivo:** `src/etl/sonar/extract.py:421`

**ANTES:**
```python
for t, row in df_projects.iterrows():  # LENTO
    result = extraer_componentes(row["project"])
```

**DESPUÉS:**
```python
# Opción 1: apply()
df_projects['componentes'] = df_projects['project'].apply(extraer_componentes)

# Opción 2: Vectorizado puro (mejor)
df_projects[['namespace', 'tipo', 'lenguaje']] = (
    df_projects['project']
    .str.split(':', expand=True)[0]
    .str.split('.', expand=True).iloc[:, -3:]
)
```

**Mejora esperada:** 15-20%

### 1.2 Reducción de Logging en Bucles

**ANTES:**
```python
for i, row in df_projects.iterrows():
    logging.debug(f"Procesando {i}/{total}")  # Cada iteración
```

**DESPUÉS:**
```python
for i, row in df_projects.iterrows():
    if i % 10 == 0:  # Log cada 10
        logging.info(f"Procesados {i}/{total}")
```

**Mejora esperada:** 5-10%

### 1.3 Optimización de Creación de DataFrames

**ANTES:**
```python
project_ids = []
for ...:
    project_ids.append((val1, val2, ...))
df = pd.DataFrame(project_ids, columns=[...])
```

**DESPUÉS:**
```python
data = {'col1': [], 'col2': [], 'col3': []}
for ...:
    data['col1'].append(val1)
    data['col2'].append(val2)
df = pd.DataFrame(data)
```

**Mejora esperada:** 10-15%

### 1.4 Caché de Extracción de Proyectos

Crear `src/utils/cache.py`:

```python
import os
import time
import pandas as pd

def extract_proyectos_cached(sonar_handle, cache_hours=24):
    cache_file = '.cache/projects.pkl'

    if os.path.exists(cache_file):
        mtime = os.path.getmtime(cache_file)
        age_hours = (time.time() - mtime) / 3600

        if age_hours < cache_hours:
            print(f"📦 Cargando proyectos desde caché ({age_hours:.1f}h)")
            return pd.read_pickle(cache_file)

    print("🔄 Extrayendo proyectos de SonarQube...")
    df = extract_proyectos(sonar_handle)

    os.makedirs('.cache', exist_ok=True)
    df.to_pickle(cache_file)

    return df
```

**Mejora esperada:** 50-70% en re-ejecuciones

---

## FASE 2: Concurrencia y Paralelización

**Impacto esperado:** 50-70% (acumulativo con Fase 1)
**Riesgo:** Medio

### 2.1 Llamadas API Concurrentes con ThreadPoolExecutor

Crear `src/utils/concurrent.py`:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

def fetch_quality_gates_parallel(sonar_handle, project_keys, max_workers=10):
    """
    Obtiene Quality Gates en paralelo

    Args:
        sonar_handle: SonarAPIHandler
        project_keys: Lista de claves de proyectos
        max_workers: Número de threads concurrentes

    Returns:
        Dict {project_key: quality_gate_name}
    """
    def fetch_one(project_key):
        try:
            response = sonar_handle.get_qualitygate_by_project(project_key)
            data = response.json()
            return project_key, data["qualityGate"]["name"]
        except Exception as e:
            logging.error(f"Error QG {project_key}: {e}")
            return project_key, "ERROR"

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, pk): pk for pk in project_keys}

        for future in as_completed(futures):
            project_key, qg_name = future.result()
            results[project_key] = qg_name

    return results
```

**Uso en `extract_proyectos()`:**
```python
# Recolectar project_keys
project_keys = [p["project"] for p in datos_json["components"]]

# Fetch paralelo
qg_results = fetch_quality_gates_parallel(sonar_handle, project_keys)

# Usar resultados
for project in datos_json["components"]:
    qg = qg_results[project["project"]]
```

**Mejora esperada:** 60-80% en extracción de proyectos

### 2.2 Procesamiento Paralelo de Históricos

```python
from multiprocessing import Pool, cpu_count

def process_project_history_worker(args):
    """Worker picklable para multiprocessing"""
    project_data, sonar_config, date_from = args

    # Recrear handler
    sonar_handle = SonarAPIHandler()

    # Extraer histórico del proyecto
    return extract_single_project_metrics(project_data, sonar_handle, date_from)

def extract_historico_parallel(df_projects, date_from=None, max_workers=None):
    if max_workers is None:
        max_workers = max(1, cpu_count() - 1)

    args_list = [
        (row.to_dict(), None, date_from)
        for _, row in df_projects.iterrows()
    ]

    with Pool(processes=max_workers) as pool:
        results = pool.map(process_project_history_worker, args_list)

    return pd.concat(results, ignore_index=True)
```

**Mejora esperada:** 50-70% en máquinas multi-core

---

## FASE 3: Refactorización para Mantenibilidad

**Impacto:** Mejora significativa en mantenibilidad
**Riesgo:** Medio-Alto

### 3.1 Extracción de Lógica Común

Crear `src/etl/common/pagination.py`:

```python
class APIPageIterator:
    """Iterator genérico para paginación de APIs"""

    def __init__(self, fetch_func, page_size=100):
        self.fetch_func = fetch_func
        self.page_size = page_size
        self.current_page = 1
        self.total = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.total and self.current_page * self.page_size >= self.total + self.page_size:
            raise StopIteration

        response = self.fetch_func(page=self.current_page, page_size=self.page_size)
        data = response.json()

        if self.total is None:
            self.total = data["paging"]["total"]

        self.current_page += 1
        return data
```

**Uso:**
```python
for page_data in APIPageIterator(lambda p, ps: sonar.get_component("TRK", p, ps)):
    process_page(page_data)
```

### 3.2 Separación de Responsabilidades

Crear clases especializadas:

```python
# src/etl/sonar/extractors.py
class ProjectExtractor:
    def __init__(self, sonar_handle):
        self.sonar = sonar_handle

    def fetch_all_projects(self) -> List[Dict]:
        """Solo extrae datos RAW"""
        pass

    def fetch_quality_gates(self, project_keys: List[str]) -> Dict:
        """Solo extrae quality gates"""
        pass

# src/etl/sonar/transformers.py
class ProjectTransformer:
    def parse_components(self, raw_projects: List[Dict]) -> pd.DataFrame:
        """Solo transformaciones"""
        pass
```

### 3.3 Configuración Centralizada

Crear `src/config/settings.py`:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class APISettings:
    page_size: int = 100
    timeout: int = 30
    max_retries: int = 3

@dataclass
class PerformanceSettings:
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    max_concurrent_requests: int = 10

@dataclass
class SonarSettings:
    api: APISettings = APISettings(page_size=200)
    performance: PerformanceSettings = PerformanceSettings()
    excluded_namespaces: List[str] = None
    only_dashboard: bool = False

settings = SonarSettings()
```

---

## FASE 4: Mejoras de Claridad y Documentación

**Impacto:** Mejora significativa en claridad
**Riesgo:** Bajo

### 4.1 Type Hints Completos

**ANTES:**
```python
def extract_proyectos(sonar_handle):
    return df_project
```

**DESPUÉS:**
```python
from typing import Optional
import pandas as pd

def extract_proyectos(
    sonar_handle: SonarAPIHandler,
    cache_enabled: bool = True
) -> pd.DataFrame:
    """
    Extrae todos los proyectos de SonarQube

    Args:
        sonar_handle: Instancia autenticada de SonarAPIHandler
        cache_enabled: Si True, usa caché de proyectos

    Returns:
        DataFrame con columnas: project, namespace, name, tipo, lenguaje, quality_gate

    Raises:
        APIError: Si hay error en comunicación con SonarQube

    Example:
        >>> sonar = SonarAPIHandler()
        >>> df = extract_proyectos(sonar)
        >>> print(len(df))
        1000
    """
```

### 4.2 Refactorización de Nombres

**Cambios:**

- `i, j, t` → `project_index, tag_count, processed_count`
- `df_extract` → `df_projects_raw`
- `no_tratado` → `unprocessed_count`
- `fich_salida_gitlab` → `output_file_gitlab`
- Constantes en UPPER_CASE

### 4.3 Documentación de Magic Numbers

```python
# ANTES
total = 5000

# DESPUÉS
INITIAL_PAGINATION_ESTIMATE = 5000  # Estimación antes de conocer total real de API
```

---

## FASE 5: Optimizaciones Avanzadas (OPCIONAL)

**Impacto:** 20-30% adicional
**Riesgo:** Alto

### 5.1 Sistema de Caché Distribuido (Redis)

```python
import redis
import pickle

class RedisCache:
    def __init__(self, host='localhost', port=6379, ttl=86400):
        self.client = redis.Redis(host=host, port=port)
        self.ttl = ttl

    def get(self, key):
        cached = self.client.get(key)
        return pickle.loads(cached) if cached else None

    def set(self, key, value):
        self.client.setex(key, self.ttl, pickle.dumps(value))
```

### 5.2 Streaming Processing

```python
def extract_historico_streaming(df_projects, chunk_size=100):
    output_file = "sonar_historico.csv"

    for chunk_start in range(0, len(df_projects), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(df_projects))
        df_chunk = df_projects.iloc[chunk_start:chunk_end]

        df_metrics = process_chunk(df_chunk)

        mode = 'w' if chunk_start == 0 else 'a'
        header = chunk_start == 0
        df_metrics.to_csv(output_file, mode=mode, header=header)
```

---

## Roadmap Recomendado

### Opción A: Enfoque en Rendimiento (Recomendado)

```
Sprint 1: Fase 0 + Fase 1 → 40% mejora, bajo riesgo
Sprint 2: Fase 2 → 70% mejora total, riesgo medio
Sprint 3: Fase 3 → Consolidación código
Sprint 4: Fase 4 → Documentación y claridad
```

### Opción B: Quick Wins (1 semana)

```
Implementar solo:
- Fase 1.1: Vectorización (20% mejora, 1-2 días)
- Fase 1.4: Caché (50% mejora dev, 1 día)
- Fase 4.2: Renombrar variables (1 día)
- Fix B1: Bug año hardcodeado (1 hora)
```

---

## Métricas de Éxito

### Rendimiento

- ✅ Reducción de 50%+ en tiempo total ETL SonarQube
- ✅ Reducción de 40%+ en número de llamadas API
- ✅ Uso de memoria < 2GB para 5000 proyectos

### Mantenibilidad

- ✅ Complejidad ciclomática < 10 en todas las funciones
- ✅ Cobertura de tests > 80%
- ✅ Cero duplicación de código en lógica de negocio

### Claridad

- ✅ 100% type hints en funciones públicas
- ✅ Todas las funciones < 50 líneas
- ✅ Cero warnings de linters

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Regresión en resultados | Media | Alto | Tests de regresión (Fase 0) |
| Límites rate API | Media | Medio | Rate limiting inteligente |
| Overhead concurrencia | Media | Medio | Benchmarking, config ajustable |

---

## Próximos Pasos

1. ✅ Revisar y aprobar este plan
2. ⏭️ Crear issues en GitHub por cada tarea
3. ⏭️ Asignar fases a sprints
4. ⏭️ Ejecutar Fase 0 (benchmarking)
5. ⏭️ Comenzar Fase 1

---

**Para más detalles técnicos:** Consultar [OPTIMIZACION_RENDIMIENTO.md](./OPTIMIZACION_RENDIMIENTO.md)
