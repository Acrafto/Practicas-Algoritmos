# practica3_quicksort.py
"""
Práctica 3 - Ordenación Rápida (Quicksort) con Mediana de 3 y umbral

Estructura y estilo adaptados de la Práctica 2:
- Implementación de mediana3, ord_rapida_aux y ord_rapida.
- Validación básica.
- Medición de tiempos (función reutilizada medir_tiempo_ejecucion).
- Presentación en tablas y normalizaciones empíricas (t/(n log n), t/n^p, ...).

Instrucciones:
    python practica3_quicksort.py

Autor: (tu nombre aquí)
Fecha límite: 2025-11-08 23:59
"""

import time
import random
from typing import Callable, List, Tuple, Dict
import math

# ------------------------------
# Algoritmos de ordenación
# ------------------------------

def ord_insercion(v: list) -> list:
    """Ordenación por inserción (in-place). Mantener para uso final si umbral>1."""
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
    """Realiza la rutina Mediana3 sobre v[i..j] según el enunciado.
    Tras su ejecución el pivote queda en v[i] y v[j] contiene un valor >= pivote.
    Precondición: i < j
    """
    # k es el índice central
    k = (i + j) // 2
    # Asegurar orden entre k y j
    if v[k] > v[j]:
        v[k], v[j] = v[j], v[k]
    # Asegurar orden entre k y i
    if v[k] > v[i]:
        v[k], v[i] = v[i], v[k]
    # Asegurar orden entre i y j
    if v[i] > v[j]:
        v[i], v[j] = v[j], v[i]
    # Ahora la mediana está en v[i], y v[j] >= v[i]

def ord_rapida_aux(v: List[int], izq: int, der: int, umbral: int) -> None:
    """Procedimiento OrdenarAux recursivo de Quicksort con mediana3 y umbral.
    Implementación fiel a la figura del enunciado.
    (Indices: izq..der inclusive)
    """
    if izq + umbral <= der:  # sólo particionar si tamaño >= umbral
        # elegir pivote por mediana de tres
        mediana3(v, izq, der)
        pivote = v[izq]
        i = izq
        j = der
        # partición del tipo Hoare modificado tal y como figura
        while True:
            # mover i hasta encontrar v[i] >= pivote
            i += 1
            while i <= der and v[i] < pivote:
                i += 1
            # mover j hasta encontrar v[j] <= pivote
            j -= 1
            while j >= izq and v[j] > pivote:
                j -= 1
            if j <= i:
                # deshacer el último intercambio (el bucle del pseudocódigo ya lo hace)
                break
            # intercambio
            v[i], v[j] = v[j], v[i]
        # tras terminar, colocar pivote en su posición final
        # en el pseudocódigo realizan un intercambio final:
        # intercambiar (V[i], V[j]); <- deshace último swap
        # intercambiar (V[izq], V[j])
        # Como hemos salido cuando j <= i, el pivote queda en v[izq] y debe ir a v[j]
        v[izq], v[j] = v[j], v[izq]
        # llamadas recursivas
        ord_rapida_aux(v, izq, j - 1, umbral)
        ord_rapida_aux(v, j + 1, der, umbral)
    # en caso contrario (subvector pequeño) no hacemos nada aquí, será insertion final

def ord_rapida(v: List[int], umbral: int) -> List[int]:
    """Ordenación rápida (Quicksort) pública.
    Aplica ord_rapida_aux y si umbral>1 realiza ord_insercion final.
    """
    n = len(v)
    if n == 0:
        return v
    # Para evitar accesos fuera de rango en ord_rapida_aux cuando se
    # hacen comparaciones en v[i]/v[j], añadimos centinelas temporales:
    # Sin embargo, la mediana3 garantiza que v[der] >= pivote y que hay al menos 2 elementos
    # solo si izq<der; la implementación de ord_rapida_aux controla límites.
    ord_rapida_aux(v, 0, n - 1, umbral)
    if umbral > 1:
        ord_insercion(v)
    return v

# ------------------------------
# Generadores de vectores y utilidades
# ------------------------------

def aleatorio(size:int) -> List[int]:
    """Genera lista de 'size' enteros aleatorios en [-size, size]."""
    return [random.randint(-size, size) for _ in range(size)]

def ascendente(size:int) -> List[int]:
    """Genera lista ascendente 1..size."""
    return list(range(1, size+1))

def descendente(size:int) -> List[int]:
    """Genera lista descendente size..1."""
    return list(range(size, 0, -1))

def microsegundos() -> int:
    """Cronómetro en microsegundos (usa perf_counter_ns)."""
    return time.perf_counter_ns() // 1000

