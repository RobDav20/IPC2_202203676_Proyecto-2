# reporte_html.py
import xml.etree.ElementTree as ET

class ReporteHTML:
    def __init__(self, ruta_xml):
        self.tree = ET.parse(ruta_xml)
        self.root = self.tree.getroot()

    def generar(self, salida="ReporteInvernaderos.html"):
        with open(salida, "w", encoding="utf-8") as f:
            f.write("<html><head><meta charset='utf-8'><title>Reporte de Invernaderos</title>")
            f.write("""<style>
                body {
                    background-color: #0d0d0d;
                    color: #e0b3ff;
                    font-family: "Courier New", monospace;
                    margin: 20px;
                }
                h1 { color: #d580ff; text-shadow: 0px 0px 10px #9933ff; }
                h2 { color: #cc80ff; text-shadow: 0px 0px 8px #ff1aff; }
                h3 { color: #b366ff; margin-top: 15px; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 25px; box-shadow: 0px 0px 15px #660066; }
                th, td { border: 2px solid #9933ff; padding: 8px; text-align: center; }
                th { background-color: #260026; color: #ffccff; text-shadow: 0px 0px 5px #ff1aff; }
                td { background-color: #1a001a; color: #e6ccff; }
                tr:hover td { background-color: #330033; }
            </style></head><body>""")

            # recorrer invernaderos (proteger contra nodos faltantes)
            lista_invernaderos = self.root.find("listaInvernaderos")
            if lista_invernaderos is None:
                f.write("<h1>No hay datos para mostrar</h1>")
            else:
                for inv in lista_invernaderos.findall("invernadero"):
                    nombre_inv = inv.get("nombre", "SinNombre")
                    f.write(f"<h1>Invernadero: {nombre_inv}</h1>")

                    lista_planes = inv.find("listaPlanes")
                    if lista_planes is not None:
                        for plan in lista_planes.findall("plan"):
                            nombre_plan = plan.get("nombre", "PlanSinNombre")
                            f.write(f"<h2>Plan de Riego: {nombre_plan}</h2>")

                            eficiencia = plan.find("eficienciaDronesRegadores")
                            f.write("<h3>Tabla 1 - Drones asignados y uso</h3>")
                            f.write("<table><tr><th>Dron</th><th>Litros Agua</th><th>Fertilizante (g)</th></tr>")
                            if eficiencia is not None:
                                for d in eficiencia.findall("dron"):
                                    nombre_dron = d.get("nombre", "SinNombre")
                                    agua = d.get("litrosAgua", "0")
                                    fert = d.get("gramosFertilizante", "0")
                                    f.write(f"<tr><td>{nombre_dron}</td><td>{agua}</td><td>{fert}</td></tr>")
                            f.write("</table>")

                            instrucciones = plan.find("instrucciones")
                            f.write("<h3>Tabla 2 - Instrucciones en el tiempo</h3>")
                            f.write("<table><tr><th>Tiempo (s)</th><th>Dron</th><th>Acción</th></tr>")
                            if instrucciones is not None:
                                for tiempo in instrucciones.findall("tiempo"):
                                    segundos = tiempo.get("segundos", "0")
                                    for d in tiempo.findall("dron"):
                                        nombre_dron = d.get("nombre", "SinNombre")
                                        accion = d.get("accion", "")
                                        f.write(f"<tr><td>{segundos}</td><td>{nombre_dron}</td><td>{accion}</td></tr>")
                            f.write("</table>")

                            tiempo_opt = plan.find("tiempoOptimoSegundos")
                            agua_total = plan.find("aguaRequeridaLitros")
                            fert_total = plan.find("fertilizanteRequeridoGramos")

                            f.write("<h3>Tabla 3 - Estadísticas Totales</h3>")
                            f.write("<table><tr><th>Tiempo (s)</th><th>Agua Total (L)</th><th>Fertilizante Total (g)</th></tr>")
                            f.write(f"<tr><td>{tiempo_opt.text if tiempo_opt is not None else '0'}</td>"
                                    f"<td>{agua_total.text if agua_total is not None else '0'}</td>"
                                    f"<td>{fert_total.text if fert_total is not None else '0'}</td></tr>")
                            f.write("</table>")

            f.write("</body></html>")

        print(f"Reporte HTML retro generado: {salida}")


if __name__ == "__main__":
    reporte = ReporteHTML("salida.xml")
    reporte.generar()
