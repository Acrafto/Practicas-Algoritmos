import time
import random
from typing import Callable

def ord_insercion(v: list) -> list:
    """Ordena una lista usando el algoritmo de ordenación por inserción.

    Realiza la ordenación in-place y devuelve la misma lista ordenada.

    Parameters
    ----------
    v : list
        Lista de elementos comparables a ordenar.

    Returns
    -------
    list
        La lista `v` ordenada de forma ascendente.
    """
    n = len(v)
    for i in range(1, n):
        x = v[i]
        j = i - 1
        while j >= 0 and v[j] > x:
            v[j+1] = v[j]
            j -= 1
        v[j+1] = x
    return v

def ord_shell(v: list[int], inc: list[int]) -> list:
    """Ordena una lista usando el algoritmo de ordenación Shell
    con incrementos dados.
    El algoritmo realiza incrementos (gaps) según la secuencia `inc` y
    aplica inserción sobre sublistas separadas por cada gap.
    La ordenación es in-place y devuelve la misma lista ordenada.

    Parameters
    ----------
    v : list[int]
        Lista de enteros a ordenar.
    inc : list[int]
        Secuencia de incrementos (gaps) a usar para Shell sort. Debe contener
        enteros positivos menores que len(v), normalmente en orden creciente.

    Returns
    -------
    list[int]
        La lista `v` ordenada de forma ascendente.
    """
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

def aleatorio(size:int):
    """Genera lista de n enteros aleatorios en el rango [-n, n].

    Parameters
    ----------
    size : int
        Tamaño del vector a generar.

    Returns
    -------
    list[int]
        Lista de `size` enteros aleatorios en el intervalo [-size, size].
    """
    return [random.randint(-size,size) for _ in range(size)]

def ascendente(size:int):
    """Genera una lista ordenada ascendentemente de 1 a n.

    Parameters
    ----------
    size : int
        Tamaño de la lista a generar.

    Returns
    -------
    list[int]
        Lista [1, 2, ..., size].
    """
    return list(range(1, size+1))

def descendente(size:int):
    """Genera una lista ordenada descendentemente de n a 1.

    Parameters
    ----------
    size : int
        Tamaño de la lista a generar.

    Returns
    -------
    list[int]
        Lista [size, size-1, ..., 1].
    """
    return list(range(size, 0, -1))

def microsegundos():
    """Devuelve el tiempo actual en microsegundos desde el inicio del sistema.

    Se utiliza `time.perf_counter_ns()` y se convierte a microsegundos.
    Es útil como cronómetro interno para medir duraciones cortas.

    Parameters
    ----------
    None

    Returns
    -------
    int
        Tiempo actual en microsegundos (entero).
    """
    return time.perf_counter_ns() // 1000

def ordenado(v:list[int]) -> bool:
    """Comprueba si una lista está ordenada ascendentemente.

    Parameters
    ----------
    v : list[int]
        Lista a comprobar.

    Returns
    -------
    bool
        True si `v` está ordenada de forma no decreciente,
        False en caso contrario.
    """
    n = len(v)
    for i in range(1, n):
        if v[i] < v[i-1]:
            return False
    return True

def Test_sort_algorithms(ord_shell:Callable, ord_insercion:Callable,
gen_vector:Callable, size_vector:int) -> bool:
    """Valida el correcto funcionamiento de los algoritmos de ordenación.
    Ejecuta tests básicos mostrando resultados por pantalla según el formato
    del enunciado. Prueba Shell sort con distintas secuencias de incrementos
    y comprobación con insertion sort en casos específicos.
    """
    ord_insercion_correct, ord_shell_correct, inc_seq = True, True, []
    secuencias = (seq_hibbard, seq_knuth, seq_sedgewick, seq_ciura)
    casos_insercion = (descendente, aleatorio, ascendente)
    for secuencia in secuencias:
        inc_seq.append(secuencia(size_vector))
    for i in range(7):
        if i < 4:
            print("Inicialización Aleatoria:")
            v = gen_vector(size_vector)
            print(v)
            print(f"Ordenación Shell Incrementos {secuencias[i].__name__}")
            resultado = ord_shell(v, inc_seq[i])
            print(resultado)
            is_sorted = ordenado(resultado)
            print("Ordenado?", is_sorted, "\n")
            if not is_sorted:
                ord_shell_correct = False
        else:
            print(f"Inicialización {casos_insercion[i-4].__name__}:")
            v = casos_insercion[i-4](size_vector)
            print(v)
            resultado = ord_insercion(v)
            print(resultado)
            is_sorted = ordenado(resultado)
            print("Ordenado?", is_sorted, "\n")
            if not is_sorted:
                ord_insercion_correct = False
    if ord_insercion_correct and ord_shell_correct:
        print("\nLos algoritmos funcionan correctamente.")
        return True
    else:
        print("No funcionan")
        return False

def medir_tiempo_ejecucion(alg: Callable, gen_vector: Callable,
                           muestra_inicial:int,
                           muestras:int, factor:int=2) -> dict:
    """Mide el tiempo de ejecución de un algoritmo de ordenación.

    Aplica corrección empírica para tiempos pequeños (< 1000 µs) realizando
    K ejecuciones para obtener un promedio más estable.
    Parameters
    """
    vector_tiempo = {}
    n = muestra_inicial
    for _ in range(muestras):
        vector = gen_vector(n)
        ta = microsegundos()
        alg(vector)
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
            raise Exception("El cronómetro interno de tu PC"
            "no funciona correctamente intente la medición en otro ordenador.")
        vector_tiempo[n] = (t, bucles)
        n = n * factor
    return vector_tiempo

