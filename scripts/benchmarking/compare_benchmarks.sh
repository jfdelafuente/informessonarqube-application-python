#!/bin/bash
#
# Script para comparar dos archivos de benchmark y calcular mejoras
#
# Uso:
#   ./compare_benchmarks.sh <archivo_antes> <archivo_despues>
#
# Ejemplo:
#   ./compare_benchmarks.sh \
#       .benchmark/baseline_2025-12-09_10-00-00.json \
#       .benchmark/baseline_2025-12-10_15-00-00.json
#

set -euo pipefail

# Verificar argumentos
if [ $# -ne 2 ]; then
    echo "Error: Se requieren 2 argumentos"
    echo ""
    echo "Uso: $0 <archivo_antes> <archivo_despues>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 .benchmark/baseline_2025-12-09_10-00-00.json \\"
    echo "     .benchmark/baseline_2025-12-10_15-00-00.json"
    exit 1
fi

BEFORE=$1
AFTER=$2

# Verificar que los archivos existen
if [ ! -f "$BEFORE" ]; then
    echo "Error: Archivo no encontrado: $BEFORE"
    exit 1
fi

if [ ! -f "$AFTER" ]; then
    echo "Error: Archivo no encontrado: $AFTER"
    exit 1
fi

# Verificar que jq está instalado
if ! command -v jq &> /dev/null; then
    echo "Error: jq no está instalado"
    echo "Instalar con: sudo apt-get install jq (Linux) o brew install jq (Mac)"
    exit 1
fi

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${BOLD}  COMPARACIÓN DE BENCHMARKS${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Extraer fechas de los archivos
BEFORE_DATE=$(jq -r '.timestamp' "$BEFORE" | cut -d'T' -f1)
AFTER_DATE=$(jq -r '.timestamp' "$AFTER" | cut -d'T' -f1)

echo -e "${BLUE}Archivos comparados:${NC}"
echo "  Antes:   $BEFORE ($BEFORE_DATE)"
echo "  Después: $AFTER ($AFTER_DATE)"
echo ""

# Extraer información del sistema
echo -e "${BLUE}Sistema:${NC}"
CPU_COUNT=$(jq -r '.system_info.cpu_count' "$BEFORE")
MEMORY_GB=$(jq -r '.system_info.total_memory_gb' "$BEFORE")
echo "  CPU: $CPU_COUNT cores, RAM: $MEMORY_GB GB"
echo ""

# Obtener número de benchmarks
NUM_BENCHMARKS=$(jq '.benchmarks | length' "$BEFORE")

echo "════════════════════════════════════════════════════════════════"

# Iterar sobre cada benchmark
for (( i=0; i<$NUM_BENCHMARKS; i++ )); do
    # Extraer datos del benchmark
    NAME=$(jq -r ".benchmarks[$i].name" "$BEFORE")

    # Tiempo
    TIME_BEFORE=$(jq -r ".benchmarks[$i].duration_minutes" "$BEFORE")
    TIME_AFTER=$(jq -r ".benchmarks[$i].duration_minutes" "$AFTER")

    # Memoria
    MEM_BEFORE=$(jq -r ".benchmarks[$i].memory_increase_mb" "$BEFORE")
    MEM_AFTER=$(jq -r ".benchmarks[$i].memory_increase_mb" "$AFTER")

    echo ""
    echo -e "${BOLD}${BLUE}$NAME${NC}"
    echo "────────────────────────────────────────────────────────────────"

    # Calcular mejora de tiempo
    TIME_IMPROVEMENT=$(echo "scale=2; ($TIME_BEFORE - $TIME_AFTER) / $TIME_BEFORE * 100" | bc)
    TIME_DIFF=$(echo "scale=2; $TIME_BEFORE - $TIME_AFTER" | bc)

    echo -e "${YELLOW}⏱️  Tiempo de Ejecución:${NC}"
    echo "  Antes:   $TIME_BEFORE min"
    echo "  Después: $TIME_AFTER min"
    echo "  Cambio:  $TIME_DIFF min"

    # Color según mejora de tiempo
    if (( $(echo "$TIME_IMPROVEMENT > 0" | bc -l) )); then
        echo -e "  ${GREEN}✅ Mejora:  $TIME_IMPROVEMENT%${NC}"
    elif (( $(echo "$TIME_IMPROVEMENT < 0" | bc -l) )); then
        ABS_IMPROVEMENT=$(echo "$TIME_IMPROVEMENT * -1" | bc)
        echo -e "  ${RED}❌ Regresión: -$ABS_IMPROVEMENT%${NC}"
    else
        echo "  ⚖️  Sin cambio: 0%"
    fi

    echo ""

    # Calcular cambio de memoria
    MEM_CHANGE=$(echo "scale=2; ($MEM_AFTER - $MEM_BEFORE) / $MEM_BEFORE * 100" | bc)
    MEM_DIFF=$(echo "scale=2; $MEM_AFTER - $MEM_BEFORE" | bc)

    echo -e "${YELLOW}💾 Uso de Memoria:${NC}"
    echo "  Antes:   $MEM_BEFORE MB"
    echo "  Después: $MEM_AFTER MB"
    echo "  Cambio:  $MEM_DIFF MB"

    # Color según cambio de memoria (negativo es bueno)
    if (( $(echo "$MEM_CHANGE < 0" | bc -l) )); then
        ABS_CHANGE=$(echo "$MEM_CHANGE * -1" | bc)
        echo -e "  ${GREEN}✅ Reducción: $ABS_CHANGE%${NC}"
    elif (( $(echo "$MEM_CHANGE > 0" | bc -l) )); then
        echo -e "  ${YELLOW}⚠️  Aumento: +$MEM_CHANGE%${NC}"
    else
        echo "  ⚖️  Sin cambio: 0%"
    fi

    echo "────────────────────────────────────────────────────────────────"
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${BOLD}  RESUMEN TOTAL${NC}"
echo "════════════════════════════════════════════════════════════════"

# Calcular totales
TOTAL_TIME_BEFORE=0
TOTAL_TIME_AFTER=0
TOTAL_MEM_BEFORE=0
TOTAL_MEM_AFTER=0

for (( i=0; i<$NUM_BENCHMARKS; i++ )); do
    TIME_B=$(jq -r ".benchmarks[$i].duration_minutes" "$BEFORE")
    TIME_A=$(jq -r ".benchmarks[$i].duration_minutes" "$AFTER")
    MEM_B=$(jq -r ".benchmarks[$i].memory_increase_mb" "$BEFORE")
    MEM_A=$(jq -r ".benchmarks[$i].memory_increase_mb" "$AFTER")

    TOTAL_TIME_BEFORE=$(echo "$TOTAL_TIME_BEFORE + $TIME_B" | bc)
    TOTAL_TIME_AFTER=$(echo "$TOTAL_TIME_AFTER + $TIME_A" | bc)
    TOTAL_MEM_BEFORE=$(echo "$TOTAL_MEM_BEFORE + $MEM_B" | bc)
    TOTAL_MEM_AFTER=$(echo "$TOTAL_MEM_AFTER + $MEM_A" | bc)
done

TOTAL_TIME_IMPROVEMENT=$(echo "scale=2; ($TOTAL_TIME_BEFORE - $TOTAL_TIME_AFTER) / $TOTAL_TIME_BEFORE * 100" | bc)
TOTAL_MEM_CHANGE=$(echo "scale=2; ($TOTAL_MEM_AFTER - $TOTAL_MEM_BEFORE) / $TOTAL_MEM_BEFORE * 100" | bc)

echo ""
echo -e "${YELLOW}⏱️  Tiempo Total:${NC}"
echo "  Antes:   $TOTAL_TIME_BEFORE min"
echo "  Después: $TOTAL_TIME_AFTER min"

if (( $(echo "$TOTAL_TIME_IMPROVEMENT > 0" | bc -l) )); then
    echo -e "  ${GREEN}${BOLD}✅ Mejora Total: $TOTAL_TIME_IMPROVEMENT%${NC}"
elif (( $(echo "$TOTAL_TIME_IMPROVEMENT < 0" | bc -l) )); then
    ABS_IMPROVEMENT=$(echo "$TOTAL_TIME_IMPROVEMENT * -1" | bc)
    echo -e "  ${RED}${BOLD}❌ Regresión Total: -$ABS_IMPROVEMENT%${NC}"
else
    echo "  ⚖️  Sin cambio: 0%"
fi

echo ""
echo -e "${YELLOW}💾 Memoria Total:${NC}"
echo "  Antes:   $TOTAL_MEM_BEFORE MB"
echo "  Después: $TOTAL_MEM_AFTER MB"

if (( $(echo "$TOTAL_MEM_CHANGE < 0" | bc -l) )); then
    ABS_CHANGE=$(echo "$TOTAL_MEM_CHANGE * -1" | bc)
    echo -e "  ${GREEN}${BOLD}✅ Reducción: $ABS_CHANGE%${NC}"
elif (( $(echo "$TOTAL_MEM_CHANGE > 0" | bc -l) )); then
    echo -e "  ${YELLOW}${BOLD}⚠️  Aumento: +$TOTAL_MEM_CHANGE%${NC}"
else
    echo "  ⚖️  Sin cambio: 0%"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Conclusión final
if (( $(echo "$TOTAL_TIME_IMPROVEMENT >= 10" | bc -l) )); then
    echo -e "${GREEN}${BOLD}🎉 EXCELENTE MEJORA DE RENDIMIENTO${NC}"
elif (( $(echo "$TOTAL_TIME_IMPROVEMENT > 0" | bc -l) )); then
    echo -e "${GREEN}${BOLD}✅ MEJORA DE RENDIMIENTO${NC}"
elif (( $(echo "$TOTAL_TIME_IMPROVEMENT == 0" | bc -l) )); then
    echo -e "${YELLOW}${BOLD}⚖️  SIN CAMBIOS SIGNIFICATIVOS${NC}"
else
    echo -e "${RED}${BOLD}⚠️  ADVERTENCIA: REGRESIÓN DE RENDIMIENTO${NC}"
fi

echo ""
