import time
import random
from typing import Callable #solo para typing hints.

def suma_sub_max1(v:list) -> int:
    """
    Calcula la suma máxima de una subcadena contigua en la lista v usando un algoritmo O(n^2).

    Parámetros:
        v (list): Lista de enteros sobre la que se busca la suma máxima de una subcadena contigua.

    Retorna:
        int: Suma máxima de una subcadena contigua.
    """
    n = len(v)
    sumMax = 0
    for i in range(0, n):
        thisSum = 0
        for j in range(i, n):
            thisSum = thisSum + v[j]
            if thisSum > sumMax:
                sumMax = thisSum
    return sumMax

def suma_sub_max2(v:list) -> int:
    """
    Calcula la suma máxima de una subcadena contigua en la lista v usando un algoritmo O(n).

    Parámetros:
        v (list): Lista de enteros sobre la que se busca la suma máxima de una subcadena contigua.

    Retorna:
        int: Suma máxima de una subcadena contigua.
    """
    esta_suma = 0
    suma_max = 0
    for j in range(len(v)):
        esta_suma += v[j]
        if esta_suma > suma_max:
            suma_max = esta_suma
        elif esta_suma < 0:
            esta_suma = 0
    return suma_max

def print_and_test(secuencias: list, tamaño_secuencia_mayor: int) -> None: 
    """
    Valida los algoritmos suma_sub_max1 y suma_sub_max2 comparando sus resultados sobre varias secuencias.

    Parámetros:
        secuencias (list): Lista de listas de enteros a validar.
        tamaño_secuencia_mayor (int): Tamaño de la secuencia más grande para formato de impresión.

    Retorna:
        None
    """
    #"c2 validación de los algoritmos con función test" .
    tamaño_secuencia_mayor = tamaño_secuencia_mayor*4 + 2 
    #en el peor de los casos (todos los números negativos) 
    #cada número ocupa 4 caracteres 
    #más los dos carácteres de apertura y cierre de una lista "[" y "]".
    #El resto es formateo de texto.
    print(
        f"{'secuencia':{tamaño_secuencia_mayor}}" 
        f"{'Sumasubmax1':15} {'sumasubmax2':15} Iguales?"
        ) 
    for secuencia in secuencias:
        suma_algoritmo_1 = suma_sub_max1(secuencia)
        suma_algoritmo_2 = suma_sub_max2(secuencia)
        son_iguales = suma_algoritmo_1 == suma_algoritmo_2
        if son_iguales:
            print(
                f"{str(secuencia):{tamaño_secuencia_mayor}}"
                f"{suma_algoritmo_1:<15} {suma_algoritmo_2:<15} {son_iguales}"
                )
        else:
            raise Exception("No funcionan.")
    return None

def aleatorio(n):
    """
    Genera una lista de n enteros aleatorios en el rango [-n, n].

    Parámetros:
        n (int): Tamaño de la lista y rango de los valores aleatorios.

    Retorna:
        list: Lista de enteros aleatorios.
    """
    v=list(range(n))
    for i in v:
        v[i] = random.randint(-n, n)
    return v

def microsegundos():
    """
    Devuelve el tiempo actual en microsegundos desde el inicio del sistema.

    Retorna:
        float: Tiempo en microsegundos.
    """
    return time.perf_counter_ns()//1000 #Corrección, previamente división no entera

def tiempo_ejecucion(muestra: int, n:int, alg: Callable) -> dict:
    """
    Calcula el tiempo de ejecución promedio de un algoritmo sobre vectores aleatorios de tamaño creciente.

    Parámetros:
        muestra (int): Tamaño inicial de los vectores.
        n (int): Número de muestras (iteraciones).
        alg (Callable): Algoritmo a medir (función).

    Retorna:
        dict: Diccionario con el tamaño de muestra como clave y el tiempo promedio en microsegundos como valor.
    """
    vector_tiempo = {}
    for _ in range(n):
        bucles=" "
        vector = aleatorio(muestra)
        ta = microsegundos() #t_antes
        alg(vector) #No hace falta guardar el resultado en ninguna variable
        td = microsegundos() #t_después
        t = td-ta
        if t < 1000:
            bucles="*"
            K = 1000 # potencia de 10
            ta = microsegundos()
            for _ in range(K):
                alg(vector)
            td = microsegundos()
            t = (td - ta) / K
        vector_tiempo[muestra] = (t, bucles) #round(t, 4) #"e7" basta con tener
        #al menos tres cifras significativas.
        muestra = muestra*2 # "e5" progresión geométrica de razón 2
    return vector_tiempo

