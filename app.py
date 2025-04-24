import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import json

# Set page configuration
st.set_page_config(
    page_title="Evaluación de Riesgo CCR",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing user data
if 'page' not in st.session_state:
    st.session_state.page = 0
    st.session_state.data = {}

# Function to change pages without using experimental_rerun
def change_page(page_number):
    st.session_state.page = page_number

# Helper functions
def calculate_age(dob):
    """Calculate age from date of birth"""
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def calculate_bmi(height_cm, weight_kg):
    """Calculate Body Mass Index"""
    if height_cm <= 0 or weight_kg <= 0:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def validate_numeric_input(value, min_val=0, max_val=None):
    """Validate numeric input within specified range"""
    try:
        val = float(value)
        if val <= min_val:
            return False, f"Value must be greater than {min_val}"
        if max_val and val > max_val:
            return False, f"Value must be less than {max_val}"
        return True, val
    except:
        return False, "Please enter a valid number"

def generate_pdf(edad, imc, resumen, categoria_riesgo, recomendacion, lifestyle_advice=None, symptoms_flag=False):
    """Generate PDF with assessment results and educational content"""
    pdf = FPDF()
    pdf.add_page()

    # Helper function to sanitize text for FPDF
    def sanitize_text(text):
        if text is None:
            return ""
        # Replace problematic Unicode characters
        return (text.replace('\u2013', '-')   # en dash
                   .replace('\u2014', '-')    # em dash
                   .replace('\u201C', '"')    # left double quote
                   .replace('\u201D', '"')    # right double quote
                   .replace('\u2019', "'")    # right single quote
                   .replace('\u2018', "'")    # left single quote
                   .replace('\u2022', '*')    # bullet
                   .replace('\u2026', '...')) # ellipsis

    # Header
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(
        200, 10, txt="Evaluacion de Riesgo para Cancer Colorrectal", ln=1, align="C")
    pdf.set_font("Arial", style="I", size=10)
    pdf.cell(
        200, 6, txt="Basado en Guias del Instituto Nacional del Cancer Argentina", ln=1, align="C")
    pdf.ln(10)

    # Basic information
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Informacion Personal", ln=1)
    pdf.set_font("Arial", size=11)

    pdf.cell(200, 8, txt=f"Edad: {edad} anos", ln=1)
    pdf.cell(200, 8, txt=f"IMC: {imc} kg/m2", ln=1)

    # Risk category with formatting
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Categoria de Riesgo", ln=1)
    pdf.set_font("Arial", style="B", size=11)

    if "Alto" in categoria_riesgo:
        pdf.set_text_color(255, 0, 0)  # Red for high risk
    elif "Incrementado" in categoria_riesgo or "Intermedio" in categoria_riesgo:
        pdf.set_text_color(0, 0, 255)  # Blue for intermediate risk
    else:
        pdf.set_text_color(0, 128, 0)  # Green for average risk

    pdf.cell(200, 8, txt=f"{sanitize_text(categoria_riesgo)}", ln=1)
    pdf.set_text_color(0, 0, 0)  # Reset to black

    # Symptom warning if applicable
    if symptoms_flag:
        pdf.ln(3)
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(255, 0, 0)  # Red
        pdf.cell(
            200, 8, txt="IMPORTANTE: Los sintomas que has reportado requieren atencion medica", ln=1)
        pdf.cell(
            200, 8, txt="inmediata, independientemente de tu categoria de riesgo.", ln=1)
        pdf.set_text_color(0, 0, 0)  # Reset to black

    # Recommendations
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Recomendaciones de Tamizaje", ln=1)
    pdf.set_font("Arial", size=11)

    # Clean markdown and special characters from recommendation for PDF
    clean_recommendation = sanitize_text(recomendacion)
    clean_recommendation = clean_recommendation.replace('**', '').replace('✅', '->').replace(
        '🟡', '->').replace('🔍', '->').replace('📹', '->').replace('🔬', '->').replace('🧭', '->')
    pdf.multi_cell(0, 7, clean_recommendation)

    # Summary
    pdf.ln(3)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Resumen", ln=1)
    pdf.set_font("Arial", size=11)
    clean_summary = sanitize_text(resumen.replace('📝', ''))
    pdf.multi_cell(0, 7, clean_summary)

    # Add lifestyle advice if provided
    if lifestyle_advice:
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 8, txt="Recomendaciones para Reducir el Riesgo", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, sanitize_text(lifestyle_advice))

    # Add information about screening intervals
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Informacion sobre Metodos de Tamizaje", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, "* Test de sangre oculta inmunoquimico (TSOMFi): Detecta sangre en las heces que podria indicar polipos o cancer. Es simple y no invasivo.\n* Colonoscopia: Examen visual directo del colon completo, permite la deteccion y extirpacion de polipos durante el procedimiento.\n* Rectosigmoidoscopia: Examina el tercio inferior del colon y es menos invasiva que la colonoscopia completa.")

    # Disclaimer and footer
    pdf.ln(5)
    pdf.set_font("Arial", style="I", size=9)
    pdf.multi_cell(0, 5, "Esta evaluacion es informativa y esta basada en la guia \"Recomendaciones para el tamizaje de CCR en poblacion de riesgo promedio en Argentina\" del Instituto Nacional del Cancer. No reemplaza la consulta medica. Comparta estos resultados con su profesional de salud para una evaluacion personalizada.")

    pdf.ln(3)
    pdf.set_font("Arial", style="B", size=9)
    pdf.cell(
        200, 5, txt=f"Fecha de evaluacion: {datetime.today().strftime('%d/%m/%Y')}", ln=1)

    # Output to buffer
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def evaluate_serrated_polyps(polyp_history):
    """
    Specialized evaluation for serrated polyps based on more detailed criteria

    Args:
        polyp_history: Dictionary containing polyp details

    Returns:
        Dictionary with risk assessment for serrated polyps
    """
    serrated_risk = {
        "is_high_risk": False,
        "reason": "",
        "recommendation": ""
    }

    # Check for serrated polyps presence
    if not polyp_history.get("serrated", False):
        return serrated_risk

    # If polyps were resected, evaluate risk
    if polyp_history.get("resected", False):
        # For simplicity, we classify all resected serrated polyps as high risk
        # In a complete system, we would collect more data about size, number, and dysplasia
        serrated_risk["is_high_risk"] = True
        serrated_risk["reason"] = "Pólipo serrado resecado"
        serrated_risk["recommendation"] = "Colonoscopia cada 3–5 años + evaluación genética."

    return serrated_risk

