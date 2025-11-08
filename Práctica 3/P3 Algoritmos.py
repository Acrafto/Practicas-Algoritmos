import time
import random
from typing import Callable, List, Tuple, Dict
import math

# ------------------------------
# Algoritmos de ordenación
# ------------------------------

def ord_insercion(v: list) -> list:
    """
    Ordena una lista mediante el algoritmo de ordenación por inserción.

    Args:
        v (list): Lista de números enteros a ordenar.

    Returns:
        list: Lista ordenada de menor a mayor.
    """
    n = len(v)
    for i in range(1, n):
        x = v[i]
        j = i - 1
        while j >= 0 and v[j] > x:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = x
    return v


def mediana3(v: List[int], i: int, j: int) -> None:
    """
    Reorganiza tres elementos (v[i], v[k], v[j]) para elegir el pivote
    como la mediana de los tres valores.

    Args:
        v (List[int]): Lista de enteros.
        i (int): Índice inicial del subvector.
        j (int): Índice final del subvector.

    Side effects:
        Modifica la lista en su lugar, colocando el pivote en v[i].
    """
    k = (i + j) // 2
    if v[k] > v[j]:
        v[k], v[j] = v[j], v[k]
    if v[k] > v[i]:
        v[k], v[i] = v[i], v[k]
    if v[i] > v[j]:
        v[i], v[j] = v[j], v[i]


def ord_rapida_aux(v: List[int], izq: int, der: int, umbral: int) -> None:
    """
    Función recursiva auxiliar para el algoritmo de ordenación rápida.
    Utiliza la mediana de tres y detiene la recursión si el tamaño del
    subvector es menor que el umbral especificado.

    Args:
        v (List[int]): Lista de enteros a ordenar.
        izq (int): Índice del extremo izquierdo del subvector.
        der (int): Índice del extremo derecho del subvector.
        umbral (int): Límite inferior para aplicar ordenación por inserción.

    Side effects:
        Modifica la lista 'v' en su lugar.
    """
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
    """
    Implementa el algoritmo de ordenación rápida (QuickSort) con selección
    del pivote mediante mediana de tres. Aplica ordenación por inserción
    cuando el tamaño de los subproblemas es menor que el umbral.

    Args:
        v (List[int]): Lista de enteros a ordenar.
        umbral (int): Tamaño mínimo de subvector para usar QuickSort.

    Returns:
        List[int]: Lista ordenada.
    """
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

def aleatorio(size: int) -> List[int]:
    """
    Genera un vector de enteros aleatorios en el rango [-size, size].

    Args:
        size (int): Tamaño del vector a generar.

    Returns:
        List[int]: Vector aleatorio de tamaño 'size'.
    """
    return [random.randint(-size, size) for _ in range(size)]


def ascendente(size: int) -> List[int]:
    """
    Genera un vector ordenado de forma ascendente.

    Args:
        size (int): Tamaño del vector.

    Returns:
        List[int]: Vector con números del 1 al 'size'.
    """
    return list(range(1, size + 1))


def descendente(size: int) -> List[int]:
    """
    Genera un vector ordenado de forma descendente.

    Args:
        size (int): Tamaño del vector.

    Returns:
        List[int]: Vector con números de 'size' hasta 1.
    """
    return list(range(size, 0, -1))


def microsegundos() -> int:
    """
    Devuelve el tiempo actual en microsegundos usando un reloj de alta resolución.

    Returns:
        int: Tiempo en microsegundos.
    """
    return time.perf_counter_ns() // 1000


def ordenado(v: List[int]) -> bool:
    """
    Verifica si una lista está ordenada de forma no decreciente.

    Args:
        v (List[int]): Lista de enteros.

    Returns:
        bool: True si está ordenada, False en caso contrario.
    """
    return all(v[i] >= v[i - 1] for i in range(1, len(v)))


# ------------------------------
# Medición de tiempos
# ------------------------------

