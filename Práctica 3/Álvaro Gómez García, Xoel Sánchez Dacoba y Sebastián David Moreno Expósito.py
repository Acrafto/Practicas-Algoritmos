import time
import random
from typing import Callable, List, Tuple, Dict
import math

# ------------------------------
# Algoritmos de ordenación
# ------------------------------

def ord_insercion(v: List[int]) -> List[int]:
    """
    Ordena una lista mediante el algoritmo de Inserción (in place).
    """
    for i in range(1, len(v)):
        x = v[i]
        j = i - 1
        while j >= 0 and v[j] > x:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = x
    return v

def mediana3(v: List[int], i: int, j: int) -> None:
    """
    Median-of-3: reordena v[i], v[k], v[j] y deja la mediana en v[i] (pivote).
    """
    k = (i + j) // 2
    if v[i] > v[k]:
        v[i], v[k] = v[k], v[i]
    if v[i] > v[j]:
        v[i], v[j] = v[j], v[i]
    if v[k] > v[j]:
        v[k], v[j] = v[j], v[k]
    # La mediana queda en v[k]; colócala en v[i]
    v[i], v[k] = v[k], v[i]

def ord_rapida_aux(v: List[int], izq: int, der: int, umbral: int) -> None:
    """
    Quicksort (recursivo) con mediana de tres y umbral.
    """
    if izq + umbral <= der:
        mediana3(v, izq, der)
        piv = v[izq]
        i, j = izq, der
        while True:
            i += 1
            while i <= der and v[i] < piv:
                i += 1
            j -= 1
            while j >= izq and v[j] > piv:
                j -= 1
            if j <= i:
                break
            v[i], v[j] = v[j], v[i]
        v[izq], v[j] = v[j], v[izq]
        ord_rapida_aux(v, izq, j - 1, umbral)
        ord_rapida_aux(v, j + 1, der, umbral)

def ord_rapida(v: List[int], umbral: int) -> List[int]:
    """
    Quicksort con mediana de tres y umbral; inserción final si umbral>1.
    """
    if not v:
        return v
    ord_rapida_aux(v, 0, len(v) - 1, umbral)
    if umbral > 1:
        ord_insercion(v)  # "peina" los segmentos pequeños
    return v

# ------------------------------
# Generadores y utilidades
# ------------------------------

def aleatorio(size: int) -> List[int]:
    return [random.randint(-size, size) for _ in range(size)]

def ascendente(size: int) -> List[int]:
    return list(range(1, size + 1))

def descendente(size: int) -> List[int]:
    return list(range(size, 0, -1))

def microsegundos() -> int:
    return time.perf_counter_ns() // 1000

def ordenado(v: List[int]) -> bool:
    return all(v[i] >= v[i - 1] for i in range(1, len(v)))

# ------------------------------
# Medición de tiempos (compacta)
# ------------------------------

def _tiempo_corregido(alg: Callable[[List[int]], List[int]],
                      gen: Callable[[int], List[int]], n: int) -> float:
    ta = microsegundos()
    alg(gen(n))
    td = microsegundos()
    t = td - ta
    if t >= 1000:
        return float(t), " "
    # Corrección por repeticiones K y resta del generador
    K = 1000
    ta = microsegundos()
    for _ in range(K):
        alg(gen(n))
    td = microsegundos()
    t1 = td - ta
    ta = microsegundos()
    for _ in range(K):
        gen(n)
    td = microsegundos()
    t2 = td - ta
    return (t1 - t2) / K, "*"

def medir_tiempo_ejecucion(alg: Callable[[List[int]], List[int]],
                           gen_vector: Callable[[int], List[int]],
                           muestra_inicial: int,
                           muestras: int, factor: int = 2) -> Dict[int, Tuple[float, str]]:
    """
    Devuelve {n: (tiempo_µs, marca)} con corrección si t<1000 µs.
    """
    res: Dict[int, Tuple[float, str]] = {}
    n = muestra_inicial
    for _ in range(muestras):
        t, m = _tiempo_corregido(lambda v: alg(v.copy()), gen_vector, n)
        if t < 0:
            raise RuntimeError("Cronómetro interno no fiable.")
        res[n] = (t, m)
        n *= factor
    return res

# ------------------------------
# Presentación de resultados
# ------------------------------

