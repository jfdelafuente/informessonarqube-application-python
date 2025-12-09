# Arquitectura Actual del Proyecto
## informessonarqube-application-python

**Fecha:** 2025-12-09
**Versión:** Commit `a96efb7`

---

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
3. [Componentes Principales](#componentes-principales)
4. [Flujos de Datos](#flujos-de-datos)
5. [Decisiones de Diseño](#decisiones-de-diseño)
6. [Diagramas](#diagramas)

---

## Visión General

### Patrón Arquitectónico

**ETL (Extract-Transform-Load)** con arquitectura en capas:

```
┌─────────────────────────────────────────────────────────┐
│                  Capa de Presentación                   │
│              (Archivos CSV/Excel, Logs)                 │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│                Capa de Orquestación                     │
│         (main_etl_sonar.py, main_etl_gitlab.py)        │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│                  Capa de Negocio (ETL)                  │
│         Extract → Transform → Load (src/etl/)           │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│               Capa de Integración (API)                 │
│         (SonarAPIHandler, GitLabAPIHandler)             │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│                Servicios Externos                       │
│           (SonarQube REST API, GitLab API)              │
└─────────────────────────────────────────────────────────┘
```

---

## Arquitectura de Alto Nivel

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     APLICACIÓN ETL                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CONFIGURACIÓN                          │  │
│  │  - configSonar.py                                   │  │
│  │  - configGitlab.py                                  │  │
│  │  - .env (credenciales)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CAPA DE ORQUESTACIÓN                   │  │
│  │  ┌─────────────────┐    ┌──────────────────┐       │  │
│  │  │ main_etl_sonar  │    │ main_etl_gitlab  │       │  │
│  │  │      .py        │    │      .py         │       │  │
│  │  └─────────────────┘    └──────────────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↓                              ↓                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CAPA DE INTEGRACIÓN (API)              │  │
│  │  ┌─────────────────┐    ┌──────────────────┐       │  │
│  │  │ SonarAPIHandler │    │ GitLabAPIHandler │       │  │
│  │  │  (requests)     │    │ (python-gitlab)  │       │  │
│  │  └─────────────────┘    └──────────────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↓                              ↓                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CAPA DE NEGOCIO (ETL)                  │  │
│  │                                                     │  │
│  │  ┌──────────────┐         ┌──────────────┐        │  │
│  │  │ sonar/       │         │ gitlab/      │        │  │
│  │  │ - extract.py │         │ - extract.py │        │  │
│  │  │ - transform  │         │ - transform  │        │  │
│  │  └──────────────┘         └──────────────┘        │  │
│  │                                                     │  │
│  │         ┌─────────────────────┐                    │  │
│  │         │ utils/              │                    │  │
│  │         │ - utils.py (CSV)    │                    │  │
│  │         │ - lastdate.py       │                    │  │
│  │         └─────────────────────┘                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CAPA DE PERSISTENCIA                   │  │
│  │                                                     │  │
│  │  📁 xlsx/SONAR/     📁 xlsx/GITLAB/                │  │
│  │  📁 logs/           📄 last_date.txt                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

         ↕ HTTP/HTTPS                     ↕ HTTP/HTTPS

┌───────────────────┐              ┌───────────────────┐
│  SonarQube API    │              │   GitLab API      │
│  (REST)           │              │   (REST v4)       │
└───────────────────┘              └───────────────────┘
```

---

## Componentes Principales

### 1. Capa de Integración (API)

#### `SonarAPIHandler.py`

**Responsabilidades:**
- Abstracción de la API REST de SonarQube
- Gestión de autenticación (Bearer token)
- Manejo de paginación automática
- Rate limiting y timeouts

**Endpoints implementados:**

| Método | Endpoint | Propósito |
|--------|----------|-----------|
| `get_component()` | `/api/components/search` | Buscar componentes/proyectos |
| `get_project()` | `/api/projects/search` | Buscar proyectos específicos |
| `get_qualitygate_by_project()` | `/api/qualitygates/get_by_project` | Quality Gate de proyecto |
| `get_measures_component()` | `/api/measures/component` | Métricas actuales |
| `get_measures_history()` | `/api/measures/search_history` | Histórico de métricas |
| `get_measures_history_from()` | `/api/measures/search_history` | Histórico incremental |
| `get_project_analyses()` | `/api/project_analyses/search` | Análisis de proyecto |

**Configuración:**
```python
DEFAULT_PAGE_SIZE = 200
DEFAULT_TIMEOUT = 30
METRICS = "alert_status,complexity,duplicated_lines_density,..."
```

**Autenticación:**
```python
headers = {
    'Authorization': f'Bearer {self.token}',
    'Accept': 'application/json'
}
```

#### `GitLabAPIHandler.py`

**Responsabilidades:**
- Wrapper del SDK oficial `python-gitlab`
- Gestión de autenticación (Private Token)
- Acceso a proyectos, commits, tags, pipelines

**Características:**
- Usa iteradores para paginación automática
- Manejo de errores específicos de GitLab
- Filtrado de proyectos por lenguaje

---

### 2. Capa de Negocio (ETL)

#### `etl/sonar/extract.py` (720 líneas)

**Funciones principales:**

##### `extract_proyectos(sonar_handle) -> pd.DataFrame`

Extrae todos los proyectos de SonarQube con paginación.

**Flujo:**
```
1. Inicializar: index=1, total=5000 (estimación)
2. Loop de paginación:
   a. Llamar get_component(qualifiers="TRK", index=index)
   b. Parsear respuesta JSON
   c. Actualizar total con paging.total
   d. Para cada proyecto:
      - Extraer componentes (namespace, tipo, lenguaje)
      - Obtener Quality Gate
      - Agregar a lista project_ids
   e. index++
3. Construir DataFrame con columnas:
   - project, namespace, name, tipo, lenguaje, quality_gate
4. Retornar DataFrame
```

**Problema actual:** Quality Gates se obtienen secuencialmente (N+1 problem)

##### `_extract_historico_columnas_internal()` (140 líneas)

Extrae histórico de métricas en formato columnar.

**Flujo:**
```
Para cada proyecto:
  1. Inicializar paginación (index=1, total=500)
  2. Loop de paginación de métricas:
     a. Llamar get_measures_history[_from](project, index)
     b. Para cada punto en histórico:
        - Crear dict_metrics con datos base del proyecto
        - Para cada métrica en la respuesta:
          * Extraer valor
          * Añadir a dict_metrics[metric_name]
        - Si es el último registro: añadir a metrics_ids
        - Añadir a project_ids
     c. index++
  3. Actualizar barra de progreso
4. Construir 2 DataFrames:
   - df_historico (todos los registros)
   - df_metrics (solo últimos registros)
5. Retornar (df_historico, df_metrics)
```

**Columnas de salida:**
```python
COLUMNS = [
    'project', 'aplicacion', 'name', 'tipo', 'lenguaje', 'date',
    'complexity', 'coverage', 'ncloc', 'duplicated_lines_density',
    'code_smells', 'bugs', 'vulnerabilities', 'sqale_index',
    'sqale_rating', 'sqale_debt_ratio', 'reliability_rating',
    'security_rating', 'alert_status', 'quality_gate'
]
```

##### `extract_analisis(df_projects, sonar_handle) -> pd.DataFrame`

Extrae análisis de versiones de proyectos.

**Flujo:**
```
Para cada proyecto:
  1. Llamar get_project_analyses(project_key)
  2. Parsear respuesta JSON
  3. Para cada análisis:
     - Para cada evento:
       * Si category == "VERSION":
         - Extraer: namespace, name, lenguaje, date, version
         - Añadir a project_ids
  4. Actualizar progreso
5. Construir DataFrame
6. Retornar DataFrame con versiones
```

#### `etl/sonar/transform.py` (90 líneas)

##### `extraer_componentes(project_key: str) -> Dict`

Parsea la clave de proyecto de SonarQube.

**Formato esperado:**
```
"com.empresa.namespace.tipo.lenguaje:nombre"
```

**Ejemplo:**
```python
# Input
"com.orange.webmethods.differential.package:webmethods"

# Output
{
    'namespace': 'webmethods',
    'tipo': 'package',
    'lenguaje': 'differential'
}
```

**Lógica de parsing:**
```
1. Split por ":"
2. Tomar primera parte (antes de ":")
3. Split por "."
4. Tomar últimos 3 elementos [namespace, tipo, lenguaje]
```

##### `eliminar_namespaces(df, namespace_list) -> (DataFrame, int)`

Filtra proyectos excluyendo namespaces específicos.

**Flujo:**
```
1. Para cada namespace en namespace_list:
   - Crear condición: df['namespace'].str.contains(namespace, case=False)
   - Acumular condiciones con OR
2. Invertir condición (~condicion_total)
3. Filtrar DataFrame
4. Retornar (df_filtrado, num_filas_eliminadas)
```

#### `etl/gitlab/extract.py` (226 líneas)

##### `esJava(name: str) -> bool`

Valida si un proyecto es Java o C según su nombre.

**Formato esperado:**
```
"namespace-tipología-lenguaje"
```

**Ejemplo:**
```python
esJava("webmethods-package-java")  # True
esJava("altamena-service-c")       # True
esJava("portal-web-python")        # False
```

##### `extract_proyectos() -> pd.DataFrame`

**Flujo:**
```
1. Conectar a GitLab
2. Obtener lista completa de proyectos (iterator)
3. Para cada proyecto:
   - Si esJava(project.name):
     * Añadir (id, name, id_namespace, namespace, web_url)
4. Construir DataFrame
5. Retornar DataFrame con proyectos Java/C
```

##### `extract_tags(df_project) -> pd.DataFrame`

**Flujo:**
```
Para cada proyecto en df_project:
  1. Obtener objeto proyecto de GitLab
  2. Listar tags: project.tags.list()
  3. Para cada tag:
     - Extraer: tag_name, commit_id, commit_created_at
     - Añadir a lista proyectos
4. Construir DataFrame
5. Eliminar duplicados
6. Retornar DataFrame
```

**Columnas:**
```
id, name, id_namespace, namespace, web_url, tag_name, commit_id, commit_created_at
```

##### `extract_commits(df_project) -> pd.DataFrame`

Similar a `extract_tags()` pero para commits del repositorio.

##### `extract_pipelines(df_project) -> pd.DataFrame`

**Flujo:**
```
Para cada proyecto:
  1. Obtener pipelines: project.pipelines.list()
  2. Para cada pipeline:
     - Obtener detalles completos: project.pipelines.get(id)
     - Si finished_at no es None:
       * Extraer: sha, status, ref, finished_at, id_pipeline, web_url
  3. Manejar errores GitlabListError
4. Construir DataFrame
5. Retornar DataFrame
```

#### `etl/gitlab/transform.py`

##### `transformar_created_at(df) -> pd.DataFrame`

Filtra registros del año actual (2023 en el código).

**Nota:** Año hardcodeado, debería ser dinámico.

##### `eliminar_duplicados(df_tags, df_commits) -> pd.DataFrame`

Elimina commits que ya están presentes como tags.

**Flujo:**
```
1. Encontrar commit_ids presentes en df_tags
2. Filtrar df_commits excluyendo esos commit_ids
3. Retornar df_commits sin duplicados
```

---

### 3. Capa de Utilidades

#### `utils/utils.py`

##### `load_to_csv(targetfile, data_to_load)`

Guarda DataFrame a CSV con configuración estándar.

**Configuración:**
- Separador: `;`
- Encoding: `utf-8`
- Sin índice: `index=False`

##### `extract_from_csv(file_to_process) -> pd.DataFrame`

Lee CSV con separador `;`.

#### `utils/lastdate.py`

##### `leer_last_date(file) -> str`

Lee fecha de última extracción desde archivo.

**Formato:**
```
YYYY-MM-DD HH:MM:SS
```

**Retorna:** String vacío si no existe (primera ejecución).

##### `save_current_date(file)`

Guarda fecha/hora actual en archivo.

##### `nombre_fichero(tipo, fecha) -> str`

Genera nombre de archivo con timestamp.

**Ejemplos:**
```python
nombre_fichero("historico", "")
# → "sonar_salida_historico_etl_tc.csv"

nombre_fichero("historico", "2024-01-15 10:30:45")
# → "sonar_salida_historico_2024_01_15_10_30_45_tc.csv"
```

---

### 4. Capa de Orquestación

#### `main_etl_sonar.py` (291 líneas)

**Responsabilidad:** Orquestar el flujo completo del ETL SonarQube.

**Flujo principal:**
```
1. setup_directories()
   - Crear logs/, xlsx/SONAR/ si no existen

2. Conectar a SonarQube:
   sonar_handler = SonarAPIHandler()

3. PASO 1: extract_projects()
   - Extraer proyectos
   - Guardar sonar_salida_projects_etl_tc.csv

4. PASO 2: clean_projects()
   - Eliminar namespaces excluidos
   - Aplicar filtros configurados

5. PASO 3: extract_history()
   - Leer last_date.txt
   - Si vacío: carga completa
   - Si existe: carga incremental desde fecha
   - Guardar:
     * sonar_salida_historico_[timestamp].csv
     * sonar_salida_measure_etl_tc.csv
   - Actualizar last_date.txt

6. PASO 4 (condicional): extract_analysis()
   - Solo si ONLY_DASHBOARD = True
   - Guardar sonar_salida_project_analisis_etl_tc.csv

7. print_summary()
   - Mostrar duración total
   - Archivos generados
```

**Funciones auxiliares:**
- `print_step()` - Cabecera de paso
- `print_success()` - Mensaje de éxito
- `print_info()` - Mensaje informativo
- `format_duration()` - Formateo de tiempo

#### `main_etl_gitlab.py` (133 líneas)

**Flujo principal:**
```
1. Validar/crear directorios (logs/, xlsx/GITLAB/)

2. Configurar logging

3. Extracción de Proyectos:
   - Si existe gitlab_salida_proyectos.csv:
     * Cargar desde caché local
   - Si no existe:
     * Extraer de GitLab
     * Filtrar namespaces
     * Guardar gitlab_salida_proyectos.csv

4. Extracción de Tags:
   - extract_tags(df_projects)
   - Filtrar por año actual
   - Guardar gitlab_salida_tags.csv

5. Extracción de Commits:
   - extract_commits(df_projects)
   - Filtrar por año actual
   - Guardar gitlab_salida_commits.csv

6. Consolidación:
   - eliminar_duplicados(df_tags, df_commits)
   - Concatenar tags + commits
   - Guardar gitlab_data.xlsx

7. Extracción de Pipelines:
   - extract_pipelines(df_projects)
   - Filtrar por año actual
   - Guardar gitlab_salida_pipelines.csv
```

---

## Flujos de Datos

### Flujo ETL SonarQube (Completo)

```
┌─────────────────────────────────────────────────────────────┐
│                   INICIO ETL SonarQube                      │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Extracción de Proyectos                           │
│  ┌───────────────────────────────────────┐                 │
│  │ SonarQube API                         │                 │
│  │ /api/components/search?qualifiers=TRK │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ Paginación (200 proyectos/página)     │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ - Parsear componentes (namespace/etc) │                 │
│  │ - Obtener Quality Gate (N calls)      │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 sonar_salida_projects_etl_tc.csv                       │
│  Columnas: project, namespace, name, tipo, lenguaje, qg    │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: Limpieza de Datos                                 │
│  ┌───────────────────────────────────────┐                 │
│  │ eliminar_namespaces()                 │                 │
│  │ Filtrar: APLICACIONES_EXCLUIDAS       │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  DataFrame limpio (proyectos válidos)                      │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: Extracción de Histórico y Métricas               │
│  ┌───────────────────────────────────────┐                 │
│  │ Leer last_date.txt                    │                 │
│  │ ¿Existe fecha?                        │                 │
│  │  NO → Carga COMPLETA                  │                 │
│  │  SÍ → Carga INCREMENTAL (desde fecha) │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ Loop paginación de histórico:         │                 │
│  │ - get_measures_history[_from]()       │                 │
│  │ - Extraer todas las métricas          │                 │
│  │ - Formatear en columnas               │                 │
│  │ - Identificar última métrica          │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 sonar_salida_historico_[timestamp].csv                 │
│  📄 sonar_salida_measure_etl_tc.csv                        │
│  📄 last_date.txt (actualizado)                            │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 4: Extracción de Análisis (OPCIONAL)                │
│  ┌───────────────────────────────────────┐                 │
│  │ if ONLY_DASHBOARD == True:            │                 │
│  │   extract_analisis()                  │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ - get_project_analyses()              │                 │
│  │ - Buscar eventos VERSION              │                 │
│  │ - Extraer versiones                   │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 sonar_salida_project_analisis_etl_tc.csv               │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FIN ETL SonarQube                        │
│  Archivos generados:                                       │
│  - sonar_salida_projects_etl_tc.csv                        │
│  - sonar_salida_measure_etl_tc.csv                         │
│  - sonar_salida_historico_[timestamp].csv                  │
│  - sonar_salida_project_analisis_etl_tc.csv (opcional)     │
└─────────────────────────────────────────────────────────────┘
```

### Flujo ETL GitLab (Completo)

```
┌─────────────────────────────────────────────────────────────┐
│                    INICIO ETL GitLab                        │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Extracción de Proyectos                                   │
│  ┌───────────────────────────────────────┐                 │
│  │ ¿Existe gitlab_salida_proyectos.csv?  │                 │
│  │  SÍ → Cargar desde caché local        │                 │
│  │  NO → Extraer de GitLab API           │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ GitLab API: projects.list(iterator)   │                 │
│  │ Filtrar: esJava(project.name)         │                 │
│  │ → Solo proyectos *-java o *-c         │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ eliminar_namespaces()                 │                 │
│  │ (filtrado adicional)                  │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 gitlab_salida_proyectos.csv                            │
│  Columnas: id, name, id_namespace, namespace, web_url      │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Extracción de Tags                                        │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ - project.tags.list()                 │                 │
│  │ - Extraer tag_name, commit_id, fecha  │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ transformar_created_at()              │                 │
│  │ → Filtrar año 2023                    │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 gitlab_salida_tags.csv                                 │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Extracción de Commits                                     │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ - project.commits.list()              │                 │
│  │ - Extraer short_id, created_at        │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ transformar_created_at()              │                 │
│  │ → Filtrar año 2023                    │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 gitlab_salida_commits.csv                              │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Consolidación (Tags + Commits)                            │
│  ┌───────────────────────────────────────┐                 │
│  │ eliminar_duplicados(tags, commits)    │                 │
│  │ → Quitar commits que son tags         │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ pd.concat([df_tags, df_commits])      │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📊 gitlab_data.xlsx                                       │
│  (archivo consolidado Excel)                               │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Extracción de Pipelines                                   │
│  ┌───────────────────────────────────────┐                 │
│  │ Para cada proyecto:                   │                 │
│  │ - project.pipelines.list()            │                 │
│  │ - Para cada pipeline:                 │                 │
│  │   * project.pipelines.get(id)         │                 │
│  │   * Si finished_at != None: extraer   │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  ┌───────────────────────────────────────┐                 │
│  │ transformar_created_at()              │                 │
│  │ → Filtrar año 2023                    │                 │
│  └───────────────────────────────────────┘                 │
│                   ▼                                         │
│  📄 gitlab_salida_pipelines.csv                            │
│  Columnas: sha, status, ref, finished_at, id, web_url      │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     FIN ETL GitLab                          │
│  Archivos generados:                                       │
│  - gitlab_salida_proyectos.csv                             │
│  - gitlab_salida_tags.csv                                  │
│  - gitlab_salida_commits.csv                               │
│  - gitlab_salida_pipelines.csv                             │
│  - gitlab_data.xlsx (consolidado)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Decisiones de Diseño

### 1. Arquitectura ETL en Capas

**Decisión:** Separar en capas (API, ETL, Utils, Orquestación)

**Justificación:**
- Separación de responsabilidades
- Facilita testing (mock de APIs)
- Permite reutilización de componentes

**Trade-off:**
- Más archivos y estructura
- Requiere navegación entre módulos

### 2. DataFrames de Pandas como Estructura Central

**Decisión:** Usar pandas.DataFrame para toda la manipulación de datos

**Justificación:**
- Operaciones vectorizadas eficientes
- API rica para transformaciones
- Integración nativa con CSV/Excel
- Familiaridad del equipo

**Trade-off:**
- Alto consumo de memoria para grandes datasets
- No es thread-safe

### 3. Paginación Manual en APIs

**Decisión:** Implementar paginación manual con loops

**Justificación:**
- Control fino sobre cada página
- Permite progress bars
- Manejo de errores por página

**Trade-off:**
- Código más verboso
- Más propenso a bugs (off-by-one)

### 4. Formato CSV con Separador `;`

**Decisión:** Usar `;` en lugar de `,` como separador

**Justificación:**
- Evita conflictos con datos que contienen comas
- Compatible con Excel europeo
- Estándar en algunos países

**Trade-off:**
- Menos estándar que `,`
- Requiere especificar separador al leer

### 5. Carga Incremental con `last_date.txt`

**Decisión:** Archivo de texto simple para tracking

**Justificación:**
- Simplicidad extrema
- No requiere base de datos
- Fácil de leer/editar manualmente

**Trade-off:**
- No thread-safe
- No guarda estado por proyecto (solo global)
- Pérdida de datos si se borra

### 6. Configuración con Archivos Python

**Decisión:** `configSonar.py`, `configGitlab.py` como archivos `.py`

**Justificación:**
- Permite comentarios explicativos
- Sintaxis familiar (Python)
- Importación directa

**Trade-off:**
- No es JSON/YAML estándar
- Difícil de editar por no-programadores
- Puede ejecutar código arbitrario (riesgo)

### 7. Modo `ONLY_DASHBOARD` para Control de Alcance

**Decisión:** Flag booleano para incluir/excluir extracción de análisis

**Justificación:**
- Control de rendimiento
- Diferentes casos de uso
- Evita extracción innecesaria

**Trade-off:**
- Comportamiento no obvio (nombre poco claro)
- Podría ser más granular

### 8. Logging a Archivos + Print en Terminal

**Decisión:** Dual output (archivos de log + stdout con colores)

**Justificación:**
- Experiencia de usuario visual en terminal
- Auditoría con logs persistentes
- Debugging facilitado

**Trade-off:**
- Duplicación de lógica
- Overhead de I/O

### 9. Sin Base de Datos, Solo Archivos

**Decisión:** No usar base de datos, solo CSV/Excel

**Justificación:**
- Simplicidad de deployment
- Portabilidad de datos
- No requiere servidor DB

**Trade-off:**
- No permite queries complejas
- Performance limitado con grandes volúmenes
- Sin ACID transactions

### 10. Procesamiento Secuencial (Sin Concurrencia)

**Decisión:** Procesar proyectos uno por uno

**Justificación:**
- Simplicidad de implementación
- Fácil de debuggear
- Evita problemas de concurrencia

**Trade-off:**
- **Rendimiento muy subóptimo**
- No aprovecha múltiples cores
- Tiempo de ejecución elevado

---

## Diagramas

### Diagrama de Secuencia: Extracción de Proyectos SonarQube

```
Usuario     main_etl_sonar   extract.py    SonarAPIHandler    SonarQube API
  |              |               |                |                  |
  |--run-------->|               |                |                  |
  |              |               |                |                  |
  |              |--extract_proyectos()---------->|                  |
  |              |               |                |                  |
  |              |               |--get_component(page=1)----------->|
  |              |               |                |--200 proyectos-->|
  |              |               |                |<-----------------|
  |              |               |                |                  |
  |              |               |                |                  |
  |              |               |--[loop por cada proyecto]         |
  |              |               |  extraer_componentes()            |
  |              |               |  get_qualitygate_by_project()---->|
  |              |               |                |<-----------------|
  |              |               |                |                  |
  |              |               |--get_component(page=2)----------->|
  |              |               |                |<-----------------|
  |              |               |                |                  |
  |              |               |--[repetir hasta procesar todo]----|
  |              |               |                |                  |
  |              |<-----------DataFrame-----------|                  |
  |              |               |                |                  |
  |              |--load_to_csv()                 |                  |
  |              |               |                |                  |
  |<--Archivo CSV--|            |                |                  |
```

### Diagrama de Clases Simplificado

```
┌─────────────────────────┐
│   SonarAPIHandler       │
├─────────────────────────┤
│ - _host: str            │
│ - token: str            │
│ - _timeout: int         │
├─────────────────────────┤
│ + get_component()       │
│ + get_measures_history()│
│ + get_project_analyses()│
│ + get_qualitygate_...() │
└─────────────────────────┘
           ▲
           │ usa
           │
┌─────────────────────────┐
│   extract (módulo)      │
├─────────────────────────┤
│ + extract_proyectos()   │
│ + extract_historico_...()│
│ + extract_analisis()    │
└─────────────────────────┘
           ▲
           │ importa
           │
┌─────────────────────────┐
│   transform (módulo)    │
├─────────────────────────┤
│ + extraer_componentes() │
│ + eliminar_namespaces() │
└─────────────────────────┘
           ▲
           │ usa
           │
┌─────────────────────────┐
│   main_etl_sonar        │
├─────────────────────────┤
│ + extract_projects()    │
│ + clean_projects()      │
│ + extract_history()     │
│ + extract_analysis()    │
│ + main()                │
└─────────────────────────┘
```

---

**Fin del Documento de Arquitectura Actual**

Para continuar con las propuestas de mejora, consultar: [PLAN_MEJORAS.md](./PLAN_MEJORAS.md)