def medir_tiempo_ejecucion(alg: Callable, gen_vector: Callable,
                           muestra_inicial: int,
                           muestras: int, factor: int = 2) -> dict:
    """
    Mide los tiempos de ejecución de un algoritmo de ordenación para varios tamaños
    de entrada, aplicando corrección cuando el tiempo es inferior a 1000 µs.

    Args:
        alg (Callable): Función de ordenación a evaluar.
        gen_vector (Callable): Función generadora del vector de prueba.
        muestra_inicial (int): Tamaño inicial de n.
        muestras (int): Número de tamaños a evaluar.
        factor (int, optional): Factor de crecimiento de n (por defecto 2).

    Returns:
        dict: Diccionario {n: (tiempo, indicador)} con los tiempos promedio.
    """
    vector_tiempo: Dict[int, Tuple[float, str]] = {}
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
        n *= factor
    return vector_tiempo


# ------------------------------
# Presentación de resultados
# ------------------------------

def mostrar_tiempo_rapida(alg_name: str, v: dict, case: str) -> None:
    """
    Imprime en consola una tabla con los tiempos de ejecución y las columnas
    normalizadas para el algoritmo de ordenación rápida.

    Args:
        alg_name (str): Nombre del algoritmo.
        v (dict): Diccionario con resultados {n: (t, indicador)}.
        case (str): Tipo de inicialización del vector.
    """
    print()
    print(f"**{alg_name} - caso: {case}**")
    header = (f"{'n[-]':>8} {'t(n)[µs]':>14} {'t(n)/(n·log2n)':>20}"
              f"{'t(n)/n^1.3':>18} {'t(n)/n^2':>18}")
    print(header)
    for n, (t_n, bucles) in v.items():
        denom_log = 1.0 if n <= 1 else n * math.log2(n)
        v1 = t_n / denom_log
        v2 = t_n / (n ** 1.3)
        v3 = t_n / (n ** 2)
        print(f"{bucles}{n:8d} {t_n:14.3f} {v1:20.6g}{v2:18.6g}{v3:18.6g}")
    print("\nNota: Si (*) -> 't(n)<1000' : tiempo promedio de K=1000 ejecuciones.\n")


# ------------------------------
# Validación y experimentos
# ------------------------------

def Test_quicksort(ord_rapida: Callable, gen_vector: Callable,
                   size_vector: int, umbral: int) -> bool:
    """
    Valida el correcto funcionamiento del algoritmo QuickSort verificando
    que el resultado esté efectivamente ordenado.

    Args:
        ord_rapida (Callable): Función principal del algoritmo.
        gen_vector (Callable): Generador de vector de prueba.
        size_vector (int): Tamaño del vector a ordenar.
        umbral (int): Valor del umbral utilizado.

    Returns:
        bool: True si el algoritmo ordena correctamente, False si falla.
    """
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


def experimento_completo(muestra_inicial: int = 500,
                         muestras: int = 6, factor: int = 2):
    """
    Ejecuta los experimentos completos de medición de tiempos para QuickSort
    con los tres valores de umbral y los tres casos de inicialización.

    Args:
        muestra_inicial (int, optional): Tamaño inicial de los vectores.
        muestras (int, optional): Número de tamaños de entrada.
        factor (int, optional): Factor de crecimiento entre tamaños.
    """
    umbrales = [1, 10, 100]
    casos = [
        ("ascendente", ascendente),
        ("descendente", descendente),
        ("aleatorio", aleatorio)
    ]

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
    """
    Punto de entrada del programa. Realiza una validación inicial del
    algoritmo y ejecuta los experimentos de medición de tiempos completos.
    """
    print("VALIDACIÓN inicial Quicksort (umbral=1):")
    ok = Test_quicksort(ord_rapida, aleatorio, 11, umbral=1)
    if not ok:
        print("Error en la implementación de Quicksort (umbral=1). Revise el código.")
    else:
        print("Validación correcta.\n")

    muestra_inicial, muestras, factor = 500, 6, 2
    experimento_completo(muestra_inicial, muestras, factor)

    print("\n--- FIN MEDICIONES PRÁCTICA 3 ---")
