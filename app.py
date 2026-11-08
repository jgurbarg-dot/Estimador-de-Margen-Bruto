# ==========================================
    # NUEVA SECCIÓN: EXPORTACIÓN A EXCEL
    # ==========================================
    st.markdown("---")
    st.subheader("5. Exportar Informe a Excel")
    
    # Preparar el cuadro de datos para el Excel
    datos_excel = []
    # Parámetros Generales
    datos_excel.append({"Concepto": "Tipo de Proceso", "Valor": tipo_proceso, "Unidad / Notas": ""})
    datos_excel.append({"Concepto": "Horas Trabajadas", "Valor": horas_trabajadas, "Unidad / Notas": "hs/año"})
    datos_excel.append({"Concepto": "Producción Anual", "Valor": produccion_anual, "Unidad / Notas": "Ton/año"})
    datos_excel.append({"Concepto": "Reacción Química", "Valor": datos_proceso['ecuacion'], "Unidad / Notas": "Estequiometría base"})
    datos_excel.append({"Concepto": "", "Valor": "", "Unidad / Notas": ""}) # Espaciador
    
    # Consumos Específicos
    datos_excel.append({"Concepto": "--- ESTEQUIOMETRÍA Y RELACIONES ---", "Valor": "", "Unidad / Notas": ""})
    for nombre, prop in consumos.items():
        datos_excel.append({
            "Concepto": f"Relación (CE) - {nombre}", 
            "Valor": round(prop['ce'], 4), 
            "Unidad / Notas": f"Ton {nombre} / Ton {prod_princ['nombre']}"
        })
    datos_excel.append({"Concepto": "", "Valor": "", "Unidad / Notas": ""})
    
    # Precios
    datos_excel.append({"Concepto": "--- PRECIOS DE ENTRADA Y SALIDA ---", "Valor": "", "Unidad / Notas": ""})
    for nombre, precio in precios.items():
        datos_excel.append({
            "Concepto": f"Precio/Costo - {nombre}", 
            "Valor": precio, 
            "Unidad / Notas": "USD/Ton"
        })
    datos_excel.append({"Concepto": "", "Valor": "", "Unidad / Notas": ""})
    
    # Resultados
    datos_excel.append({"Concepto": "--- RESULTADOS FINALES ---", "Valor": "", "Unidad / Notas": ""})
    datos_excel.append({"Concepto": "Margen Bruto Unitario", "Valor": round(margen_bruto, 2), "Unidad / Notas": f"USD / Ton {prod_princ['nombre']}"})
    datos_excel.append({"Concepto": "Ganancia Bruta Anual Total", "Valor": round(margen_bruto * produccion_anual, 2), "Unidad / Notas": "USD/año"})
    
    # Crear DataFrame y generar el archivo Excel en memoria
    df_excel = pd.DataFrame(datos_excel)
    
    output = io.BytesIO()
    # Cambio aquí: Simplificado para usar openpyxl directamente
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False, sheet_name="Memoria de Calculo")
        
        # Ajustar el ancho de las columnas para que se vea bien
        worksheet = writer.sheets['Memoria de Calculo']
        for idx, col in enumerate(df_excel.columns):
            max_len = max(df_excel[col].astype(str).map(len).max(), len(col)) + 2
            try:
                worksheet.column_dimensions[chr(65 + idx)].width = max_len
            except Exception:
                pass
                
    output.seek(0)
    
    st.download_button(
        label="📥 Descargar Memoria de Cálculo (Excel)",
        data=output,
        file_name="Memoria_Calculo_Biodiesel.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
