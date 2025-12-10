#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para comparar dos archivos de benchmark JSON y calcular mejoras de rendimiento

Uso:
    python compare_benchmarks.py <archivo_antes> <archivo_despues>

Ejemplo:
    python compare_benchmarks.py \
        .benchmark/baseline_2025-12-09_10-00-00.json \
        .benchmark/baseline_2025-12-10_15-00-00.json

Características:
    - Compara tiempo de ejecución y uso de memoria
    - Calcula porcentaje de mejora/regresión
    - Output colorizado para fácil interpretación
    - Genera resumen total de todos los benchmarks
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Fix encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Colors:
    """Códigos ANSI para colores en terminal"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def load_benchmark(file_path: str) -> dict:
    """Carga un archivo de benchmark JSON"""
    path = Path(file_path)

    if not path.exists():
        print(f"Error: Archivo no encontrado: {file_path}")
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: JSON inválido en {file_path}: {e}")
        sys.exit(1)


def calculate_improvement(before: float, after: float) -> float:
    """Calcula el porcentaje de mejora (positivo) o regresión (negativo)"""
    if before == 0:
        return 0.0
    return ((before - after) / before) * 100


def format_change(value: float, reverse: bool = False) -> str:
    """
    Formatea un cambio porcentual con color

    Args:
        value: Valor del cambio (positivo = mejora en tiempo)
        reverse: Si True, invierte la interpretación (para memoria)
    """
    if value > 0:
        color = Colors.GREEN if not reverse else Colors.YELLOW
        symbol = "✅" if not reverse else "⚠️"
        prefix = "Mejora" if not reverse else "Aumento"
        return f"{color}{symbol} {prefix}: {value:.2f}%{Colors.NC}"
    elif value < 0:
        color = Colors.RED if not reverse else Colors.GREEN
        symbol = "❌" if not reverse else "✅"
        prefix = "Regresión" if not reverse else "Reducción"
        return f"{color}{symbol} {prefix}: {abs(value):.2f}%{Colors.NC}"
    else:
        return "⚖️  Sin cambio: 0%"


def compare_single_benchmark(
    name: str,
    before_data: dict,
    after_data: dict
) -> Tuple[float, float]:
    """
    Compara un solo benchmark y retorna mejoras de tiempo y memoria

    Returns:
        Tuple (time_improvement, memory_change)
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}{name}{Colors.NC}")
    print("─" * 64)

    # Comparar tiempo
    time_before = before_data['duration_minutes']
    time_after = after_data['duration_minutes']
    time_improvement = calculate_improvement(time_before, time_after)
    time_diff = time_before - time_after

    print(f"{Colors.YELLOW}⏱️  Tiempo de Ejecución:{Colors.NC}")
    print(f"  Antes:   {time_before:.2f} min")
    print(f"  Después: {time_after:.2f} min")
    print(f"  Cambio:  {time_diff:+.2f} min")
    print(f"  {format_change(time_improvement)}")

    # Comparar memoria
    mem_before = before_data['memory_increase_mb']
    mem_after = after_data['memory_increase_mb']
    mem_change = calculate_improvement(mem_before, mem_after)
    mem_diff = mem_after - mem_before

    print(f"\n{Colors.YELLOW}💾 Uso de Memoria:{Colors.NC}")
    print(f"  Antes:   {mem_before:.2f} MB")
    print(f"  Después: {mem_after:.2f} MB")
    print(f"  Cambio:  {mem_diff:+.2f} MB")
    print(f"  {format_change(mem_change, reverse=True)}")

    # Mostrar métricas adicionales
    print(f"\n{Colors.BLUE}ℹ️  Detalles Adicionales:{Colors.NC}")
    print(f"  Duración (segundos): {before_data['duration_seconds']:.2f}s → "
          f"{after_data['duration_seconds']:.2f}s")
    print(f"  Memoria final: {before_data['end_memory_mb']:.2f} MB → "
          f"{after_data['end_memory_mb']:.2f} MB")
    print(f"  Pico memoria: {before_data['peak_memory_mb']:.2f} MB → "
          f"{after_data['peak_memory_mb']:.2f} MB")

    print("─" * 64)

    return time_improvement, mem_change


