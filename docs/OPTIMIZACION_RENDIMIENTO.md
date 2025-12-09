# Guía de Optimización de Rendimiento

**Proyecto:** informessonarqube-application-python
**Fecha:** 2025-12-09

---

## Índice

1. [Quick Wins (1 Semana)](#quick-wins-1-semana)
2. [Benchmarking y Medición](#benchmarking-y-medición)
3. [Técnicas de Optimización](#técnicas-de-optimización)
4. [Ejemplos Antes/Después](#ejemplos-antesdespués)
5. [Herramientas de Profiling](#herramientas-de-profiling)

---

## Quick Wins (1 Semana)

Implementaciones rápidas con alto impacto:

### 1. Vectorizar operaciones Pandas (2 días, 20% mejora)

**Archivo:** `src/etl/sonar/extract.py:421`

```python
# ❌ ANTES (LENTO)
for t, row in df_projects.iterrows():
    result = extraer_componentes(row["project"])
    # ... usar result ...

# ✅ DESPUÉS (RÁPIDO)
df_projects['components'] = df_projects['project'].apply(extraer_componentes)
```

### 2. Caché de proyectos (1 día, 50% mejora en dev)

**Archivo:** Crear `src/utils/cache.py`

```python
import os
import pickle
import time

def load_cached(cache_file, ttl_hours=24):
    if os.path.exists(cache_file):
        age = (time.time() - os.path.getmtime(cache_file)) / 3600
        if age < ttl_hours:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    return None

def save_cache(cache_file, data):
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
```

### 3. Fix bug año hardcodeado (1 hora, crítico)

**Archivo:** `src/etl/gitlab/transform.py`

```python
# ❌ ANTES (BUG)
df = df[df['commit_created_at'].str.contains('2023')]

# ✅ DESPUÉS (CORRECTO)
from datetime import datetime
current_year = str(datetime.now().year)
df = df[df['commit_created_at'].str.contains(current_year)]
```

### 4. Reducir logging en loops (1 día, 10% mejora)

```python
# ❌ ANTES
for i in range(1000):
    logging.debug(f"Processing {i}")  # 1000 I/O calls

# ✅ DESPUÉS
for i in range(1000):
    if i % 100 == 0:  # 10 I/O calls
        logging.info(f"Processed {i}/1000")
```

---

## Benchmarking y Medición

### Script de Benchmarking

Crear `benchmark_etl.py`:

```python
import time
import psutil
import pandas as pd
from src.main_etl_sonar import main

def benchmark():
    process = psutil.Process()

    # Medir memoria inicial
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Medir tiempo
    start = time.time()
    main()
    duration = time.time() - start

    # Medir memoria final
    mem_after = process.memory_info().rss / 1024 / 1024

    results = {
        'duration_seconds': duration,
        'duration_minutes': duration / 60,
        'memory_mb': mem_after,
        'memory_increase_mb': mem_after - mem_before
    }

    return results

if __name__ == '__main__':
    print("🔍 Ejecutando benchmark...")
    results = benchmark()

    print(f"\n📊 Resultados:")
    print(f"  Tiempo: {results['duration_minutes']:.2f} minutos")
    print(f"  Memoria: {results['memory_mb']:.2f} MB")
    print(f"  Incremento memoria: {results['memory_increase_mb']:.2f} MB")
```

### Profiling con cProfile

```bash
# Profiling detallado
python -m cProfile -s cumtime src/main_etl_sonar.py > profile.txt

# Ver top 20 funciones más lentas
head -n 30 profile.txt
```

### Profiling con line_profiler

```bash
# Instalar
pip install line_profiler

# Decorar función a profilear
@profile
def extract_proyectos(sonar_handle):
    # ...

# Ejecutar
kernprof -l -v src/etl/sonar/extract.py
```

---

## Técnicas de Optimización

### 1. Concurrencia con ThreadPoolExecutor

**Cuándo usar:** I/O-bound (llamadas API, lectura archivos)

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_data_parallel(items, fetch_func, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_func, item) for item in items]
        for future in as_completed(futures):
            results.append(future.result())
    return results
```

**Mejora típica:** 60-80% en operaciones I/O

### 2. Paralelización con Multiprocessing

**Cuándo usar:** CPU-bound (procesamiento de datos)

```python
from multiprocessing import Pool, cpu_count

def process_parallel(items, process_func):
    with Pool(processes=cpu_count()-1) as pool:
        results = pool.map(process_func, items)
    return results
```

**Mejora típica:** 50-70% en máquinas multi-core

### 3. Vectorización Pandas

**Cuándo usar:** Operaciones sobre DataFrames

```python
# ❌ LENTO: Loop explícito
for i, row in df.iterrows():
    df.at[i, 'result'] = row['a'] + row['b']

# ✅ RÁPIDO: Vectorizado
df['result'] = df['a'] + df['b']

# ✅ RÁPIDO: apply() cuando no se puede vectorizar
df['result'] = df.apply(lambda row: complex_func(row['a'], row['b']), axis=1)
```

**Mejora típica:** 10-50x más rápido

### 4. Caché Inteligente

```python
from functools import lru_cache

# Caché en memoria (para funciones puras)
@lru_cache(maxsize=1000)
def expensive_computation(param):
    # ... cálculo costoso ...
    return result

# Caché en disco (para datos grandes)
def get_cached_or_fetch(key, fetch_func, ttl_hours=24):
    cache_file = f".cache/{key}.pkl"

    # Intentar leer caché
    if os.path.exists(cache_file):
        age_hours = (time.time() - os.path.getmtime(cache_file)) / 3600
        if age_hours < ttl_hours:
            return pd.read_pickle(cache_file)

    # Fetch y guardar
    data = fetch_func()
    os.makedirs(".cache", exist_ok=True)
    data.to_pickle(cache_file)
    return data
```

### 5. Chunking para Grandes Volúmenes

```python
def process_large_dataset(df, chunk_size=1000):
    results = []

    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start+chunk_size]
        result = process_chunk(chunk)
        results.append(result)

    return pd.concat(results, ignore_index=True)
```

### 6. Lazy Loading

```python
# ❌ Carga todo en memoria
df_all = pd.read_csv('huge_file.csv')
df_filtered = df_all[df_all['year'] == 2023]

# ✅ Lee solo lo necesario
df_filtered = pd.read_csv(
    'huge_file.csv',
    usecols=['date', 'value', 'year'],  # Solo columnas necesarias
    parse_dates=['date'],
    chunksize=10000  # Procesar en chunks
)
```

---

## Ejemplos Antes/Después

### Ejemplo 1: Extracción de Quality Gates

**❌ ANTES (Secuencial - 33 minutos para 1000 proyectos)**

```python
def extract_proyectos(sonar_handle):
    project_ids = []

    for project in projects:
        # Llamada bloqueante
        qg = sonar_handle.get_qualitygate_by_project(project['key'])
        qg_name = qg.json()['qualityGate']['name']

        project_ids.append((
            project['key'],
            project['name'],
            qg_name
        ))

    return pd.DataFrame(project_ids, columns=['project', 'name', 'qg'])
```

**✅ DESPUÉS (Paralelo - 7 minutos para 1000 proyectos)**

```python
from concurrent.futures import ThreadPoolExecutor

def extract_proyectos(sonar_handle):
    def fetch_qg(project_key):
        qg = sonar_handle.get_qualitygate_by_project(project_key)
        return qg.json()['qualityGate']['name']

    # Extraer keys
    project_keys = [p['key'] for p in projects]

    # Fetch paralelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        qg_names = list(executor.map(fetch_qg, project_keys))

    # Construir DataFrame
    data = {
        'project': [p['key'] for p in projects],
        'name': [p['name'] for p in projects],
        'qg': qg_names
    }

    return pd.DataFrame(data)
```

**Mejora:** 78% más rápido

### Ejemplo 2: Procesamiento de Histórico

**❌ ANTES (row-by-row - 45 minutos)**

```python
metrics_list = []
for i, row in df_projects.iterrows():
    project_key = row['project']
    componentes = extraer_componentes(project_key)  # Parse complejo

    metrics_list.append({
        'project': project_key,
        'namespace': componentes['namespace'],
        'tipo': componentes['tipo']
    })

df_metrics = pd.DataFrame(metrics_list)
```

**✅ DESPUÉS (Vectorizado - 5 minutos)**

```python
# Extraer componentes una sola vez
df_projects['componentes'] = df_projects['project'].apply(extraer_componentes)

# Expandir a columnas separadas
df_metrics = pd.DataFrame(df_projects['componentes'].tolist())
df_metrics['project'] = df_projects['project']
```

**Mejora:** 89% más rápido

### Ejemplo 3: Construcción de DataFrames

**❌ ANTES (Append incremental - lento)**

```python
df_result = pd.DataFrame()
for chunk in chunks:
    df_chunk = process(chunk)
    df_result = df_result.append(df_chunk)  # Copia completa cada vez
```

**✅ DESPUÉS (Lista + concat - rápido)**

```python
results = []
for chunk in chunks:
    df_chunk = process(chunk)
    results.append(df_chunk)

df_result = pd.concat(results, ignore_index=True)  # Una sola operación
```

**Mejora:** 95% más rápido para 1000+ iteraciones

---

## Herramientas de Profiling

### 1. cProfile (Built-in)

```bash
python -m cProfile -s cumtime src/main_etl_sonar.py
```

### 2. line_profiler (Línea por línea)

```bash
pip install line_profiler
kernprof -l -v script.py
```

### 3. memory_profiler (Memoria)

```bash
pip install memory_profiler
python -m memory_profiler script.py
```

### 4. py-spy (Sampling profiler)

```bash
pip install py-spy
py-spy record -o profile.svg -- python script.py
```

### 5. snakeviz (Visualización)

```bash
pip install snakeviz
python -m cProfile -o profile.prof script.py
snakeviz profile.prof
```

---

## Checklist de Optimización

Antes de optimizar, verificar:

- [ ] ¿Mediste el baseline actual?
- [ ] ¿Identificaste el cuello de botella real? (profiling)
- [ ] ¿La optimización es realmente necesaria?
- [ ] ¿Tienes tests de regresión?

Después de optimizar, verificar:

- [ ] ¿Mediste la mejora? (benchmark antes/después)
- [ ] ¿Los tests siguen pasando?
- [ ] ¿El código sigue siendo legible?
- [ ] ¿Documentaste los cambios?

---

## Reglas de Oro

1. **Measure first, optimize second** - Siempre medir antes de optimizar
2. **80/20 Rule** - 80% del tiempo se gasta en 20% del código
3. **Premature optimization is evil** - Optimizar solo lo necesario
4. **Readability counts** - Código legible > código micro-optimizado
5. **Test, test, test** - Cada optimización debe tener tests

---

**Para implementar estas optimizaciones:** Consultar [PLAN_MEJORAS.md](./PLAN_MEJORAS.md)
