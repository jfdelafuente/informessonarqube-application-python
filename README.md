# Generacion Informes

Proyecto ETL para extraer métricas de calidad de código desde SonarQube y datos de repositorios desde GitLab.

> **🚀 Inicio Rápido:** Si quieres empezar inmediatamente, lee la [Guía Rápida (QUICKSTART.md)](QUICKSTART.md)

## Requisitos

- Python 3.11+
- Acceso a APIs de SonarQube y GitLab con tokens de autenticación

## Instalación

### 1. Crear Entorno Virtual (Recomendado)

Es altamente recomendable usar un entorno virtual para aislar las dependencias del proyecto:

**En Windows:**

```bash
# Navegar al directorio del proyecto
cd informessonarqube-application-python

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar que estás en el entorno virtual (debe aparecer (venv) en el prompt)
```

**En Linux/Mac:**

```bash
# Navegar al directorio del proyecto
cd informessonarqube-application-python

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar que estás en el entorno virtual (debe aparecer (venv) en el prompt)
```

**Desactivar el entorno virtual:**

```bash
deactivate
```

> **Nota:** El entorno virtual debe estar activado cada vez que trabajes en el proyecto. Si cierras la terminal, necesitarás activarlo nuevamente.

### 2. Instalar Dependencias

Con el entorno virtual activado:

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### Validar Configuración

Después de instalar las dependencias, ejecuta el script de validación para verificar que todo esté correctamente configurado:

```bash
python validate_setup.py
```

Este script verificará:

- ✓ Versión de Python (>= 3.11)
- ✓ Dependencias instaladas
- ✓ Archivo `.env` con variables requeridas
- ✓ Conectividad con SonarQube y GitLab
- ✓ Estructura de directorios
- ✓ Permisos de escritura
- ✓ Archivos de configuración

## Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# SonarQube Configuration
SONAR_DEFAULT_HOST=https://your-sonarqube-instance.com
SONAR_ACCESS_TOKEN=your-sonar-access-token

# GitLab Configuration
GITLAB_DEFAULT_HOST=https://your-gitlab-instance.com
GITLAB_ACCESS_TOKEN=your-gitlab-access-token
```

### Obtener Tokens de Acceso

**SonarQube:**

1. Accede a tu instancia de SonarQube
2. Ve a `My Account > Security > Generate Tokens`
3. Genera un token con permisos de lectura

**GitLab:**

1. Accede a tu instancia de GitLab
2. Ve a `User Settings > Access Tokens`
3. Genera un token con scopes: `read_api`, `read_repository`

> **Nota:** Los directorios `logs/` y `xlsx/SONAR/` y `xlsx/GITLAB/` se crean automáticamente al ejecutar los scripts.

## Uso - ETL SonarQube

### Configuración SonarQube

Edita el fichero [src/configSonar.py](src/configSonar.py) con los siguientes parámetros:

```python
# Namespaces/aplicaciones a excluir del procesamiento
APLICACIONES_EXCLUIDAS = ['tdccicdosp','viveorangeosp','altamenaosp', 'error']

# Modo de extracción
ONLY_DASHBOARD = False  # True = incluye análisis de versiones (más lento)
                        # False = solo métricas de calidad (más rápido)

