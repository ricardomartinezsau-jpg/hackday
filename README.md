# Gemma Edu-Agent 🧠

**Ganando 15 horas semanales de tiempo docente mediante andamiaje pedagógico automatizado.**

Este proyecto es la entrega para el **Gemma 4 - GDG CDMX Hackday**, atacando directamente el problema de la sobrecarga docente en escuelas públicas de LATAM (categoría: *El futuro de la educación*).

## El Problema
En entornos masivos (40+ alumnos por profesor), la personalización pedagógica es humanamente imposible por falta de tiempo. El uso de IA tradicional como "máquina de respuestas" causa degradación cognitiva (según estudios del MIT) ya que el estudiante no desarrolla razonamiento profundo.

## La Solución
**Gemma Edu-Agent** no entrega tareas resueltas. Su propósito es actuar como andamiaje cognitivo, traduciendo conceptos académicos abstractos procedentes de literatura abierta certificada (OER, como OpenStax) hacia **analogías personalizadas** basadas en los intereses de vida de cada estudiante.

## Arquitectura y Stack (Diseñado para el Hackday)
* **Motor Inferencial:** Gemma 4 (vía API o local usando llama.cpp con pesos cuantizados) con Function Calling nativo.
* **Canalización RAG:** Recuperación semántica de textos en ChromaDB usando EmbeddingGemma.
* **Interfaz:** Streamlit.

### Por qué Gemma 4:
Se utilizan las capacidades de la familia Gemma 4 (E4B y Function Calling nativo) para garantizar salidas estructuradas en un formato JSON determinista (esquema estricto) para uso educativo sin riesgo de alucinaciones.

## Instrucciones para Correr Localmente (Demo)

1. Clonar este repositorio.
2. Crear un entorno virtual: `python -m venv .venv` y activarlo.
3. Instalar dependencias: `pip install -r requirements.txt`
4. Copiar `.env.example` a `.env` y configurar `GEMINI_API_KEY`.
5. Ejecutar: `streamlit run app.py`

## Licencia
Creative Commons Attribution 4.0 International (CC BY 4.0)
