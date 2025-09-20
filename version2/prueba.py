import xml.etree.ElementTree as ET

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

    def buscar_cola(self, hilera):
        actual = self.primero
        while actual and actual.hilera != hilera:
            actual = actual.siguiente
        return actual

    def mostrar_colas(self):
        actual = self.primero
        while actual:
            actual.mostrar()
            actual = actual.siguiente


# ==========================
# CLASES EXTRA
# ==========================
class Dron:
    def __init__(self, id_dron, nombre):
        self.id = id_dron
        self.nombre = nombre
        self.hilera_asignada = None
        self.cola_asignada = None
        self.contador_agua = 0
        self.contador_fertilizante = 0

    def __str__(self):
        return f"{self.nombre} (ID {self.id}) -> Hilera {self.hilera_asignada}"


class PlanRiego:
    def __init__(self, nombre, secuencia):
        self.nombre = nombre
        self.secuencia = [item.strip() for item in secuencia.split(",")]

    def __str__(self):
        return f"{self.nombre}: {self.secuencia}"


class Creacion:
    def __init__(self, ruta):
        tree = ET.parse(ruta)
        self.root = tree.getroot()


class crear(Creacion):
    def creacion(self):
        # 1. Leer lista de drones
        lista_drones = self.root.find("listaDrones")
        drones = {}
        if lista_drones is not None:
            for dron in lista_drones.findall("dron"):
                id_dron = dron.get("id")
                nombre = dron.get("nombre")
                drones[id_dron] = Dron(id_dron, nombre)

        # 2. Recorremos invernaderos
        lista_invernaderos = self.root.find("listaInvernaderos")
        if lista_invernaderos is None:
            return

        for invernadero in lista_invernaderos.findall("invernadero"):
            nombre_inv = invernadero.get("nombre")
            print(f"\nInvernadero: {nombre_inv}")

            gestor = GestorColas()
            numero_hileras = int(invernadero.find("numeroHileras").text)

            # crear las colas H1..Hn
            for h in range(1, numero_hileras + 1):
                gestor.agregar_cola(h)

            # 3. Leer plantas y encolarlas
            lista_plantas = invernadero.find("listaPlantas")
            if lista_plantas is not None:
                for planta in lista_plantas.findall("planta"):
                    hil = int(planta.get("hilera"))
                    pos = planta.get("posicion")
                    etiqueta_pos = f"P{pos}"

                    cola_obj = gestor.buscar_cola(f"H{hil}")
                    if cola_obj:
                        cola_obj.encolar_pos(etiqueta_pos)

            gestor.mostrar_colas()

            # 4. Leer asignación de drones
            asignacion = invernadero.find("asignacionDrones")
            if asignacion is not None:
                for dron in asignacion.findall("dron"):
                    id_dron = dron.get("id")
                    hilera = dron.get("hilera")
                    if id_dron in drones:
                        drones[id_dron].hilera_asignada = hilera
                        drones[id_dron].cola_asignada = gestor.buscar_cola(f"H{hilera}")

            print("\nAsignación de drones:")
            for d in drones.values():
                if d.hilera_asignada:
                    print(d)

            # 5. Leer planes de riego
            planes = []
            lista_planes = invernadero.find("planesRiego")
            if lista_planes is not None:
                for plan in lista_planes.findall("plan"):
                    nombre = plan.get("nombre")
                    secuencia = plan.text.strip()
                    planes.append(PlanRiego(nombre, secuencia))

            print("\nPlanes de riego:")
            for p in planes:
                print(p)


if __name__ == "__main__":
    obj = crear("entrada.xml")
    obj.creacion()