def get_lifestyle_recommendations(bmi, age):
    """
    Provide lifestyle recommendations based on BMI and age

    Args:
        bmi: Body Mass Index
        age: Age in years

    Returns:
        String with lifestyle recommendations
    """
    recommendations = [
        "• Mantener un peso saludable (IMC entre 18.5 y 24.9)",
        "• Realizar actividad física regularmente (al menos 30 minutos diarios)",
        "• Limitar el consumo de carnes rojas y procesadas",
        "• Aumentar el consumo de fibra, frutas y verduras",
        "• Limitar el consumo de alcohol",
        "• Evitar el tabaco"
    ]

    # Add specific recommendations based on BMI
    if bmi and bmi >= 30:
        recommendations.insert(
            1, "• Consultar con un especialista en nutrición para un plan de reducción de peso (tu IMC indica obesidad, un factor de riesgo importante para CCR)")
    elif bmi and bmi >= 25:
        recommendations.insert(
            1, "• Considerar un plan de alimentación para alcanzar un peso saludable (tu IMC indica sobrepeso)")

    # Add age-specific recommendations
    if age >= 60:
        recommendations.append(
            "• Mantener un consumo adecuado de calcio y vitamina D (puede tener efecto protector)")

    return "Las siguientes recomendaciones pueden ayudar a reducir tu riesgo de cáncer colorrectal:\n\n" + "\n".join(recommendations)

def get_symptoms_detail():
    """
    Return detailed information about warning symptoms

    Returns:
        String with symptoms details
    """
    return """
    Los siguientes síntomas requieren evaluación médica inmediata:
    
    • Sangrado rectal o sangre en las heces
    • Cambio persistente en los hábitos intestinales (diarrea, estreñimiento)
    • Pérdida de peso sin causa aparente
    • Dolor abdominal persistente
    • Sensación de evacuación incompleta
    
    Estos síntomas pueden estar relacionados con varias condiciones, incluyendo el cáncer colorrectal, por lo que es importante una evaluación médica oportuna.
    """

