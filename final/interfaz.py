import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, webbrowser
import xml.etree.ElementTree as ET

# importar crear desde main.py
try:
    from main import crear
except Exception as e:
    def crear(*args, **kwargs):
        raise ImportError("No se pudo importar 'crear' desde 'main.py'. Asegúrate de que 'main.py' existe en el mismo directorio.") from e

from reporte_html import ReporteHTML


class AppInvernaderos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Riego Inteligente")
        self.root.geometry("900x650")
        self.root.configure(bg="#1a001a")  # negro con toque morado

        style = ttk.Style()
        style.theme_use("clam")  # para que respete los colores

        # Estilos generales
        style.configure("TLabel", background="#1a001a", foreground="#d8b4fe", font=("Arial", 12))
        style.configure("Purple.TButton",
                        background="#a855f7",
                        foreground="white",
                        font=("Arial", 11, "bold"),
                        padding=6,
                        relief="flat")
        style.map("Purple.TButton",
                  background=[("active", "#c084fc")],  # hover
                  foreground=[("active", "white")])

        # Combobox
        style.configure("TCombobox",
                        fieldbackground="#1a001a",
                        background="#6d28d9",
                        foreground="white")

        # --- Variables ---
        self.archivo_xml = None
        self.invernaderos = []
        self.planes = {}
        self.invernadero_actual = tk.StringVar()
        self.plan_actual = tk.StringVar()

        # --- Título ---
        titulo = tk.Label(root, text="- INTERFAZ DE USUARIO - RIEGO AUTOMATIZADO -",
                          bg="#1a001a", fg="#c084fc", font=("Arial Black", 16))
        titulo.pack(pady=15)

        # --- Contenedor ---
        frame = tk.Frame(root, bg="#1a001a")
        frame.pack(pady=20)

        # Botón cargar archivo
        btn_cargar = ttk.Button(frame, text="Cargar XML", style="Purple.TButton", command=self.cargar_xml)
        btn_cargar.grid(row=0, column=0, padx=10, pady=5)

        # Combobox invernaderos
        tk.Label(frame, text="Invernadero:", bg="#1a001a", fg="#d8b4fe").grid(row=1, column=0, sticky="w")
        self.combo_invernaderos = ttk.Combobox(frame, textvariable=self.invernadero_actual, state="readonly")
        self.combo_invernaderos.grid(row=1, column=1, padx=10, pady=5)
        self.combo_invernaderos.bind("<<ComboboxSelected>>", self.actualizar_planes)

        # Combobox planes
        tk.Label(frame, text="Plan de Riego:", bg="#1a001a", fg="#d8b4fe").grid(row=2, column=0, sticky="w")
        self.combo_planes = ttk.Combobox(frame, textvariable=self.plan_actual, state="readonly")
        self.combo_planes.grid(row=2, column=1, padx=10, pady=5)

        # Botones
        btn_simular = ttk.Button(frame, text="Simular", style="Purple.TButton", command=self.simular)
        btn_simular.grid(row=3, column=0, padx=10, pady=10)

        btn_reporte = ttk.Button(frame, text="📑 Generar Reporte HTML", style="Purple.TButton", command=self.generar_reporte)
        btn_reporte.grid(row=3, column=1, padx=10, pady=10)

        btn_ayuda = ttk.Button(frame, text="Ayuda", style="Purple.TButton", command=self.mostrar_ayuda)
        btn_ayuda.grid(row=3, column=2, padx=10, pady=10)

        # --- Área de resultados con scroll ---
        frame_text = tk.Frame(root, bg="#1a001a")
        frame_text.pack(pady=10, fill="both", expand=True)

        self.text_area = tk.Text(frame_text, bg="#0f0a1a", fg="#bc97e4", font=("Consolas", 11), wrap="word")
        self.text_area.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_text, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

    # --- Métodos (no los cambié, siguen igual) ---
    def cargar_xml(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
        if not archivo:
            return
        try:
            tree = ET.parse(archivo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el XML: {e}")
            return

        self.archivo_xml = archivo
        root = tree.getroot()

        self.invernaderos.clear()
        self.planes.clear()

        lista_inv = root.find("listaInvernaderos")
        if lista_inv is not None:
            for inv in lista_inv.findall("invernadero"):
                nombre = inv.get("nombre")
                self.invernaderos.append(nombre)
                self.planes[nombre] = []
                lista_planes = inv.find("planesRiego")
                if lista_planes is not None:
                    for plan in lista_planes.findall("plan"):
                        self.planes[nombre].append(plan.get("nombre"))

        self.combo_invernaderos["values"] = self.invernaderos
        if self.invernaderos:
            self.combo_invernaderos.current(0)
            self.actualizar_planes()

        messagebox.showinfo("XML cargado", f"Archivo {os.path.basename(archivo)} cargado correctamente.")

    def actualizar_planes(self, *_):
        inv = self.invernadero_actual.get()
        if inv in self.planes:
            self.combo_planes["values"] = self.planes[inv]
            if self.planes[inv]:
                self.combo_planes.current(0)

    def simular(self):
        if not self.archivo_xml:
            messagebox.showwarning("Advertencia", "Primero cargue un archivo XML.")
            return
        try:
            obj = crear(self.archivo_xml)
            obj.creacion()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo la simulación: {e}")
            return
        try:
            tree = ET.parse("salida.xml")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir salida.xml: {e}")
            return

        root = tree.getroot()
        self.text_area.delete("1.0", tk.END)
        lista_inv = root.find("listaInvernaderos")
        if lista_inv is None:
            self.text_area.insert(tk.END, "No hay resultados en salida.xml\n")
            return
        for inv in lista_inv.findall("invernadero"):
            nombre_inv = inv.get("nombre")
            self.text_area.insert(tk.END, f"\nInvernadero: {nombre_inv}\n")
            lista_planes = inv.find("listaPlanes")
            if lista_planes is None:
                continue
            for plan in lista_planes.findall("plan"):
                nombre_plan = plan.get("nombre")
                tiempo = plan.find("tiempoOptimoSegundos").text if plan.find("tiempoOptimoSegundos") is not None else "0"
                agua = plan.find("aguaRequeridaLitros").text if plan.find("aguaRequeridaLitros") is not None else "0"
                fert = plan.find("fertilizanteRequeridoGramos").text if plan.find("fertilizanteRequeridoGramos") is not None else "0"
                self.text_area.insert(tk.END, f"  Plan {nombre_plan}:\n")
                self.text_area.insert(tk.END, f"    Tiempo: {tiempo}s, Agua: {agua}L, Fertilizante: {fert}g\n")
        messagebox.showinfo("Simulación completada", "Los resultados se muestran en la pantalla y en salida.xml")

    def generar_reporte(self):
        if not os.path.exists("salida.xml"):
            messagebox.showwarning("Advertencia", "Primero debe ejecutar una simulación.")
            return
        reporte = ReporteHTML("salida.xml")
        archivo_html = "ReporteInvernaderos.html"
        reporte.generar(salida=archivo_html)
        webbrowser.open(f"file://{os.path.abspath(archivo_html)}")
        messagebox.showinfo("Reporte generado", f"Se creó y abrió {archivo_html}")

    def mostrar_ayuda(self):
        messagebox.showinfo("Acerca de", 
            "Proyecto de Riego Automático\n"
            "Estudiante: Tu Nombre Aquí\n"
            "Carnet: 2025-XXXXX\n"
            "Curso: Introducción a la Programación\n"
            "Universidad: USAC\n\n"
            "Funciones:\n"
            "1. Cargar archivo XML\n"
            "2. Seleccionar invernadero y plan de riego\n"
            "3. Simular proceso de riego\n"
            "4. Generar salida.xml y reporte HTML\n"
            "5. Abrir reporte directamente en el navegador"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AppInvernaderos(root)
    root.mainloop()
