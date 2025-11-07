import time
import random
from typing import Callable, List, Tuple, Dict
import math

# ------------------------------
# Algoritmos de ordenación
# ------------------------------

def ord_insercion(v: list) -> list:
    n = len(v)
    for i in range(1, n):
        x = v[i]
        j = i - 1
        while j >= 0 and v[j] > x:
            v[j+1] = v[j]
            j -= 1
        v[j+1] = x
    return v

def mediana3(v: List[int], i: int, j: int) -> None:
    k = (i + j) // 2
    if v[k] > v[j]:
        v[k], v[j] = v[j], v[k]
    if v[k] > v[i]:
        v[k], v[i] = v[i], v[k]
    if v[i] > v[j]:
        v[i], v[j] = v[j], v[i]

def ord_rapida_aux(v: List[int], izq: int, der: int, umbral: int) -> None:
    if izq + umbral <= der:
        mediana3(v, izq, der)
        pivote = v[izq]
        i = izq
        j = der
        while True:
            i += 1
            while i <= der and v[i] < pivote:
                i += 1
            j -= 1
            while j >= izq and v[j] > pivote:
                j -= 1
            if j <= i:
                break
            v[i], v[j] = v[j], v[i]
        v[izq], v[j] = v[j], v[izq]
        ord_rapida_aux(v, izq, j - 1, umbral)
        ord_rapida_aux(v, j + 1, der, umbral)

def ord_rapida(v: List[int], umbral: int) -> List[int]:
    n = len(v)
    if n == 0:
        return v
    ord_rapida_aux(v, 0, n - 1, umbral)
    if umbral > 1:
        ord_insercion(v)
    return v

# ------------------------------
# Generadores de vectores y utilidades
# ------------------------------

def aleatorio(size:int) -> List[int]:
    return [random.randint(-size, size) for _ in range(size)]

def ascendente(size:int) -> List[int]:
    return list(range(1, size+1))

def descendente(size:int) -> List[int]:
    return list(range(size, 0, -1))

def microsegundos() -> int:
    return time.perf_counter_ns() // 1000

def ordenado(v: List[int]) -> bool:
    return all(v[i] >= v[i-1] for i in range(1, len(v)))

# ------------------------------
# Medición de tiempos
# ------------------------------

def medir_tiempo_ejecucion(alg: Callable, gen_vector: Callable,
                           muestra_inicial:int,
                           muestras:int, factor:int=2) -> dict:
    vector_tiempo: Dict[int, Tuple[float,str]] = {}
    n = muestra_inicial
    for _ in range(muestras):
        vector = gen_vector(n)
        ta = microsegundos()
        alg(vector.copy())
        td = microsegundos()
        t = td - ta
        bucles = " "
        if t < 1000:
            bucles = "*"
            K = 1000
            ta = microsegundos()
            for _ in range(K):
                alg(gen_vector(n))
            td = microsegundos()
            t1 = td - ta
            ta = microsegundos()
            for _ in range(K):
                gen_vector(n)
            td = microsegundos()
            t2 = td - ta
            t = (t1 - t2) / K
        if t < 0:
            raise Exception("Cronómetro interno no fiable.")
        vector_tiempo[n] = (t, bucles)
        n = n * factor
    return vector_tiempo

# ------------------------------
# Presentación de resultados para Quicksort (cabeceras corregidas)
# ------------------------------

def mostrar_tiempo_rapida(alg_name:str, v:dict, case:str) -> None:
    """
    Muestra tabla de tiempos y normalizaciones para Quicksort.
    Nota: solo la columna t(n) está en µs; las demás son cocientes (adimensionales o con otra unidad),
    por lo que NO se etiquetan con 'µs'.
    """
    print()
    print(f"**{alg_name} - caso: {case}**")
    header = (f"{'n[-]':>8} {'t(n)[µs]':>14} {'t(n)/(n·log2n)':>20}"
              f"{'t(n)/n^1.3':>18} {'t(n)/n^2':>18}")
    print(header)
    for n, (t_n, bucles) in v.items():
        if n <= 1:
            denom_log = 1.0
        else:
            denom_log = n * math.log2(n)
        v1 = t_n / denom_log
        v2 = t_n / (n ** 1.3)
        v3 = t_n / (n ** 2)
        print(f"{bucles}{n:8d} {t_n:14.3f} {v1:20.6g}{v2:18.6g}{v3:18.6g}")
    print("\nNota: Si (*) -> 't(n)<1000' : tiempo promedio de K=1000 ejecuciones.\n")

# ------------------------------
# Validación y experimentos
# ------------------------------

def Test_quicksort(ord_rapida:Callable, gen_vector:Callable, size_vector:int, umbral:int) -> bool:
    print(f"Validación QuickSort (umbral={umbral}) con tamaño {size_vector}:")
    v = gen_vector(size_vector)
    print("Vector inicial:")
    print(v)
    resultado = ord_rapida(v.copy(), umbral)
    print("Resultado ordenado:")
    print(resultado)
    ok = ordenado(resultado)
    print("Ordenado?", ok, "\n")
    return ok

def experimento_completo(muestra_inicial:int = 500, muestras:int = 6, factor:int = 2):
    umbrales = [1, 10, 100]
    casos = [
        ("ascendente", ascendente),
        ("descendente", descendente),
        ("aleatorio", aleatorio)
    ]

    for umbral in umbrales:
        for nombre_caso, generador in casos:
            print(f"\n=== Mediciones Quicksort - caso: {nombre_caso} - UMBRAL={umbral} ===")
            resultados = medir_tiempo_ejecucion(lambda vec, u=umbral: ord_rapida(vec, u),
                                                generador, muestra_inicial, muestras, factor)
            mostrar_tiempo_rapida("ord_rapida", resultados, f"{nombre_caso} (umbral={umbral})")

# ------------------------------
# Bloque principal (sin comparación con Shell)
# ------------------------------

if __name__ == "__main__":

    print("VALIDACIÓN inicial Quicksort (umbral=1):")
    ok = Test_quicksort(ord_rapida, aleatorio, 11, umbral=1)
    if not ok:
        print("Error en la implementación de Quicksort (umbral=1). Revise el código.")
    else:
        print("Validación correcta.\n")

    muestra_inicial, muestras, factor = 500, 6, 2

    experimento_completo(muestra_inicial, muestras, factor)

    print("\n--- FIN MEDICIONES PRÁCTICA 3 ---")
