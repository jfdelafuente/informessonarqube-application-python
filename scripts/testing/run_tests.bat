@echo off
REM Script para ejecutar tests en Windows
REM Uso: run_tests.bat [opcion]
REM   sin opcion: ejecuta todos los tests
REM   unit: solo tests unitarios
REM   integration: solo tests de integracion
REM   coverage: tests con reporte de cobertura

echo ========================================
echo   ETL SonarQube - Test Runner
echo ========================================
echo.

REM Verificar que el entorno virtual está activado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    echo Asegurate de activar el entorno virtual:
    echo   venv\Scripts\activate
    exit /b 1
)

if "%1"=="unit" (
    echo Ejecutando tests unitarios...
    pytest tests/unit/ -v
) else if "%1"=="integration" (
    echo Ejecutando tests de integracion...
    pytest tests/integration/ -v
) else if "%1"=="coverage" (
    echo Ejecutando tests con cobertura...
    pytest --cov=src --cov-report=html --cov-report=term-missing
    echo.
    echo Reporte generado en: htmlcov\index.html
    echo Abriendo reporte...
    start htmlcov\index.html
) else if "%1"=="quick" (
    echo Ejecutando tests rapidos (sin lentos)...
    pytest -v -m "not slow"
) else (
    echo Ejecutando todos los tests...
    pytest -v
)

echo.
echo ========================================
echo Tests completados
echo ========================================
