#!/bin/bash

# Script para crear issues de GitHub del plan de mejoras
# Requiere: gh CLI (GitHub CLI) instalado y autenticado
# Uso: bash create_issues.sh

set -e

REPO="jfdelafuente/informessonarqube-application-python"

echo "🚀 Creando issues en GitHub para el plan de mejoras..."
echo ""

# ============================================================================
# BUGS CRÍTICOS
# ============================================================================

echo "📌 Creando bug crítico B1..."
gh issue create --repo "$REPO" \
  --title "[BUG CRÍTICO] Año hardcodeado en GitLab transform filtra todos los datos desde 2024" \
  --label "bug,priority:critical,quick-win" \
  --body "## 🔴 Bug Crítico en Producción

**Severidad:** Crítica
**Esfuerzo:** Muy Bajo (5 minutos)
**Prioridad:** URGENTE

### Problema

El archivo \`src/etl/gitlab/transform.py\` tiene el año 2023 hardcodeado, lo que causa que **TODOS los commits/tags sean filtrados desde 2024**.

\`\`\`python
def transformar_created_at(df):
    # 🔴 Año 2023 hardcodeado!
    df = df[df['commit_created_at'].str.contains('2023')]
    return df
\`\`\`

**Ubicación:** \`src/etl/gitlab/transform.py\`

### Impacto

- ❌ ETL GitLab no extrae datos desde 2024
- ❌ Dashboards sin datos del año actual
- ❌ Reportes vacíos o incompletos

### Solución

\`\`\`python
from datetime import datetime

def transformar_created_at(df):
    current_year = str(datetime.now().year)
    df = df[df['commit_created_at'].str.contains(current_year)]
    return df
\`\`\`

### Tareas

- [ ] Modificar \`src/etl/gitlab/transform.py\`
- [ ] Reemplazar año hardcodeado por \`datetime.now().year\`
- [ ] Añadir test para verificar que usa año dinámico
- [ ] Ejecutar ETL GitLab y verificar datos actuales

### Referencias

- Documentación: [docs/HALLAZGOS_TECNICOS.md#b1](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-b1-año-hardcodeado-en-gitlab-transform)
- Plan: [docs/OPTIMIZACION_RENDIMIENTO.md](../blob/develop/docs/OPTIMIZACION_RENDIMIENTO.md#3-fix-bug-año-hardcodeado-1-hora-crítico)

**Tiempo estimado:** 5-10 minutos"

# ============================================================================
# FASE 1: QUICK WINS
# ============================================================================

echo "📌 Creando Fase 1.1 - Vectorización Pandas..."
gh issue create --repo "$REPO" \
  --title "[Performance] Vectorizar operaciones Pandas (20% mejora)" \
  --label "enhancement,performance,phase-1,quick-win" \
  --milestone "Fase 1: Quick Wins" \
  --body "## ⚡ Quick Win - Vectorización Pandas

**Fase:** 1
**Prioridad:** Alta
**Esfuerzo:** Bajo (2 días)
**Impacto:** 20% mejora en rendimiento

### Problema

Uso de \`iterrows()\` que es 10-20x más lento que operaciones vectorizadas.

**Ubicación:** \`src/etl/sonar/extract.py:421\`

\`\`\`python
# ❌ LENTO (ANTI-PATTERN)
for t, row in df_projects.iterrows():
    project_key = row[\"project\"]
    result = extraer_componentes(project_key)
    # ... procesamiento ...
\`\`\`

### Solución

\`\`\`python
# ✅ RÁPIDO (Vectorizado)
df_projects['componentes'] = df_projects['project'].apply(extraer_componentes)
\`\`\`

### Tareas

- [ ] Identificar todos los usos de \`iterrows()\` en el proyecto
- [ ] Refactorizar \`extract_proyectos()\` para usar \`.apply()\`
- [ ] Refactorizar \`_extract_historico_columnas_internal()\`
- [ ] Benchmarking antes/después
- [ ] Tests de regresión

### Archivos Afectados

- \`src/etl/sonar/extract.py\`
- \`src/etl/gitlab/extract.py\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#p2](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-p2-iteración-row-by-row-en-dataframes-crítico)
- [docs/PLAN_MEJORAS.md#11](../blob/develop/docs/PLAN_MEJORAS.md#11-vectorización-de-operaciones-pandas)

**Mejora esperada:** 15-20% más rápido"

echo "📌 Creando Fase 1.2 - Reducción de logging..."
gh issue create --repo "$REPO" \
  --title "[Performance] Reducir logging en bucles críticos (10% mejora)" \
  --label "enhancement,performance,phase-1" \
  --milestone "Fase 1: Quick Wins" \
  --body "## ⚡ Optimización de Logging

**Fase:** 1
**Prioridad:** Media
**Esfuerzo:** Bajo (1 día)
**Impacto:** 5-10% mejora

### Problema

Logging en cada iteración causa overhead I/O innecesario.

**Ubicación:** \`src/etl/sonar/extract.py:433\`

\`\`\`python
# ❌ ANTES: I/O en cada iteración
for t, row in df_projects.iterrows():
    logging.debug(f\"Procesando proyecto {t}/{tratados}\")
    # 1000 proyectos = 1000 escrituras a disco
\`\`\`

### Solución

\`\`\`python
# ✅ DESPUÉS: Log cada N iteraciones
for t, row in df_projects.iterrows():
    if t % 10 == 0:  # Solo cada 10 proyectos
        logging.info(f\"Procesados {t}/{tratados} proyectos\")
    # 1000 proyectos = 100 escrituras (90% reducción)
\`\`\`

### Tareas

- [ ] Identificar bucles con logging en cada iteración
- [ ] Implementar logging condicional (cada 10 o 50 iteraciones)
- [ ] Usar nivel INFO en lugar de DEBUG
- [ ] Medir impacto en I/O

### Archivos Afectados

- \`src/etl/sonar/extract.py\`
- \`src/etl/gitlab/extract.py\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#p5](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-p5-logging-excesivo-en-bucles-menor)

**Mejora esperada:** 5-10% en operaciones I/O intensivas"

echo "📌 Creando Fase 1.3 - Optimización DataFrames..."
gh issue create --repo "$REPO" \
  --title "[Performance] Optimizar construcción de DataFrames (10-15% mejora)" \
  --label "enhancement,performance,phase-1" \
  --milestone "Fase 1: Quick Wins" \
  --body "## ⚡ Optimización de Construcción de DataFrames

**Fase:** 1
**Prioridad:** Media
**Esfuerzo:** Bajo (1-2 días)
**Impacto:** 10-15% mejora

### Problema

Acumulación ineficiente de datos antes de crear DataFrame.

\`\`\`python
# ❌ LENTO: Lista de tuplas
project_ids = []
for ...:
    project_ids.append((val1, val2, val3))
df = pd.DataFrame(project_ids, columns=[...])
\`\`\`

### Solución

\`\`\`python
# ✅ RÁPIDO: Dict de listas
data = {'col1': [], 'col2': [], 'col3': []}
for ...:
    data['col1'].append(val1)
    data['col2'].append(val2)
    data['col3'].append(val3)
df = pd.DataFrame(data)
\`\`\`

### Tareas

- [ ] Refactorizar acumulación en \`extract_proyectos()\`
- [ ] Refactorizar acumulación en \`_extract_historico_columnas_internal()\`
- [ ] Aplicar en extractores de GitLab
- [ ] Benchmarking

### Archivos Afectados

- \`src/etl/sonar/extract.py\`
- \`src/etl/gitlab/extract.py\`

### Referencias

- [docs/PLAN_MEJORAS.md#13](../blob/develop/docs/PLAN_MEJORAS.md#13-optimización-de-creación-de-dataframes)

**Mejora esperada:** 10-15% más rápido"

echo "📌 Creando Fase 1.4 - Sistema de caché..."
gh issue create --repo "$REPO" \
  --title "[Performance] Implementar caché de proyectos (50% mejora en dev)" \
  --label "enhancement,performance,phase-1,quick-win" \
  --milestone "Fase 1: Quick Wins" \
  --body "## ⚡ Quick Win - Sistema de Caché

**Fase:** 1
**Prioridad:** Alta
**Esfuerzo:** Bajo (1 día)
**Impacto:** 50-70% mejora en re-ejecuciones

### Problema

Cada ejecución re-extrae TODOS los proyectos, desperdiciando tiempo en desarrollo/testing.

**Ubicación:** \`src/etl/sonar/extract.py:177\`

### Solución

Crear \`src/utils/cache.py\`:

\`\`\`python
import os
import time
import pandas as pd

def extract_proyectos_cached(sonar_handle, cache_hours=24):
    cache_file = '.cache/projects.pkl'

    if os.path.exists(cache_file):
        age_hours = (time.time() - os.path.getmtime(cache_file)) / 3600
        if age_hours < cache_hours:
            return pd.read_pickle(cache_file)

    df = extract_proyectos(sonar_handle)
    os.makedirs('.cache', exist_ok=True)
    df.to_pickle(cache_file)
    return df
\`\`\`

### Tareas

- [ ] Crear módulo \`src/utils/cache.py\`
- [ ] Implementar \`extract_proyectos_cached()\`
- [ ] Añadir flag \`--no-cache\` en scripts principales
- [ ] Actualizar \`.gitignore\` para excluir \`.cache/\`
- [ ] Documentar uso en README
- [ ] Tests

### Configuración

- TTL por defecto: 24 horas
- Ubicación: \`.cache/projects.pkl\`
- Invalidación: Automática por TTL o flag \`--no-cache\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#p3](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-p3-sin-caché-de-proyectos-moderado)
- [docs/PLAN_MEJORAS.md#14](../blob/develop/docs/PLAN_MEJORAS.md#14-caché-de-extracción-de-proyectos)

**Mejora esperada:** 50-70% en re-ejecuciones de desarrollo"

# ============================================================================
# FASE 2: CONCURRENCIA
# ============================================================================

echo "📌 Creando Fase 2.1 - Llamadas API concurrentes..."
gh issue create --repo "$REPO" \
  --title "[Performance] Implementar llamadas API concurrentes con ThreadPoolExecutor (60-80% mejora)" \
  --label "enhancement,performance,phase-2" \
  --milestone "Fase 2: Concurrencia" \
  --body "## 🚀 Llamadas API Concurrentes

**Fase:** 2
**Prioridad:** Crítica
**Esfuerzo:** Medio (3-4 días)
**Impacto:** 60-80% mejora en extracción de proyectos

### Problema

Llamadas API secuenciales desperdician 70% del tiempo potencial (N+1 problem).

**Ubicación:** \`src/etl/sonar/extract.py:206\`

\`\`\`python
# ❌ SECUENCIAL: 1000 proyectos × 2s = 2000s (33 minutos)
for project in projects:
    qg = sonar_handle.get_qualitygate_by_project(project['key'])
\`\`\`

### Solución

Crear \`src/utils/concurrent.py\`:

\`\`\`python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_quality_gates_parallel(sonar_handle, project_keys, max_workers=10):
    def fetch_one(pk):
        try:
            response = sonar_handle.get_qualitygate_by_project(pk)
            return pk, response.json()[\"qualityGate\"][\"name\"]
        except Exception as e:
            logging.error(f\"Error QG {pk}: {e}\")
            return pk, \"ERROR\"

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, pk): pk for pk in project_keys}
        for future in as_completed(futures):
            pk, qg = future.result()
            results[pk] = qg

    return results
\`\`\`

### Tareas

- [ ] Crear módulo \`src/utils/concurrent.py\`
- [ ] Implementar \`fetch_quality_gates_parallel()\`
- [ ] Refactorizar \`extract_proyectos()\` para usar ThreadPoolExecutor
- [ ] Añadir configuración \`MAX_API_WORKERS\` en configSonar.py
- [ ] Implementar rate limiting para respetar límites de API
- [ ] Tests con mocks
- [ ] Benchmarking antes/después

### Configuración

\`\`\`python
# configSonar.py
MAX_CONCURRENT_API_CALLS = 10  # Ajustar según límites API
\`\`\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#p1](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-p1-llamadas-api-secuenciales-crítico)
- [docs/PLAN_MEJORAS.md#21](../blob/develop/docs/PLAN_MEJORAS.md#21-llamadas-api-concurrentes-con-threadpoolexecutor)
- [docs/OPTIMIZACION_RENDIMIENTO.md](../blob/develop/docs/OPTIMIZACION_RENDIMIENTO.md#1-concurrencia-con-threadpoolexecutor)

**Mejora esperada:** 60-80% más rápido (33min → 7min para 1000 proyectos)"

echo "📌 Creando Fase 2.2 - Procesamiento paralelo..."
gh issue create --repo "$REPO" \
  --title "[Performance] Implementar procesamiento paralelo con multiprocessing (50-70% mejora)" \
  --label "enhancement,performance,phase-2" \
  --milestone "Fase 2: Concurrencia" \
  --body "## 🚀 Procesamiento Paralelo Multi-Core

**Fase:** 2
**Prioridad:** Alta
**Esfuerzo:** Alto (4-5 días)
**Impacto:** 50-70% mejora en máquinas multi-core

### Problema

Procesamiento secuencial no aprovecha múltiples cores de CPU.

**Ubicación:** \`src/etl/sonar/extract.py:392\`

### Solución

\`\`\`python
from multiprocessing import Pool, cpu_count

def process_project_history_worker(args):
    project_data, sonar_config, date_from = args
    sonar_handle = SonarAPIHandler()
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
\`\`\`

### Tareas

- [ ] Crear función \`extract_project_measures()\` independiente y picklable
- [ ] Implementar \`extract_historico_parallel()\`
- [ ] Añadir progress bar con \`tqdm\`
- [ ] Configurar número de workers desde configSonar.py
- [ ] Gestionar tokens de API en procesos hijos
- [ ] Tests
- [ ] Benchmarking en máquinas con diferentes núcleos

### Consideraciones

- Solo efectivo en máquinas con 4+ cores
- Requiere que las funciones sean picklable (sin closures)
- Mayor consumo de memoria (un handler por proceso)

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#p4](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-p4-ausencia-de-paralelización-multi-proceso-moderado)
- [docs/PLAN_MEJORAS.md#22](../blob/develop/docs/PLAN_MEJORAS.md#22-procesamiento-paralelo-de-históricos)

**Mejora esperada:** 50-70% en máquinas multi-core (8+ cores)"

# ============================================================================
# FASE 3: MANTENIBILIDAD
# ============================================================================

echo "📌 Creando Fase 3.1 - Refactorización código duplicado..."
gh issue create --repo "$REPO" \
  --title "[Refactor] Eliminar código duplicado en extractores (40% reducción)" \
  --label "refactor,tech-debt,phase-3" \
  --milestone "Fase 3: Mantenibilidad" \
  --body "## 🧹 Eliminación de Código Duplicado

**Fase:** 3
**Prioridad:** Alta
**Esfuerzo:** Medio (2-3 días)
**Impacto:** Mejora significativa en mantenibilidad

### Problema

Duplicación del 30-40% del código ETL.

**Ubicación:**
- \`src/etl/sonar/extract.py:336-360\` (\`extract_historico_columnas\`)
- \`src/etl/sonar/extract.py:363-389\` (\`extract_historico_columnas_from\`)

\`\`\`python
# ❌ Código duplicado (90% compartido)
def extract_historico_columnas(...):
    return _extract_historico_columnas_internal(..., date_from=None)

def extract_historico_columnas_from(..., date_from):
    return _extract_historico_columnas_internal(..., date_from)
\`\`\`

### Solución

Ya existe función interna compartida. Eliminar wrappers.

\`\`\`python
# ✅ Usar directamente con parámetro opcional
def extract_historico_columnas(df_projects, sonar_handle, date_from=None):
    # ... implementación ...
    pass
\`\`\`

### Tareas

- [ ] Eliminar wrapper \`extract_historico_columnas_from()\`
- [ ] Refactorizar \`extract_historico_columnas()\` con parámetro opcional
- [ ] Actualizar llamadas en \`main_etl_sonar.py\`
- [ ] Crear módulo \`src/etl/common/pagination.py\` con lógica compartida
- [ ] Extraer lógica de paginación reutilizable
- [ ] Tests de regresión

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#m1](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-m1-código-duplicado-crítico-crítico)
- [docs/PLAN_MEJORAS.md#31](../blob/develop/docs/PLAN_MEJORAS.md#31-extracción-de-lógica-común)

**Impacto:** 30-40% reducción en código duplicado"

echo "📌 Creando Fase 3.2 - Separación de responsabilidades..."
gh issue create --repo "$REPO" \
  --title "[Refactor] Dividir funciones largas y separar responsabilidades" \
  --label "refactor,tech-debt,phase-3" \
  --milestone "Fase 3: Mantenibilidad" \
  --body "## 🧹 Separación de Responsabilidades (SOLID)

**Fase:** 3
**Prioridad:** Alta
**Esfuerzo:** Alto (5-6 días)
**Impacto:** Testabilidad++, Mantenibilidad++

### Problema

Funciones de 140+ líneas mezclando extracción, transformación y validación.

**Ubicación:** \`src/etl/sonar/extract.py:392\` (\`_extract_historico_columnas_internal\`)

### Solución

Crear clases especializadas:

\`\`\`python
# src/etl/sonar/extractors.py
class ProjectExtractor:
    def fetch_all_projects(self) -> List[Dict]:
        \"\"\"Solo extrae datos RAW\"\"\"
        pass

# src/etl/sonar/transformers.py
class ProjectTransformer:
    def parse_components(self, raw_projects: List[Dict]) -> pd.DataFrame:
        \"\"\"Solo transformaciones\"\"\"
        pass
\`\`\`

### Tareas

- [ ] Crear clases \`ProjectExtractor\`, \`MeasureExtractor\`, \`AnalysisExtractor\`
- [ ] Crear clases \`ProjectTransformer\`, \`MeasureTransformer\`
- [ ] Refactorizar \`extract_proyectos()\` usando nuevas clases
- [ ] Refactorizar \`_extract_historico_columnas_internal()\`
- [ ] Dividir funciones en < 50 líneas
- [ ] Tests unitarios para cada clase
- [ ] Documentación

### Meta

- ✅ Todas las funciones < 50 líneas
- ✅ Complejidad ciclomática < 10
- ✅ 100% testeables unitariamente

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#m2](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-m2-funciones-muy-largas-crítico)
- [docs/PLAN_MEJORAS.md#32](../blob/develop/docs/PLAN_MEJORAS.md#32-separación-de-responsabilidades)

**Impacto:** Funciones < 50 líneas, 100% testeables"

echo "📌 Creando Fase 3.3 - Configuración centralizada..."
gh issue create --repo "$REPO" \
  --title "[Refactor] Centralizar configuración en settings.py" \
  --label "refactor,tech-debt,phase-3" \
  --milestone "Fase 3: Mantenibilidad" \
  --body "## 🧹 Configuración Centralizada

**Fase:** 3
**Prioridad:** Media
**Esfuerzo:** Medio (2 días)
**Impacto:** Configuración consistente y tipada

### Problema

Constantes dispersas y contradictorias en múltiples archivos.

\`\`\`python
DEFAULT_PAGE_SIZE = 200  # En SonarAPIHandler.py
DEFAULT_PAGE_SIZE = 100  # En extract.py (¡diferente!)
INITIAL_TOTAL = 5000     # Magic number
\`\`\`

### Solución

Crear \`src/config/settings.py\`:

\`\`\`python
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
\`\`\`

### Tareas

- [ ] Crear \`src/config/settings.py\` con dataclasses
- [ ] Migrar constantes desde configSonar.py, configGitlab.py
- [ ] Actualizar todos los imports
- [ ] Añadir validación de configuración
- [ ] Tests
- [ ] Documentar estructura de configuración

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#m4](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-m4-configuración-dispersa-moderado)
- [docs/PLAN_MEJORAS.md#33](../blob/develop/docs/PLAN_MEJORAS.md#33-configuración-centralizada)

**Impacto:** Configuración centralizada, fácil de testear"

# ============================================================================
# FASE 4: CLARIDAD
# ============================================================================

echo "📌 Creando Fase 4.1 - Type hints completos..."
gh issue create --repo "$REPO" \
  --title "[Clarity] Añadir type hints completos a todos los módulos" \
  --label "documentation,clarity,phase-4" \
  --milestone "Fase 4: Claridad" \
  --body "## 📝 Type Hints Completos

**Fase:** 4
**Prioridad:** Media
**Esfuerzo:** Medio (3-4 días)
**Impacto:** Claridad++, Autocomplete IDE

### Problema

Sin type hints, causando errores solo en runtime.

\`\`\`python
# ❌ Sin tipos
def extract_proyectos(sonar_handle):
    return df_project
\`\`\`

### Solución

\`\`\`python
# ✅ Con tipos completos
from typing import Optional
import pandas as pd

def extract_proyectos(
    sonar_handle: SonarAPIHandler,
    cache_enabled: bool = True
) -> pd.DataFrame:
    \"\"\"
    Extrae todos los proyectos de SonarQube

    Args:
        sonar_handle: Instancia autenticada de SonarAPIHandler
        cache_enabled: Si True, usa caché de proyectos

    Returns:
        DataFrame con columnas: project, namespace, name, tipo, lenguaje, quality_gate

    Raises:
        APIError: Si hay error en comunicación con SonarQube
    \"\"\"
    pass
\`\`\`

### Tareas

- [ ] Añadir type hints a TODAS las funciones públicas
- [ ] Añadir type hints a parámetros y retornos
- [ ] Configurar mypy en pre-commit hooks
- [ ] Configurar mypy strict mode en CI/CD
- [ ] Actualizar docstrings con formato Google/NumPy
- [ ] Fix todos los warnings de mypy

### Configuración mypy

\`\`\`ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
\`\`\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#c1](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-c1-falta-de-type-hints-crítico)
- [docs/PLAN_MEJORAS.md#41](../blob/develop/docs/PLAN_MEJORAS.md#41-type-hints-completos)

**Impacto:** IDE autocomplete, detección errores en desarrollo"

echo "📌 Creando Fase 4.2 - Refactorización de nombres..."
gh issue create --repo "$REPO" \
  --title "[Clarity] Renombrar variables y funciones con nombres descriptivos" \
  --label "refactor,clarity,phase-4" \
  --milestone "Fase 4: Claridad" \
  --body "## 📝 Nombres Descriptivos

**Fase:** 4
**Prioridad:** Media
**Esfuerzo:** Bajo (2 días)
**Impacto:** Código más legible

### Problema

Nombres poco descriptivos dificultan la lectura del código.

\`\`\`python
# ❌ Nombres ambiguos
i, j, t
df_extract
no_tratado
fich_salida_gitlab
acumulado
\`\`\`

### Solución

\`\`\`python
# ✅ Nombres descriptivos
project_index, tag_count, processed_count
df_projects_raw
unprocessed_count
output_file_gitlab
accumulated_metrics_count
\`\`\`

### Tareas

- [ ] Renombrar variables de loop: \`i, j, t\` → descriptivos
- [ ] Estandarizar nombres de DataFrames: \`df_*_raw\`, \`df_*_clean\`
- [ ] Convertir nombres en español a inglés
- [ ] Expandir abreviaciones: \`fich\` → \`file\`, \`proj\` → \`project\`
- [ ] Aplicar convención PEP8 para constantes (UPPER_CASE)
- [ ] Actualizar documentación

### Convenciones

- Variables de loop: \`project_index\`, \`tag_count\`
- DataFrames: \`df_projects_raw\`, \`df_projects_clean\`
- Constantes: \`UPPER_SNAKE_CASE\`
- Funciones: \`lower_snake_case\`
- Clases: \`PascalCase\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#c2](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-c2-nombres-poco-descriptivos-moderado)
- [docs/PLAN_MEJORAS.md#42](../blob/develop/docs/PLAN_MEJORAS.md#42-refactorización-de-nombres)

**Impacto:** Código más legible y profesional"

echo "📌 Creando Fase 4.3 - Documentación de magic numbers..."
gh issue create --repo "$REPO" \
  --title "[Clarity] Documentar magic numbers con constantes nombradas" \
  --label "documentation,clarity,phase-4,quick-win" \
  --milestone "Fase 4: Claridad" \
  --body "## 📝 Documentación de Magic Numbers

**Fase:** 4
**Prioridad:** Baja
**Esfuerzo:** Muy Bajo (1 día)
**Impacto:** Código auto-explicativo

### Problema

Magic numbers sin explicación hacen el código difícil de entender.

\`\`\`python
# ❌ Magic numbers
total = 5000
if seconds < 60:
max_workers = 10
\`\`\`

### Solución

\`\`\`python
# ✅ Constantes nombradas
INITIAL_PAGINATION_ESTIMATE = 5000  # Estimación antes de conocer total real
SECONDS_PER_MINUTE = 60  # Conversión a minutos
DEFAULT_MAX_CONCURRENT_WORKERS = 10  # Balance rendimiento/recursos
\`\`\`

### Tareas

- [ ] Identificar todos los magic numbers
- [ ] Crear constantes nombradas con documentación
- [ ] Mover constantes a \`src/config/settings.py\`
- [ ] Actualizar código para usar constantes

### Ejemplos

\`\`\`python
# src/config/constants.py
INITIAL_PAGINATION_ESTIMATE = 5000
DEFAULT_CACHE_TTL_HOURS = 24
MAX_API_PAGE_SIZE = 200
HTTP_TIMEOUT_SECONDS = 30
\`\`\`

### Referencias

- [docs/HALLAZGOS_TECNICOS.md#c3](../blob/develop/docs/HALLAZGOS_TECNICOS.md#-c3-magic-numbers-sin-explicación-moderado)
- [docs/PLAN_MEJORAS.md#43](../blob/develop/docs/PLAN_MEJORAS.md#43-documentación-de-magic-numbers)

**Impacto:** Lógica auto-explicativa"

# ============================================================================
# FASE 0: PREPARACIÓN
# ============================================================================

echo "📌 Creando Fase 0 - Benchmarking baseline..."
gh issue create --repo "$REPO" \
  --title "[Setup] Establecer baseline de rendimiento y tests de regresión" \
  --label "setup,testing,phase-0" \
  --milestone "Fase 0: Preparación" \
  --body "## 🔬 Fase 0: Preparación y Baseline

**Fase:** 0 (Prerequisito)
**Prioridad:** Alta
**Esfuerzo:** Bajo (1-2 días)
**Impacto:** Fundación para medir mejoras

### Objetivos

1. Establecer baseline de rendimiento actual
2. Crear tests de regresión
3. Documentar arquitectura actual

### Tareas

#### 1. Benchmarking Inicial

- [ ] Crear \`benchmark_baseline.py\` con medición de:
  - Tiempo total ETL SonarQube
  - Tiempo total ETL GitLab
  - Tiempo por fase
  - Uso de memoria pico
  - Número de llamadas API
- [ ] Ejecutar 3 veces y promediar resultados
- [ ] Documentar en \`docs/PERFORMANCE_BASELINE.md\`

#### 2. Tests de Regresión

- [ ] Guardar outputs de referencia en \`tests/fixtures/baseline/\`
- [ ] Crear tests que validen:
  - Formato exacto de CSV generados
  - Cantidad de registros procesados
  - Valores de métricas específicas
- [ ] Configurar en CI para ejecutar en cada PR

#### 3. Documentación

- [x] Crear \`docs/ARQUITECTURA_ACTUAL.md\` ✅
- [x] Crear diagramas de flujo ✅
- [x] Documentar decisiones de diseño ✅

### Script de Benchmarking

\`\`\`python
import time
import psutil
from src.main_etl_sonar import main

def benchmark():
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024

    start = time.time()
    main()
    duration = time.time() - start

    mem_after = process.memory_info().rss / 1024 / 1024

    return {
        'duration_minutes': duration / 60,
        'memory_mb': mem_after,
        'memory_increase_mb': mem_after - mem_before
    }
\`\`\`

### Referencias

- [docs/PLAN_MEJORAS.md#fase-0](../blob/develop/docs/PLAN_MEJORAS.md#fase-0-preparación-y-fundamentos)

**Resultado esperado:** Baseline documentado para comparar mejoras"

# ============================================================================
# RESUMEN
# ============================================================================

echo ""
echo "✅ Issues creados exitosamente!"
echo ""
echo "📊 Resumen:"
echo "  - 1 Bug crítico (B1)"
echo "  - 4 Quick Wins (Fase 1)"
echo "  - 2 Optimizaciones de concurrencia (Fase 2)"
echo "  - 3 Refactorizaciones (Fase 3)"
echo "  - 3 Mejoras de claridad (Fase 4)"
echo "  - 1 Setup inicial (Fase 0)"
echo ""
echo "Total: 14 issues creados"
echo ""
echo "🔗 Ver issues en: https://github.com/$REPO/issues"
echo ""
echo "💡 Próximos pasos:"
echo "  1. Revisar y priorizar issues"
echo "  2. Asignar a developers"
echo "  3. Comenzar con Bug B1 (5 minutos)"
echo "  4. Luego Quick Wins de Fase 1 (1 semana)"
