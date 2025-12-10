from collections.abc import Callable

#Importación de datos
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
        print(f"Error: Carlos se ha vuelto a colar en la tabla, nadie está a salvo")#Carlos da miedo
    return tabla


def validar_tablas():
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
#Conteo de Colisiones punto 3
def insertar_datos_y_contar_colisiones(tabla: TablaAbierta| TablaCerrada, datos: list[tuple[str, str]]) -> int:#Pequeña función para no repetir código 
    total_colisiones = 0                                                                            #al insertar los datos y contar las colisiones de todas las tablas
    for clave, sinonimos in datos:
        colisiones = tabla.insertar(clave, sinonimos)
        total_colisiones += colisiones
    return total_colisiones
if __name__ == "__main__":
    #validar_tablas()
    datos=leer_sinonimos()
    ##Calculo de Colisiones Tabla Abierta
    #A
    tabla_abierta_A=TablaAbierta(20011, dispersionA)
    total_colisiones_abierta_A=insertar_datos_y_contar_colisiones(tabla_abierta_A, datos)
    print(f"Total colisiones Tabla Abierta Dispersion A: {total_colisiones_abierta_A}")
    print()
    #B
    tabla_abierta_B=TablaAbierta(20011, dispersionB)
    total_colisiones_abierta_B=insertar_datos_y_contar_colisiones(tabla_abierta_B, datos)
    print(f"Total colisiones Tabla Abierta Dispersion A: {total_colisiones_abierta_B}")
    print()
    ##Calculo de Colisiones Tabla Cerrada
    #A Lineal
    tabla_cerrada_lineal=TablaCerrada(20011, dispersionA, exploracion_lineal)
    total_colisiones_cerrada_lineal=insertar_datos_y_contar_colisiones(tabla_cerrada_lineal, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Lineal: {total_colisiones_cerrada_lineal}")
    print()
    #A Cuadratica
    tabla_cerrada_cuadratica=TablaCerrada(20011, dispersionA, exploracion_cuadratica)
    total_colisiones_cerrada_cuadratica=insertar_datos_y_contar_colisiones(tabla_cerrada_cuadratica, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Cuadratica: {total_colisiones_cerrada_cuadratica}")
    print()
    #A Doble
    tabla_cerrada_doble=TablaCerrada(20011, dispersionA, exploracion_doble)
    total_colisiones_cerrada_doble=insertar_datos_y_contar_colisiones(tabla_cerrada_doble, datos)
    print(f"Total colisiones Tabla Cerrada Dispersion A Doble: {total_colisiones_cerrada_doble}")
    print()