def mostrar_tiempo_ejecucion(alg:str,v:dict):
    """
    Muestra en pantalla los tiempos de ejecución y sus normalizaciones para un algoritmo dado.

    Parámetros:
        alg (str): Nombre del algoritmo ("suma_sub_max1" o "suma_sub_max2").
        v (dict): Diccionario con tamaños de entrada y tiempos de ejecución.

    Retorna:
        None
    """
    print()
    print(f"**{alg}**")
    if alg == "suma_sub_max2":
        n_c_su,n_c_so,n_c_ajus="t(n)/n^0.8","t(n)/n^1.2","t(n)/n"
    else:
        n_c_su,n_c_so,n_c_ajus="t(n)/n^1.8","t(n)/n^2.2","t(n)/n^2"
    print(
        f"{"n[-]":20} {"t(n)[µs]":>20} {n_c_su+"[µs]":>20}"
        f"{n_c_ajus+'[µs]':>20} {n_c_so+'[µs]':>20}"
        )

    for n, (t_n,bucles) in v.items():

        if alg == "suma_sub_max2":
            v_c_su,v_c_so,v_c_ajus= t_n/n**0.8,t_n/n**1.2,t_n/n
        else:
            v_c_su,v_c_so,v_c_ajus= t_n/n**1.8,t_n/n**2.2,t_n/n**2

        #if t_n < 1000:
        #    n = "*" + str(n) #El asterisco indica que recibieron
            #un tratamiento especial en el que se calculo K veces
            #el alg sobre el vector y se hizo promedio para obtener
            #un tiempo más preciso.

        print(f"{bucles}{n:>20} {t_n:>20} {v_c_su:>20} {v_c_ajus:>20} {v_c_so:>20}")
    print("\nSi (*) -> 't(n)<1000' : tiempo promedio de K=1000 ejecuciones.\n")

#2 - Validación de las secuencias tanto con las dadas en el pdf 
# como con las generadas de forma aleatoria por medio del módulo random:

secuencias = [[-9,2,-5,-4,6,3], [4,0,9,2,5], [-2,-1,-9,-7,-1], 
              [9,-2,1,-7,-8], [15,-2,-5,-4,16], [7,-5,6,7,-7]]
print_and_test(secuencias, 6)
print()
secuencias2 = []
for _ in range(10):
    secuencias2.append(aleatorio(10))
print_and_test(secuencias2,10)

#3 - Determinación de los tiempos de ejecución

#"c1 - plantilla de correcion" tiempos de procesado < 1ms:
#1000 microsegundos no son fiables por limitaciones 
#en la precisión del cronómetro. Necesitamos
#hacer un promedio para que la medida sea más precisa
#para ello ver diapositiva 5 de:
#"Técnicas para la verificación empírica de la complejidad - Tema 1".
#Nuestras funciones (algoritmos) no modifican la entrada (v)
#por lo que la correción cuando t<1000 es fácil.

vector_tiempo1 = tiempo_ejecucion(500, 5 , suma_sub_max1)
vector_tiempo2 = tiempo_ejecucion(500, 10, suma_sub_max2)

#"d1" -> K potencia 10, t=(td-ta)/K,n_i *2 o *10
#se miden 10 valores > 5(mínimo), > 7-8 ideal.
#Microsegundos() por definición jamás < 0 y
#es monotonamente creciente -> t_i siempre > 0
#todo t_i<1000µs tiene su estrategia.
#En principio cumple todos los requisitos para d1 = 1
#d1-> apartado de correción y requisitos sacados de:
#"Técnicas para la verificación empírica de la complejidad - Tema 1".


#4 - Determinación de los tiempos de ejecución.
print()
mostrar_tiempo_ejecucion("suma_sub_max2",vector_tiempo2)
mostrar_tiempo_ejecucion("suma_sub_max1",vector_tiempo1)