# Directorios de salida
DIR_SONAR = './'
DIR_SONAR_LOGS = DIR_SONAR + 'logs/'
DIR_SONAR_XLSX = DIR_SONAR + 'xlsx/SONAR/'
```

#### Parámetro ONLY_DASHBOARD

Este parámetro controla el alcance de la extracción:

**Opción 1: `ONLY_DASHBOARD = False` (Por defecto - ✅ Recomendado)**

- ⚡ **Velocidad**: Rápido
- 📁 **Archivos generados**: 2 archivos
  - `sonar_salida_projects_etl_tc.csv` (Proyectos)
  - `sonar_salida_measure_etl_tc.csv` (Métricas/Histórico)
- 🎯 **Uso**: Reportes de calidad de código
- 📊 **Pasos ejecutados**: PASO 1, 2, 3 (omite PASO 4)

**Opción 2: `ONLY_DASHBOARD = True` (Modo completo)**

- 🐌 **Velocidad**: Más lento (consultas adicionales)
- 📁 **Archivos generados**: 3 archivos
  - `sonar_salida_projects_etl_tc.csv` (Proyectos)
  - `sonar_salida_measure_etl_tc.csv` (Métricas/Histórico)
  - `sonar_salida_project_analisis_etl_tc.csv` (Análisis de versiones)
- 🎯 **Uso**: Dashboards con tracking de versiones
- 📊 **Pasos ejecutados**: PASO 1, 2, 3, 4 (todos)

### Ejecutar ETL SonarQube

```bash
python ./src/main_etl_sonar.py
```

### Procesos SonarQube

El script ejecuta los siguientes pasos:

#### PASO 1: Extracción de Proyectos

- Obtiene todos los proyectos de SonarQube con sus propiedades
- Genera: `sonar_salida_projects_etl_tc.csv`

#### PASO 2: Limpieza de Datos

- Elimina proyectos de namespaces excluidos (configurados en `APLICACIONES_EXCLUIDAS`)
- Filtra proyectos inválidos o con errores

#### PASO 3: Extracción de Histórico y Métricas

- Extrae métricas actuales: `sonar_salida_measure_etl_tc.csv`
- Extrae histórico completo o incremental con timestamp
- Soporta carga incremental usando `last_date.txt`
- Genera: `sonar_salida_historico_YYYY-MM-DD_HH-MM-SS.csv`

#### PASO 4: Extracción de Análisis (⚠️ Solo si `ONLY_DASHBOARD = True`)

- Extrae análisis de versiones de proyectos
- Genera: `sonar_salida_project_analisis_etl_tc.csv`
- Este paso se OMITE si `ONLY_DASHBOARD = False`

### Métricas SonarQube

- Calidad de código: `code_smells`, `bugs`, `vulnerabilities`
- Cobertura: `coverage`, `tests`
- Complejidad: `complexity`, `ncloc`
- Deuda técnica: `sqale_index`, `sqale_debt_ratio`
- Ratings: `sqale_rating`, `reliability_rating`, `security_rating`
- Estado: `alert_status`, `quality_gate`

## Uso - ETL GitLab

### Configuración GitLab

Edita el fichero [src/configGitlab.py](src/configGitlab.py) con los siguientes parámetros:

```python
DIR_GITLAB = './'
DIR_GITLAB_LOGS = DIR_GITLAB + 'logs/'
DIR_GITLAB_XLSX = DIR_GITLAB + 'xlsx/GITLAB/'
fich_salida_gitlab = 'gitlab_data.xlsx'
```

### Ejecutar ETL GitLab

```bash
python ./src/main_etl_gitlab.py
```

### Procesos GitLab

El script realizará las siguientes operaciones:

- **Extracción de proyectos**: Filtra proyectos Java y C → `gitlab_salida_proyectos.csv`
- **Extracción de tags**: Obtiene tags de versiones → `gitlab_salida_tags.csv`
- **Extracción de commits**: Obtiene commits del año actual → `gitlab_salida_commits.csv`
- **Consolidación**: Elimina duplicados entre tags y commits → `gitlab_data.xlsx`
- **Extracción de pipelines**: Obtiene estados de CI/CD → `gitlab_salida_pipelines.csv`

### Datos GitLab Extraídos

- **Proyectos**: id, name, namespace, web_url
- **Tags**: tag_name, commit_id, commit_created_at
- **Commits**: short_id, created_at
- **Pipelines**: sha, status, ref, finished_at, web_url (Jenkins)

## Estructura del Proyecto

```text
informessonarqube-application-python/
├── src/                        # Código fuente
│   ├── api/                    # Clientes HTTP para APIs
│   │   ├── SonarAPIHandler.py
│   │   └── GitLabAPIHandler.py
│   ├── etl/                    # Procesos ETL
│   │   ├── sonar/
│   │   │   ├── extract.py
│   │   │   └── transform.py
│   │   └── gitlab/
│   │       ├── extract.py
│   │       └── transform.py
│   ├── utils/                  # Utilidades
│   │   ├── utils.py
│   │   └── lastdate.py
│   ├── configSonar.py          # Configuración SonarQube
│   ├── configGitlab.py         # Configuración GitLab
│   ├── main_etl_sonar.py       # Script principal Sonar
│   └── main_etl_gitlab.py      # Script principal GitLab
├── tests/                      # 🧪 Suite de pruebas
│   ├── unit/                   # Tests unitarios
│   │   ├── test_transform.py
│   │   ├── test_utils.py
│   │   ├── test_lastdate.py
│   │   └── test_sonar_extract.py
│   ├── integration/            # Tests de integración
│   │   ├── test_sonar_api_handler.py
│   │   └── test_extract_pipeline.py
│   ├── fixtures/               # Datos de prueba
│   ├── conftest.py             # Configuración pytest
│   └── README.md               # Documentación de tests
├── .github/                    # 🔄 CI/CD con GitHub Actions
│   └── workflows/
│       ├── tests.yml           # Tests automáticos
│       ├── pr-checks.yml       # Validación de PRs
│       ├── badges.yml          # Generación de badges
│       ├── release.yml         # Releases automáticos
│       ├── maintenance.yml     # Mantenimiento semanal
│       └── README.md           # Documentación de workflows
├── logs/                       # Archivos de log
├── xlsx/                       # Archivos de salida
│   ├── SONAR/
│   └── GITLAB/
├── validate_setup.py           # Script de validación completa
├── test_connection.py          # Script de prueba de conexiones
├── run_tests.bat               # Ejecutar tests (Windows)
├── run_tests.sh                # Ejecutar tests (Linux/Mac)
├── .env                        # Variables de entorno (no en git)
├── .env.example                # Plantilla de variables de entorno
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo/testing
├── pytest.ini                  # Configuración de pytest
├── .coveragerc                 # Configuración de cobertura
└── README.MD                   # Documentación principal
```

## Dependencias del Proyecto

### Paquetes Principales

| Paquete | Versión | Propósito | Uso en el Proyecto |
|---------|---------|-----------|-------------------|
| **pandas** | 2.0.3 | Manipulación de datos | Procesamiento de DataFrames para SonarQube y GitLab |
| **requests** | 2.31.0 | Cliente HTTP | Llamadas a APIs REST de SonarQube |
| **python-gitlab** | 3.15.0 | Cliente GitLab | Interacción con API de GitLab |
| **python-dotenv** | 1.0.0 | Variables de entorno | Carga de credenciales desde `.env` |
| **openpyxl** | 3.1.2 | Excel | Exportación de datos a archivos `.xlsx` |
| **numpy** | 1.24.3 | Computación numérica | Dependencia de pandas |
| **python-dateutil** | 2.8.2 | Manejo de fechas | Parsing y formateo de fechas |
| **platformdirs** | 3.2.0 | Rutas del sistema | Manejo de directorios multiplataforma |

### Dependencias de Desarrollo y Testing

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| **pylint** | 2.17.7 | Linter de código Python |
| **pytest** | 7.4.3 | Framework de testing |
| **pytest-cov** | 4.1.0 | Cobertura de código |
| **pytest-mock** | 3.12.0 | Mocking facilitado |
| **responses** | 0.24.1 | Mock de requests HTTP |

> **Nota:** Para instalar dependencias de desarrollo y testing: `pip install -r requirements-dev.txt`

### Seguridad y Actualizaciones

**Estado de Seguridad:** ✅ Todas las dependencias están actualizadas y sin vulnerabilidades críticas conocidas.

**Última verificación de versiones:**

- `requests==2.31.0` - Incluye parches de seguridad importantes
- `pandas==2.0.3` - Versión moderna con mejoras de rendimiento
- `python-gitlab==3.15.0` - Compatible con APIs modernas de GitLab

**Nota sobre actualizaciones:**

- Las versiones están fijadas (`==`) para garantizar reproducibilidad
- Antes de actualizar, prueba en entorno de desarrollo
- Todas las dependencias son compatibles entre sí

### Instalación de Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar versiones instaladas
pip list

# Verificar dependencias de seguridad (opcional)
pip install pip-audit
pip-audit
```

