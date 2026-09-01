import streamlit as st
import pandas as pd
try:
    from chempy import balance_stoichiometry
    from chempy import Substance
except ImportError:
    st.error("Por favor instala 'chempy' para utilizar la función de balanceo automático.")

st.set_page_config(page_title="Estimador de Margen Bruto - Biodiesel", layout="wide")

# 1. Información inicial de horas
st.title("Estimador de Margen Bruto de Ganancias")
st.info("💡 **Referencia:** Se considera un año base de **8760 horas** de trabajo.")

# 2. Selección de proceso y capacidad
st.sidebar.header("Parámetros del Proceso")
proceso = st.sidebar.selectbox(
    "Seleccione el proceso de producción:",
    ["Biodiesel con Metanol", "Biodiesel con Etanol", "Biodiesel con Acetato de Metilo", "Otro"]
)

produccion_anual = st.sidebar.number_input("Producción deseada (Toneladas/año):", min_value=1.0, value=120000.0, step=1000.0)

tipo_proceso = st.sidebar.radio("Tipo de proceso:", ["Batch", "Continuo"])
horas_trabajadas = 0
if tipo_proceso == "Batch":
    horas_trabajadas = 6000
    st.sidebar.write(f"Horas trabajadas al año: **{horas_trabajadas} hs**")
else:
    disponibilidad = st.sidebar.radio("Disponibilidad de planta:", ["80%", "90%"])
    if disponibilidad == "80%":
        horas_trabajadas = 8760 * 0.8
    else:
        horas_trabajadas = 8760 * 0.9
    st.sidebar.write(f"Horas trabajadas calculadas (8760 * {disponibilidad}): **{horas_trabajadas} hs**")

# Definir datos estándar para las rutas conocidas
rutas = {
    "Biodiesel con Metanol": {
        "ecuacion": r"C_3H_5(OOCR)_3 + 3 CH_3OH \rightleftharpoons 3 R-COOCH_3 + C_3H_5(OH)_3",
        "reactivos": [{"nombre": "Aceite de Soja", "pm": 874.0, "moles": 1}, {"nombre": "Metanol", "pm": 32.0, "moles": 3}],
        "productos": [{"nombre": "Biodiesel", "pm": 292.67, "moles": 3}, {"nombre": "Glicerina", "pm": 92.0, "moles": 1}],
        "producto_principal": "Biodiesel"
    },
    "Biodiesel con Etanol": {
        "ecuacion": r"C_3H_5(OOCR)_3 + 3 C_2H_5OH \rightleftharpoons 3 R-COOC_2H_5 + C_3H_5(OH)_3",
        "reactivos": [{"nombre": "Aceite de Soja", "pm": 874.0, "moles": 1}, {"nombre": "Etanol", "pm": 46.07, "moles": 3}],
        "productos": [{"nombre": "Biodiesel", "pm": 306.667, "moles": 3}, {"nombre": "Glicerina", "pm": 92.0, "moles": 1}],
        "producto_principal": "Biodiesel"
    },
    "Biodiesel con Acetato de Metilo": {
        "ecuacion": r"C_3H_5(OOCR)_3 + 3 CH_3COOCH_3 \rightleftharpoons 3 R-COOCH_3 + C_3H_5(OOCCH_3)_3",
        "reactivos": [{"nombre": "Aceite de Soja", "pm": 874.0, "moles": 1}, {"nombre": "Acetato de Metilo", "pm": 74.08, "moles": 3}],
        "productos": [{"nombre": "Biodiesel", "pm": 292.67, "moles": 3}, {"nombre": "Triacetina", "pm": 218.21, "moles": 1}],
        "producto_principal": "Biodiesel"
    }
}

datos_proceso = None

