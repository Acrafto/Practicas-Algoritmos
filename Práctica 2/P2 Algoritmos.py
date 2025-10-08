import time
import random
from typing import Callable #solo para typing hints.
def Insertion_sort(v:list)->list:
    n=len(v)
    for i in range(1,n):
        x=v[i]
        j=i-1
        while j>=0 and v[j]>x:
            v[j+1]=v[j]
            j-=1
        v[j+1]=x 
       
    return v

def Shell_sort(v:list,inc:list)->list:#Where inc is a list of increments
    n=len(v)
    m=len(inc)
    for k in range(m - 1, -1, -1):  
        h=inc[k]
        for i in range(h,n):
            x=v[i]
            j=i
            while j>=h and v[j - h]>x:
                v[j]=v[j - h]
                j=j - h
            v[j]=x
    return v

def ordered(v:list)->bool:
    n=len(v)
    for i in range(1,n):
        if v[i]<v[i-1]:
            return False
    return True
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

def Test_sort_algorithms(Shell_sort:Callable, Insertion_sort:Callable, List_generator:Callable) -> bool:
    # Test both sorting algorithms with different sequences
    inc_sec_ciura = [1, 4, 10, 23, 57, 132, 301, 701, 1750] # Ciura increments
    inc_sec_sedgewick = [1, 5, 19, 41, 109, 209, 505, 929, 2161] # Sedgewick increments
    incs = [inc_sec_ciura, inc_sec_sedgewick]
    Insertion_sort_correct = True
    Shell_sort_correct = True

    secuencias_Insertion = [
        List_generator(5),
        List_generator(10),
        List_generator(50)
    ]
    secuencias_Shell = [
        [7, 4, -1, -4, -6, 0, -8, -11, 8, -3, -4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1]
    ]

    for secuencia in secuencias_Insertion: # Insertion Sort testing
        secuencia_ordenada = Insertion_sort(secuencia.copy()) # Using a copy here to avoid modifying the original
        if not ordered(secuencia_ordenada):
            Insertion_sort_correct = False

    for i in range(len(secuencias_Shell)):#Shell testing
        secuencia = secuencias_Shell[i].copy() 
        inc = incs[i]
        secuencia_ordenada = Shell_sort(secuencia, inc)
        if not ordered(secuencia_ordenada):
            Shell_sort_correct = False

    if Insertion_sort_correct and Shell_sort_correct: 
        print("Los algoritmos funcionan correctamente") # The algorithms work correctly
        return True
    else:
        if not Insertion_sort_correct:
            print("Error en Insertion_sort") # Error in Insertion_sort
        if not Shell_sort_correct:
            print("Error en Shell_sort") # Error in Shell_sort
        print("Error en los algoritmos") # Error in the algorithms
        return False

Test_sort_algorithms(Shell_sort,Insertion_sort,aleatorio)