def _alpha_por_caso(caso_base: str) -> float:
    """
    Devuelve el α para la sobreestimada según el caso:
    - ascendente/descendente: 1.35
    - aleatorio: 1.6
    """
    return 1.35 if caso_base in ("ascendente", "descendente") else 1.6

def _denominadores(n: int, alpha: float) -> Tuple[float, float, float]:
    # Subestimada: n (crece más lento que n log n)
    sub = float(max(1, n))
    # Ajustada: n log2 n
    adj = float(1.0 if n <= 1 else n * math.log2(n))
    # Sobreestimada: n^alpha
    over = n ** alpha
    return sub, adj, over

def _constante_ajustada_promedio(tfilas: List[Tuple[int, float]]) -> float:
    # Promedio de los 3 últimos t(n)/(n log n) como estimador de c
    ult = tfilas[-3:] if len(tfilas) >= 3 else tfilas
    vals = []
    for n, t in ult:
        adj = (1.0 if n <= 1 else n * math.log2(n))
        vals.append(t / adj)
    return sum(vals) / len(vals)

def _extraer_caso_base(case_str: str) -> str:
    """
    De 'ascendente (umbral=10)' devuelve 'ascendente'.
    """
    p = case_str.find(" (")
    return case_str[:p] if p != -1 else case_str

def mostrar_tiempo_rapida(alg_name: str, v: Dict[int, Tuple[float, str]], case: str) -> None:
    """
    Imprime tabla con t(n), y normaliza con sub (n), ajustada (n log n) y sobre (n^alpha).
    También estima c ≈ promedio de t(n)/(n log n) en las 3 mayores n.
    """
    caso_base = _extraer_caso_base(case)
    alpha = _alpha_por_caso(caso_base)

    print()
    print(f"**{alg_name} - caso: {case} | α={alpha}**")
    header = (f"{'n[-]':>8} {'t(n)[µs]':>14} {'t(n)/n':>14}"
              f"{'t(n)/(n·log2n)':>20} {f't(n)/n^α (α={alpha})':>22}")
    print(header)

    filas = []
    for n, (t_n, signo) in v.items():
        sub, adj, over = _denominadores(n, alpha)
        v_sub = t_n / sub
        v_adj = t_n / adj
        v_over = t_n / over
        filas.append((n, t_n))
        print(f"{signo}{n:8d} {t_n:14.3f} {v_sub:14.6g} {v_adj:20.6g} {v_over:22.6g}")

    c = _constante_ajustada_promedio(filas)
    print("\nNota: Si (*) -> 't(n)<1000': tiempo promedio de K=1000 ejecuciones.")
    print(f"Estimación constante ajustada (c en t ≈ c·n·log2n): c ≈ {c:.6g}\n")

# ------------------------------
# Validación y experimentos
# ------------------------------

def Test_quicksort(ord_rapida_fun: Callable[[List[int], int], List[int]],
                   gen_vector: Callable[[int], List[int]],
                   size_vector: int, umbral: int) -> bool:
    """
    Valida Quicksort imprimiendo entrada/salida y comprobando orden.
    """
    print(f"Validación QuickSort (umbral={umbral}) con tamaño {size_vector}:")
    v = gen_vector(size_vector)
    print("Vector inicial:\n", v)
    resultado = ord_rapida_fun(v.copy(), umbral)
    print("Resultado ordenado:\n", resultado)
    ok = ordenado(resultado)
    print("Ordenado?", ok, "\n")
    return ok

def experimento_completo(muestra_inicial: int = 500,
                         muestras: int = 6, factor: int = 2):
    """
    Ejecuta mediciones para QuickSort con umbrales [1,10,100]
    y casos ascendente/descendente/aleatorio.
    """
    umbrales = [1, 10, 100]
    casos = [("ascendente", ascendente),
             ("descendente", descendente),
             ("aleatorio", aleatorio)]
    for umbral in umbrales:
        for nombre_caso, generador in casos:
            print(f"\n=== Mediciones Quicksort - caso: {nombre_caso} - UMBRAL={umbral} ===")
            resultados = medir_tiempo_ejecucion(
                lambda vec, u=umbral: ord_rapida(vec, u),
                generador, muestra_inicial, muestras, factor)
            mostrar_tiempo_rapida("ord_rapida", resultados,
                                  f"{nombre_caso} (umbral={umbral})")

# ------------------------------
# Bloque principal
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