## Notas Importantes

- Los directorios de salida se crean automáticamente
- La extracción de SonarQube soporta **carga incremental** usando el archivo `last_date.txt`
- Los filtros de namespace se configuran en `configSonar.py`
- GitLab filtra automáticamente por proyectos Java y C (configurable en `etl/gitlab/extract.py`)
- Los logs se guardan en el directorio `logs/` para auditoría

## Scripts de Utilidad

### validate_setup.py

Script completo de validación que verifica toda la configuración del proyecto:

```bash
python validate_setup.py
```

**Verifica:**

- Versión de Python compatible
- Todas las dependencias instaladas
- Archivo `.env` configurado correctamente
- Conectividad con SonarQube y GitLab
- Estructura de directorios
- Permisos de escritura
- Archivos de configuración

### test_connection.py

Script rápido para probar conexiones con las APIs:

```bash
# Probar ambas APIs
python test_connection.py

# Probar solo SonarQube
python test_connection.py sonar

# Probar solo GitLab
python test_connection.py gitlab
```

Este script intenta conectarse y obtener datos de muestra para verificar que las credenciales funcionan.

## Testing

El proyecto incluye una suite completa de tests unitarios y de integración usando **pytest**.

### Configuración de Testing

```bash
# Instalar dependencias de testing
pip install -r requirements-dev.txt
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura de código
pytest --cov=src --cov-report=html

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v

# Ver reporte de cobertura en el navegador
# El reporte se genera en htmlcov/index.html
start htmlcov/index.html  # Windows
```

### Estructura de Tests