if proceso != "Otro":
    datos_proceso = rutas[proceso]
    
    st.subheader("1. Diagrama de Bloques y Reacción")
    reac_nombres = "<br>".join([r['nombre'] for r in datos_proceso['reactivos']])
    prod_nombres = "<br>".join([p['nombre'] for p in datos_proceso['productos']])
    
    diagrama_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; margin: 20px; font-family: sans-serif;">
        <div style="text-align: right; margin-right: 15px; font-size: 18px; font-weight: bold; color: #2C3E50;">
            {reac_nombres}
        </div>
        <div style="font-size: 30px; margin-right: 10px;">&rarr;</div>
        <div style="border: 3px solid #2980B9; padding: 25px; background-color: #ECF0F1; color: #2C3E50; border-radius: 10px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #2980B9;">REACTOR</h3>
            <p style="margin: 5px 0 0 0; font-style: italic;">Transesterificación</p>
        </div>
        <div style="font-size: 30px; margin-left: 10px;">&rarr;</div>
        <div style="text-align: left; margin-left: 15px; font-size: 18px; font-weight: bold; color: #27AE60;">
            {prod_nombres}
        </div>
    </div>
    """
    st.markdown(diagrama_html, unsafe_allow_html=True)
    st.latex(datos_proceso['ecuacion'])
    
else:
    st.subheader("1. Configuración de Reacción Personalizada (Otro)")
    st.write("Ingrese las fórmulas químicas válidas (ej. H2, O2, H2O, CH4) para balancear la ecuación.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Reactivos**")
        num_reac = st.number_input("Cantidad de Reactivos", min_value=1, max_value=5, value=2)
        reactivos_formulas = []
        for i in range(num_reac):
            reactivos_formulas.append(st.text_input(f"Fórmula Reactivo {i+1}", value="H2" if i==0 else "O2"))
            
    with col2:
        st.write("**Productos**")
        num_prod = st.number_input("Cantidad de Productos", min_value=1, max_value=5, value=1)
        productos_formulas = []
        for i in range(num_prod):
            productos_formulas.append(st.text_input(f"Fórmula Producto {i+1}", value="H2O"))
            
    if st.button("Balancear y Calcular Propiedades"):
        try:
            reac_set, prod_set = balance_stoichiometry(set(reactivos_formulas), set(productos_formulas))
            st.success("¡Ecuación balanceada con éxito!")
            
            datos_proceso = {
                "reactivos": [],
                "productos": [],
                "producto_principal": productos_formulas[0]
            }
            
            ecuacion_str = ""
            for idx, (f, moles) in enumerate(reac_set.items()):
                sub = Substance.from_formula(f)
                datos_proceso["reactivos"].append({"nombre": f, "pm": sub.mass, "moles": moles})
                ecuacion_str += f"{moles} {f} "
                if idx < len(reac_set) - 1: ecuacion_str += "+ "
                
            ecuacion_str += r"\rightarrow "
            
            for idx, (f, moles) in enumerate(prod_set.items()):
                sub = Substance.from_formula(f)
                datos_proceso["productos"].append({"nombre": f, "pm": sub.mass, "moles": moles})
                ecuacion_str += f"{moles} {f} "
                if idx < len(prod_set) - 1: ecuacion_str += "+ "
                
            datos_proceso["ecuacion"] = ecuacion_str
            st.session_state['datos_proceso'] = datos_proceso
            
        except Exception as e:
            st.error(f"Error al balancear. Verifique las fórmulas. Detalles: {e}")

if proceso == "Otro" and 'datos_proceso' in st.session_state:
    datos_proceso = st.session_state['datos_proceso']
    st.latex(datos_proceso['ecuacion'])
    producto_principal_opcion = st.selectbox("Seleccione cuál es el Producto Principal:", [p['nombre'] for p in datos_proceso['productos']])
    datos_proceso['producto_principal'] = producto_principal_opcion


if datos_proceso is not None:
    st.markdown("---")
    st.subheader("2. Estequiometría y Consumo Específico")
    
    prod_princ = next(p for p in datos_proceso['productos'] if p['nombre'] == datos_proceso['producto_principal'])
    pm_base = prod_princ['pm']
    moles_base = prod_princ['moles']
    masa_base_total = pm_base * moles_base
    
    st.write(f"**Producción ingresada:** {produccion_anual:,.2f} Toneladas/año de {prod_princ['nombre']}")
    
    col_reac, col_prod = st.columns(2)
    
    consumos = {}
    
    with col_reac:
        st.write("#### Reactivos")
        for r in datos_proceso['reactivos']:
            masa_r = r['pm'] * r['moles']
            ce = masa_r / masa_base_total
            consumos[r['nombre']] = {"tipo": "reactivo", "ce": ce, "moles": r['moles'], "pm": r['pm']}
            st.markdown(f"**{r['nombre']}**:")
            st.write(f"- Peso Molecular: {r['pm']:.2f} g/mol")
            st.write(f"- Moles reaccionantes: {r['moles']}")
            st.write(f"- Consumo Específico: `{ce:.4f}` Ton {r['nombre']} / Ton {prod_princ['nombre']}")
            
    with col_prod:
        st.write("#### Productos")
        for p in datos_proceso['productos']:
            masa_p = p['pm'] * p['moles']
            ce = masa_p / masa_base_total
            consumos[p['nombre']] = {"tipo": "producto", "ce": ce, "moles": p['moles'], "pm": p['pm']}
            st.markdown(f"**{p['nombre']}**:")
            st.write(f"- Peso Molecular: {p['pm']:.2f} g/mol")
            st.write(f"- Moles producidos: {p['moles']}")
            if p['nombre'] != prod_princ['nombre']:
                st.write(f"- Generación Específica: `{ce:.4f}` Ton {p['nombre']} / Ton {prod_princ['nombre']}")
            else:
                st.write(f"- Base de cálculo (1 Ton / Ton)")

    st.markdown("---")
    st.subheader("3. Análisis Económico y Margen Bruto")
    st.write("Ingrese los precios (USD/Tonelada) consultados. Si no compra un reactivo, seleccione 'No' y se asignará 0 USD/Ton.")
    
    precios = {}
    clasificacion_prod = {}
    factores = {}
    
    col_econ_r, col_econ_p = st.columns(2)
    
    with col_econ_r:
        st.write("#### Precios de Reactivos")
        for r in datos_proceso['reactivos']:
            compra = st.radio(f"¿Compra {r['nombre']}?", ["Sí", "No"], key=f"compra_{r['nombre']}")
            if compra == "Sí":
                precio = st.number_input(f"Precio {r['nombre']} (USD/Ton)", min_value=0.0, value=1000.0, step=10.0, key=f"precio_{r['nombre']}")
                precios[r['nombre']] = precio
            else:
                st.info(f"{r['nombre']} asignado con 0 USD/Ton")
                precios[r['nombre']] = 0.0

    with col_econ_p:
        st.write("#### Precios de Productos")
        for p in datos_proceso['productos']:
            if p['nombre'] == prod_princ['nombre']:
                precio = st.number_input(f"Precio Venta {p['nombre']} (USD/Ton)", min_value=0.0, value=1500.0, step=10.0, key=f"precio_{p['nombre']}")
                precios[p['nombre']] = precio
                clasificacion_prod[p['nombre']] = "Principal"
            else:
                tipo = st.selectbox(f"Categoría de {p['nombre']}", ["Subproducto", "Residuo"], key=f"tipo_{p['nombre']}")
                clasificacion_prod[p['nombre']] = tipo
                precio = st.number_input(f"Precio/Costo {p['nombre']} (USD/Ton)", min_value=0.0, value=150.0, step=10.0, key=f"precio_{p['nombre']}")
                precios[p['nombre']] = precio
                if tipo == "Subproducto":
                    factor = st.slider(f"Factor de venta {p['nombre']} (Ajuste de mercado)", 0.0, 1.0, 1.0, key=f"factor_{p['nombre']}")
                    factores[p['nombre']] = factor

    ingresos = precios[prod_princ['nombre']]
    costos_reactivos = 0.0
    ingresos_sub = 0.0
    costos_residuos = 0.0
    
    st.write("#### Detalle del Cálculo (Por Tonelada de Producto Principal)")
    for nombre, prop in consumos.items():
        if prop['tipo'] == 'reactivo':
            costo = prop['ce'] * precios[nombre]
            costos_reactivos += costo
            st.write(f"- Costo {nombre}: {prop['ce']:.4f} * {precios[nombre]:.2f} = **-{costo:.2f} USD**")
        elif prop['tipo'] == 'producto' and nombre != prod_princ['nombre']:
            if clasificacion_prod[nombre] == "Subproducto":
                ingreso_s = prop['ce'] * precios[nombre] * factores[nombre]
                ingresos_sub += ingreso_s
                st.write(f"- Ingreso {nombre} (Subproducto): {prop['ce']:.4f} * {precios[nombre]:.2f} * Factor({factores[nombre]}) = **+{ingreso_s:.2f} USD**")
            elif clasificacion_prod[nombre] == "Residuo":
                costo_r = prop['ce'] * precios[nombre]
                costos_residuos += costo_r
                st.write(f"- Costo tratamiento {nombre} (Residuo): {prop['ce']:.4f} * {precios[nombre]:.2f} = **-{costo_r:.2f} USD**")

    margen_bruto = ingresos + ingresos_sub - costos_reactivos - costos_residuos
    
    st.markdown("### Resultado del Margen Bruto de Ganancia")
    formula_str = f"**Margen Bruto** = Precio Principal ({ingresos:.2f}) + Subproductos ({ingresos_sub:.2f}) - Reactivos ({costos_reactivos:.2f}) - Residuos ({costos_residuos:.2f})"
    st.write(formula_str)
    
    if margen_bruto >= 0:
        st.success(f"### 💰 Margen Bruto: {margen_bruto:.2f} USD / Ton de {prod_princ['nombre']}")
    else:
        st.error(f"### ⚠️ Margen Bruto Negativo: {margen_bruto:.2f} USD / Ton de {prod_princ['nombre']}")
        
    st.info(f"Ganancia Bruta Anual Estimada: **USD {(margen_bruto * produccion_anual):,.2f}**")
