"""
Create GitHub issues for the performance optimization plan using REST API
Alternative to create_issues.sh that doesn't require gh CLI

Usage:
    python create_issues.py

Requirements:
    pip install requests

    Set GITHUB_TOKEN environment variable with your personal access token
"""

import os
import sys
import requests
from getpass import getpass


def get_github_token():
    """Get GitHub token from environment or prompt user"""
    token = os.environ.get('GITHUB_TOKEN')

    if not token:
        print("\n[WARNING] GITHUB_TOKEN not found in environment variables")
        print("\nYou need a GitHub Personal Access Token with 'repo' scope.")
        print("Create one at: https://github.com/settings/tokens/new")
        print("")
        token = getpass("Enter your GitHub token: ")

    return token.strip()


def get_repo_info():
    """Get repository owner and name from git remote"""
    import subprocess

    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )

        remote_url = result.stdout.strip()

        if 'github.com' in remote_url:
            if remote_url.startswith('https://'):
                parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            else:
                parts = remote_url.split(':')[1].replace('.git', '').split('/')

            if len(parts) >= 2:
                return parts[0], parts[1]

        raise ValueError("Could not parse repository from remote URL")

    except Exception as e:
        print(f"[ERROR] Error getting repository info: {e}")
        owner = input("Repository owner: ").strip()
        repo = input("Repository name: ").strip()
        return owner, repo


def create_issue(token, owner, repo, issue_data):
    """Create an issue in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.post(url, json=issue_data, headers=headers)

    if response.status_code == 201:
        return True, response.json()['html_url']
    else:
        return False, f"Error {response.status_code}: {response.text}"


# Issue definitions
ISSUES = [
    # BUG CRÍTICO
    {
        "title": "[BUG CRÍTICO] Año hardcodeado en GitLab transform filtra todos los datos desde 2024",
        "labels": ["bug", "priority:critical", "quick-win"],
        "body": """## Bug Crítico en Producción

**Severidad:** Crítica
**Esfuerzo:** Muy Bajo (5 minutos)
**Prioridad:** URGENTE

### Problema

El archivo `src/etl/gitlab/transform.py` tiene el año 2023 hardcodeado, lo que causa que **TODOS los commits/tags sean filtrados desde 2024**.

```python
def transformar_created_at(df):
    # Año 2023 hardcodeado!
    df = df[df['commit_created_at'].str.contains('2023')]
    return df
```

**Ubicación:** `src/etl/gitlab/transform.py`

### Impacto

- ETL GitLab no extrae datos desde 2024
- Dashboards sin datos del año actual
- Reportes vacíos o incompletos

### Solución

```python
from datetime import datetime

def transformar_created_at(df):
    current_year = str(datetime.now().year)
    df = df[df['commit_created_at'].str.contains(current_year)]
    return df
```

### Checklist

- [ ] Leer archivo `src/etl/gitlab/transform.py`
- [ ] Reemplazar año hardcodeado por `datetime.now().year`
- [ ] Ejecutar tests de regresión
- [ ] Verificar que ETL GitLab extrae datos 2024

**Refs:** docs/HALLAZGOS_TECNICOS.md (B1)
"""
    },

    # FASE 1: QUICK WINS
    {
        "title": "P2: Vectorizar iterrows() en extract.py (20% mejora)",
        "labels": ["performance", "phase-1", "quick-win"],
        "body": """## Optimización de Rendimiento: Vectorización

**Impacto:** 20% más rápido
**Esfuerzo:** Bajo (2 días)
**Tipo:** Quick Win

### Problema

`src/etl/sonar/extract.py:421` usa `iterrows()` que es 10-20x más lento que operaciones vectorizadas.

```python
# LENTO
for t, row in df_projects.iterrows():
    project_key = row["project"]
    result = extraer_componentes(project_key)
```

### Solución

```python
# RÁPIDO
df_projects['componentes'] = df_projects['project'].apply(extraer_componentes)
```

### Checklist

- [ ] Identificar todos los usos de `iterrows()` en extract.py
- [ ] Reemplazar con `apply()` o vectorización pura
- [ ] Ejecutar benchmark antes/después
- [ ] Validar con tests de regresión