def evaluate_risk(age, bmi, personal_history, family_history, polyp_history, symptoms):
    """
    Evaluate colorectal cancer risk according to Argentine guidelines with enhanced criteria

    Args:
        age: Age in years
        bmi: Body Mass Index
        personal_history: Dictionary of personal medical history
        family_history: Dictionary of family history
        polyp_history: Dictionary of polyp history
        symptoms: Boolean indicating presence of symptoms

    Returns:
        Tuple containing:
        - risk_category: string with risk category
        - recommendation: string with screening recommendation
        - summary: string with summary of assessment
        - lifestyle_advice: string with lifestyle recommendations
        - symptoms_detail: string with detailed symptom information if applicable
        - bmi_note: string with BMI-related information
        - symptoms_warning: string with warning about symptoms
    """

    # Initialize variables
    risk_category = ""
    recommendation = ""
    summary = ""

    # Get lifestyle advice
    lifestyle_advice = get_lifestyle_recommendations(bmi, age)

    # Get detailed symptom information if applicable
    symptoms_detail = get_symptoms_detail() if symptoms else ""

    # 1. Evaluate high risk conditions first (follow hierarchy in guidelines)
    if personal_history.get("lynch", False):
        risk_category = "Riesgo Alto: Síndrome de Lynch"
        recommendation = "Colonoscopia cada 1–2 años."
        summary = "Riesgo alto debido a síndrome de Lynch. Se recomienda colonoscopia cada 1–2 años. Este síndrome hereditario aumenta significativamente el riesgo de cáncer colorrectal y requiere vigilancia intensiva."

    elif personal_history.get("ibd", False):
        risk_category = "Riesgo Alto: Enfermedad Inflamatoria Intestinal"
        recommendation = "Colonoscopia cada 1–5 años."
        summary = "Riesgo alto por enfermedad inflamatoria intestinal. Colonoscopia entre 1–5 años. El intervalo específico dependerá de la duración, extensión y actividad de tu enfermedad inflamatoria intestinal."

    elif personal_history.get("fap", False) or personal_history.get("fasha", False):
        risk_category = "Riesgo Alto: Poliposis Adenomatosa Familiar"
        recommendation = "Colonoscopia cada 1–2 años."
        summary = "Riesgo alto por poliposis adenomatosa familiar. Colonoscopia cada 1–2 años. Esta condición genética requiere vigilancia intensiva y posible evaluación para cirugía preventiva."

    elif personal_history.get("hamart", False):
        risk_category = "Riesgo Alto: Síndrome hamartomatoso"
        recommendation = "Colonoscopia cada 1–2 años."
        summary = "Riesgo alto por síndrome hamartomatoso. Colonoscopia cada 1–2 años. Estos síndromes raros requieren vigilancia especial y evaluación multidisciplinaria."

    elif personal_history.get("serrated_synd", False):
        risk_category = "Riesgo Alto: Poliposis serrada"
        recommendation = "Colonoscopia anual."
        summary = "Riesgo alto por poliposis serrada. Colonoscopia anual. Este síndrome aumenta el riesgo de cáncer colorrectal por vía serrada y requiere vigilancia intensiva."

    # 2. Evaluate intermediate risk conditions (polyps)
    elif polyp_history.get("polyp10", False):
        # Specialized evaluation for serrated polyps
        serrated_risk = evaluate_serrated_polyps(polyp_history)

        if polyp_history.get("advanced_poly", False) and polyp_history.get("resected", False):
            risk_category = "Riesgo Alto: Adenoma avanzado resecado"
            recommendation = "Colonoscopia a los 3 años + FIT anual."
            summary = "Riesgo alto por adenoma avanzado resecado. Colonoscopia a los 3 años + FIT anual. Los adenomas avanzados (>1cm, componente velloso o displasia de alto grado) tienen mayor potencial de malignización."

        elif serrated_risk["is_high_risk"]:
            risk_category = f"Riesgo Alto: {serrated_risk['reason']}"
            recommendation = serrated_risk["recommendation"]
            summary = f"Riesgo alto por {serrated_risk['reason'].lower()}. {serrated_risk['recommendation']} Los pólipos serrados siguen una vía alternativa de carcinogénesis y requieren vigilancia específica."

        elif polyp_history.get("resected", False):
            risk_category = "Riesgo Intermedio: Pólipos simples resecados"
            recommendation = "Colonoscopia a los 5 años."
            summary = "Riesgo intermedio por pólipos simples resecados. Colonoscopia a los 5 años. Los pólipos adenomatosos, incluso pequeños, indican mayor riesgo de desarrollar nuevos pólipos o CCR."

    # 3. Evaluate family history
    elif family_history.get("family_crc", False):
        if family_history.get("family_before_60", False):
            risk_category = "Riesgo Incrementado: Familiar <60 años"
            recommendation = "Colonoscopia a los 40 años o 10 años antes del caso familiar más joven, lo que ocurra primero. Repetir cada 5 años."
            summary = "Riesgo incrementado por antecedente familiar diagnosticado antes de los 60 años. Se recomienda colonoscopia temprana (a los 40 años o 10 años antes de la edad de diagnóstico del familiar, lo que ocurra primero) y repetir cada 5 años."
        else:
            risk_category = "Riesgo Incrementado: Familiar ≥60 años"
            recommendation = "Colonoscopia a los 50 años + repetir cada 5 años."
            summary = "Riesgo incrementado por familiar con CCR diagnosticado a los 60 años o más. Colonoscopia desde los 50 años y repetir cada 5 años."

    # 4. Evaluate by age (average risk)
    elif 50 <= age <= 75:
        risk_category = "Riesgo Promedio"
        recommendation = """
        **Tu médico puede ayudarte a revisar las siguientes opciones disponibles de tamizaje, considerando la disponibilidad de las pruebas con tu prestador de salud:**

        - ✅ **Test de sangre oculta inmunoquímico (TSOMFi)** cada 2 años *(recomendado como primera opción)*
        - 🟡 **Test con guayaco (TSOMFg)** cada 2 años *(si no se dispone de TSOMFi)*
        - 🔍 **Colonoscopia** cada 10 años
        - 📹 **Videocolonoscopía (VCC)** cada 5 años
        - 🔬 **Rectosigmoidoscopía (RSC)** cada 5 años *(sola o combinada con TSOMFi anual)*
        - 🧭 **Colonoscopia virtual** *(solo si no se dispone de las anteriores)*
        """
        summary = "📝 Resumen: Aunque no se detectaron factores de riesgo adicionales, cumplís con los criterios de edad (50–75 años) para tamizaje de rutina. Se recomienda realizar el tamizaje de acuerdo con las opciones disponibles, con preferencia por el test de sangre oculta inmunoquímico (TSOMFi) cada 2 años como primera opción."

    elif age < 50:
        risk_category = "Edad menor a 50 años sin factores de riesgo adicionales"
        recommendation = "No requiere tamizaje según las guías actuales para población de riesgo promedio."
        summary = "Actualmente no cumplís criterios para tamizaje por edad según las guías argentinas, que recomiendan iniciar a los 50 años en población de riesgo promedio. Sin embargo, debes estar atento a cualquier síntoma digestivo y consultar inmediatamente si aparecen."

    elif age > 75:
        risk_category = "Mayor de 75 años"
        recommendation = "Evaluar caso a caso con tu médico tratante."
        summary = "Por tu edad, se recomienda evaluar caso a caso con tu médico tratante. El tamizaje de rutina no se recomienda después de los 75 años, pero puede considerarse individualmente basado en tu estado de salud general, comorbilidades y expectativa de vida. El beneficio del tamizaje disminuye después de los 75 años, particularmente si has tenido tamizajes previos normales."

    # 5. Add BMI note if applicable
    bmi_note = ""
    if bmi and bmi >= 30:
        bmi_note = f"**Nota importante:** IMC elevado ({bmi}): la obesidad es un factor de riesgo significativo para CCR. Para mejorar tu salud y reducir riesgos, el IMC recomendado es entre 18.5 y 24.9. Se recomienda consulta con un profesional de nutrición."
    elif bmi and bmi >= 25:
        bmi_note = f"**Nota:** IMC elevado ({bmi}): el sobrepeso es un factor de riesgo para CCR. Para mejorar tu salud y reducir riesgos, el IMC recomendado es entre 18.5 y 24.9. Consultá con un profesional para orientación nutricional."

    # 6. Add symptoms warning if applicable
    symptoms_warning = ""
    if symptoms:
        symptoms_warning = "**ATENCIÓN:** Presentás síntomas clínicos como sangrado rectal, cambios en el ritmo intestinal o pérdida de peso sin explicación. Se recomienda consulta médica inmediata independientemente de tu categoría de riesgo, ya que estos síntomas requieren evaluación diagnóstica y no tamizaje."

    return risk_category, recommendation, summary, lifestyle_advice, symptoms_detail, bmi_note, symptoms_warning