def ordenado(v: List[int]) -> bool:
    """Comprueba si v está ordenado no decrecientemente."""
    return all(v[i] >= v[i-1] for i in range(1, len(v)))

# ------------------------------
# Medición de tiempos (reutilizado/adaptado)
# ------------------------------

def medir_tiempo_ejecucion(alg: Callable, gen_vector: Callable,
                           muestra_inicial:int,
                           muestras:int, factor:int=2) -> dict:
    """Mide tiempo de ejecución del algoritmo 'alg' sobre vectores generados
    por 'gen_vector' para tamaños crecientes.
    Aplica corrección empírica para tiempos pequeños (<1000 µs) usando K ejecuciones.
    Devuelve dict: {n: (t_promedio_µs, bucles_flag)}.
    """
    vector_tiempo: Dict[int, Tuple[float,str]] = {}
    n = muestra_inicial
    for _ in range(muestras):
        vector = gen_vector(n)
        ta = microsegundos()
        # clonamos para garantizar que el algoritmo no reciba vector ya ordenado por referencia
        alg(vector.copy())
        td = microsegundos()
        t = td - ta
        bucles = " "
        if t < 1000:
            # corrección por ruido usando K ejecuciones
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
# Presentación de resultados para Quicksort
# ------------------------------

def mostrar_tiempo_rapida(alg_name:str, v:dict, case:str) -> None:
    """Muestra tabla de tiempos y normalizaciones para Quicksort.
    Normalizaciones: t(n)/(n*log2(n)), t(n)/n^1.3, t(n)/n^2
    """
    print()
    print(f"**{alg_name} - caso: {case}**")
    header = (f"{'n[-]':>8} {'t(n)[µs]':>14} {'t(n)/(n·log2n)[µs]':>20}"
              f"{'t(n)/n^1.3[µs]':>18} {'t(n)/n^2[µs]':>18}")
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
    """Valida funcionamiento de Quicksort (umbral dado). Usa impresión similar a práctica 2."""
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
    """Realiza experimentos para Quicksort con umbrales [1,10,100] y
    para cada caso inicial (asc, desc, aleat). Muestra 9 tablas.
    """
    umbrales = [1, 10, 100]
    casos = [
        ("ascendente", ascendente),
        ("descendente", descendente),
        ("aleatorio", aleatorio)
    ]

    # calcular v_max_size para generar secuencias de incremento en otros algoritmos (si se necesita)
    v_max_size = (factor ** (muestras - 1)) * muestra_inicial

    for umbral in umbrales:
        for nombre_caso, generador in casos:
            print(f"\n=== Mediciones Quicksort - caso: {nombre_caso} - UMBRAL={umbral} ===")
            # medimos con lambda que aplica ord_rapida con el umbral
            resultados = medir_tiempo_ejecucion(lambda vec, u=umbral: ord_rapida(vec, u),
                                                generador, muestra_inicial, muestras, factor)
            mostrar_tiempo_rapida("ord_rapida", resultados, f"{nombre_caso} (umbral={umbral})")

# ------------------------------
# Comparación con Shell (práctica 2) - función para ejecutar ambas y comparar
# ------------------------------

