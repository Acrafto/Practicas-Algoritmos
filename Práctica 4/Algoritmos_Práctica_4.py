from collections.abc import Callable 
import random
import time

##Importación de datos
def leer_sinonimos(nombre="sinonimos.txt"):
    datos = []
    with open(nombre, "r", encoding="utf-8") as f:
        for linea in f:
            clave, sinonimos = linea.strip().split("\t", 1)
            datos.append((clave, sinonimos))
    return datos#Lista de 19062 tuplas (clave, sinonimos)

#Funciones de dispersión A y B
def dispersionA(clave : str, tamTabla : int) -> int:
    n = min(8, len(clave))
    valor = ord(clave[0])
    for i in range(1, n):
        valor += ord(clave[i])
    return valor % tamTabla

def dispersionB(clave : str, tamTabla : int) -> int:
    n = min(8, len(clave))
    valor = ord(clave[0])
    for i in range(1, n):
        valor = ((valor * 32) + ord(clave[i])) # desplazamiento de 5 bits equivale
    return valor % tamTabla # a multiplicar por 32

#Clase auxiliar para la tabla de dispersión abierta
class Nodo:
    def __init__(self, clave : str, sinonimos : str):
        self.clave = clave
        self.sinonimos = sinonimos
        self.siguiente = None

#Tabla de dispersión abierta con listas enlazadas para manejar colisiones
class TablaAbierta:
    def __init__(self, tam : int, dispersion : Callable[[str, int], int]):
        self.tabla = [None] * tam
        self.tam = tam
        self.dispersion = dispersion
    
    def buscar(self, clave: str) -> tuple[ str | None, int]: #Basicamente pide devolver el nodo y el numero de colisiones que hubo
        indice=self.dispersion(clave,self.tam)
        item=self.tabla[indice]
        if item is None:
            return None,0 #Si no hay nada en esa posicion, no hay colisiones y no existe la clave
        colisiones=0
        while item is not None:
            if item.clave==clave:
                return item.sinonimos,colisiones #Recordar que los elementos de la tabla son nodos que tienen clave y sinonimos
            item=item.siguiente
            colisiones+=1
        return None, colisiones


    def insertar(self, clave: str, sinonimos:str) -> int: #Devolver el numero de colisiones que hubo al insertar
        indice = self.dispersion(clave, self.tam)
        nuevo_nodo = Nodo(clave, sinonimos)
        
        if self.tabla[indice] is None:
            self.tabla[indice] = nuevo_nodo
            return 0 
            
        else:
            nuevo_nodo.siguiente = self.tabla[indice]
            self.tabla[indice] = nuevo_nodo
            return 1 #Colisión al insertar en una lista enlazada, no entiendo muy bien por qué pediría mostrar las colisiones
                    #si siempre pide insertar al inicio y por tanto siempre hay sólo una colisión si ya hay algo en esa posición

    def mostrar(self):
        for i, item in enumerate(self.tabla):#enumerate es una función incorporada en Python que permite iterar sobre una secuencia y
                                            #da tanto el índice como el valor de cada elemento en cada iteración.
            print(f"Índice {i}: ", end="")
            actual = item
            while actual is not None:
                print(f"({actual.clave}: {actual.sinonimos}) -> ", end="")
                actual = actual.siguiente
            print("None")

#Funciones de exploración para la tabla de dispersión cerrada
def exploracion_lineal(pos_ini: int, intento: int) -> int:
    return pos_ini + intento

def exploracion_cuadratica(pos_ini: int, intento: int) -> int:
    return pos_ini + intento**2 #pareciera algo simple, pero es simplemente elevar al cuadrado el intento cada vez
def exploracion_doble(pos_ini: int, intento: int) -> int: #Con R de 10007 según el pdf
    R = 10007
    paso = R - (pos_ini % R)
    return pos_ini + intento * paso
#Clase auxiliar para la tabla de dispersión cerrada
class Entrada:
    def __init__(self):
        self.ocupada = False   # Indica si la casilla contiene un dato válido [cite: 57]
        self.clave = None      # La clave almacenada [cite: 57]
        self.sinonimos = None  # Los sinónimos almacenados [cite: 58]