- **tests/unit/** - Tests unitarios de funciones individuales
  - `test_transform.py` - Tests de transformación de datos
  - `test_utils.py` - Tests de utilidades CSV
  - `test_lastdate.py` - Tests de manejo de fechas
  - `test_sonar_extract.py` - Tests de funciones auxiliares de extracción

- **tests/integration/** - Tests de integración con APIs
  - `test_sonar_api_handler.py` - Tests del cliente SonarQube
  - `test_extract_pipeline.py` - Tests del pipeline completo de extracción

- **tests/conftest.py** - Fixtures compartidas y configuración pytest

### Cobertura de Código

El proyecto está configurado para mantener una cobertura mínima del 70%:

```bash
# Fallar si cobertura < 70%
pytest --cov=src --cov-fail-under=70
```

📖 **Documentación completa de testing:** Ver [tests/README.md](tests/README.md)

## CI/CD - Integración Continua

El proyecto incluye workflows de GitHub Actions para automatizar testing, linting y releases.

### Workflows Disponibles

#### 🧪 Tests Automáticos ([tests.yml](.github/workflows/tests.yml))

- **Trigger:** Push y Pull Requests a master/develop
- **Ejecuta:** Tests en Python 3.9, 3.10, 3.11
- **Incluye:** Linting, seguridad, cobertura
- **Reportes:** Codecov, artefactos HTML

#### ✅ Validación de PRs ([pr-checks.yml](.github/workflows/pr-checks.yml))

- **Trigger:** Apertura/actualización de Pull Requests
- **Verifica:** Cobertura, tests para código nuevo, tamaño del PR
- **Alerta:** Falta de documentación o tests

#### 📊 Badges ([badges.yml](.github/workflows/badges.yml))

- **Trigger:** Push a master
- **Genera:** Badges de cobertura y cantidad de tests

#### 🚀 Releases ([release.yml](.github/workflows/release.yml))

- **Trigger:** Tags v*.*.* o manual
- **Crea:** Release automático con changelog

#### 🔧 Mantenimiento ([maintenance.yml](.github/workflows/maintenance.yml))

- **Trigger:** Semanal (lunes 3AM UTC)
- **Ejecuta:** Auditoría de dependencias, métricas de código

### Ejecutar Localmente

```bash
# Windows
run_tests.bat            # Todos los tests
run_tests.bat unit       # Solo unitarios
run_tests.bat coverage   # Con reporte de cobertura

# Linux/Mac
./run_tests.sh            # Todos los tests
./run_tests.sh unit       # Solo unitarios
./run_tests.sh coverage   # Con reporte de cobertura
```

### Estado de los Workflows

Los workflows se ejecutan automáticamente en cada push y PR. Ver estado en la pestaña "Actions" de GitHub.

📖 **Documentación completa de CI/CD:** Ver [.github/workflows/README.md](.github/workflows/README.md)

## Troubleshooting

### Entorno Virtual

**El entorno virtual no se activa:**

Windows:

```bash
# Si hay error de permisos de ejecución
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego activar
venv\Scripts\activate
```

Linux/Mac:

```bash
# Asegurar permisos correctos
chmod +x venv/bin/activate

# Activar
source venv/bin/activate
```

**Cómo verificar que el entorno virtual está activo:**

- El prompt de tu terminal debe mostrar `(venv)` al inicio
- Ejecutar `python validate_setup.py` debería confirmar que estás en un entorno virtual

**Recrear entorno virtual si está corrupto:**

```bash
# Desactivar si está activo
deactivate

# Eliminar entorno virtual existente
# Windows:
rmdir /s venv
# Linux/Mac:
rm -rf venv

# Crear nuevo entorno virtual
python -m venv venv

# Activar y reinstalar dependencias
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### Error de autenticación

1. Verifica que las variables `SONAR_ACCESS_TOKEN` y `GITLAB_ACCESS_TOKEN` en `.env` sean correctas
2. Ejecuta `python test_connection.py` para diagnosticar el problema
3. Regenera los tokens si es necesario

### Error de directorios

Los directorios se crean automáticamente. Si persiste el error:

1. Verifica permisos de escritura con `python validate_setup.py`
2. Ejecuta manualmente: `mkdir -p logs xlsx/SONAR xlsx/GITLAB` (Linux/Mac) o `md logs xlsx\SONAR xlsx\GITLAB` (Windows)

### Dependencias faltantes

**Asegúrate de tener el entorno virtual activado**, luego:

```bash
pip install -r requirements.txt
```

Si alguna dependencia falla, verifica con:

```bash
python validate_setup.py
```

**Error "ModuleNotFoundError":**

- Verifica que el entorno virtual esté activado
- Reinstala las dependencias: `pip install -r requirements.txt`

### Problemas de conectividad

Si no puedes conectar con SonarQube o GitLab:

1. Verifica que las URLs en `.env` sean accesibles desde tu red
2. Verifica que no haya firewalls bloqueando las conexiones
3. Usa `python test_connection.py` para diagnóstico detallado

### Errores comunes

**"python: command not found":**

- En Windows, usa `python` o `py`
- En Linux/Mac, usa `python3`

**Conflictos de versiones de paquetes:**

```bash
# Limpiar cache de pip
pip cache purge

# Reinstalar todas las dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```