# App layout
st.title("Evaluación de riesgo para tamizaje de cáncer colorrectal")
st.markdown(
    "Herramienta para pacientes: responde tus datos para obtener tu estrategia de tamizaje según la Guía Argentina del Instituto Nacional del Cáncer."
)

# Sidebar with educational content
with st.sidebar:
    st.header("Información sobre el Cáncer Colorrectal")

    st.subheader("¿Qué es el cáncer colorrectal?")
    st.markdown("""
    El cáncer colorrectal es un tumor maligno que se desarrolla en el colon o en el recto. 
    En Argentina, es el segundo cáncer más frecuente, con aproximadamente 15.000 nuevos casos por año.
    """)

    st.subheader("Factores de riesgo")
    st.markdown("""
    - **Edad**: El riesgo aumenta significativamente después de los 50 años
    - **Historia familiar**: Especialmente si un familiar de primer grado fue diagnosticado
    - **Condiciones hereditarias**: Síndrome de Lynch, PAF, etc.
    - **Enfermedad inflamatoria intestinal**: Colitis ulcerosa, enfermedad de Crohn
    - **Pólipos**: Especialmente adenomas o pólipos serrados
    - **Factores de estilo de vida**:
        - Obesidad (IMC > 30)
        - Dieta rica en carnes rojas y procesadas
        - Sedentarismo
        - Consumo de alcohol
        - Tabaquismo
    """)

    st.subheader("Síntomas de alarma")
    st.markdown("""
    - Sangrado rectal o sangre en las heces
    - Cambio en los hábitos intestinales (diarrea, estreñimiento)
    - Pérdida de peso sin causa aparente
    - Dolor abdominal persistente
    - Sensación de evacuación incompleta
    
    **La presencia de estos síntomas requiere evaluación médica inmediata, no tamizaje.**
    """)

    st.subheader("Prevención")
    st.markdown("""
    - Mantener un peso saludable
    - Realizar actividad física regularmente
    - Limitar el consumo de carnes rojas y procesadas
    - Aumentar el consumo de fibra, frutas y verduras
    - Limitar el consumo de alcohol
    - Evitar el tabaco
    - Realizar el tamizaje según las recomendaciones
    """)

    st.markdown("---")
    st.caption("Esta herramienta está basada en la guía \"Recomendaciones para el tamizaje de CCR en población de riesgo promedio en Argentina\" del Instituto Nacional del Cáncer.")