class TablaCerrada:
    def __init__(self, tam : int, dispersion : Callable[[str, int], int],
        resol_colisiones : Callable[[int, int], int]):
        self.tabla = [Entrada() for _ in range(tam)]
        self.tam = tam
        self.dispersion = dispersion
        self.resol_colisiones = resol_colisiones

    def buscar(self, clave : str) -> tuple[str | None, int]:
        indice = self.dispersion(clave, self.tam)
        intento = 0
        colisiones = 0

        while intento < self.tam:
            nueva_pos = self.resol_colisiones(indice, intento) % self.tam
            entrada = self.tabla[nueva_pos]

            if not entrada.ocupada:
                return None, colisiones  # La clave no está en la tabla

            if entrada.clave == clave:
                return entrada.sinonimos, colisiones  # Clave encontrada

            intento += 1
            colisiones += 1

        return None, colisiones  # La clave no está en la tabla después de revisar todas las posiciones
    
    def insertar(self, clave : str, sinonimos : str) -> int:
        indice = self.dispersion(clave, self.tam)
        intento = 0
        colisiones = 0

        while intento < self.tam:
            nueva_pos = self.resol_colisiones(indice, intento) % self.tam
            entrada = self.tabla[nueva_pos]
            if entrada.ocupada and entrada.clave == clave:
                return colisiones  # La clave ya existe, no se inserta. Esto creo que no haria falta si el .txt 
                                    #esta libre de claves repetidas, pero uno nunca sabe  
            if not entrada.ocupada:
                entrada.clave = clave
                entrada.sinonimos = sinonimos
                entrada.ocupada = True
                return colisiones  # Retorna el número de colisiones al insertar
            intento += 1
            colisiones += 1

        raise Exception("Tabla llena, no se puede insertar")#No debería raisear esto generalmente
    
    def mostrar(self):
        for i, entrada in enumerate(self.tabla):
            if entrada.ocupada:
                print(f"Índice {i}: ({entrada.clave}: {entrada.sinonimos})")
            else:
                print(f"Índice {i}: None")

#Validaciones y verificaciones del punto 2
def dispersionTestTeoria(clave: str, tam_tabla: int) -> int:
    if clave in ("ANA", "JOSE", "OLGA"):
        return 7
    return 6

def exploracion_dobleTeoria(pos_ini: int, intento: int) -> int:
    R = 5
    paso = R - (pos_ini % R)
    return pos_ini + intento * paso

def validar_tabla_abierta(tabla: TablaAbierta):
    """
    Función para validar una tabla abierta con los datos de prueba del enunciado.
    """
    datos = ["ANA", "LUIS", "JOSE", "ROSA", "OLGA", "IVAN"]    
    Carlos="CARLOS"#Xd
    total_colisiones = 0
    for dato in datos:
        colisiones = tabla.insertar(dato, "sinonimo") # Aquí se puede usar un sinonimo genérico para la prueba    
        total_colisiones += colisiones
    tabla.mostrar()
    print(f"Número total de colisiones al insertar los elementos: {total_colisiones}")
    for dato in datos:
        encontrado, colisiones=tabla.buscar(dato)
        print(f"Al buscar:\"{dato}\", encuentro: {encontrado}, colisiones: {colisiones}")
    encontrado,colisiones=tabla.buscar(Carlos)
    
    if encontrado is None:
        print(f"No encuentro: {Carlos}, colisiones: {colisiones}")
    else:
        print(f"Error: Carlos sabe dónde vives, y va a por ti")#Carlos da miedo
    return tabla

def validar_tabla_cerrada(tabla: TablaCerrada):
    """
    Función para validar una tabla cerrada con los datos de prueba del enunciado.
    """
    datos = ["ANA", "LUIS", "JOSE", "ROSA", "OLGA", "IVAN"]   
    Carlos="CARLOS"
    total_colisiones = 0
    for dato in datos:
        colisiones = tabla.insertar(dato, "sinonimo")     
        total_colisiones += colisiones
    tabla.mostrar()
    print(f"Número total de colisiones al insertar los elementos: {total_colisiones}")
    for dato in datos:
        encontrado, colisiones=tabla.buscar(dato)
        print(f"Al buscar:\"{dato}\", encuentro: {encontrado}, colisiones: {colisiones}")
    encontrado,colisiones=tabla.buscar(Carlos)
    if encontrado is None:
        print(f"No encuentro: {Carlos}, colisiones: {colisiones}")
    else:
        print(f"Error: Carlos se ha vuelto a colar en la tabla, nadie está a salvo")#Dios se ampare de nosotros
    return tabla