def mostrar_tiempo_ejecucion(alg_name:str, v:dict, case:str) -> None:
    """Muestra en pantalla una tabla con los tiempos y sus normalizaciones.

    Calcula y presenta t(n) y normalizaciones t(n)/n^p para los exponentes
    teóricos esperados según `COTAS`.
    Parameters
    """
    COTAS = {
    "ord_insercion": {
        "ascendente":  (0.8,  1,  1.2),  # Θ(n) mejor caso
        "aleatorio":   (1.8, 2.0, 2.2),  # Θ(n^2)
        "descendente": (1.8, 2.0, 2.2),  # Θ(n^2)
    },
    "ord_shell": {
        "seq_hibbard":   (1.15,   1.22,   1.33),   # ~ n^{3/2}
        "seq_knuth":     (1.15,   1.21,   1.34),   # ~ n^{3/2}
        "seq_sedgewick": (1.15,   1.23,   1.32),   # ~ n^{4/3}
        "seq_ciura":     (1.1,    1.2,   1.30),  # ~ n^{1.25} aprox.
    },
    }
    print()
    print(f"**{alg_name} - caso: {case}**")
    a, b, c = COTAS[alg_name][case]
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

def seq_ciura(limit: int) -> list[int]:
    """Devuelve la secuencia de incrementos de Ciura hasta un límite dado.

    Parte de la secuencia de Ciura conocida y la extiende
    multiplicando por ~2.25
    hasta que el siguiente incremento supere `limit`.

    Parameters
    ----------
    limit : int
        Límite superior para los incrementos (normalmente relacionado con n).

    Returns
    -------
    list[int]
        Secuencia de incrementos en orden creciente, terminando con el mayor
        h <= limit.
    """
    seq = [1, 4, 10, 23, 57, 132, 301, 701, 1750]
    h = seq[-1]
    while True:
        nh = int(h * 2.25)
        if nh > limit:
            break
        seq.append(nh)
        h = nh
    return seq

def seq_sedgewick(limit: int) -> list[int]:
    """Devuelve la secuencia de incrementos de Sedgewick hasta un límite dado.

    Usa la fórmula de Sedgewick (1982): h_k = 9*4^k - 9*2^k + 1 y recoge todos
    los h_k <= limit en orden creciente.

    Parameters
    ----------
    limit : int
        Límite superior para la secuencia de incrementos.

    Returns
    -------
    list[int]
        Lista de incrementos de Sedgewick hasta `limit`.
    """
    seq = []
    k = 0
    while True:
        h = 9 * (4**k) - 9 * (2**k) + 1
        if h > limit:
            break
        seq.append(h)
        k += 1
    return seq

def seq_knuth(limit: int):
    """Genera la secuencia de Knuth hasta un límite dado.

    La secuencia está definida por h_k = (3^k - 1)/2. Se generan valores
    crecientes hasta que superan `limit`.
    Se asegura que la secuencia contenga 1.

    Parameters
    ----------
    limit : int
        Límite superior para la secuencia de incrementos.

    Returns
    -------
    list[int]
        Secuencia de incrementos de Knuth (al menos [1]).
    """
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

def seq_hibbard(limit:int):
    """Genera la secuencia de Hibbard (2^k - 1) hasta un límite dado.

    Parameters
    ----------
    limit : int
        Límite superior para la secuencia de incrementos.

    Returns
    -------
    list[int]
        Secuencia de incrementos de Hibbard (al menos [1]).
    """
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

if __name__ == "__main__":
    # random.seed(4)
    # for _ in range(2):
    #     print(aleatorio(10))
    # random.seed(42)
    # for _ in range(2):
    #     print(aleatorio(10))

    print("VALIDACIÓN inicial de algoritmos:")
    Test_sort_algorithms(ord_shell, ord_insercion, aleatorio, 11)
#-----------------
    muestra_inicial, muestras, factor = 500, 6, 2
    v_max_size = (factor**(muestras-1))*muestra_inicial
#-----------------
    # Insertion Sort
    casos_insertion = [
        ("ASCENDENTE (mejor caso)", ascendente),
        ("DESCENDENTE (peor caso)", descendente),
        ("ALEATORIO (medio)", aleatorio),
    ]

    for nombre, generador in casos_insertion:
        print(f"\n=== Mediciones Insertion Sort - caso {nombre} ===")
        #Previously we created a list of tuples, then we iterate throught
        #each tuple extracting each element, then we call the
        #"medir_tiempo_ejecucion"
        resultados = medir_tiempo_ejecucion(ord_insercion, generador,
                                           muestra_inicial, muestras, factor)
        mostrar_tiempo_ejecucion(ord_insercion.__name__, resultados,
                                 generador.__name__)

    # Shell Sort
    secuencias = {
        "seq_ciura": seq_ciura(v_max_size-1),
        "seq_sedgewick": seq_sedgewick(v_max_size-1),
        "seq_knuth": seq_knuth(v_max_size-1),
        "seq_hibbard": seq_hibbard(v_max_size-1)
    }

    for nombre, inc in secuencias.items():
        print(f"\n=== Mediciones Shell Sort - secuencia: {nombre} ===")
        resultados = medir_tiempo_ejecucion(lambda v, inc_seq=inc:
                                            ord_shell(v, inc_seq),
                                           aleatorio, muestra_inicial,
                                           muestras, factor)
        mostrar_tiempo_ejecucion(ord_shell.__name__, resultados,
                                 nombre)

    print("\n--- FIN MEDICIONES ---")

    Putas mierdas jajaja