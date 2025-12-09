# GitHub Actions Workflows

Este directorio contiene los workflows de CI/CD para el proyecto ETL SonarQube.

## 📋 Workflows Disponibles

### 1. Tests y Calidad de Código (`tests.yml`)

**Trigger:** Push y Pull Request a `master` y `develop`

**Descripción:** Ejecuta la suite completa de tests en múltiples versiones de Python.

**Jobs:**
- **test** - Ejecuta tests unitarios e integración
  - Python 3.9, 3.10, 3.11
  - Tests con cobertura mínima 70%
  - Genera reporte de cobertura
  - Sube cobertura a Codecov
- **lint** - Verificación de calidad de código
  - pylint
  - black (formateo)
  - isort (orden de imports)
- **security** - Análisis de seguridad
  - pip-audit para vulnerabilidades
- **summary** - Resumen de resultados

**Badges:**
```markdown
![Tests](https://github.com/usuario/repo/workflows/Tests%20y%20Calidad%20de%20Código/badge.svg)
```

---

### 2. Pull Request Checks (`pr-checks.yml`)

**Trigger:** Apertura o actualización de Pull Requests

**Descripción:** Validaciones adicionales específicas para PRs.

**Jobs:**
- **pr-info** - Información del PR
  - Autor, commits, archivos cambiados
- **code-quality** - Calidad específica del PR
  - Tests con cobertura
  - Comentario automático con % de cobertura
- **changed-files** - Análisis de cambios
  - Verifica que haya tests para código nuevo
  - Alerta si falta actualizar tests
- **size-check** - Tamaño del PR
  - Alerta si el PR es muy grande (>500 líneas)
- **documentation-check** - Verificación de docs
  - Alerta si falta actualizar README

**Características:**
- ✅ Comentarios automáticos en el PR
- ⚠️ Warnings si falta documentación o tests
- 📊 Estadísticas del PR

---

### 3. Badges (`badges.yml`)

**Trigger:** Push a `master` o manual

**Descripción:** Genera badges dinámicos de estado del proyecto.

**Jobs:**
- **update-badges** - Actualiza badges
  - Badge de cobertura de código
  - Badge de cantidad de tests

**Configuración requerida:**
1. Crear un Gist secreto para almacenar badges
2. Configurar secrets en GitHub:
   - `GIST_SECRET` - Token con permisos de gist
   - `BADGE_GIST_ID` - ID del gist

**Uso:**
```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/USUARIO/GIST_ID/raw/coverage-badge.json)
![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/USUARIO/GIST_ID/raw/tests-badge.json)
```

---

### 4. Release (`release.yml`)

**Trigger:**
- Push de tag `v*.*.*` (ej: v1.0.0)
- Manual con versión especificada

**Descripción:** Automatiza la creación de releases.

**Jobs:**
- **test-before-release** - Tests previos
  - Suite completa de tests
  - Verificación de linting
- **create-release** - Crear release
  - Genera changelog automático
  - Crea release en GitHub
  - Incluye notas de la versión
- **notify-release** - Notificación
  - Confirma release exitoso

**Crear un release:**
```bash
# Crear tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Pushear tag
git push origin v1.0.0

# GitHub Actions automáticamente:
# 1. Ejecuta todos los tests
# 2. Genera changelog
# 3. Crea el release
```

---

### 5. Mantenimiento (`maintenance.yml`)

**Trigger:**
- Semanal (lunes 3:00 AM UTC)
- Manual

**Descripción:** Tareas de mantenimiento automatizadas.

**Jobs:**
- **dependency-check** - Dependencias
  - Lista dependencias desactualizadas
  - Auditoría de seguridad
- **code-metrics** - Métricas de código
  - Complejidad ciclomática
  - Índice de mantenibilidad
  - Conteo de líneas de código
- **stale-check** - Issues antiguos
  - Marca issues inactivos >60 días
  - Marca PRs inactivos >30 días
- **cleanup-artifacts** - Limpieza
  - Elimina artefactos >30 días
  - Mantiene los 5 más recientes

