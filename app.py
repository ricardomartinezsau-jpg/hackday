import streamlit as st
import os
from dotenv import load_dotenv
from agent import GemmaEduAgent
from rag import EduRAG
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Gemma Edu-Agent", page_icon="🧠", layout="wide")

st.title("🧠 Gemma Edu-Agent")
st.subheader("Traduciendo la complejidad académica a la realidad del estudiante")

# Inicialización de dependencias
@st.cache_resource
def get_rag():
    rag = EduRAG()
    # Ingestamos el texto de prueba si la colección está vacía
    if not rag.documents:
        rag.ingest_document("mock_data.txt")
    return rag

@st.cache_resource
def get_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_de_ai_studio_aqui":
        st.warning("⚠️ No se encontró una GEMINI_API_KEY válida en el archivo .env. Usando modo simulación (mock) para la demo.")
        return None
    return GemmaEduAgent(api_key=api_key)

rag = get_rag()
agent = get_agent()

with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/googlelogo/2x/googlelogo_color_160x56dp.png", width=150)
    st.markdown("### Configuración Pedagógica")
    st.write("**Colección RAG:** OpenStax Physics 2e")
    st.write("**Modelo:** Gemma 4 E4B (Vía AI Studio)")
    
    st.markdown("---")
    st.markdown("### El Problema")
    st.markdown("*Profesores de escuelas públicas en LATAM pierden 15h semanales personalizando analogías para aulas masivas.*")

st.write("### 1. Selección de Concepto (Profesor)")
tema = st.selectbox(
    "Selecciona el tema de la currícula que enseñarás hoy:",
    ["Leyes de Conservación del Momento", "Termodinámica Básica", "Electromagnetismo"]
)

st.write("### 2. Contexto del Alumno")
interes = st.text_input(
    "¿Cuáles son los intereses principales del alumno?",
    placeholder="Ej. Videojuegos de carreras, producción musical, fútbol..."
)

if st.button("Generar Andamiaje Pedagógico", type="primary"):
    if not interes:
        st.error("Por favor, ingresa los intereses del alumno.")
    else:
        with st.spinner("Buscando literatura certificada en base vectorial local (EmbeddingGemma)..."):
            contexto = rag.search(query=tema)
            st.success("Texto académico recuperado exitosamente.")
            with st.expander("Ver contexto original de OpenStax"):
                st.write(contexto)
        
        with st.spinner("Gemma 4 ejecutando Function Calling para generar analogía..."):
            if agent:
                try:
                    resultado = agent.generate_analogy(context_text=contexto, student_interest=interes)
                    
                    st.write("---")
                    st.header("🎯 Resultado Estructurado (JSON Parsed)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Concepto Técnico:** {resultado['technical_concept']}")
                        st.markdown(f"**Fuente Académica:** {resultado['source_citation']}")
                    with col2:
                        st.info(f"**Analogía Personalizada:**\n\n{resultado['conceptual_analogy']}")
                        
                    st.write("### Matriz de Mapeo (Evaluación Estructural)")
                    
                    # Convertimos la matriz a un DataFrame para una tabla bonita
                    if 'mapping_matrix' in resultado:
                        df = pd.DataFrame(resultado['mapping_matrix'])
                        st.table(df)
                        
                    st.warning(f"**Pregunta de Verificación (Metacognición):**\n\n{resultado['verification_question']}")
                    
                except Exception as e:
                    st.error(f"Error al generar con la API: {e}")
            else:
                # Mock response para poder hacer la demo en caso de no tener API key aún
                import time
                time.sleep(1.5)
                st.write("---")
                st.header("🎯 Resultado Estructurado (Modo Simulación)")
                st.info("**Concepto Técnico:** Conservación del Momento Lineal")
                st.success(f"**Analogía Personalizada (Interés: {interes}):**\nImagina que los dos coches de tu videojuego chocan en la pista...")
                st.table(pd.DataFrame([
                    {"academico": "Masa de objeto 1", "analogico": "Peso del camión en el juego"},
                    {"academico": "Velocidad de impacto", "analogico": "Velocidad del turbo"}
                ]))
                st.warning("**Pregunta de Verificación:** Si tu coche choca contra uno que está estacionado, ¿qué le pasa a tu velocidad según la física?")
