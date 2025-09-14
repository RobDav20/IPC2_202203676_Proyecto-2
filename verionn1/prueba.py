import xml.etree.ElementTree as ET

class Creacion:
    def __init__(self, ruta):
        tree = ET.parse(ruta)
        self.root = tree.getroot()

class NodoPos:
    def __init__(self, etiqueta_pos):
        self.pos = etiqueta_pos
        self.siguiente = None

class Cola:
    def __init__(self, numero_hilera):
        self.hilera = f"H{numero_hilera}"
        self.frente = None
        self.final = None
        self.siguiente = None

    def encolar_pos(self, etiqueta_pos):
        nuevo = NodoPos(etiqueta_pos)
        if self.frente is None:
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo

    def mostrar(self):
        print(f"{self.hilera}:", end=" ")
        actual = self.frente
        if actual is None:
            print("None")
            return
        while actual:
            print(actual.pos, end=" -> ")
            actual = actual.siguiente
        print("None")

class GestorColas:
    def __init__(self):
        self.primero = None

    def agregar_cola(self, numero_hilera):
        nueva = Cola(numero_hilera)
        if self.primero is None:
            self.primero = nueva
        else:
            actual = self.primero
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nueva
        return nueva

    def mostrar_colas(self):
        actual = self.primero
        while actual:
            actual.mostrar()
            actual = actual.siguiente

class crear(Creacion):
    def creacion(self):
        # Recorremos todos los invernaderos (si hay más de uno)
        lista_invernaderos = self.root.find("listaInvernaderos")
        if lista_invernaderos is None:
            return

        for invernadero in lista_invernaderos.findall("invernadero"):
            nombre_inv = invernadero.get("nombre")
            print(f"Invernadero: {nombre_inv}")

            # nuevo gestor por invernadero
            gestor = GestorColas()

            # número de hileras
            numero_hileras = int(invernadero.find("numeroHileras").text)

            # crear las colas H1..Hn (solo las "cabezas")
            for h in range(1, numero_hileras + 1):
                gestor.agregar_cola(h)


            lista_plantas = invernadero.find("listaPlantas")
            if lista_plantas is not None:
                for planta in lista_plantas.findall("planta"):
                    hil = int(planta.get("hilera"))
                    pos = planta.get("posicion")
                    etiqueta_pos = f"P{pos}"

                    # buscar la cola H{hil} (recorriendo enlaces)
                    actual = gestor.primero
                    objetivo = f"H{hil}"
                    while actual and actual.hilera != objetivo:
                        actual = actual.siguiente

                    if actual:
                        actual.encolar_pos(etiqueta_pos)


            gestor.mostrar_colas()

class drones:
    pass

class patrones_de_riego:
    pass



obj = crear("entrada.xml")
obj.creacion()