---

## 🚀 Configuración Inicial

### 1. Activar GitHub Actions

En tu repositorio de GitHub:
1. Ve a **Settings** → **Actions** → **General**
2. En "Actions permissions", selecciona "Allow all actions and reusable workflows"
3. Guarda los cambios

### 2. Configurar Secrets (Opcional)

Para badges y notificaciones:

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Agrega los siguientes secrets:

| Secret | Descripción | Requerido |
|--------|-------------|-----------|
| `GIST_SECRET` | Token para actualizar badges | Opcional |
| `BADGE_GIST_ID` | ID del gist de badges | Opcional |
| `CODECOV_TOKEN` | Token de Codecov | Opcional |

### 3. Crear Token para Badges

```bash
# 1. Ve a GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token (classic)
# 3. Selecciona scope: gist
# 4. Copia el token y agrégalo como GIST_SECRET

# 5. Crea un gist público
# 6. Copia el ID del gist (último segmento de la URL)
# 7. Agrégalo como BADGE_GIST_ID
```

---

## 📊 Ver Resultados

### En el Repositorio

1. **Actions Tab**
   - Ve a la pestaña "Actions" en GitHub
   - Ver todos los workflows ejecutados

2. **Commit Status**
   - Cada commit muestra checkmarks verdes/rojos
   - Click en detalles para ver logs

3. **Pull Requests**
   - Checks automáticos en cada PR
   - Comentarios con cobertura de código

### Artefactos Generados

Los workflows generan artefactos que se pueden descargar:

- **coverage-report** - Reporte HTML de cobertura (30 días)
- **test-results** - Resultados detallados de tests

**Descargar:**
1. Ve a Actions → Workflow específico
2. Click en la ejecución
3. Scroll hasta "Artifacts"
4. Download

---

## 🔧 Personalización

### Cambiar Python Versions

Editar `tests.yml`:
```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12']  # Agregar 3.12
```

### Ajustar Cobertura Mínima

Editar `tests.yml`:
```yaml
pytest --cov=src --cov-fail-under=80  # Cambiar de 70 a 80
```

### Modificar Schedule de Mantenimiento

Editar `maintenance.yml`:
```yaml
schedule:
  - cron: '0 3 * * 1'  # Lunes 3AM
  # Cambiar a diario:
  - cron: '0 3 * * *'
```

---

## 🐛 Troubleshooting

### Tests Fallan en CI pero Pasan Localmente

**Posibles causas:**
1. Diferencias de sistema operativo
2. Variables de entorno faltantes
3. Dependencias de versiones

**Solución:**
```yaml
# Agregar variables de entorno en el workflow
env:
  SONAR_DEFAULT_HOST: "https://sonar.test.com"
```

### Workflow No Se Ejecuta

**Verificar:**
1. El archivo YAML está en `.github/workflows/`
2. La sintaxis YAML es correcta (usar yamllint)
3. GitHub Actions está habilitado en el repo

### Permisos Insuficientes

**Error:** "Resource not accessible by integration"

**Solución:**
```yaml
permissions:
  contents: write
  pull-requests: write
```

---

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov](https://about.codecov.io/)

---

## ✅ Checklist de Configuración

- [ ] Activar GitHub Actions en el repositorio
- [ ] Verificar que los workflows se ejecutan correctamente
- [ ] Configurar secrets para badges (opcional)
- [ ] Agregar badges al README principal
- [ ] Configurar protección de branch basada en checks
- [ ] Personalizar triggers según necesidades del equipo
- [ ] Configurar notificaciones (Slack, email, etc.)

---

## 🎯 Mejores Prácticas

1. **Commits pequeños:** Facilita identificar qué cambio rompió los tests
2. **Tests antes de push:** Ejecutar `pytest` localmente primero
3. **Revisar logs:** Si falla, revisar los logs detallados en Actions
4. **Branch protection:** Requiere que pasen los checks antes de merge
5. **Keep workflows DRY:** Usar composite actions para código repetido

---

🤖 **Workflows creados automáticamente por Claude Code**