def comparar_con_shell(muestra_inicial:int = 500, muestras:int = 6, factor:int = 2):
    """Compara tiempos de Quicksort y Shell (aleatorio) en el mismo esquema.
    Reutiliza seq_ciura y ord_shell si se desea comparación directa.
    """
    # importamos/definimos secuencias Shell y ord_shell (copiadas de práctica 2)
    def seq_ciura(limit: int) -> List[int]:
        seq = [1, 4, 10, 23, 57, 132, 301, 701, 1750]
        h = seq[-1]
        while True:
            nh = int(h * 2.25)
            if nh > limit:
                break
            seq.append(nh)
            h = nh
        return seq

    def seq_sedgewick(limit: int) -> List[int]:
        seq = []
        k = 0
        while True:
            h = 9 * (4**k) - 9 * (2**k) + 1
            if h > limit:
                break
            seq.append(h)
            k += 1
        return seq

    def seq_knuth(limit: int) -> List[int]:
        inc = []
        k = 1
        while True:
            val = (3**k - 1) // 2
            if val > limit:
                break
            inc.append(val)
            k += 1
        if inc and inc[0] != 1:
            inc.insert(0, 1)
        if not inc:
            inc = [1]
        return inc

    def seq_hibbard(limit:int) -> List[int]:
        inc = []
        k = 1
        while True:
            val = 2**k - 1
            if val > limit:
                break
            inc.append(val)
            k += 1
        if inc and inc[0] != 1:
            inc.insert(0, 1)
        if not inc:
            inc = [1]
        return inc

    def ord_shell(v: List[int], inc: List[int]) -> List[int]:
        n = len(v)
        m = len(inc)
        for k in range(m - 1, -1, -1):
            h = inc[k]
            for i in range(h, n):
                x = v[i]
                j = i
                while j >= h and v[j - h] > x:
                    v[j] = v[j - h]
                    j -= h
                v[j] = x
        return v

    # preparar secuencias
    v_max_size = (factor ** (muestras - 1)) * muestra_inicial
    secuencias = {
        "seq_ciura": seq_ciura(v_max_size-1),
        "seq_sedgewick": seq_sedgewick(v_max_size-1),
        "seq_knuth": seq_knuth(v_max_size-1),
        "seq_hibbard": seq_hibbard(v_max_size-1)
    }

    # comparar Quicksort (umbral 10, por ejemplo) vs Shell (Ciura)
    umbral = 10
    print(f"\n=== Comparación Quicksort(umbral={umbral}) vs Shell(seq_ciura) - caso ALEATORIO ===")
    resultados_q = medir_tiempo_ejecucion(lambda v: ord_rapida(v, umbral), aleatorio, muestra_inicial, muestras, factor)
    resultados_s = medir_tiempo_ejecucion(lambda v, inc=secuencias["seq_ciura"]: ord_shell(v, inc),
                                         aleatorio, muestra_inicial, muestras, factor)
    print("\n--- QuickSort ---")
    mostrar_tiempo_rapida("ord_rapida", resultados_q, f"aleatorio (umbral={umbral})")
    print("\n--- Shell (Ciura) ---")
    # usar la función de mostrar de la práctica 2 para shell — se toma una aproximación: mostrar_tiempo_ejecucion
    # Reutilizamos mostrar_tiempo_ejecucion original (versión simple adaptada aquí):
    def mostrar_tiempo_ejecucion(alg_name:str, v:dict, case:str) -> None:
        COTAS = {
        "ord_insercion": {
            "ascendente":  (0.8,  1,  1.2),
            "aleatorio":   (1.8, 2.0, 2.2),
            "descendente": (1.8, 2.0, 2.2),
        },
        "ord_shell": {
            "seq_hibbard":   (1.15,   1.22,   1.33),
            "seq_knuth":     (1.15,   1.21,   1.34),
            "seq_sedgewick": (1.15,   1.23,   1.32),
            "seq_ciura":     (1.1,    1.2,   1.30),
        },
        }
        print()
        print(f"**{alg_name} - caso: {case}**")
        # intentar extraer cotas si existen, sino usar n^1.2 como referencia
        if alg_name == "ord_shell" and case in COTAS["ord_shell"]:
            a,b,c = COTAS["ord_shell"][case]
        else:
            a,b,c = (1.0, 1.2, 1.4)
        c_sub, c_ajus, c_sob = f"t(n)/n^{a}", f"t(n)/n^{b}", f"t(n)/n^{c}"

        header = (f"{'n[-]':>8} {'t(n)[µs]':>14} {c_sub+'[µs]':>18}"
                  f"{c_ajus+'[µs]':>18} {c_sob+'[µs]':>18}")
        print(header)
        for n, (t_n, bucles) in v.items():
            v_c_sub = t_n / (n ** a)
            v_c_ajus = t_n /(n ** b)
            v_c_sob = t_n / (n ** c)
            print(f"{bucles}{n:8d} {t_n:14.3f} {v_c_sub:18.6g}"
                  f"{v_c_ajus:18.6g} {v_c_sob:18.6g}")
        print("\nNota: Si (*) -> 't(n)<1000' :"
            "tiempo promedio de K=1000 ejecuciones.\n")

    mostrar_tiempo_ejecucion("ord_shell", resultados_s, "seq_ciura")

# ------------------------------
# Bloque principal
# ------------------------------

if __name__ == "__main__":
    random.seed(42)  # reproducibilidad básica

    print("VALIDACIÓN inicial Quicksort (umbral=1):")
    ok = Test_quicksort(ord_rapida, aleatorio, 11, umbral=1)
    if not ok:
        print("Error en la implementación de Quicksort (umbral=1). Revise el código.")
    else:
        print("Validación correcta.\n")

    # Parámetros de medición (igual que práctica 2)
    muestra_inicial, muestras, factor = 500, 6, 2

    # Ejecutar experimentos (genera 9 tablas: 3 umbrales × 3 casos)
    experimento_completo(muestra_inicial, muestras, factor)

    # Comparación con Shell para visualizar diferencias
    comparar_con_shell(muestra_inicial, muestras, factor)

    print("\n--- FIN MEDICIONES PRÁCTICA 3 ---")
