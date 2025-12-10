# Script de Comparación de Benchmarks

## Descripción

El script `compare_benchmarks.py` compara dos archivos de benchmark JSON para calcular las mejoras o regresiones de rendimiento entre dos ejecuciones del ETL.

## Uso

```bash
python scripts/benchmarking/compare_benchmarks.py <archivo_antes> <archivo_despues>
```

### Ejemplo

```bash
python scripts/benchmarking/compare_benchmarks.py \
    .benchmark/baseline_2025-12-10_11-02-08.json \
    .benchmark/baseline_2025-12-10_20-01-50.json
```

## Funcionamiento

### 1. Carga de Datos
- Lee dos archivos JSON de benchmark
- Valida que los archivos existan y tengan formato JSON válido
- Extrae información del sistema (CPU, RAM)

### 2. Comparación de Métricas

#### Tiempo de Ejecución
```
Mejora de Tiempo (%) = ((Tiempo_Antes - Tiempo_Después) / Tiempo_Antes) × 100
```

**Interpretación:**
- **Positivo** → ✅ Mejora (más rápido)
- **Negativo** → ❌ Regresión (más lento)
- **Cero** → ⚖️ Sin cambio

**Ejemplo:**
```
Antes:   46.83 min (2809.66s)
Después: 37.08 min (2224.74s)
Diferencia: -9.75 min (-584.92s)
Mejora: 20.82% más rápido ✅
```

#### Uso de Memoria
```
Cambio de Memoria (%) = ((Memoria_Antes - Memoria_Después) / Memoria_Antes) × 100
```

**Interpretación:**
- **Positivo** → ✅ Reducción (menos memoria)
- **Negativo** → ⚠️ Aumento (más memoria)
- **Cero** → ⚖️ Sin cambio

**Ejemplo:**
```
Antes:   21.87 MB
Después: 23.26 MB
Diferencia: +1.39 MB
Cambio: -6.36% (aumento de memoria) ⚠️
```

### 3. Métricas Reportadas

#### Por Benchmark Individual:

**Tiempo de Ejecución:**
- Duración antes (minutos y segundos)
- Duración después (minutos y segundos)
- Diferencia absoluta (minutos y segundos)
- Porcentaje de mejora/regresión

**Uso de Memoria:**
- Incremento de memoria antes (MB)
- Incremento de memoria después (MB)
- Diferencia absoluta (MB)
- Porcentaje de cambio

**Detalles Adicionales:**
- Memoria inicial del proceso
- Memoria final del proceso
- Pico de memoria durante ejecución

#### Resumen Total:
- Suma de todos los tiempos de ejecución
- Suma de todos los incrementos de memoria
- Mejora/regresión total en porcentaje
- Conclusión final del rendimiento

### 4. Código de Colores

- 🟢 **Verde** → Mejoras (tiempo más rápido, memoria reducida)
- 🟡 **Amarillo** → Advertencias (memoria aumentada)
- 🔴 **Rojo** → Regresiones (tiempo más lento)
- 🔵 **Azul** → Información general

### 5. Conclusión Final

El script evalúa la mejora total de tiempo:

- **≥ 10%** → 🎉 EXCELENTE MEJORA DE RENDIMIENTO
- **> 0%** → ✅ MEJORA DE RENDIMIENTO
- **= 0%** → ⚖️ SIN CAMBIOS SIGNIFICATIVOS
- **< 0%** → ⚠️ ADVERTENCIA: REGRESIÓN DE RENDIMIENTO

## Cálculos Verificados

### Ejemplo Real

**Datos de entrada:**
```json
Archivo 1 (antes):
{
  "benchmarks": [{
    "name": "SonarQube ETL",
    "duration_seconds": 2809.66,
    "duration_minutes": 46.83,
    "memory_increase_mb": 21.87
  }]
}

Archivo 2 (después):
{
  "benchmarks": [{
    "name": "SonarQube ETL",
    "duration_seconds": 2224.74,
    "duration_minutes": 37.08,
    "memory_increase_mb": 23.26
  }]
}
```

**Cálculos:**

1. **Tiempo:**
   - Diferencia: 2809.66s - 2224.74s = 584.92s = 9.75 min
   - Mejora: (9.75 / 46.83) × 100 = **20.82%** ✅

2. **Memoria:**
   - Diferencia: 23.26 MB - 21.87 MB = 1.39 MB
   - Cambio: ((21.87 - 23.26) / 21.87) × 100 = **-6.36%** ⚠️
   - Interpretación: La memoria aumentó un 6.36%

**Resultado:**
- ✅ El proceso es **20.82% más rápido**
- ⚠️ El proceso usa **6.36% más memoria**
- 🎉 Conclusión: **EXCELENTE MEJORA DE RENDIMIENTO**

## Correcciones Realizadas

### Problemas Corregidos (v2):

1. ✅ **Error en signo de diferencia de tiempo**
   - Antes: `+9.75 min` (confuso)
   - Ahora: `-9.75 min` (correcto: ahorro de tiempo)

2. ✅ **Error en interpretación de memoria**
   - Antes: "Reducción: 6.36%" cuando aumentó
   - Ahora: "Aumento: 6.36%" (correcto)

3. ✅ **Funciones separadas para tiempo y memoria**
   - `format_time_change()` → Tiempo (positivo = más rápido)
   - `format_memory_change()` → Memoria (positivo = menos memoria)

4. ✅ **Información más clara**
   - Muestra segundos además de minutos
   - Etiquetas más descriptivas
   - Detalles de memoria inicial, final y pico

## Notas Importantes

- El script solo compara benchmarks en el mismo orden
- Si hay diferente número de benchmarks, muestra advertencia
- Los colores requieren terminal compatible con ANSI
- En Windows, se configura automáticamente la codificación UTF-8

## Ver También

- [run_benchmark.py](run_benchmark.py) - Ejecuta benchmarks y genera archivos JSON
- [generate_baseline.py](generate_baseline.py) - Genera fixtures baseline para testing
