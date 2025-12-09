# Flujo de Trabajo con GitHub Issues

**Proyecto:** informessonarqube-application-python
**Fecha:** 2025-12-09
**Propósito:** Guía paso a paso para trabajar con issues, branches y PRs durante el plan de optimización

---

## Índice

1. [Estado Actual](#estado-actual)
2. [Fase 0: Completar Preparación](#fase-0-completar-preparación)
3. [Workflow General por Fase](#workflow-general-por-fase)
4. [Workflow por Issue Individual](#workflow-por-issue-individual)
5. [Comandos Git Útiles](#comandos-git-útiles)
6. [Comandos GitHub CLI](#comandos-github-cli)
7. [Estructura de Commits](#estructura-de-commits)
8. [Resolución de Conflictos](#resolución-de-conflictos)

---

## Estado Actual

### Branch Actual
```
feature/performance-optimization-phase-0
```

### Issues Creados en GitHub
- Labels configurados (bug, performance, phase-0 a phase-4, quick-win, etc.)
- Milestones creados (Fase 0 a Fase 5)
- Issues creados para Fase 1 (ver en GitHub)

### Archivos Importantes
- `docs/FASE_0_PREPARACION.md` - Guía de Fase 0
- `docs/PLAN_MEJORAS.md` - Plan completo de mejoras
- `docs/HALLAZGOS_TECNICOS.md` - Issues técnicos identificados
- `scripts/benchmarking/benchmark_baseline.py` - Script de benchmarking
- `tests/test_regression.py` - Tests de regresión

---

## Fase 0: Completar Preparación

### Paso 1: Ejecutar Benchmark Inicial

```bash
# Instalar dependencias de desarrollo si no lo has hecho
pip install -r requirements-dev.txt

# Ejecutar benchmark (mide rendimiento actual)
python scripts/benchmarking/benchmark_baseline.py

# Esto genera:
# - .benchmark/baseline_YYYY-MM-DD_HH-MM-SS.json
# - docs/PERFORMANCE_BASELINE.md (actualizado)
```

**Resultado esperado:**
```
[BENCHMARK] ETL Performance Baseline Benchmark
============================================================
Target: all
Timestamp: 2025-12-09 10:30:00
============================================================

[OK] Benchmark completed: SonarQube ETL
Duration: 45.23 seconds (0.75 minutes)
Memory increase: 120.45 MB
Peak memory: 345.67 MB

[OK] Benchmark completed: GitLab ETL
Duration: 32.10 seconds (0.54 minutes)
Memory increase: 89.23 MB
Peak memory: 234.56 MB

[OK] Benchmarking Complete
Results saved to:
  - JSON: .benchmark/baseline_2025-12-09_10-30-00.json
  - Docs: docs/PERFORMANCE_BASELINE.md
```

### Paso 2: Ejecutar Tests de Regresión

```bash
# Ejecutar todos los tests
pytest tests/test_regression.py -v

# Solo tests de SonarQube
pytest tests/test_regression.py::TestRegressionSonarETL -v

# Solo tests de GitLab
pytest tests/test_regression.py::TestRegressionGitLabETL -v
```

**Resultado esperado:**
```
tests/test_regression.py::TestRegressionSonarETL::test_projects_output_structure PASSED
tests/test_regression.py::TestRegressionSonarETL::test_projects_data_types PASSED
tests/test_regression.py::TestRegressionGitLabETL::test_gitlab_output_structure PASSED
tests/test_regression.py::TestRegressionGitLabETL::test_gitlab_year_filter FAILED

============================== 1 failed, 5 passed ==============================
```

> **Nota:** Es normal que `test_gitlab_year_filter` falle porque detecta el bug B1 (año hardcodeado). Esto se corregirá en Fase 1.

### Paso 3: Commit y Push de Fase 0

```bash
# Ver cambios pendientes
git status

# Agregar archivos generados (si existen)
git add .benchmark/ tests/fixtures/baseline/ docs/PERFORMANCE_BASELINE.md

# Commit de finalización de Fase 0
git commit -m "feat: completar Fase 0 - baseline y fixtures

- Ejecutar benchmark inicial del ETL
- Generar fixtures de baseline para regresión
- Documentar métricas de rendimiento actual
- Tests de regresión: 5/6 PASS (1 falla esperada: bug B1)

Métricas baseline:
- SonarQube ETL: 45.2s, 120MB memoria
- GitLab ETL: 32.1s, 89MB memoria

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push al branch remoto
git push origin feature/performance-optimization-phase-0
```

### Paso 4: Crear Pull Request de Fase 0

**Opción 1: GitHub CLI**
```bash
gh pr create \
  --title "Fase 0: Preparación y Fundamentos" \
  --body "## Resumen

Establecer baseline y tests de regresión antes de optimizaciones.

## Tareas Completadas

- ✅ Script de benchmarking (`benchmark_baseline.py`)
- ✅ Script de generación de fixtures (`generate_baseline.py`)
- ✅ Tests de regresión (`tests/test_regression.py`)
- ✅ Baseline de rendimiento documentado
- ✅ Fixtures de prueba generados
- ✅ Documentación completa

## Archivos Clave

- \`scripts/benchmarking/benchmark_baseline.py\` - Mide rendimiento
- \`scripts/benchmarking/generate_baseline.py\` - Genera fixtures
- \`tests/test_regression.py\` - Valida integridad post-optimización
- \`docs/FASE_0_PREPARACION.md\` - Documentación completa

## Métricas Baseline

| Proceso | Duración | Memoria | Estado |
|---------|----------|---------|--------|
| SonarQube ETL | 45.2s | 120MB | ✅ |
| GitLab ETL | 32.1s | 89MB | ✅ |

## Tests de Regresión

- ✅ 5/6 tests PASS
- ⚠️ 1 test falla (esperado): detecta bug B1 (año hardcodeado)

## Siguiente Fase

➡️ **Fase 1: Quick Wins** - Optimizaciones de bajo riesgo (30-40% mejora)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)" \
  --base develop
```

**Opción 2: GitHub Web**
1. Ir a: https://github.com/jfdelafuente/informessonarqube-application-python/pulls
2. Click "New pull request"
3. Base: `develop` ← Compare: `feature/performance-optimization-phase-0`
4. Copiar el contenido del body de arriba

### Paso 5: Merge del PR

Una vez revisado y aprobado:

```bash
# Opción 1: Desde GitHub CLI
gh pr merge --squash

# Opción 2: Desde GitHub web
# Click en "Squash and merge"
```

---

## Workflow General por Fase

### 1. Crear Branch para Nueva Fase

```bash
# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear branch para la nueva fase
git checkout -b feature/performance-optimization-phase-1

# Push inicial del branch
git push -u origin feature/performance-optimization-phase-1
```

### 2. Trabajar en los Issues

Ver sección [Workflow por Issue Individual](#workflow-por-issue-individual)

### 3. Finalizar la Fase

```bash
# Asegurarse de que todos los commits están pusheados
git push origin feature/performance-optimization-phase-1

# Crear PR de la fase completa
gh pr create \
  --title "Fase 1: Quick Wins - Optimizaciones de Bajo Riesgo" \
  --body "## Mejoras Implementadas

- ✅ Fix año hardcodeado (#1)
- ✅ Vectorización de operaciones (#2)
- ✅ Reducción de logging (#3)
- ✅ Caché de proyectos (#4)
- ✅ Optimización DataFrames (#5)

## Métricas de Rendimiento

### Antes (Baseline)
- SonarQube: 45.2s, 120MB
- GitLab: 32.1s, 89MB

### Después (Optimizado)
- SonarQube: 29.4s (-35%), 102MB (-15%)
- GitLab: 20.8s (-35%), 75MB (-16%)

**Mejora total: 35% más rápido, 15% menos memoria**

## Tests de Regresión

✅ Todos los tests PASS (6/6)

## Próxima Fase

➡️ **Fase 2: Concurrencia** - Threading y multiprocessing (50-70% mejora total)

---

Closes milestone 'Fase 1: Quick Wins'

🤖 Generated with [Claude Code](https://claude.com/claude-code)" \
  --base develop
```

---

## Workflow por Issue Individual

### 1. Asignar Issue a Ti

**GitHub Web:**
- Ir al issue
- Click "Assignees" → Seleccionarte

**GitHub CLI:**
```bash
gh issue edit 123 --add-assignee @me
```

### 2. Mover a "In Progress" (si usas Project Board)

```bash
# Si tienes project board configurado
gh project item-edit --field-id "Status" --field-value "In Progress" 123
```

### 3. Implementar el Cambio

Ejemplo: Corregir el bug del año hardcodeado (Issue #1)

```bash
# Editar el archivo problemático
# En este caso: src/etl/gitlab/transform.py

# Buscar la línea con el año hardcodeado:
# df = df[df['commit_created_at'].str.contains('2024')]

# Cambiar por:
from datetime import datetime, timedelta

def transformar_created_at(df):
    # Filtrar commits del último año
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    df = df[df['commit_created_at'] >= one_year_ago]
    return df
```

### 4. Re-ejecutar Benchmark

```bash
# Medir el impacto del cambio
python scripts/benchmarking/benchmark_baseline.py

# Comparar con baseline anterior
# Verificar mejora en rendimiento/memoria
```

### 5. Re-ejecutar Tests de Regresión

```bash
# Asegurarse de que no rompimos nada
pytest tests/test_regression.py -v

# Todos los tests deben pasar (incluido test_gitlab_year_filter)
```

### 6. Commit del Cambio

```bash
git add src/etl/gitlab/transform.py

git commit -m "fix: eliminar año hardcodeado en GitLab transform

- Cambiar filtro estático de 2024 a año dinámico
- Filtrar últimos 12 meses basado en fecha actual
- Permite procesar datos de cualquier año

Impacto:
- Funcionalidad: ✅ Corrige bug B1
- Tests de regresión: ✅ 6/6 PASS
- Rendimiento: Sin cambios (0%)

Fixes #1

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

> **Importante:** `Fixes #1` cierra automáticamente el issue cuando se mergea el PR.

### 7. Push del Commit

```bash
git push origin feature/performance-optimization-phase-1
```

### 8. Verificar Issue Cerrado

Si hiciste un commit directo a develop con `Fixes #1`, el issue se cierra automáticamente.

Si trabajas en un branch:
- El issue se cierra cuando se mergea el PR a develop

---

## Comandos Git Útiles

### Ver Estado del Repositorio

```bash
# Ver branch actual y cambios
git status

# Ver historial de commits
git log --oneline --graph --all --decorate

# Ver cambios no commiteados
git diff

# Ver cambios en staging
git diff --staged
```

### Gestión de Branches

```bash
# Listar todos los branches
git branch -a

# Cambiar de branch
git checkout develop

# Crear y cambiar a nuevo branch
git checkout -b feature/nueva-funcionalidad

# Eliminar branch local
git branch -d feature/branch-viejo

# Eliminar branch remoto
git push origin --delete feature/branch-viejo
```

### Sincronizar con Remoto

```bash
# Traer cambios de develop sin merge
git fetch origin develop

# Actualizar develop local
git checkout develop
git pull origin develop

# Rebase tu branch sobre develop actualizado
git checkout feature/performance-optimization-phase-1
git rebase develop
```

### Deshacer Cambios

```bash
# Descartar cambios en archivo no commiteado
git checkout -- archivo.py

# Descartar todos los cambios no commiteados
git reset --hard

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer último commit (descartar cambios)
git reset --hard HEAD~1

# Revertir un commit ya pusheado (crea nuevo commit)
git revert abc123
```

---

## Comandos GitHub CLI

### Issues

```bash
# Listar todos los issues
gh issue list

# Listar issues de un milestone
gh issue list --milestone "Fase 1: Quick Wins"

# Listar issues con un label
gh issue list --label "quick-win"

# Ver detalles de un issue
gh issue view 123

# Cerrar un issue
gh issue close 123 --comment "Implementado en commit abc123"

# Reabrir un issue
gh issue reopen 123

# Asignar issue a ti
gh issue edit 123 --add-assignee @me
```

### Pull Requests

```bash
# Listar PRs
gh pr list

# Ver estado de tus PRs
gh pr status

# Ver detalles de un PR
gh pr view 456

# Ver diff de un PR
gh pr diff 456

# Hacer checkout de un PR para revisarlo
gh pr checkout 456

# Aprobar un PR
gh pr review 456 --approve

# Mergear un PR
gh pr merge 456 --squash

# Ver checks de CI/CD
gh pr checks 456
```

### Repositorio

```bash
# Ver información del repo
gh repo view

# Abrir repo en navegador
gh repo view --web

# Clonar un repo
gh repo clone jfdelafuente/informessonarqube-application-python
```

---

## Estructura de Commits

### Formato de Commits Convencionales

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types Comunes

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `perf`: Mejora de rendimiento
- `refactor`: Refactorización de código
- `docs`: Cambios en documentación
- `test`: Añadir/modificar tests
- `chore`: Tareas de mantenimiento

### Ejemplos

**Bug fix simple:**
```bash
git commit -m "fix: corregir año hardcodeado en GitLab transform

Fixes #1"
```

**Mejora de rendimiento:**
```bash
git commit -m "perf: vectorizar operaciones en extract.py

- Reemplazar iterrows() por operaciones vectorizadas en pandas
- Mejora de rendimiento: 20%
- Tests de regresión: ✅ PASS

Benchmarks:
- Antes: 45.2s
- Después: 36.1s (-20%)

Closes #2"
```

**Refactorización:**
```bash
git commit -m "refactor: extraer función de caché de proyectos

- Crear módulo utils/cache.py
- Implementar caché con TTL de 24h
- Tests de regresión: ✅ PASS
- Mejora en re-ejecuciones: 50%

Closes #4"
```

### Keywords para Cerrar Issues

En el footer del commit:
- `Fixes #123` - Cierra issue #123
- `Closes #123` - Cierra issue #123
- `Resolves #123` - Cierra issue #123

Múltiples issues:
```
Fixes #1, #2, #3
```

---

## Resolución de Conflictos

### Conflictos durante Rebase

```bash
# Iniciar rebase
git rebase develop

# Si hay conflictos:
# 1. Git te mostrará los archivos conflictivos
# 2. Editar archivos y resolver conflictos manualmente
# 3. Agregar archivos resueltos
git add archivo-conflictivo.py

# 4. Continuar rebase
git rebase --continue

# O abortar si algo sale mal
git rebase --abort
```

### Conflictos durante Merge

```bash
# Al hacer merge
git merge develop

# Si hay conflictos:
# 1. Resolver conflictos en archivos
# 2. Agregar archivos resueltos
git add archivo-conflictivo.py

# 3. Completar merge
git commit
```

### Estrategia para Evitar Conflictos

1. **Actualizar develop frecuentemente**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Rebase tu branch regularmente**
   ```bash
   git checkout feature/mi-branch
   git rebase develop
   ```

3. **Commits pequeños y frecuentes**
   - Mejor 10 commits pequeños que 1 commit gigante

4. **Comunicación con el equipo**
   - Avisar si vas a trabajar en archivos sensibles

---

## Checklist por Fase

### ✅ Antes de Empezar Fase

- [ ] Develop está actualizado (`git pull origin develop`)
- [ ] Branch de fase creado (`git checkout -b feature/...`)
- [ ] Issues de la fase revisados en GitHub
- [ ] Milestone de fase creado en GitHub

### ✅ Durante la Fase

- [ ] Cada issue tiene assignee
- [ ] Commits siguen convención (`type: subject`)
- [ ] Tests de regresión pasan después de cada cambio
- [ ] Benchmark ejecutado después de optimizaciones
- [ ] Commits referencian issues (`Fixes #X`)

### ✅ Antes de Crear PR

- [ ] Todos los tests pasan (`pytest tests/`)
- [ ] Benchmark final ejecutado y documentado
- [ ] Todos los commits pusheados
- [ ] Changelog actualizado (si existe)
- [ ] Documentación actualizada

### ✅ Después del Merge

- [ ] Issues cerrados automáticamente
- [ ] Milestone actualizado
- [ ] Branch local eliminado
- [ ] Develop actualizado localmente

---

## Recursos Adicionales

### Documentación del Proyecto

- [README.md](../README.md) - Introducción al proyecto
- [PLAN_MEJORAS.md](PLAN_MEJORAS.md) - Plan completo de optimización
- [FASE_0_PREPARACION.md](FASE_0_PREPARACION.md) - Guía de Fase 0
- [GITHUB_AUTOMATION.md](GITHUB_AUTOMATION.md) - Scripts de automatización
- [DEPENDENCIES.md](../DEPENDENCIES.md) - Gestión de dependencias

### Enlaces Externos

- [GitHub CLI Docs](https://cli.github.com/manual/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Branching Strategy](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)

---

## Troubleshooting

### Problema: "Your branch has diverged"

```bash
# Opción 1: Forzar push (cuidado, sobrescribe remoto)
git push --force-with-lease origin feature/mi-branch

# Opción 2: Rebase y resolver
git fetch origin
git rebase origin/feature/mi-branch
git push origin feature/mi-branch
```

### Problema: "Cannot push to protected branch"

Develop está protegido, debes usar Pull Requests.

```bash
# NO hacer:
git push origin develop

# SÍ hacer:
# 1. Crear branch
# 2. Push al branch
# 3. Crear PR
# 4. Mergear PR desde GitHub
```

### Problema: Issue no se cierra automáticamente

Verifica:
1. Usaste keyword correcto (`Fixes #123`, `Closes #123`)
2. El commit fue mergeado a la branch base (develop)
3. El número de issue es correcto

---

**Última actualización:** 2025-12-09
**Branch actual:** feature/performance-optimization-phase-0
**Siguiente paso:** Completar Fase 0 → PR → Merge → Iniciar Fase 1
