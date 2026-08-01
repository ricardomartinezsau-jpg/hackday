# Gemma Edu-Agent 🧠

**Andamiaje pedagógico personalizado, generado en el tiempo de un café.**

Entrega para el **Gemma 4 · GDG CDMX Hackday** — categoría *El futuro de la educación*.

## El problema

En aulas públicas de LATAM con 40+ alumnos por docente, personalizar la explicación
para cada estudiante es humanamente imposible. Y la respuesta fácil —usar IA como
máquina de respuestas— resuelve la tarea del alumno y erosiona su razonamiento.

## La solución

Gemma Edu-Agent **no resuelve tareas**. Toma un concepto de un recurso educativo
abierto (OpenStax, CC BY 4.0) y lo traduce a una analogía anclada en el mundo real
del estudiante, más una matriz de mapeo explícita y una pregunta de verificación
metacognitiva. El objetivo es el andamiaje: que el alumno llegue solo.

## Arquitectura

```
Documento OpenStax (OER)
      ↓
gemini-embedding-001  ──> índice vectorial en memoria (NumPy, similitud coseno)
      ↓
Fragmento relevante
      ↓
Gemma 4 (gemma-4-31b-it)  ──> salida estructurada por responseSchema
      ↓
Validación Pydantic
      ↓
Interfaz IBM Carbon for AI
```

### Qué hace Gemma 4, exactamente

**Gemma 4 es el motor de razonamiento pedagógico del producto.** Todo el acto
generativo —comprender el concepto físico, elegir el anclaje analógico, construir
el mapeo y formular la pregunta de verificación— ocurre en `gemma-4-31b-it`.

La recuperación semántica usa `gemini-embedding-001` porque **la familia Gemma no
expone un endpoint de embeddings en Google AI Studio**. EmbeddingGemma existe, pero
Google lo distribuye para descarga o Vertex AI, no como endpoint de la Gemini API.
Preferimos decirlo así antes que atribuirle al proyecto una pureza de stack que no
tiene.

Del mismo modo: usamos **structured output** (`responseSchema`), no *function
calling*. Son cosas distintas y solo la primera está en juego aquí.

## Decisiones de ingeniería del hackday

| Decisión | Por qué |
| --- | --- |
| NumPy en vez de ChromaDB | Para un corpus de pocas secciones el producto punto es exacto, y evita dependencias nativas que compilar en Windows. El repo queda clonable sin fricción. |
| Instrucciones en el prompt, no en `system_instruction` | La combinación `system_instruction` + `responseSchema` resultó inestable contra el endpoint de Gemma 4 (peticiones colgadas). El rol vive en el prompt. |
| Esquema JSON **plano** | Un `ARRAY` de objetos anidados disparaba bucles de repetición que agotaban el presupuesto de tokens y truncaban el JSON. Aplanar `mapping_matrix` a `"academico :: analogico"` bajó la latencia de ~120 s a ~9 s. |
| `maxOutputTokens` ajustado + 3 reintentos | La decodificación restringida no elimina la degeneración estocástica. Un techo ceñido hace que el fallo sea barato y el reintento, invisible. |
| Selector limitado a las secciones indexadas | Ofrecer temas ausentes del corpus produciría recuperación irrelevante presentada como si estuviera fundamentada. |

## Correr localmente

```bash
pip install -r requirements.txt
cp .env.example .env   # y coloca tu GEMINI_API_KEY de Google AI Studio
streamlit run app.py
```

## Licencia

Creative Commons Attribution 4.0 International (CC BY 4.0).
Corpus de demostración derivado de OpenStax Physics 2e (CC BY 4.0).