# Simple navigation
pages = ["Datos Personales", "Antecedentes", "Historia de Pólipos", "Síntomas", "Evaluación"]
progress_value = st.session_state.page / (len(pages) - 1)
st.progress(progress_value)
st.write(f"Paso {st.session_state.page + 1} de {len(pages)}: **{pages[st.session_state.page]}**")

# Display the current page
if st.session_state.page == 0:  # Datos Personales
    st.subheader("Datos personales básicos")
    
    # Date of birth
    dob = st.date_input(
        "Fecha de nacimiento",
        value=None,
        min_value=datetime(1900, 1, 1),
        max_value=datetime.today(),
        help="Selecciona tu fecha de nacimiento para calcular tu edad"
    )
    
    # Current age (calculated from DOB)
    if dob:
        age = calculate_age(dob)
        st.info(f"Edad actual: {age} años")
        st.session_state.data['dob'] = dob
        st.session_state.data['age'] = age
    
    # Height and weight
    col1, col2 = st.columns(2)
    with col1:
        height_str = st.text_input(
            "Altura (cm)", placeholder="Ej: 170", help="Mide tu altura sin zapatos")
    with col2:
        weight_str = st.text_input(
            "Peso (kg)", placeholder="Ej: 65", help="Ingresa tu peso actual")
    
    # Validate height and weight
    valid_height = False
    valid_weight = False
    height_cm = None
    weight_kg = None
    
    if height_str:
        valid_height, result = validate_numeric_input(height_str, 50, 250)
        if valid_height:
            height_cm = result
            st.session_state.data['height_cm'] = height_cm
        else:
            st.error(result)
    
    if weight_str:
        valid_weight, result = validate_numeric_input(weight_str, 20, 300)
        if valid_weight:
            weight_kg = result
            st.session_state.data['weight_kg'] = weight_kg
        else:
            st.error(result)
    
    # Calculate and display BMI
    if valid_height and valid_weight:
        bmi = calculate_bmi(height_cm, weight_kg)
        st.session_state.data['bmi'] = bmi
        
        # Display BMI with color-coded category
        if bmi < 18.5:
            st.warning(f"Tu IMC es: {bmi} kg/m² (Bajo peso)")
        elif bmi < 25:
            st.success(f"Tu IMC es: {bmi} kg/m² (Peso normal)")
        elif bmi < 30:
            st.warning(f"Tu IMC es: {bmi} kg/m² (Sobrepeso)")
        else:
            st.error(f"Tu IMC es: {bmi} kg/m² (Obesidad)")
        
        # Add explanation about BMI and cancer risk
        if bmi >= 25:
            st.info("El sobrepeso y la obesidad son factores de riesgo para el cáncer colorrectal. Mantener un IMC entre 18.5 y 24.9 puede reducir este riesgo.")
    
    # Navigation button
    st.markdown("---")
    if dob and valid_height and valid_weight:
        if st.button("Continuar a Antecedentes →", type="primary"):
            change_page(1)
    else:
        st.warning("Complete todos los campos obligatorios para continuar")