def validar_tablas():
    """
    Función para validar las tablas con los datos de prueba del enunciado.
    """        
    print("** TEST TABLA ABIERTA")
    tabla_abierta=TablaAbierta(10, dispersionTestTeoria)
    validar_tabla_abierta(tabla_abierta)
    print()
    print("** TEST TABLA CERRADA LINEA")
    tabla_cerrada_lineal=TablaCerrada(10, dispersionTestTeoria, exploracion_lineal)
    validar_tabla_cerrada(tabla_cerrada_lineal)
    print()
    print("** TEST TABLA CERRADA CUADRATICA")
    tabla_cerrada_cuadratica=TablaCerrada(10, dispersionTestTeoria, exploracion_cuadratica)
    validar_tabla_cerrada(tabla_cerrada_cuadratica)
    print()
    print("** TEST TABLA CERRADA DOBLE")
    tabla_cerrada_doble=TablaCerrada(10, dispersionTestTeoria, exploracion_dobleTeoria)
    validar_tabla_cerrada(tabla_cerrada_doble)
    return True

##Conteo de Colisiones punto 3
def insertar_datos_y_contar_colisiones(tabla: TablaAbierta| TablaCerrada, datos: list[tuple[str, str]]) -> int:#Pequeña función para no repetir código 
                                                                                                            #al insertar los datos y contar las colisiones de todas las tablas
    """                                                                                                        
    Inserta los datos en la tabla y cuenta las colisiones totales.
    Devuelve el número total de colisiones.
    """   
    total_colisiones = 0                                                                            
    for clave, sinonimos in datos:
        colisiones = tabla.insertar(clave, sinonimos)
        total_colisiones += colisiones
    return total_colisiones

def conteos_tabla_abierta(datos: list[tuple[str, str]]):
    #A
    tabla_abierta_A=TablaAbierta(20011, dispersionA)
    total_colisiones_abierta_A=insertar_datos_y_contar_colisiones(tabla_abierta_A, datos)
    print(f"Total colisiones Tabla Abierta Dispersion A: {total_colisiones_abierta_A}")
    #B
    tabla_abierta_B=TablaAbierta(20011, dispersionB)
    total_colisiones_abierta_B=insertar_datos_y_contar_colisiones(tabla_abierta_B, datos)
    print(f"Total colisiones Tabla Abierta Dispersion B: {total_colisiones_abierta_B}")
    print()
    return tabla_abierta_A, tabla_abierta_B

