import streamlit as st
import matplotlib.pyplot as plt
import random

# Importación de la base de datos externa (debe estar en el mismo repositorio)
from materiales import materiales

# CONFIGURACIÓN DE LA PÁGINA WEB
st.set_page_config(page_title="Control Industrial de Fragua v2.0", layout="wide")

st.title(" SISTEMA DE CONTROL, GEMELO DIGITAL Y COSTOS - PANEL DE FRAGUA")
st.caption("Versión Web optimizada para el sector industrial peruano (Tarifas en Soles)")

# =================================================
# ESTRUCTURA DE LA INTERFAZ: COLUMNAS PRINCIPALES
# =================================================
col_izquierda, col_derecha = st.columns([1, 2])

with col_izquierda:
    st.header("⚙️ Configuración")
    
    lista_metales = [k for k in materiales.keys() if not k.startswith("PARED:")]
    lista_paredes = [k for k in materiales.keys() if k.startswith("PARED:")]
    lista_combustibles = ["Gas Natural (GN)", "Gas Licuado (GLP)", "Electricidad (Inducción)"]

    metal = st.selectbox("Metal a Fraguar", lista_metales, index=0)
    pared = st.selectbox("Revestimiento de la Pared (Refractario)", lista_paredes, index=0)
    combustible = st.selectbox("Fuente de Energía / Combustible", lista_combustibles, index=0)
    
    temp_inicial = st.number_input("Temperatura Inicial (°C)", value=25.0, step=5.0)
    diametro = st.number_input("Diámetro del Metal (m)", value=0.10, step=0.01)
    largo = st.number_input("Largo del Metal (m)", value=1.00, step=0.1)
    potencia_kw = st.number_input("Potencia del Quemador / Inducción (kW)", value=250.0, step=50.0)

    btn_simular = st.button("🚀 EJECUTAR SIMULACIÓN INDUSTRIAL", use_container_width=True)

# =================================================
# LÓGICA DE SIMULACIÓN Y PROCESAMIENTO
# =================================================
if btn_simular:
    if diametro <= 0 or largo <= 0 or potencia_kw <= 0:
        st.error("Error: Verifique que todos los valores numéricos sean mayores a cero.")
    else:
        d_metal = materiales[metal]
        temp_obj = d_metal["temp"]
        delta_t = temp_obj - temp_inicial

        if delta_t <= 0:
            st.warning("La temperatura inicial ingresada ya es igual o mayor a la de fragua.")
        else:
            # Cálculos físicos
            vol_metal = 3.1416 * (diametro / 2) ** 2 * largo
            masa_metal = vol_metal * d_metal["densidad"]
            calor_metal = masa_metal * d_metal["calor_especifico"] * delta_t 

            d_pared = materiales[pared]
            espesor_pared = 0.12  
            radio_int = (diametro / 2) + 0.15  
            radio_ext = radio_int + espesor_pared
            
            vol_pared = 3.1416 * (radio_ext**2 - radio_int**2) * (largo + 0.3)
            masa_pared = vol_pared * d_pared["densidad"]
            calor_pared = masa_pared * d_pared["calor_especifico"] * (delta_t * 0.5)

            calor_neto_necesario = calor_metal + calor_pared

            # Módulo Económico (Soles)
            if combustible == "Gas Natural (GN)":
                eficiencia_base = random.uniform(68, 75) if "Ladrillo" in pared else random.uniform(78, 84)
                calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
                consumo = calor_bruto / 38000
                unidad = "m³"
                costo = consumo * 1.65          
                co2 = consumo * 1.95            
                
            elif combustible == "Gas Licuado (GLP)":
                eficiencia_base = random.uniform(72, 78) if "Ladrillo" in pared else random.uniform(82, 88)
                calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
                consumo = calor_bruto / 46000
                unidad = "kg"
                costo = consumo * 4.50          
                co2 = consumo * 3.00            
                
            elif combustible == "Electricidad (Inducción)":
                eficiencia_base = random.uniform(88, 94)
                calor_bruto = calor_neto_necesario / (eficiencia_base / 100)
                consumo = calor_bruto / 3600    
                unidad = "kWh"
                costo = consumo * 0.42          
                co2 = 0.00                      

            tiempo_minutos = (calor_bruto / potencia_kw) / 60

            # Despliegue en el panel derecho organizando por pestañas web
            with col_derecha:
                tab_scada, tab_grafico, tab_costos = st.tabs(["📊 Monitor SCADA", "📈 Telemetría Gráfica", "💰 Costos y Sostenibilidad"])
                
                with tab_scada:
                    if temp_obj >= 1150:
                        st.error(f"🔴 ALERTA SCADA: ALTA TEMPERATURA OPERATIVA ({temp_obj}°C)")
                    else:
                        st.success("🟢 ESTADO SCADA: HORNO ACTIVO EN RANGO SEGURO")
                        
                    st.metric(label="Tiempo Estimado de Proceso", value=f"{tiempo_minutos:.1f} min")
                    
                    st.text(f"""
==================================================
MONITOR SCADA - TELEMETRÍA DEL PROCESO
==================================================
• Estado de Carga: Metal [{metal}] detectado en cámara.
• Masa Neta del Metal: {masa_metal:.2f} kg
• Energía Térmica Directa Absorbiéndose: {calor_metal:.2f} kJ

• Estado de la Estructura: Pared [{pared.replace("PARED: ", "")}]
• Masa de Material Refractario: {masa_pared:.2f} kg
• Calor Absorbido por Inercia Estructural: {calor_pared:.2f} kJ
--------------------------------------------------
• Potencia Suministrada por Sistema de Fuego: {potencia_kw:.0f} kW
• Eficiencia del Sistema Combinado: {eficiencia_base:.1f} %
                    """)

                with tab_costos:
                    st.subheader("Balances Financieros Industriales")
                    st.metric(label="Total Facturado por el Ciclo", value=f"S/. {costo:.2f} PEN")
                    st.metric(label="Huella de Carbono Generada", value=f"{co2:.2f} kg CO₂")
                    
                    st.text(f"""
• Vector Energético Utilizado: {combustible}
• Consumo Energético Total Bruto: {calor_bruto:.2f} kJ
• Cantidad de Suministro Requerido: {consumo:.2f} {unidad}
• Tarifa Eléctrica/Combustible Aplicada: S/. {costo/consumo if consumo > 0 else 0:.4f} por {unidad}
                    """)

                with tab_grafico:
                    temperaturas = []
                    temp_actual = temp_inicial
                    incremento = (temp_obj - temp_inicial) / 30
                    for _ in range(30):
                        temp_actual += incremento
                        temperaturas.append(temp_actual + random.uniform(-6, 6))

                    fig, ax = plt.subplots(figsize=(8, 4))
                    fig.patch.set_facecolor('#0e1117')
                    ax.set_facecolor('#1a1a1a')
                    
                    ax.plot(temperaturas, linewidth=3, color="#ef4444", label="Curva Térmica Dinámica")
                    ax.axhline(y=temp_obj, color='#10b981', linestyle='--', label=f'SetPoint Objetivo ({temp_obj}°C)')
                    
                    ax.tick_params(colors='white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')
                    ax.set_title("Evolución del Proceso Térmico", color="white")
                    ax.grid(True, color="#444444", linestyle="--")
                    ax.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
                    
                    st.pyplot(fig)
else:
    with col_derecha:
        st.info("Configure los parámetros a la izquierda y presione el botón para iniciar el Gemelo Digital.")