**Refs:** docs/OPTIMIZACION_RENDIMIENTO.md (Ejemplo 2)
"""
    },

    {
        "title": "P5: Reducir logging en bucles (10% mejora)",
        "labels": ["performance", "phase-1", "quick-win"],
        "body": """## Optimización: Reducción de Logging

**Impacto:** 10% más rápido
**Esfuerzo:** Muy Bajo (1 día)
**Tipo:** Quick Win

### Problema

Logging en cada iteración causa overhead I/O innecesario.

```python
# PROBLEMA
for t, row in df_projects.iterrows():
    logging.debug(f"Procesando proyecto {t}/{tratados}")  # 1000+ llamadas I/O
```

### Solución

```python
# SOLUCIÓN
for t, row in df_projects.iterrows():
    if t % 10 == 0:  # Log cada 10 proyectos
        logging.info(f"Procesados {t}/{tratados} proyectos")
```

### Checklist

- [ ] Buscar logging dentro de loops
- [ ] Implementar logging condicional (cada N iteraciones)
- [ ] Cambiar nivel de debug a info donde aplique
- [ ] Medir impacto con benchmark

**Refs:** docs/HALLAZGOS_TECNICOS.md (P5)
"""
    },

    {
        "title": "P3: Implementar caché de proyectos (50% mejora en dev)",
        "labels": ["performance", "phase-1"],
        "body": """## Caché de Proyectos

**Impacto:** 50-70% más rápido en re-ejecuciones
**Esfuerzo:** Bajo (1 día)

### Problema

Cada ejecución re-extrae TODOS los proyectos de SonarQube, aunque raramente cambian.

### Solución

Implementar sistema de caché con TTL de 24 horas:

```python
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
```

### Checklist

- [ ] Crear `src/utils/cache.py`
- [ ] Implementar funciones de caché con TTL
- [ ] Integrar en `extract_proyectos()`
- [ ] Agregar flag `--no-cache` para forzar refresh
- [ ] Documentar uso de caché

**Refs:** docs/PLAN_MEJORAS.md (Fase 1.4)
"""
    },

    {
        "title": "Optimizar construcción de DataFrames (15% mejora)",
        "labels": ["performance", "phase-1"],
        "body": """## Optimización: Construcción de DataFrames

**Impacto:** 15% más rápido
**Esfuerzo:** Bajo (1 día)

### Problema

Construcción ineficiente de DataFrames con lista de tuplas.

```python
# LENTO
project_ids = []
for ...:
    project_ids.append((val1, val2, val3))
df = pd.DataFrame(project_ids, columns=[...])
```

### Solución

```python
# RÁPIDO
data = {'col1': [], 'col2': [], 'col3': []}
for ...:
    data['col1'].append(val1)
    data['col2'].append(val2)
df = pd.DataFrame(data)
```

### Checklist

- [ ] Identificar construcciones de DataFrame ineficientes
- [ ] Reemplazar con diccionarios de listas
- [ ] Benchmark antes/después
- [ ] Validar integridad de datos

**Refs:** docs/PLAN_MEJORAS.md (Fase 1.3)
"""
    },
]


def main():
    print("=" * 70)
    print("Creating GitHub Issues for Performance Optimization Plan")
    print("=" * 70)
    print()

    # Get token
    token = get_github_token()

    # Get repository info
    print("\nDetecting repository...")
    owner, repo = get_repo_info()
    print(f"Repository: {owner}/{repo}")

    # Verify token works
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    test_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(test_url, headers=headers)

    if response.status_code != 200:
        print(f"\n[ERROR] Could not access repository")
        print(f"Status: {response.status_code}")
        sys.exit(1)

    print(f"[OK] Repository access confirmed\n")

    # Create issues
    print(f"Creating {len(ISSUES)} issues...\n")

    created = 0
    errors = 0

    for idx, issue_data in enumerate(ISSUES, 1):
        print(f"[{idx}/{len(ISSUES)}] {issue_data['title'][:60]}...")

        success, result = create_issue(token, owner, repo, issue_data)

        if success:
            print(f"  [OK] Created: {result}")
            created += 1
        else:
            print(f"  [ERROR] {result}")
            errors += 1

    # Summary
    print("\n" + "=" * 70)
    print("GitHub Issues Creation Complete")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  Created: {created}")
    print(f"  Errors: {errors}")
    print(f"\nView issues at: https://github.com/{owner}/{repo}/issues")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
