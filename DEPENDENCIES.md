# Gestión de Dependencias

Este proyecto utiliza dos archivos de requisitos para separar dependencias de producción y desarrollo.

---

## Archivos de Requisitos

### requirements.txt

Dependencias **necesarias** para ejecutar el ETL en producción.

**Instalar:**
```bash
pip install -r requirements.txt
```

**Incluye:**
- `numpy`, `pandas` - Procesamiento de datos
- `requests` - Llamadas HTTP a APIs
- `python-gitlab` - Cliente de GitLab API
- `python-dotenv` - Gestión de variables de entorno
- `openpyxl` - Exportación a Excel
- `pylint` - Análisis de código

### requirements-dev.txt

Dependencias **opcionales** para desarrollo, testing y benchmarking.

**Instalar:**
```bash
pip install -r requirements-dev.txt
```

**Incluye:**
- `pytest` - Framework de testing
- `psutil` - Medición de memoria y CPU (benchmarking)
- `pytest-cov` - Cobertura de tests
- `black`, `isort`, `mypy` - Herramientas de calidad de código
- `responses`, `faker` - Utilidades para testing

---

## Instalación Completa

### Desarrollo (recomendado)

Para trabajar en el proyecto con todas las herramientas:

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

### Producción

Solo para ejecutar el ETL:

```bash
pip install -r requirements.txt
```

---

## Uso por Funcionalidad

| Tarea | Comando de Instalación |
|-------|------------------------|
| **Ejecutar ETL** | `pip install -r requirements.txt` |
| **Ejecutar tests** | `pip install -r requirements-dev.txt` |
| **Benchmarking** | `pip install -r requirements-dev.txt` |
| **Desarrollo completo** | `pip install -r requirements.txt requirements-dev.txt` |

---

## Troubleshooting

### Error: psutil requiere Microsoft C++ Build Tools (Windows)

Si encuentras este error al instalar `requirements-dev.txt`:

```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Soluciones:**

1. **Opción 1 (Recomendada)**: Instalar psutil pre-compilado
   ```bash
   pip install psutil --only-binary :all:
   ```

2. **Opción 2**: Instalar Microsoft C++ Build Tools
   - Descargar: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Instalar "Desktop development with C++" workload
   - Luego ejecutar: `pip install -r requirements-dev.txt`

3. **Opción 3**: Omitir benchmarking temporalmente
   - No instalar `requirements-dev.txt`
   - Solo ejecutar el ETL (no podrás hacer benchmarking ni tests)

---

## Notas

- **requirements.txt**: Mínimo necesario para producción
- **requirements-dev.txt**: Herramientas adicionales para desarrollo
- Los scripts de benchmarking (`scripts/benchmarking/`) requieren `psutil`
- Los tests (`tests/`) requieren `pytest`
- Ambos archivos se mantienen sincronizados con las versiones probadas

---

**Última actualización:** 2025-12-09
**Branch:** feature/performance-optimization-phase-0
