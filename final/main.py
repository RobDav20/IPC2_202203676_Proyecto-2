# main.py
import xml.etree.ElementTree as ET
from reporte_html import ReporteHTML

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

class Dron:
    def __init__(self, id_dron, nombre):
        self.id = id_dron
        self.nombre = nombre
        self.hilera_asignada = None  # sera string numero '1', '2', ...
        self.cola_asignada = None
        self.contador_agua = 0
        self.contador_fertilizante = 0

    def __str__(self):
        return f"{self.nombre} (ID {self.id}) -> Hilera {self.hilera_asignada}"

class PlanRiego:
    def __init__(self, nombre, secuencia):
        self.nombre = nombre
        # secuencia ejemplo: "H1-P1,H1-P2,H1-P3" -> normalizamos internamente
        self.secuencia = [item.strip() for item in secuencia.split(",")]

    def __str__(self):
        return f"{self.nombre}: {self.secuencia}"

class Creacion:
    def __init__(self, ruta):
        tree = ET.parse(ruta)
        self.root = tree.getroot()

class crear(Creacion):
    def creacion(self):
        # raíz salida.xml
        root_salida = ET.Element("datosSalida")
        lista_invernaderos_out = ET.SubElement(root_salida, "listaInvernaderos")

        # 1. Leer lista de drones (global, luego reiniciaremos contadores por invernadero/plan)
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

            inv_out = ET.SubElement(lista_invernaderos_out, "invernadero", {"nombre": nombre_inv})
            lista_planes_out = ET.SubElement(inv_out, "listaPlanes")

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

            # 4. Leer asignación de drones (hilera en XML puede ser "1" o "H1" — normalizamos)
            asignacion = invernadero.find("asignacionDrones")
            if asignacion is not None:
                for dron in asignacion.findall("dron"):
                    id_dron = dron.get("id")
                    hilera_raw = dron.get("hilera")
                    if not hilera_raw:
                        continue
                    # normalizar: quitar 'H' si existe
                    hilera = hilera_raw.upper().replace("H", "")
                    if id_dron in drones:
                        drones[id_dron].hilera_asignada = hilera  # guardamos "1", "2", ...
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

            # 6. Simulación: para cada plan, reiniciamos contadores y posiciones
            print("\nSimulación de planes:")
            for p in planes:
                # reiniciar contadores del dron para estadísticas por plan
                for d in drones.values():
                    d.contador_agua = 0
                    d.contador_fertilizante = 0

                self.simular_plan(drones, gestor, p, lista_planes_out)

        # guardar salida.xml
        tree_out = ET.ElementTree(root_salida)
        tree_out.write("salida.xml", encoding="utf-8", xml_declaration=True)
        print("\nArchivo salida.xml generado correctamente.")

        # 🚀 Generar reporte HTML automáticamente
        reporte = ReporteHTML("salida.xml")
        reporte.generar()
        print("Reporte HTML creado.")

    def simular_plan(self, drones, gestor, plan, lista_planes_out):
        tiempo = 0
        instrucciones = []
        total_agua = 0
        total_fert = 0

        # posiciones iniciales por dron (0 significa antes de P1)
        posiciones = {d.id: 0 for d in drones.values()}

        for paso in plan.secuencia:
            # esperamos formato como "H1-P3" o "1-P3"; normalizamos
            if "-" not in paso:
                continue
            hilera_raw, pos_raw = paso.split("-")
            hilera_num = hilera_raw.upper().replace("H", "")  # ahora es "1", "2", ...
            # pos_raw ejemplo "P3" -> extraer número 3
            try:
                pos = int(pos_raw.upper().replace("P", ""))
            except:
                continue

            # buscar dron que tenga asignada esa hilera
            dron_obj = None
            for d in drones.values():
                if d.hilera_asignada == hilera_num:
                    dron_obj = d
                    break
            if not dron_obj:
                # si no hay dron asignado a esa hilera, saltamos ese paso
                continue

            # mover dron hasta la posicion
            while posiciones[dron_obj.id] < pos:
                tiempo += 1
                posiciones[dron_obj.id] += 1
                instrucciones.append((tiempo, dron_obj.nombre,
                                      f"Adelante (H{dron_obj.hilera_asignada}P{posiciones[dron_obj.id]})"))
            while posiciones[dron_obj.id] > pos:
                tiempo += 1
                posiciones[dron_obj.id] -= 1
                instrucciones.append((tiempo, dron_obj.nombre,
                                      f"Atrás (H{dron_obj.hilera_asignada}P{posiciones[dron_obj.id]})"))

            # regar en la posicion actual (pos)
            tiempo += 1
            instrucciones.append((tiempo, dron_obj.nombre, f"Regar (H{dron_obj.hilera_asignada}P{pos})"))
            dron_obj.contador_agua += 1
            dron_obj.contador_fertilizante += 100
            total_agua += 1
            total_fert += 100

        # imprimir instrucciones y estadisticas
        print("\nInstrucciones:")
        for t, dron, accion in instrucciones:
            print(f"{t:2d}s -> {dron}: {accion}")

        print("\nEstadísticas:")
        print(f"Tiempo total: {tiempo} segundos")
        print(f"Agua total: {total_agua} litros")
        print(f"Fertilizante total: {total_fert} gramos")
        for d in drones.values():
            print(f"{d.nombre} -> Agua: {d.contador_agua}, Fertilizante: {d.contador_fertilizante}")

        # escribir salida XML para este plan
        plan_out = ET.SubElement(lista_planes_out, "plan", {"nombre": plan.nombre})
        ET.SubElement(plan_out, "tiempoOptimoSegundos").text = str(tiempo)
        ET.SubElement(plan_out, "aguaRequeridaLitros").text = str(total_agua)
        ET.SubElement(plan_out, "fertilizanteRequeridoGramos").text = str(total_fert)

        eficiencia = ET.SubElement(plan_out, "eficienciaDronesRegadores")
        for d in drones.values():
            ET.SubElement(eficiencia, "dron", {
                "nombre": d.nombre,
                "litrosAgua": str(d.contador_agua),
                "gramosFertilizante": str(d.contador_fertilizante)
            })

        instrucciones_xml = ET.SubElement(plan_out, "instrucciones")
        tiempos_dict = {}
        for t, dron, accion in instrucciones:
            if t not in tiempos_dict:
                tiempos_dict[t] = []
            tiempos_dict[t].append((dron, accion))

        for t in sorted(tiempos_dict.keys()):
            tiempo_node = ET.SubElement(instrucciones_xml, "tiempo", {"segundos": str(t)})
            for dron, accion in tiempos_dict[t]:
                ET.SubElement(tiempo_node, "dron", {"nombre": dron, "accion": accion})


if __name__ == "__main__":
    # Por defecto, si ejecutas main.py directamente:
    try:
        obj = crear("entrada.xml")
        obj.creacion()
    except FileNotFoundError:
        print("No se encontró 'entrada.xml'. Coloca un archivo XML con ese nombre o llama a crear con la ruta correcta.")