elif st.session_state.page == 1:  # Antecedentes
    st.subheader("Antecedentes de salud")
    
    # 1. Personal health history
    st.markdown("**1. Antecedentes personales de salud**")
    
    with st.expander("¿Qué son estos síndromes y condiciones?", expanded=False):
        st.markdown("""
        - **Enfermedad inflamatoria intestinal**: Incluye la colitis ulcerosa y la enfermedad de Crohn. Son condiciones crónicas que causan inflamación en el tracto digestivo.
        - **Síndrome de Lynch**: También conocido como cáncer colorrectal hereditario no asociado a poliposis (HNPCC). Es un trastorno hereditario que aumenta el riesgo de cáncer colorrectal y otros tipos de cáncer.
        - **Síndromes de pólipos hereditarios**: Incluyen Peutz-Jeghers, Cowden y otros. Son condiciones genéticas que provocan múltiples pólipos en el tracto digestivo.
        - **Poliposis adenomatosa familiar (PAF)**: Condición hereditaria que causa cientos o miles de pólipos en el revestimiento del colon y recto.
        - **Poliposis serrada**: Condición caracterizada por múltiples pólipos serrados en el colon, que tienen un riesgo elevado de transformación maligna.
        """)
    
    ibd = st.toggle("¿Tenés enfermedad intestinal inflamatoria como Crohn o colitis ulcerosa?", value=st.session_state.data.get('ibd', False),
                   help="Las enfermedades inflamatorias intestinales aumentan el riesgo de CCR, especialmente cuando son de larga evolución")
    st.session_state.data['ibd'] = ibd
    
    hered = st.toggle("¿Algún médico te dijo que tenés un síndrome hereditario como el de Lynch?", value=st.session_state.data.get('hered', False),
                     help="El síndrome de Lynch aumenta significativamente el riesgo de CCR y requiere vigilancia intensiva")
    st.session_state.data['hered'] = hered
    
    hamart = st.toggle("¿Te diagnosticaron un síndrome de pólipos hereditarios como Peutz-Jeghers o Cowden?", value=st.session_state.data.get('hamart', False),
                      help="Estos síndromes raros tienen un riesgo elevado de CCR y otros cánceres")
    st.session_state.data['hamart'] = hamart
    
    fap = st.toggle("¿Tenés diagnóstico de poliposis adenomatosa familiar (PAF)?", value=st.session_state.data.get('fap', False),
                   help="La PAF causa cientos o miles de pólipos y tiene un riesgo casi 100% de desarrollar CCR sin tratamiento")
    st.session_state.data['fap'] = fap
    
    fasha = st.toggle("¿Tenés diagnóstico de poliposis adenomatosa familiar atenuada (PAFA)?", value=st.session_state.data.get('fasha', False),
                     help="Forma menos severa de PAF, pero con riesgo elevado de CCR")
    st.session_state.data['fasha'] = fasha
    
    serrated_synd = st.toggle("¿Te diagnosticaron síndrome de poliposis serrada (múltiples pólipos serrados)?", value=st.session_state.data.get('serrated_synd', False),
                             help="Los pólipos serrados tienen un riesgo elevado de transformación maligna por una vía molecular distinta")
    st.session_state.data['serrated_synd'] = serrated_synd
    
    # 2. Family history
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
    
    family_crc = st.toggle("¿Tenés un familiar directo (padre/madre/hermano/a/hijo/a) con cáncer colorrectal?", value=st.session_state.data.get('family_crc', False),
                          help="Los familiares de primer grado son padres, hermanos e hijos")
    st.session_state.data['family_crc'] = family_crc
    
    family_before_60 = False
    family_multiple = False
    
    if family_crc:
        family_before_60 = st.toggle("¿Ese familiar fue diagnosticado antes de los 60 años?", value=st.session_state.data.get('family_before_60', False),
                                    help="El diagnóstico temprano en familiares indica mayor riesgo genético")
        st.session_state.data['family_before_60'] = family_before_60
        
        family_multiple = st.toggle("¿Tenés más de un familiar directo con cáncer colorrectal?", value=st.session_state.data.get('family_multiple', False),
                                   help="Múltiples familiares afectados aumentan significativamente el riesgo")
        st.session_state.data['family_multiple'] = family_multiple
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Volver a Datos Personales"):
            change_page(0)
    with col2:
        if st.button("Continuar a Historia de Pólipos →", type="primary"):
            change_page(2)

