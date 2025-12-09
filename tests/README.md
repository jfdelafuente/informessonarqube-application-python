# Tests - Suite de Pruebas ETL SonarQube

Este directorio contiene la suite completa de tests para el proyecto ETL de SonarQube y GitLab.

## Estructura de Tests

```
tests/
├── unit/                           # Tests unitarios (funciones individuales)
│   ├── test_transform.py          # Tests para transformaciones de datos
│   ├── test_utils.py              # Tests para utilidades CSV
│   ├── test_lastdate.py           # Tests para manejo de fechas
│   └── test_sonar_extract.py      # Tests para funciones auxiliares de extracción
│
├── integration/                    # Tests de integración (APIs, componentes)
│   ├── test_sonar_api_handler.py  # Tests de API SonarQube
│   └── test_extract_pipeline.py   # Tests del pipeline completo de extracción
│
├── fixtures/                       # Datos de prueba (JSON, CSV)
│
└── conftest.py                     # Configuración compartida de pytest
```

## Instalación de Dependencias de Testing

```bash
# Activar entorno virtual
source venv/Scripts/activate  # Windows Git Bash
# o
source venv/bin/activate      # Linux/Mac

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

## Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Tests con cobertura de código
```bash
pytest --cov=src --cov-report=html
```

### Solo tests unitarios
```bash
pytest tests/unit/ -v
```

### Solo tests de integración
```bash
pytest tests/integration/ -v
```

### Tests por archivo específico
```bash
pytest tests/unit/test_transform.py -v
```

### Tests por función específica
```bash
pytest tests/unit/test_transform.py::TestExtraerComponentes::test_formato_estandar_correcto -v
```

### Tests con markers
```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Excluir tests lentos
pytest -m "not slow"
```

### Ejecución paralela (más rápido)
```bash
pytest -n auto
```

## Cobertura de Código

### Generar reporte de cobertura
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

El reporte HTML se genera en `htmlcov/index.html`. Ábrelo en el navegador:

```bash
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Mac
open htmlcov/index.html
```

### Verificar cobertura mínima
```bash
# Fallar si cobertura < 70%
pytest --cov=src --cov-fail-under=70
```

## Tipos de Tests

### 1. Tests Unitarios (unit/)
- Prueban funciones individuales aisladas
- No requieren conexión a APIs externas
- Rápidos de ejecutar (< 0.1s cada uno)
- Usan mocks para dependencias

**Ejemplo:**
```python
def test_extraer_componentes_formato_estandar():
    result = extraer_componentes("com.orange.app.type.lang:name")
    assert result['namespace'] == 'app'
```

### 2. Tests de Integración (integration/)
- Prueban interacción entre componentes
- Usan mocks de APIs externas (responses)
- Más lentos que unitarios (0.1s - 5s)
- Verifican flujos completos

**Ejemplo:**
```python
@responses.activate
def test_get_proyectos():
    responses.add(GET, "https://sonar.test.com/api/...", json={...})
    handler = SonarAPIHandler()
    proyectos = handler.get_proyectos()
    assert len(proyectos) > 0
```

## Fixtures Disponibles

Las fixtures están definidas en `conftest.py` y disponibles para todos los tests:

### Datos de prueba
- `sample_project_keys`: Lista de claves de proyectos
- `sample_project_data`: Datos de proyectos de ejemplo
- `sample_df_projects`: DataFrame con proyectos
- `sample_df_with_namespaces`: DataFrame para tests de filtros

### Archivos temporales
- `temp_output_dir`: Directorio temporal limpiado automáticamente
- `temp_csv_file`: CSV temporal con datos de prueba
- `temp_lastdate_file`: Archivo temporal para fechas

### Configuración
- `mock_env_vars`: Variables de entorno mockeadas
- `mock_sonar_projects_response`: Respuesta API mock

## Buenas Prácticas

### ✅ DO (Hacer)
- Escribir tests para cada función nueva
- Usar nombres descriptivos de tests
- Organizar tests en clases por funcionalidad
- Usar fixtures para evitar duplicación
- Verificar casos extremos (edge cases)
- Mantener cobertura > 70%

### ❌ DON'T (No hacer)
- Tests que dependan de APIs reales en producción
- Tests que modifiquen archivos fuera de tmp_path
- Tests con lógica compleja (los tests deben ser simples)
- Tests que dependan del orden de ejecución
- Hardcodear rutas absolutas

## Añadir Nuevos Tests

### 1. Test Unitario
```python
# tests/unit/test_mi_modulo.py
import pytest
from mi_modulo import mi_funcion

class TestMiFuncion:
    @pytest.mark.unit
    def test_caso_basico(self):
        # Arrange
        entrada = "valor"

        # Act
        resultado = mi_funcion(entrada)

        # Assert
        assert resultado == "esperado"
```

### 2. Test de Integración
```python
# tests/integration/test_mi_api.py
import pytest
import responses

class TestMiAPI:
    @pytest.mark.integration
    @responses.activate
    def test_api_call(self, mock_env_vars):
        # Arrange
        responses.add(GET, "https://api.test/endpoint", json={...})

        # Act
        resultado = mi_api_call()

        # Assert
        assert resultado is not None
```

## Integración Continua (CI/CD)

Para ejecutar tests en CI/CD (GitHub Actions, GitLab CI, etc.):

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Comandos Útiles

```bash
# Ver lista de todos los tests sin ejecutarlos
pytest --collect-only

# Ejecutar solo el primer test que falle
pytest -x

# Modo verboso con prints
pytest -v -s

# Ejecutar tests modificados recientemente
pytest --lf  # last failed
pytest --ff  # failed first

# Generar reporte JUnit (para CI)
pytest --junitxml=report.xml

# Ver duración de tests más lentos
pytest --durations=10
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'src'"
**Solución:** Asegúrate de que `conftest.py` agregue `src/` al path:
```python
sys.path.insert(0, str(PROJECT_ROOT / "src"))
```

### Error: "fixture not found"
**Solución:** Las fixtures deben estar en `conftest.py` o importadas explícitamente.

### Tests pasan localmente pero fallan en CI
**Solución:** Verifica variables de entorno y rutas absolutas vs relativas.

## Recursos Adicionales

- [Documentación pytest](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [responses library](https://github.com/getsentry/responses)
- [Best practices](https://docs.pytest.org/en/latest/goodpractices.html)
