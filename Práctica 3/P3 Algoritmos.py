import time
import random
from typing import Callable

def microsegundos() -> float:
    """
    Devuelve el tiempo actual en microsegundos desde el inicio del sistema.
    Retorna:
        float: Tiempo en microsegundos.
    """
    return time.perf_counter_ns() // 1000

def generar_vector(n: int, tipo: str) -> list:
    """
    Genera un vector de tamaño n según el tipo indicado.
    Parámetros:
        n (int): tamaño del vector.
        tipo (str): 'aleatorio', 'ascendente' o 'descendente'.
    Retorna:
        list[int]: vector generado.
    """
    if tipo == "aleatorio":
        v = [random.randint(0, 10**9) for _ in range(n)]
    elif tipo == "ascendente":
        v = list(range(n))
    elif tipo == "descendente":
        v = list(range(n, 0, -1))
    else:
        raise ValueError("tipo debe ser 'aleatorio', 'ascendente' o 'descendente'")
    return v

def tiempo_ejecucion_quicksort(muestra_inicial: int, pasos: int, 
                               ratio: int, alg: Callable, umbral: int, 
                               tipo: str = "aleatorio") -> dict:
    """
    Calcula el tiempo de ejecución de Quicksort (mediana3 + inserción)
    siguiendo el método empírico de la práctica 1:
      - mide tiempo t
      - si t < 1000 µs, repite K = 1000 veces regenerando el vector
        y promedia (t1 - t2)/K
      - marca con '*' las mediciones corregidas

    Parámetros:
        muestra_inicial (int): tamaño inicial del vector
        pasos (int): número de tamaños a medir
        ratio (int): razón geométrica (2 o 10)
        alg (Callable): algoritmo de ordenación a medir
        umbral (int): umbral de inserción para quicksort
        tipo (str): 'aleatorio', 'ascendente' o 'descendente'

    Retorna:
        dict: { n : (tiempo_en_µs, marca) }
    """
    resultados = {}
    n = muestra_inicial
    for _ in range(pasos):
        marca = ""
        v = generar_vector(n, tipo)
        ta = microsegundos()
        alg(v, umbral)
        td = microsegundos()
        t = td - ta

        # Caso t < 1 ms → estrategia empírica (K = 1000)
        if t < 1000:
            marca = "*"
            K = 1000
            # medir t1: K veces (init + alg)
            ta = microsegundos()
            for _ in range(K):
                v = generar_vector(n, tipo)
                alg(v, umbral)
            td = microsegundos()
            t1 = td - ta

            # medir t2: K veces solo generación (para restar coste)
            ta = microsegundos()
            for _ in range(K):
                _ = generar_vector(n, tipo)
            td = microsegundos()
            t2 = td - ta

            t = (t1 - t2) / K

        if t < 0:
            raise Exception("Tiempo negativo: verifique el cronómetro o el hardware.")

        resultados[n] = (t, marca)
        n *= ratio  # progresión geométrica (2 o 10)
    return resultados