elif st.session_state.page == 2:  # Historia de Pólipos
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

    polyp10 = st.toggle("Durante los últimos 10 años, ¿algún médico te dijo que tenías pólipos en el colon o el recto?", value=st.session_state.data.get('polyp10', False),
                       help="La presencia de pólipos previos es un factor de riesgo para nuevos pólipos y CCR")
    st.session_state.data['polyp10'] = polyp10

    advanced_poly = False
    serrated = False
    resected = False
    multiple_polyps = False
    polyp_size = None

    if polyp10:
        advanced_poly = st.toggle("¿Alguno de esos pólipos fue grande (más de 1 cm) o de alto riesgo?", value=st.session_state.data.get('advanced_poly', False),
                                 help="Los pólipos grandes tienen mayor riesgo de transformación maligna")
        st.session_state.data['advanced_poly'] = advanced_poly

        serrated = st.toggle("¿Alguno de los pólipos era del tipo serrado?", value=st.session_state.data.get('serrated', False),
                            help="Los pólipos serrados siguen una vía diferente de carcinogénesis")
        st.session_state.data['serrated'] = serrated

        multiple_polyps = st.toggle("¿Tenías más de 3 pólipos en total?", value=st.session_state.data.get('multiple_polyps', False),
                                   help="El número de pólipos influye en el riesgo y el intervalo de vigilancia")
        st.session_state.data['multiple_polyps'] = multiple_polyps

        col1, col2 = st.columns(2)
        with col1:
            polyp_options = ["No lo sé", "Menos de 5mm", "5-10mm", "Más de 10mm"]
            polyp_size = st.selectbox("¿Cuál era el tamaño del pólipo más grande?", polyp_options,
                                     help="El tamaño del pólipo es un factor importante para determinar el riesgo",
                                     index=polyp_options.index(st.session_state.data.get('polyp_size', "No lo sé")) if st.session_state.data.get('polyp_size') in polyp_options else 0)
        st.session_state.data['polyp_size'] = polyp_size

        with col2:
            resected = st.toggle("¿Te realizaron una resección o extirpación de esos pólipos o adenomas?", value=st.session_state.data.get('resected', False),
                                help="La extirpación de pólipos reduce el riesgo pero requiere seguimiento")
        st.session_state.data['resected'] = resected

    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Volver a Antecedentes"):
            change_page(1)
    with col2:
        if st.button("Continuar a Síntomas →", type="primary"):
            change_page(3)