def conteos_tabla_cerrada_disp_A(datos: list[tuple[str, str]]):
    #A Lineal
    tabla_cerrada_lineal_A=TablaCerrada(20011, dispersionA, exploracion_lineal)
    total_colisiones_cerrada_lineal_A=insertar_datos_y_contar_colisiones(tabla_cerrada_lineal_A, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Lineal: {total_colisiones_cerrada_lineal_A}")
    #A Cuadratica
    tabla_cerrada_cuadratica_A=TablaCerrada(20011, dispersionA, exploracion_cuadratica)
    total_colisiones_cerrada_cuadratica_A=insertar_datos_y_contar_colisiones(tabla_cerrada_cuadratica_A, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Cuadratica: {total_colisiones_cerrada_cuadratica_A}")
    #A Doble
    tabla_cerrada_doble_A=TablaCerrada(20011, dispersionA, exploracion_doble)
    total_colisiones_cerrada_doble_A=insertar_datos_y_contar_colisiones(tabla_cerrada_doble_A, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Doble: {total_colisiones_cerrada_doble_A}")
    print()
    return tabla_cerrada_lineal_A, tabla_cerrada_cuadratica_A, tabla_cerrada_doble_A

def conteos_tabla_cerrada_disp_B(datos: list[tuple[str, str]]):
    #B Lineal
    tabla_cerrada_lineal_B=TablaCerrada(20011, dispersionB, exploracion_lineal)
    total_colisiones_cerrada_lineal_B=insertar_datos_y_contar_colisiones(tabla_cerrada_lineal_B, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion B Lineal: {total_colisiones_cerrada_lineal_B}")
    #B Cuadratica
    tabla_cerrada_cuadratica_B=TablaCerrada(20011, dispersionB, exploracion_cuadratica)
    total_colisiones_cerrada_cuadratica_B=insertar_datos_y_contar_colisiones(tabla_cerrada_cuadratica_B, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion B Cuadratica: {total_colisiones_cerrada_cuadratica_B}")
    #B Doble
    tabla_cerrada_doble_B=TablaCerrada(20011, dispersionB, exploracion_doble)
    total_colisiones_cerrada_doble_B=insertar_datos_y_contar_colisiones(tabla_cerrada_doble_B, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion B Doble: {total_colisiones_cerrada_doble_B}")
    print()
    return tabla_cerrada_lineal_B, tabla_cerrada_cuadratica_B, tabla_cerrada_doble_B
##Calculos de eficiencia punto 4

def microsegundos() -> int: #Esta función la hemos usado creo que en todas las prácticas
    return time.perf_counter_ns() // 1000

def generar_claves_aleatorias(datos_completos: list[tuple[str, str]], n: int) -> list[str]: 
    """
    Selecciona n claves aleatorias del conjunto completo de 19062 claves para ser buscadas.
    """
    return random.sample([d[0] for d in datos_completos], k=n)

def wrapper_busqueda(tabla, claves_a_buscar: list[str]) -> int: 
    """
    Función que realiza n búsquedas en la tabla.
    Devuelve la suma total de colisiones para esa muestra n.
    """
    total_colisiones = 0
    for clave in claves_a_buscar:
        _, colisiones = tabla.buscar(clave)
        total_colisiones += colisiones
    return total_colisiones 

def _medir_tiempo_busqueda_aux(tabla, claves_a_buscar: list[str], K: int = 1000) -> tuple[float, str, int]:
    """
    Mide el tiempo de buscar n claves en la tabla, con corrección K.
    Retorna (tiempo_µs, marca, colisiones_promedio)
    """
    
    ta = microsegundos()
    colisiones_prueba = wrapper_busqueda(tabla, claves_a_buscar) 
    td = microsegundos()
    t = td - ta
    
    if t >= 1000:
        return float(t), " ", colisiones_prueba
    
    ta = microsegundos()
    for _ in range(K):    # Corrección por repeticiones K
        wrapper_busqueda(tabla, claves_a_buscar) 
    td = microsegundos()
    t1 = td - ta
    
    # No restamos el costo del generador (t2) ya que las claves se generaron fuera por cierto. Me estuvo dando problemas
    # al restarlo y obtener movidas raras.
    
    colisiones_final = wrapper_busqueda(tabla, claves_a_buscar)

    return (t1 / K), "*", colisiones_final # t1/K es el tiempo promedio

def medir_tiempo_busqueda(tabla_llena, 
                           datos_completos: list[tuple[str, str]],
                           muestra_inicial: int,
                           muestras: int, factor: int = 2) -> dict[int, tuple[float, str, int]]:
    
    """
    Mide el tiempo total de buscar n elementos (y cuenta las colisiones)
    para n = n_inicial, n*factor, n*(factor^2), etc.
    
    Retorna: {n: (tiempo_µs, marca, colisiones_totales)}
    """
    
    res: dict[int, tuple[float, str, int]] = {}
    n = muestra_inicial
    
    for _ in range(muestras): #Generamos n claves aleatorias para esta muestra siguiendo el enunciado del punto 4
                                # Esto asegura que las búsquedas siempre son aleatorias y no en orden de inserción

        claves_a_buscar = generar_claves_aleatorias(datos_completos, n) 

        t, m, colisiones = _medir_tiempo_busqueda_aux(tabla_llena, claves_a_buscar) #La función auxliar basicamente añade la corrección K para tiempos pequeños
        
        if t < 0:
            raise RuntimeError("Cronómetro interno no fiable.") #Lol, nunca debería pasar esto
            
        res[n] = (t, m, colisiones) 
        
        n *= factor  #Esto es multiplicar n por el factor (normalmente será 2) para la siguiente muestra

        
    return res
    
def _denominadores_busqueda(n: int) -> tuple[float, float, float]: #No sé, me dio paja repetir esto en la función de mostrar tiempos una y otra vez
    """
    Calcula n^0.8, n, n^1.2 para normalización.
    """
    n_0_8 = n ** 0.8
    n_1_0 = float(max(1, n)) # Evitar división por cero, no vaya a ser
    n_1_2 = n ** 1.2
    return n_0_8, n_1_0, n_1_2

def mostrar_tiempo_busqueda(alg_name: str, 
                            v: dict[int, tuple[float, str, int]]) -> None:
    """
    Imprime tabla con t(n), y normaliza con n^0.8, n, n^1.2, e incluye Colisiones.
    """
    print()
    print(f"*** {alg_name} ***")
    
    header = (f"{'n':>8} {'t(n)[µs]':>14} {'t(n)/n^0.8':>14}"
              f"{'t(n)/n':>14} {'t(n)/n^1.2':>14} {'Colisiones':>14}")
    print(header)

    for n, (t_n, signo, colisiones) in v.items():
        n_0_8, n_1_0, n_1_2 = _denominadores_busqueda(n)
        
        v_0_8 = t_n / n_0_8
        v_1_0 = t_n / n_1_0
        v_1_2 = t_n / n_1_2
        
        print(f"{signo}{n:8d} {t_n:14.3f} {v_0_8:14.6g} {v_1_0:14.6g} {v_1_2:14.6g} {colisiones:14d}")

    return
    
def main_complejidad(datos_sinonimos):
    """
    Ejecuta el Punto 4: Mide la complejidad de la búsqueda para las 8 tablas.
    """
    
    TAM_CERRADA = 38197 #Configuración del tamaño para ambos tipos de tablas
    TAM_ABIERTA = 19069 
    
    configuraciones = [                             
        (TablaAbierta, TAM_ABIERTA, dispersionA, None, "Tabla Abierta, Disp. A"),
        (TablaAbierta, TAM_ABIERTA, dispersionB, None, "Tabla Abierta, Disp. B"),
        
        (TablaCerrada, TAM_CERRADA, dispersionA, exploracion_lineal, "Tabla Cerrada, Disp. A, Lineal"),
        (TablaCerrada, TAM_CERRADA, dispersionB, exploracion_lineal, "Tabla Cerrada, Disp. B, Lineal"),
        
        (TablaCerrada, TAM_CERRADA, dispersionA, exploracion_cuadratica, "Tabla Cerrada, Disp. A, Cuadrática"),
        (TablaCerrada, TAM_CERRADA, dispersionB, exploracion_cuadratica, "Tabla Cerrada, Disp. B, Cuadrática"),
        
        (TablaCerrada, TAM_CERRADA, dispersionA, exploracion_doble, "Tabla Cerrada, Disp. A, Doble"),
        (TablaCerrada, TAM_CERRADA, dispersionB, exploracion_doble, "Tabla Cerrada, Disp. B, Doble"),
    ]
    
    resultados_compilados = {} # Guardará los resultados de medir_tiempo_busqueda
        
    for ClaseTabla, tam, disp_func, resol_func, nombre_test in configuraciones:
        
        print(f"\nConstruyendo tabla: {nombre_test}...")
        
        if resol_func is None:
            tabla_llena = ClaseTabla(tam, disp_func)
        else:
            tabla_llena = ClaseTabla(tam, disp_func, resol_func)
            
        _ = insertar_datos_y_contar_colisiones(tabla_llena, datos_sinonimos)
        
        print(f"Midiendo tiempo de búsqueda para {nombre_test}...")#Tan solo una pequeña pijada estética
        

        tiempos_medidos = medir_tiempo_busqueda(
            tabla_llena, 
            datos_sinonimos,
            muestra_inicial=125,
            muestras=8,
            factor=2
        )
        
        mostrar_tiempo_busqueda(nombre_test, tiempos_medidos)
        
        #resultados_compilados[nombre_test] = tiempos_medidos #Si quisiera guardar los resultados para usarlos luego, pero no hace falta. Lo hice sin pensarlo

    print("\nAnálisis de Complejidad Finalizado.")
    return

if __name__ == "__main__":
    validar_tablas()
    datos=leer_sinonimos()
    ##Calculo de Colisiones Tabla Abierta
    conteos_tabla_abierta(datos)
    ##Calculo de Colisiones Tabla Cerrada
    conteos_tabla_cerrada_disp_A(datos)
    conteos_tabla_cerrada_disp_B(datos)
    ##Medición de tiempos de búsqueda
    i=0
    while i<3:#Es suficiente con hacer 3 veces la medición para ver que los resultados son consistentes y evitar variaciones inesperadas
        print(f"\n--- Medición de tiempos de búsqueda, iteración {i+1} ---")
        main_complejidad(datos)
        i+=1
    pass #Creo que es la práctica entre entender conceptos y programar que más tiempo me ha llevado.     

