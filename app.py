serrated_synd = st.toggle("¿Te diagnosticaron síndrome de poliposis serrada (múltiples pólipos serrados)?", value=False,
                                 help="Los pólipos serrados tienen un riesgo elevado de transformación maligna por una vía molecular distinta")

        # Save to session state
        st.session_state.ibd = ibd
        st.session_state.hered = hered
        st.session_state.hamart = hamart
        st.session_state.fap = fap
        st.session_state.fasha = fasha
        st.session_state.serrated_synd = serrated_synd

        # 2. Family history with additional explanations
        st.markdown("**2. Antecedentes familiares**")

        with st.expander("¿Por qué es importante la historia familiar?", expanded=False):
            st.markdown("""
            La presencia de CCR en familiares de primer grado (padres, hermanos, hijos) aumenta tu riesgo personal.
            
            El riesgo es mayor si:
            - Hay múltiples familiares afectados
            - El familiar fue diagnosticado antes de los 60 años
            - El familiar tuvo múltiples cánceres relacionados
            
            Según las guías argentinas, los antecedentes familiares modifican la edad de inicio y la frecuencia del tamizaje.
            """)

        family_crc = st.toggle("¿Tenés un familiar directo (padre/madre/hermano/a/hijo/a) con cáncer colorrectal?", value=False,
                              help="Los familiares de primer grado son padres, hermanos e hijos")

        family_before_60 = False
        family_multiple = False

        if family_crc:
            family_before_60 = st.toggle("¿Ese familiar fue diagnosticado antes de los 60 años?", value=False,
                                        help="El diagnóstico temprano en familiares indica mayor riesgo genético")

            family_multiple = st.toggle("¿Tenés más de un familiar directo con cáncer colorrectal?", value=False,
                                       help="Múltiples familiares afectados aumentan significativamente el riesgo")
        
        # Save to session state
        st.session_state.family_crc = family_crc
        st.session_state.family_before_60 = family_before_60
        st.session_state.family_multiple = family_multiple

        # Navigation buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Volver a Datos Personales"):
                st.session_state.current_tab = 0
        with col2:
            if st.button("Continuar a Historia de Pólipos →", type="primary"):
                st.session_state.current_tab = 2

    elif st.session_state.current_tab == 2:  # Historia de Pólipos tab
        # 3. Polyp history with enhanced information
        st.subheader("Historial de pólipos")

        with st.expander("¿Qué son los pólipos y por qué son importantes?", expanded=False):
            st.markdown("""
            Los pólipos son crecimientos anormales en el revestimiento del colon o recto. Aunque la mayoría son benignos, algunos pueden convertirse en cáncer con el tiempo.
            
            **Tipos de pólipos de mayor riesgo:**
            - Adenomas avanzados (>1cm, componente velloso, displasia de alto grado)
            - Pólipos serrados (especialmente los sésiles)
            - Múltiples pólipos (más de 3)
            
            La detección y extirpación de pólipos mediante colonoscopia es una forma efectiva de prevenir el cáncer colorrectal.
            """)

        polyp10 = st.toggle("Durante los últimos 10 años, ¿algún médico te dijo que tenías pólipos en el colon o el recto?", value=False,
                           help="La presencia de pólipos previos es un factor de riesgo para nuevos pólipos y CCR")

        advanced_poly = False
        serrated = False
        resected = False
        multiple_polyps = False
        polyp_size = None

        if polyp10:
            advanced_poly = st.toggle("¿Alguno de esos pólipos fue grande (más de 1 cm) o de alto riesgo?", value=False,
                                     help="Los pólipos grandes tienen mayor riesgo de transformación maligna")

            serrated = st.toggle("¿Alguno de los pólipos era del tipo serrado?", value=False,
                                help="Los pólipos serrados siguen una vía diferente de carcinogénesis")

            multiple_polyps = st.toggle("¿Tenías más de 3 pólipos en total?", value=False,
                                       help="El número de pólipos influye en el riesgo y el intervalo de vigilancia")

            col1, col2 = st.columns(2)
            with col1:
                polyp_options = ["No lo sé",
                                "Menos de 5mm", "5-10mm", "Más de 10mm"]
                polyp_size = st.selectbox("¿Cuál era el tamaño del pólipo más grande?", polyp_options,
                                         help="El tamaño del pólipo es un factor importante para determinar el riesgo")

            with col2:
                resected = st.toggle("¿Te realizaron una resección o extirpación de esos pólipos o adenomas?", value=False,
                                    help="La extirpación de pólipos reduce el riesgo pero requiere seguimiento")
        
        # Save to session state
        st.session_state.polyp10 = polyp10
        st.session_state.advanced_poly = advanced_poly
        st.session_state.serrated = serrated
        st.session_state.multiple_polyps = multiple_polyps
        st.session_state.polyp_size = polyp_size
        st.session_state.resected = resected

        # Navigation buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Volver a Antecedentes"):
                st.session_state.current_tab = 1
        with col2:
            if st.button("Continuar a Síntomas →", type="primary"):
                st.session_state.current_tab = 3

    elif st.session_state.current_tab == 3:  # Síntomas tab
        # Symptoms (detailed section)
        st.subheader("Síntomas actuales")

        with st.expander("Acerca de los síntomas digestivos", expanded=True):
            st.markdown("""
            La presencia de síntomas requiere evaluación diagnóstica, no tamizaje. El tamizaje está diseñado para personas asintomáticas.
            
            Los síntomas que requieren evaluación médica incluyen:
            - Sangrado rectal
            - Cambios en los hábitos intestinales que persisten (diarrea, estreñimiento)
            - Dolor abdominal recurrente
            - Pérdida de peso involuntaria
            - Sensación de evacuación incompleta
            - Anemia inexplicada
            
            Estos síntomas pueden tener muchas causas, pero deben ser evaluados por un médico para descartar cáncer colorrectal.
            """)

        # More specific symptom questions
        symptoms = {}
        symptoms["blood"] = st.toggle(
            "¿Has notado sangre en las heces o en el papel higiénico en el último mes?", value=False)
        symptoms["bowel_changes"] = st.toggle(
            "¿Has experimentado cambios persistentes en tus hábitos intestinales (diarrea, estreñimiento) por más de 3 semanas?", value=False)
        symptoms["weight_loss"] = st.toggle(
            "¿Has perdido peso sin explicación (sin dieta o ejercicio) en los últimos 3 meses?", value=False)
        symptoms["pain"] = st.toggle(
            "¿Tienes dolor abdominal recurrente o persistente?", value=False)
        symptoms["incomplete"] = st.toggle(
            "¿Sientes con frecuencia que no has evacuado completamente después de ir al baño?", value=False)

        # Calculate if any symptoms are present
        any_symptoms = any(symptoms.values())
        
        # Save to session state
        st.session_state.symptoms = symptoms
        st.session_state.any_symptoms = any_symptoms

        if any_symptoms:
            st.warning(
                "⚠️ Has indicado la presencia de síntomas que requieren evaluación médica. Consulta con un médico lo antes posible.")

        # Navigation buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Volver a Historia de Pólipos"):
                st.session_state.current_tab = 2
        with col2:
            if st.button("Continuar a Evaluación →", type="primary"):
                st.session_state.current_tab = 4

    elif st.session_state.current_tab == 4:  # Evaluación tab
        st.subheader("Evaluación de riesgo")

        # Get data from session state
        age = None
        bmi = None
        height_cm = None
        weight_kg = None
        
        if 'age' in st.session_state:
            age = st.session_state.age
        if 'bmi' in st.session_state:
            bmi = st.session_state.bmi
        if 'height_cm' in st.session_state:
            height_cm = st.session_state.height_cm
        if 'weight_kg' in st.session_state:
            weight_kg = st.session_state.weight_kg
            
        # Get risk factors from session state
        ibd = st.session_state.get('ibd', False)
        hered = st.session_state.get('hered', False)
        hamart = st.session_state.get('hamart', False)
        fap = st.session_state.get('fap', False)
        fasha = st.session_state.get('fasha', False)
        serrated_synd = st.session_state.get('serrated_synd', False)
        
        family_crc = st.session_state.get('family_crc', False)
        family_before_60 = st.session_state.get('family_before_60', False)
        family_multiple = st.session_state.get('family_multiple', False)
        
        polyp10 = st.session_state.get('polyp10', False)
        advanced_poly = st.session_state.get('advanced_poly', False)
        serrated = st.session_state.get('serrated', False)
        resected = st.session_state.get('resected', False)
        multiple_polyps = st.session_state.get('multiple_polyps', False)
        polyp_size = st.session_state.get('polyp_size', None)
        
        any_symptoms = st.session_state.get('any_symptoms', False)

        # Check if we have all required data
        can_evaluate = age is not None and bmi is not None

        if can_evaluate:
            st.markdown(f"**Edad:** {age} años | **IMC:** {bmi} kg/m²")

            # Collect risk factors
            personal_history = {
                "ibd": ibd,
                "lynch": hered,
                "hamart": hamart,
                "fap": fap,
                "fasha": fasha,
                "serrated_synd": serrated_synd
            }

            family_history = {
                "family_crc": family_crc,
                "family_before_60": family_before_60,
                "family_multiple": family_multiple
            }

            polyp_history = {
                "polyp10": polyp10,
                "advanced_poly": advanced_poly,
                "serrated": serrated,
                "resected": resected,
                "multiple_polyps": multiple_polyps,
                "polyp_size": polyp_size
            }

            # Button to evaluate risk
            if st.button("Evaluar riesgo", type="primary"):
                try:
                    st.markdown("---")
                    st.subheader("Estrategia de tamizaje recomendada")

                    # Get comprehensive risk assessment
                    risk_category, recommendation, summary, lifestyle_advice, symptoms_detail, bmi_note, symptoms_warning = evaluate_risk(
                        age, bmi, personal_history, family_history, polyp_history, any_symptoms
                    )

                    # Display risk category with appropriate styling
                    if "Alto" in risk_category:
                        st.error(f"**{risk_category}**")
                    elif "Incrementado" in risk_category or "Intermedio" in risk_category:
                        st.info(f"**{risk_category}**")
                    else:
                        st.success(f"**{risk_category}**")

                    # Display recommendation
                    st.markdown(recommendation)

                    # Display BMI note if applicable
                    if bmi_note:
                        st.markdown(bmi_note)

                    # Display symptoms warning if applicable
                    if any_symptoms:
                        st.error(symptoms_warning)
                        st.markdown(symptoms_detail)

                    # Display timeline visualization for screening intervals
                    st.subheader("Cronograma de tamizaje recomendado")

                    # Create a basic timeline based on risk category
                    current_year = datetime.now().year

                    if "Alto" in risk_category:
                        if "Lynch" in risk_category or "Poliposis" in risk_category:
                            interval = 1
                            timeline_years = 10
                        else:
                            interval = 3
                            timeline_years = 12
                    elif "Incrementado" in risk_category or "Intermedio" in risk_category:
                        interval = 5
                        timeline_years = 15
                    else:
                        if 50 <= age <= 75:
                            interval = 2  # For TSOMFi
                            timeline_years = 10
                        else:
                            interval = None
                            timeline_years = 0

                    if interval:
                        years = [
                            current_year + i*interval for i in range(int(timeline_years/interval) + 1)]
                        timeline_data = pd.DataFrame({
                            'Año': years,
                            'Tamizaje': [f"Tamizaje #{i+1}" for i in range(len(years))]
                        })

                        st.dataframe(timeline_data, hide_index=True)
                    else:
                        if age < 50:
                            st.info("No se recomienda tamizaje de rutina antes de los 50 años para personas de riesgo promedio. Consulta con tu médico cuando cumplas 50 años o si desarrollas síntomas.")
                        elif age > 75:
                            st.info("El tamizaje de rutina no está recomendado después de los 75 años. Tu médico evaluará individualmente la necesidad de continuar el tamizaje basado en tu estado de salud general y expectativa de vida.")

                    # Display lifestyle recommendations
                    st.subheader("Recomendaciones para reducir el riesgo")
                    st.markdown(lifestyle_advice)

                    # Display summary
                    st.markdown("---")
                    st.markdown(f"### **Resumen final:** {summary}")

                    # Option to download PDF
                    st.subheader("Guardar resultados")

                    # Ensure all variables needed for PDF generation exist and are properly formatted
                    try:
                        # Generate PDF with sanitized text for FPDF
                        pdf_buffer = generate_pdf(
                            str(age) if age is not None else "No disponible",
                            str(bmi) if bmi is not None else "No disponible",
                            summary if summary is not None else "Consulta con tu médico para recomendaciones específicas.",
                            risk_category if risk_category is not None else "No categorizado",
                            recommendation if recommendation is not None else "Consulta con un profesional de la salud.",
                            lifestyle_advice if lifestyle_advice is not None else "Mantén un estilo de vida saludable.",
                            any_symptoms
                        )

                        st.download_button(
                            label="Descargar resultados en PDF",
                            data=pdf_buffer,
                            file_name=f"evaluacion_riesgo_ccr_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            help="Descarga un PDF con los resultados de tu evaluación para compartir con tu médico"
                        )
                    except Exception as e:
                        st.error(f"No se pudo generar el PDF. Error: {str(e)}")

                    # Save assessment to file option
                    st.markdown("---")
                    save_data = {
                        "fecha_evaluacion": datetime.now().strftime("%Y-%m-%d"),
                        "edad": age,
                        "imc": bmi,
                        "categoria_riesgo": risk_category,
                        "recomendacion": recommendation,
                        "resumen": summary
                    }

                    try:
                        st.download_button(
                            label="Guardar datos en formato JSON",
                            data=json.dumps(save_data, indent=4),
                            file_name=f"evaluacion_riesgo_ccr_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            help="Descarga los datos en formato JSON para futuras consultas o seguimiento"
                        )
                    except Exception as e:
                        st.error(f"No se pudo crear el archivo JSON. Error: {str(e)}")

                except Exception as e:
                    st.error(f"Error al procesar los datos. Por favor verifica la información ingresada. Detalles: {str(e)}")
        else:
            st.warning("Por favor completa todos los campos obligatorios en las pestañas anteriores para obtener tu evaluación de riesgo.")

        # Navigation buttons
        st.markdown("---")
        if st.button("← Volver a Síntomas"):
            st.session_state.current_tab = 3

# Footer with disclaimer and links
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""**Aviso:** Esta herramienta tiene fines educativos e informativos y está adaptada a la guía \"Recomendaciones para el tamizaje de CCR en población de riesgo promedio en Argentina\" del Instituto Nacional del Cáncer. No constituye una consulta médica ni reemplaza el consejo de un profesional de la salud. Te invitamos a usar esta información como base para conversar con tu médico sobre tu riesgo de cáncer colorrectal y las alternativas recomendadas en tu caso.""")

with col2:
    st.markdown("""
    **Enlaces útiles:**
    - [Programa Nacional de Prevención y Detección Temprana de CCR](https://www.argentina.gob.ar/salud/instituto-nacional-del-cancer/institucional/el-inc/pnccr)
    - [Instituto Nacional del Cáncer](https://www.argentina.gob.ar/salud/inc)
    - [Tamizaje](https://www.argentina.gob.ar/salud/inc/lineas-programaticas/pnccr-tamizaje)
    """)

# Add just one caption at the end
st.caption("© 2025 - Desarrollado por PEGASI Chubut. Todos los derechos reservados.")
# Add just one caption at the end
st.caption("© 2025 - Desarrollado por PEGASI Chubut. Todos los derechos reservados.")