elif st.session_state.page == 3:  # Síntomas
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

    # Get symptoms dictionary or initialize empty
    symptoms = st.session_state.data.get('symptoms', {})
    
    # Specific symptom questions
    symptoms["blood"] = st.toggle(
        "¿Has notado sangre en las heces o en el papel higiénico en el último mes?", 
        value=symptoms.get("blood", False))
        
    symptoms["bowel_changes"] = st.toggle(
        "¿Has experimentado cambios persistentes en tus hábitos intestinales (diarrea, estreñimiento) por más de 3 semanas?", 
        value=symptoms.get("bowel_changes", False))
        
    symptoms["weight_loss"] = st.toggle(
        "¿Has perdido peso sin explicación (sin dieta o ejercicio) en los últimos 3 meses?", 
        value=symptoms.get("weight_loss", False))
        
    symptoms["pain"] = st.toggle(
        "¿Tienes dolor abdominal recurrente o persistente?", 
        value=symptoms.get("pain", False))
        
    symptoms["incomplete"] = st.toggle(
        "¿Sientes con frecuencia que no has evacuado completamente después de ir al baño?", 
        value=symptoms.get("incomplete", False))

    # Calculate if any symptoms are present
    any_symptoms = any(symptoms.values())
    
    # Save to session state
    st.session_state.data['symptoms'] = symptoms
    st.session_state.data['any_symptoms'] = any_symptoms

    if any_symptoms:
        st.warning(
            "⚠️ Has indicado la presencia de síntomas que requieren evaluación médica. Consulta con un médico lo antes posible.")

    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Volver a Historia de Pólipos"):
            change_page(2)
    with col2:
        if st.button("Continuar a Evaluación →", type="primary"):
            change_page(4)

elif st.session_state.page == 4:  # Evaluación
    st.subheader("Evaluación de riesgo")

    # Get data from session state
    age = st.session_state.data.get('age')
    bmi = st.session_state.data.get('bmi')
    
    # Get risk factors from session state
    personal_history = {
        "ibd": st.session_state.data.get('ibd', False),
        "lynch": st.session_state.data.get('hered', False),
        "hamart": st.session_state.data.get('hamart', False),
        "fap": st.session_state.data.get('fap', False),
        "fasha": st.session_state.data.get('fasha', False),
        "serrated_synd": st.session_state.data.get('serrated_synd', False)
    }

    family_history = {
        "family_crc": st.session_state.data.get('family_crc', False),
        "family_before_60": st.session_state.data.get('family_before_60', False),
        "family_multiple": st.session_state.data.get('family_multiple', False)
    }

    polyp_history = {
        "polyp10": st.session_state.data.get('polyp10', False),
        "advanced_poly": st.session_state.data.get('advanced_poly', False),
        "serrated": st.session_state.data.get('serrated', False),
        "resected": st.session_state.data.get('resected', False),
        "multiple_polyps": st.session_state.data.get('multiple_polyps', False),
        "polyp_size": st.session_state.data.get('polyp_size', None)
    }
    
    any_symptoms = st.session_state.data.get('any_symptoms', False)

    # Check if we have all required data
    can_evaluate = age is not None and bmi is not None

    if can_evaluate:
        st.markdown(f"**Edad:** {age} años | **IMC:** {bmi} kg/m²")

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
        change_page(3)

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

st.caption("© 2025 - Desarrollado por PEGASI Chubut. Todos los derechos reservados.")
