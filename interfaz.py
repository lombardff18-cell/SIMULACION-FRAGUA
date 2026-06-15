import random
from tkinter import messagebox
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Importación de la base de datos externa
from materiales import materiales

# =====================================================
# CONFIGURACIÓN GENERAL DE LA INTERFAZ
# =====================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SistemaFragua:

    def __init__(self, root):
        self.root = root
        self.root.title("Control Industrial de Fragua v2.0 - SCADA & Finanzas")
        self.root.geometry("1450x850")
        self.crear_interfaz()

    def crear_interfaz(self):
        # TÍTULO SUPERIOR SCADA
        titulo = ctk.CTkLabel(
            self.root, 
            text="SISTEMA DE CONTROL, GEMELO DIGITAL Y COSTOS - PANEL DE FRAGUA", 
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=15)

        # MARCO CONTENEDOR PRINCIPAL
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # =================================================
        # PANEL IZQUIERDO: CONFIGURACIÓN Y CONTROLES FIJOS
        # =================================================
        left_frame = ctk.CTkFrame(main_frame, width=380)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Filtrado de materiales desde el diccionario externo
        lista_metales = [k for k in materiales.keys() if not k.startswith("PARED:")]
        lista_paredes = [k for k in materiales.keys() if k.startswith("PARED:")]
        lista_combustibles = ["Gas Natural (GN)", "Gas Licuado (GLP)", "Electricidad (Inducción)"]

        # SELECCIÓN DE MATERIALES Y REVESTIMIENTO
        ctk.CTkLabel(left_frame, text="Metal a Fraguar", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 2))
        self.combo_material = ctk.CTkComboBox(left_frame, values=lista_metales)
        self.combo_material.pack(padx=15, pady=5, fill="x")
        self.combo_material.set("Acero")

        ctk.CTkLabel(left_frame, text="Revestimiento de la Pared (Refractario)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.combo_pared = ctk.CTkComboBox(left_frame, values=lista_paredes)
        self.combo_pared.pack(padx=15, pady=5, fill="x")
        self.combo_pared.set(lista_paredes[0])

        # SELECTOR: VARIABLE DE COMBUSTIBLE / ENERGÍA
        ctk.CTkLabel(left_frame, text="Fuente de Energía / Combustible", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.combo_combustible = ctk.CTkComboBox(left_frame, values=lista_combustibles)
        self.combo_combustible.pack(padx=15, pady=5, fill="x")
        self.combo_combustible.set("Gas Natural (GN)")

        # ENTRADAS DE PARÁMETROS GEOMÉTRICOS Y TÉRMICOS
        ctk.CTkLabel(left_frame, text="Temperatura Inicial (°C)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.entry_temp = ctk.CTkEntry(left_frame)
        self.entry_temp.pack(padx=15, pady=5, fill="x")
        self.entry_temp.insert(0, "25")

        ctk.CTkLabel(left_frame, text="Diámetro del Metal (m)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.entry_diametro = ctk.CTkEntry(left_frame)
        self.entry_diametro.pack(padx=15, pady=5, fill="x")
        self.entry_diametro.insert(0, "0.10")

        ctk.CTkLabel(left_frame, text="Largo del Metal (m)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.entry_largo = ctk.CTkEntry(left_frame)
        self.entry_largo.pack(padx=15, pady=5, fill="x")
        self.entry_largo.insert(0, "1.00")

        ctk.CTkLabel(left_frame, text="Potencia del Quemador / Inducción (kW)", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.entry_potencia = ctk.CTkEntry(left_frame)
        self.entry_potencia.pack(padx=15, pady=5, fill="x")
        self.entry_potencia.insert(0, "250")

        # BOTÓN MAESTRO DE ACCIÓN
        btn_simular = ctk.CTkButton(
            left_frame, 
            text="EJECUTAR SIMULACIÓN INDUSTRIAL", 
            height=45, 
            font=("Arial", 13, "bold"), 
            fg_color="#10b981", 
            hover_color="#059669", 
            command=self.simular
        )
        btn_simular.pack(padx=15, pady=25, fill="x")

        # =================================================
        # PANEL DERECHO: CONTENEDOR DE PESTAÑAS (TABVIEW)
        # =================================================
        self.tab_panel = ctk.CTkTabview(main_frame)
        self.tab_panel.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        # Creación de las pestañas
        self.tab_scada = self.tab_panel.add("Monitor SCADA")
        self.tab_grafico = self.tab_panel.add("Telemetría Gráfica")
        self.tab_costos = self.tab_panel.add("Costos y Sostenibilidad")

        # --- CONTENIDO DE LA PESTAÑA 1: MONITOR SCADA ---
        grid_indicadores = ctk.CTkFrame(self.tab_scada, fg_color="#1e293b", corner_radius=10)
        grid_indicadores.pack(fill="x", padx=20, pady=15)

        self.status_led = ctk.CTkLabel(grid_indicadores, text="● HORNO APAGADO", font=("Arial", 15, "bold"), text_color="#94a3b8")
        self.status_led.grid(row=0, column=0, padx=30, pady=20)

        self.label_temp = ctk.CTkLabel(grid_indicadores, text="CONSIGNA: -- °C", font=("Arial", 15, "bold"), text_color="#f87171")
        self.label_temp.grid(row=0, column=1, padx=30, pady=20)

        self.label_tiempo = ctk.CTkLabel(grid_indicadores, text="TIEMPO EST: -- min", font=("Arial", 15, "bold"), text_color="#fbbf24")
        self.label_tiempo.grid(row=0, column=2, padx=30, pady=20)

        self.texto_scada = ctk.CTkTextbox(self.tab_scada, font=("Consolas", 14))
        self.texto_scada.pack(fill="both", expand=True, padx=20, pady=10)

        # --- CONTENIDO DE LA PESTAÑA 2: TELEMETRÍA GRÁFICA ---
        self.fig = Figure(figsize=(8, 5), dpi=100, facecolor='#242424')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_grafico)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        # --- CONTENIDO DE LA PESTAÑA 3: COSTOS Y SOSTENIBILIDAD ---
        self.texto_costos = ctk.CTkTextbox(self.tab_costos, font=("Consolas", 14))
        self.texto_costos.pack(fill="both", expand=True, padx=20, pady=20)

    # =================================================
    # LÓGICA DE SIMULACIÓN Y CÁLCULOS TÉRMICOS
    # =================================================
    def simular(self):
        try:
            temp_inicial = float(self.entry_temp.get())
            diametro = float(self.entry_diametro.get())
            largo = float(self.entry_largo.get())
            potencia_kw = float(self.entry_potencia.get())
            
            if diametro <= 0 or largo <= 0 or potencia_kw <= 0: raise ValueError
        except:
            messagebox.showerror("ERROR DE ENTRADA", "Verifique que todos los valores numéricos sean mayores a cero.")
            return

        # 1. Obtención de datos del Metal
        metal = self.combo_material.get()
        d_metal = materiales[metal]
        temp_obj = d_metal["temp"]
        delta_t = temp_obj - temp_inicial

        if delta_t <= 0:
            messagebox.showwarning("OPERACIÓN INVÁLIDA", "La temperatura inicial ingresada ya es igual o mayor a la de fragua.")
            return

        vol_metal = 3.1416 * (diametro / 2) ** 2 * largo
        masa_metal = vol_metal * d_metal["densidad"]
        calor_metal = masa_metal * d_metal["calor_especifico"] * delta_t 

        # 2. Análisis estructural refractario
        pared = self.combo_pared.get()
        d_pared = materiales[pared]
        espesor_pared = 0.12  
        radio_int = (diametro / 2) + 0.15  
        radio_ext = radio_int + thickness if 'thickness' in locals() else radio_int + espesor_pared
        
        vol_pared = 3.1416 * (radio_ext**2 - radio_int**2) * (largo + 0.3)
        masa_pared = vol_pared * d_pared["densidad"]
        calor_pared = masa_pared * d_pared["calor_especifico"] * (delta_t * 0.5)

        calor_neto_necesario = calor_metal + calor_pared

        # 3. MÓDULO DE ENERGÍAS INDUSTRIALES CON TARIFAS EN SOLES (S/.)
        combustible = self.combo_combustible.get()
        
        if combustible == "Gas Natural (GN)":
            eficiencia_base = random.uniform(68, 75) if "Ladrillo" in pared else random.uniform(78, 84)
            calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
            consumo = calor_bruto / 38000  # 38,000 kJ por m3
            unidad = "m³"
            costo = consumo * 1.65          # S/. 1.65 por m3 (Tarifa industrial aproximada)
            co2 = consumo * 1.95            
            
        elif combustible == "Gas Licuado (GLP)":
            eficiencia_base = random.uniform(72, 78) if "Ladrillo" in pared else random.uniform(82, 88)
            calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
            consumo = calor_bruto / 46000  # 46,000 kJ por kg
            unidad = "kg"
            costo = consumo * 4.50          # S/. 4.50 por kg (GLP granel industrial)
            co2 = consumo * 3.00            
            
        elif combustible == "Electricidad (Inducción)":
            eficiencia_base = random.uniform(88, 94)
            calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
            consumo = calor_bruto / 3600    # 3,600 kJ por kWh
            unidad = "kWh"
            costo = consumo * 0.42          # S/. 0.42 por kWh (Tarifa MT industrial fuera de punta)
            co2 = 0.00                      

        # Tiempo estimado de quemado
        tiempo_minutos = (calor_bruto / potencia_kw) / 60

        # Alarma SCADA visual
        if temp_obj >= 1150:
            self.status_led.configure(text="⚠ ALTA TEMPERATURA", text_color="#ef4444")
        else:
            self.status_led.configure(text="● HORNO ACTIVO", text_color="#10b981")

        # Actualización de la cuadrícula superior del SCADA
        self.label_temp.configure(text=f"CONSIGNA: {temp_obj} °C")
        self.label_tiempo.configure(text=f"TIEMPO EST: {tiempo_minutos:.1f} min")

        # --- TEXTO PESTAÑA 1: MONITOR SCADA ---
        reporte_scada = f"""==================================================
MONITOR SCADA - TELEMETRÍA DEL PROCESO
==================================================
• Estado de Carga: Metal [{metal}] detectado en cámara.
• Geometría de la Pieza: Diámetro {diametro:.2f} m | Largo {largo:.2f} m
• Masa Neta del Metal: {masa_metal:.2f} kg
• Energía Térmica Directa Absorbiéndose: {calor_metal:.2f} kJ

• Estado de la Estructura: Pared [{pared.replace("PARED: ", "")}]
• Masa de Material Refractario: {masa_pared:.2f} kg
• Calor Absorbido por Inercia Estructural: {calor_pared:.2f} kJ
--------------------------------------------------
• Potencia Suministrada por Sistema de Fuego: {potencia_kw:.0f} kW
• Eficiencia del Sistema Combinado: {eficiencia_base:.1f} %
"""
        self.texto_scada.delete("0.0", "end")
        self.texto_scada.insert("0.0", reporte_scada)

        # --- TEXTO PESTAÑA 3: COSTOS Y SOSTENIBILIDAD ---
        reporte_costos = f"""==================================================
MÓDULO DE COSTOS ENERGÉTICOS Y SOSTENIBILIDAD
==================================================
• Vector Energético Utilizado: {combustible}
• Consumo Energético Total Bruto: {calor_bruto:.2f} kJ

• Cantidad de Suministro Requerido: {consumo:.2f} {unidad}
• Tarifa Eléctrica/Combustible Aplicada: S/. {costo/consumo if consumo > 0 else 0:.4f} por {unidad}
--------------------------------------------------
TOTAL FACTURADO POR EL CICLO:
> S/. {costo:.2f} PEN

IMPACTO AMBIENTAL DIRECTO (HUELLA DE CARBONO):
> {co2:.2f} kg de CO₂ emitidos a la atmósfera.
"""
        self.texto_costos.delete("0.0", "end")
        self.texto_costos.insert("0.0", reporte_costos)

        # --- ACTUALIZACIÓN DE LA PESTAÑA 2: GRÁFICO ---
        temperaturas = []
        temp_actual = temp_inicial
        incremento = (temp_obj - temp_inicial) / 30
        for _ in range(30):
            temp_actual += incremento
            temperaturas.append(temp_actual + random.uniform(-6, 6))

        self.ax.clear()
        self.ax.plot(temperaturas, linewidth=3, color="#ef4444", label="Curva Térmica Dinámica")
        self.ax.axhline(y=temp_obj, color='#10b981', linestyle='--', label=f'SetPoint Objetivo ({temp_obj}°C)')
        self.ax.set_title("Evolución del Proceso Térmico Frente al Tiempo")
        self.ax.set_xlabel("Progreso del Ciclo de Trabajo")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.grid(True, color="#444444", linestyle="--")
        self.ax.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
        self.canvas.draw()

        self.tab_panel.set("Monitor SCADA")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SistemaFragua(root)
    root.mainloop()