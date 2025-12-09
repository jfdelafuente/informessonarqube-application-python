#!/bin/bash
# Script para ejecutar tests en Linux/Mac
# Uso: ./run_tests.sh [opcion]
#   sin opcion: ejecuta todos los tests
#   unit: solo tests unitarios
#   integration: solo tests de integracion
#   coverage: tests con reporte de cobertura

echo "========================================"
echo "  ETL SonarQube - Test Runner"
echo "========================================"
echo ""

# Verificar que el entorno virtual está activado
if ! command -v python &> /dev/null; then
    echo "ERROR: Python no encontrado"
    echo "Asegurate de activar el entorno virtual:"
    echo "  source venv/bin/activate"
    exit 1
fi

case "$1" in
    unit)
        echo "Ejecutando tests unitarios..."
        pytest tests/unit/ -v
        ;;
    integration)
        echo "Ejecutando tests de integracion..."
        pytest tests/integration/ -v
        ;;
    coverage)
        echo "Ejecutando tests con cobertura..."
        pytest --cov=src --cov-report=html --cov-report=term-missing
        echo ""
        echo "Reporte generado en: htmlcov/index.html"

        # Abrir reporte en el navegador
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open htmlcov/index.html 2>/dev/null
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            open htmlcov/index.html
        fi
        ;;
    quick)
        echo "Ejecutando tests rapidos (sin lentos)..."
        pytest -v -m "not slow"
        ;;
    *)
        echo "Ejecutando todos los tests..."
        pytest -v
        ;;
esac

echo ""
echo "========================================"
echo "Tests completados"
echo "========================================"