def print_summary(
    total_time_before: float,
    total_time_after: float,
    total_mem_before: float,
    total_mem_after: float
):
    """Imprime resumen total de todos los benchmarks"""
    print("\n" + "═" * 64)
    print(f"{Colors.BOLD}  RESUMEN TOTAL{Colors.NC}")
    print("═" * 64)

    total_time_improvement = calculate_improvement(total_time_before, total_time_after)
    total_mem_change = calculate_improvement(total_mem_before, total_mem_after)

    print(f"\n{Colors.YELLOW}⏱️  Tiempo Total:{Colors.NC}")
    print(f"  Antes:   {total_time_before:.2f} min")
    print(f"  Después: {total_time_after:.2f} min")
    print(f"  {Colors.BOLD}{format_change(total_time_improvement)}{Colors.NC}")

    print(f"\n{Colors.YELLOW}💾 Memoria Total:{Colors.NC}")
    print(f"  Antes:   {total_mem_before:.2f} MB")
    print(f"  Después: {total_mem_after:.2f} MB")
    print(f"  {Colors.BOLD}{format_change(total_mem_change, reverse=True)}{Colors.NC}")

    print("\n" + "═" * 64 + "\n")

    # Conclusión final
    if total_time_improvement >= 10:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 EXCELENTE MEJORA DE RENDIMIENTO{Colors.NC}")
    elif total_time_improvement > 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ MEJORA DE RENDIMIENTO{Colors.NC}")
    elif total_time_improvement == 0:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚖️  SIN CAMBIOS SIGNIFICATIVOS{Colors.NC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  ADVERTENCIA: REGRESIÓN DE RENDIMIENTO{Colors.NC}")

    print()


def compare_benchmarks(before_file: str, after_file: str):
    """Función principal para comparar dos archivos de benchmark"""

    # Cargar datos
    before = load_benchmark(before_file)
    after = load_benchmark(after_file)

    # Encabezado
    print("\n" + "═" * 64)
    print(f"{Colors.BOLD}  COMPARACIÓN DE BENCHMARKS{Colors.NC}")
    print("═" * 64)

    # Información de archivos
    before_date = before['timestamp'].split('T')[0]
    after_date = after['timestamp'].split('T')[0]

    print(f"\n{Colors.BLUE}Archivos comparados:{Colors.NC}")
    print(f"  Antes:   {before_file}")
    print(f"           ({before_date})")
    print(f"  Después: {after_file}")
    print(f"           ({after_date})")

    # Información del sistema
    sys_info = before.get('system_info', {})
    cpu_count = sys_info.get('cpu_count', 'N/A')
    cpu_logical = sys_info.get('cpu_count_logical', 'N/A')
    memory_gb = sys_info.get('total_memory_gb', 'N/A')

    print(f"\n{Colors.BLUE}Sistema:{Colors.NC}")
    print(f"  CPU: {cpu_count} cores ({cpu_logical} lógicos)")
    print(f"  RAM: {memory_gb} GB")

    print("\n" + "═" * 64)

    # Comparar cada benchmark
    benchmarks_before = before['benchmarks']
    benchmarks_after = after['benchmarks']

    if len(benchmarks_before) != len(benchmarks_after):
        print(f"{Colors.YELLOW}⚠️  Advertencia: Número de benchmarks diferente")
        print(f"   Antes: {len(benchmarks_before)}, Después: {len(benchmarks_after)}{Colors.NC}")

    total_time_before = 0
    total_time_after = 0
    total_mem_before = 0
    total_mem_after = 0

    # Comparar benchmarks
    for bench_before, bench_after in zip(benchmarks_before, benchmarks_after):
        name = bench_before['name']

        time_imp, mem_change = compare_single_benchmark(
            name,
            bench_before,
            bench_after
        )

        # Acumular totales
        total_time_before += bench_before['duration_minutes']
        total_time_after += bench_after['duration_minutes']
        total_mem_before += bench_before['memory_increase_mb']
        total_mem_after += bench_after['memory_increase_mb']

    # Imprimir resumen
    print_summary(
        total_time_before,
        total_time_after,
        total_mem_before,
        total_mem_after
    )


def main():
    """Punto de entrada del script"""
    if len(sys.argv) != 3:
        print("Error: Se requieren 2 argumentos\n")
        print("Uso: python compare_benchmarks.py <archivo_antes> <archivo_despues>\n")
        print("Ejemplo:")
        print("  python compare_benchmarks.py \\")
        print("      .benchmark/baseline_2025-12-09_10-00-00.json \\")
        print("      .benchmark/baseline_2025-12-10_15-00-00.json")
        sys.exit(1)

    before_file = sys.argv[1]
    after_file = sys.argv[2]

    compare_benchmarks(before_file, after_file)


if __name__ == '__main__':
    main()
