#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trabajo práctico: medición de Quicksort (mediana de 3 + umbral a inserción)
Entrega: solo el código (el informe lo realiza el estudiante).
Este script:
 - implementa quicksort con mediana de 3 y umbral a ordenación por inserción
 - valida automáticamente la correcta ordenación
 - mide tiempos siguiendo progresión geométrica (razón 2 o 10)
 - automatiza re-ejecuciones si el tiempo es demasiado pequeño (umbral de confianza)
 - limpia mediciones anómalas (descarta outliers por IQR)
 - ajusta cotas (c * n log n y c * n^2) y calcula constantes de ajuste
 - genera tablas CSV y la imprime por pantalla con 3 cifras significativas
 - todo en funciones cortas y documentadas para cumplir la rúbrica

Uso:
    python3 medir_quicksort.py [--ratio 2] [--start 1024] [--steps 6] [--reps 10]
    Opciones:
      --ratio: 2 o 10 (razón de la progresión geométrica)
      --start: tamaño inicial (entero)
      --steps: número de tamaños a probar (debe producir al menos 5 filas)
      --reps: repeticiones base por tamaño (el script puede multiplicar si es necesario)
      --out: archivo CSV de salida
"""

from __future__ import annotations
import time
import random
import math
import argparse
import statistics
import csv
import gc
from typing import List, Tuple, Dict

# ---------------------------
# Algoritmo: funciones pequeñas y documentadas
# ---------------------------

def mediana3(v: List[int], i: int, j: int) -> None:
    """Coloca en v[i] la mediana de v[i], v[(i+j)//2], v[j]."""
    k = (i + j) // 2
    if v[k] > v[j]:
        v[k], v[j] = v[j], v[k]
    if v[k] > v[i]:
        v[k], v[i] = v[i], v[k]
    if v[i] > v[j]:
        v[i], v[j] = v[j], v[i]

def insertion_sort_segment(v: List[int], left: int = 0, right: int = None) -> None:
    """Ordenación por inserción del segmento v[left:right+1]."""
    if right is None:
        right = len(v) - 1
    for p in range(left + 1, right + 1):
        tmp = v[p]
        j = p - 1
        while j >= left and v[j] > tmp:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = tmp

def quick_aux(v: List[int], left: int, right: int, umbral: int) -> None:
    """Auxiliar recursiva de Quicksort con pivote mediana3."""
    if left + umbral <= right:
        mediana3(v, left, right)
        pivot = v[left]
        i = left
        j = right + 1
        while True:
            i += 1
            while i <= right and v[i] < pivot:
                i += 1
            j -= 1
            while j >= left and v[j] > pivot:
                j -= 1
            if i < j:
                v[i], v[j] = v[j], v[i]
            else:
                break
        v[left], v[j] = v[j], v[left]
        quick_aux(v, left, j - 1, umbral)
        quick_aux(v, j + 1, right, umbral)

def quicksort(v: List[int], umbral: int = 16) -> None:
    """Quicksort público: aplica quick_aux y luego inserción si umbral>1."""
    n = len(v)
    if n <= 1:
        return
    quick_aux(v, 0, n - 1, umbral)
    if umbral > 1:
        insertion_sort_segment(v, 0, n - 1)

# ---------------------------
# Utilidades de validación y medición
# ---------------------------

def is_sorted(v: List[int]) -> bool:
    """Comprueba si la lista está ordenada no-decrecientemente."""
    return all(v[i] <= v[i+1] for i in range(len(v)-1))

def warmup() -> None:
    """Rutina de calentamiento para estabilizar JIT/OS/cache (simple)."""
    x = list(range(1000))
    random.shuffle(x)
    quicksort(x, umbral=10)
    del x

def iqr_filter(values: List[float]) -> List[float]:
    """Descarta outliers usando la regla del IQR; devuelve lista filtrada."""
    if len(values) < 4:
        return values[:]
    s = sorted(values)
    q1 = statistics.median(s[:len(s)//2])
    q3 = statistics.median(s[(len(s)+1)//2:])
    iqr = q3 - q1
    if iqr == 0:
        return s
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    return [x for x in s if low <= x <= high]

def measure_sort_time(func, arr: List[int]) -> float:
    """Mide tiempo de ejecución de func sobre una copia de arr usando perf_counter."""
    a = arr.copy()
    gc.collect()
    t0 = time.perf_counter()
    func(a)
    t1 = time.perf_counter()
    if not is_sorted(a):
        raise AssertionError("La función no ordenó correctamente la lista.")
    return t1 - t0

# ---------------------------
# Medición automática con criterio de confianza
# ---------------------------

def measure_with_confidence(func, base_arr: List[int], target_reps: int = 10,
                            min_total_time: float = 0.2, max_trials: int = 5) -> Tuple[float, float, int]:
    """
    Mide tiempo medio con repetición automática:
     - realiza 'target_reps' repeticiones
     - si la suma de tiempos < min_total_time, duplica repeticiones (hasta max_trials veces)
     - devuelve (mean_seconds, std_seconds, iterations)
    """
    reps = max(1, int(target_reps))
    for trial in range(max_trials):
        times = []
        for _ in range(reps):
            t = measure_sort_time(func, base_arr)
            times.append(t)
        total = sum(times)
        if total >= min_total_time or reps >= 1 << (max_trials - 1):
            # limpiar outliers y devolver
            filtered = iqr_filter(times)
            mean = statistics.mean(filtered) if filtered else statistics.mean(times)
            std = statistics.pstdev(filtered) if filtered else statistics.pstdev(times)
            return mean, std, reps
        reps *= 2
    # último recurso: devolver lo medido
    filtered = iqr_filter(times)
    mean = statistics.mean(filtered) if filtered else statistics.mean(times)
    std = statistics.pstdev(filtered) if filtered else statistics.pstdev(times)
    return mean, std, reps

# ---------------------------
# Ajuste de cotas: c * n log n y c * n^2 (método de mínimos cuadrados unidimensional)
# ---------------------------

def fit_constant(xs: List[float], ys: List[float]) -> float:
    """Ajusta y ≈ c * x mediante mínimos cuadrados (solución c = sum(x*y)/sum(x^2))."""
    num = sum(x*y for x,y in zip(xs, ys))
    den = sum(x*x for x in xs)
    if den == 0:
        return float('nan')
    return num/den

# ---------------------------
# Generación de casos y experimento principal
# ---------------------------

def geometric_sequence(start: int, ratio: int, steps: int) -> List[int]:
    """Genera secuencia geométrica entera (start, start*ratio, ...)."""
    seq = []
    cur = int(start)
    for _ in range(steps):
        seq.append(int(cur))
        cur = max(1, int(cur * ratio))
    return seq

def run_experiments(ratio: int = 2, start: int = 1024, steps: int = 6,
                    base_reps: int = 5, umbral: int = 16,
                    seed: int = 12345, out_csv: str = "resultados_quicksort.csv") -> None:
    """
    Ejecuta los experimentos y escribe un CSV con columnas:
    n, situación, umbral, reps_empleadas, tiempo_medio_s, std_s, muestras_validas
    Además imprime un resumen y ajusta constantes de cota para n log2 n y n^2.
    """
    random.seed(seed)
    warmup()
    sizes = geometric_sequence(start, ratio, steps)
    # garantizar al menos 5 filas según rúbrica
    if len(sizes) < 5:
        raise ValueError("La progresión geométrica debe producir al menos 5 tamaños (e6).")
    header = ["n", "situación", "umbral", "reps_empleadas", "tiempo_medio_s", "std_s", "muestras_validas"]
    rows = []
    # situaciones: aleatorio, ascendente, descendente
    for n in sizes:
        # construir datos base
        base_random = [random.randint(0, 10**9) for _ in range(n)]
        base_sorted = sorted(base_random)
        base_rev = list(reversed(base_sorted))
        for situ_name, source in [("aleatorio", base_random),
                                  ("ascendente", base_sorted),
                                  ("descendente", base_rev)]:
            mean, std, reps_used = measure_with_confidence(
                lambda a, u=umbral: quicksort(a, umbral=u),
                source,
                target_reps=base_reps,
                min_total_time=0.2
            )
            # ajustar a 3 cifras significativas en la salida
            mean_3 = float(f"{mean:.3g}")
            std_3 = float(f"{std:.3g}")
            rows.append([n, situ_name, umbral, reps_used, mean_3, std_3, reps_used])
            print(f"n={n:8d} | {situ_name:10s} | reps={reps_used:3d} | mean={mean_3:.3g}s | std={std_3:.3g}s")
    # escribir CSV
    with open(out_csv, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\nDatos guardados en '{out_csv}'.\n")
    # ANALISIS: ajuste de cotas usando solo casos 'aleatorio' (más representativo)
    ns = [r[0] for r in rows if r[1] == "aleatorio"]
    times = [r[4] for r in rows if r[1] == "aleatorio"]
    # convertir a float (ya lo son) y construir x para n log2 n y n^2
    x_nlog = [n * math.log2(max(2, n)) for n in ns]
    x_n2 = [n * n for n in ns]
    c_nlog = fit_constant(x_nlog, times)
    c_n2 = fit_constant(x_n2, times)
    print("Ajustes (usando casos 'aleatorio'):")
    print(f" - c for n log2 n: {c_nlog:.6g}")
    print(f" - c for n^2      : {c_n2:.6g}")
    # generar predicciones y marcar cota sub/overestimada (usar 0.9c y 1.1c)
    pred_nlog = [c_nlog * x for x in x_nlog]
    pred_nlog_under = [0.9*c_nlog * x for x in x_nlog]
    pred_nlog_over = [1.1*c_nlog * x for x in x_nlog]
    # mostrar tabla compacta comparativa (3 cifras significativas)
    print("\nComparativa (aleatorio): n | tiempo_med | pred(n log n) | pred(0.9c) | pred(1.1c)")
    for n, t, p, pu, po in zip(ns, times, pred_nlog, pred_nlog_under, pred_nlog_over):
        print(f"{n:7d} | {t:10.3g}s | {p:12.3g}s | {pu:10.3g}s | {po:10.3g}s")
    # indicar sucesión de la cota ajustada (constante c) para e11
    print(f"\nConstante ajustada para la cota n log n: c = {c_nlog:.6g}")
    print("Para estudiar cota subestimada usamos c' = 0.9 * c; sobrestimada c'' = 1.1 * c.")
    print("Esto permite en el informe indicar una cota (ligeramente) subestimada y otra sobrestimada.")
    print("\nFin de experimento.")

# ---------------------------
# Entrada principal: argumentos
# ---------------------------

def parse_args():
    """Parsea argumentos de línea de comandos."""
    p = argparse.ArgumentParser(description="Medición de Quicksort (mediana3 + umbral a inserción).")
    p.add_argument("--ratio", type=int, default=2, choices=[2,10],
                   help="Razón de la progresión geométrica (2 o 10).")
    p.add_argument("--start", type=int, default=1024,
                   help="Tamaño inicial de la progresión geométrica.")
    p.add_argument("--steps", type=int, default=6,
                   help="Número de tamaños (debe dar al menos 5 filas).")
    p.add_argument("--reps", type=int, default=5,
                   help="Repeticiones base por tamaño (se duplican si tiempo total es pequeño).")
    p.add_argument("--umbral", type=int, default=16,
                   help="Umbral para cambiar a ordenación por inserción.")
    p.add_argument("--seed", type=int, default=12345, help="Semilla para reproducibilidad.")
    p.add_argument("--out", type=str, default="resultados_quicksort.csv", help="Archivo CSV de salida.")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_experiments(ratio=args.ratio,
                    start=args.start,
                    steps=args.steps,
                    base_reps=args.reps,
                    umbral=args.umbral,
                    seed=args.seed,
                    out_csv=args.out)
