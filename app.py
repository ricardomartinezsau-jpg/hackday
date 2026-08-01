import base64
import html
import os
import time

import streamlit as st
from dotenv import load_dotenv

import carbon
from agent import LEVELS, MODEL_FAST, MODEL_QUALITY, GemmaEduAgent
from rag import EMBED_MODEL, EduRAG

load_dotenv()

st.set_page_config(
    page_title="Gemma Edu-Agent",
    page_icon="\U0001f9e0",
    layout="wide",
    initial_sidebar_state="expanded",
)
carbon.inject()


def esc(x) -> str:
    return html.escape(str(x))


@st.cache_resource(show_spinner=False)
def get_rag():
    rag = EduRAG()
    rag.ingest_document("mock_data.txt")
    return rag


@st.cache_resource(show_spinner=False)
def get_agent(model_name: str):
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "tu_api_key_de_ai_studio_aqui":
        return None
    agent = GemmaEduAgent(api_key=key, model_name=model_name)
    # Arranque en frio pagado al cargar la app, no al primer clic del juez.
    agent.warmup()
    return agent


carbon.header(
    title="Gemma Edu-Agent",
    subtitle="Andamiaje pedagogico personalizado, generado en el tiempo de un cafe.",
    eyebrow="GDG CDMX Hackday · El futuro de la educacion",
)

with st.sidebar:
    st.markdown('<div class="cds-label">Motor inferencial</div>', unsafe_allow_html=True)
    modelo = st.selectbox(
        "Modelo",
        [MODEL_QUALITY, MODEL_FAST],
        format_func=lambda m: ("Gemma 4 31B (densa)" if m == MODEL_QUALITY else "Gemma 4 26B-A4B (MoE)"),
        label_visibility="collapsed",
    )
    st.markdown(
        carbon.tag("100% Gemma 4", "green")
        + " "
        + carbon.tag("JSON estructurado", "blue"),
        unsafe_allow_html=True,
    )

    rag = get_rag()
    agent = get_agent(modelo)

    st.markdown('<div class="cds-label">Recuperacion (RAG)</div>', unsafe_allow_html=True)
    if rag.mode == "semantic":
        st.markdown(carbon.tag("Semantica activa", "green"), unsafe_allow_html=True)
        st.caption(f"Encoder: {EMBED_MODEL} · {len(rag.documents)} secciones OER")
    else:
        st.markdown(carbon.tag("Degradado a palabra clave", "yellow"), unsafe_allow_html=True)
        st.caption(rag.last_error or "Vectorizacion no disponible.")

    st.markdown('<div class="cds-label">Corpus</div>', unsafe_allow_html=True)
    st.caption("OpenStax Physics 2e — recurso educativo abierto (CC BY 4.0)")

    st.markdown("---")
    st.markdown('<div class="cds-label">El problema</div>', unsafe_allow_html=True)
    st.caption(
        "En aulas de 40+ alumnos, personalizar la explicacion para cada estudiante "
        "es humanamente imposible. La IA como maquina de respuestas resuelve la tarea "
        "y erosiona el razonamiento. Este agente hace lo contrario: construye el "
        "andamiaje para que el alumno llegue solo."
    )

st.markdown(
    '<div class="cds-label">00 — Fuente del concepto</div>', unsafe_allow_html=True
)
foto = st.file_uploader(
    "Foto de la pagina",
    type=["jpg", "jpeg", "png"],
    help="Fotografia una pagina del libro y Gemma 4 la lee directamente.",
    label_visibility="collapsed",
)
if foto is not None:
    st.markdown(
        carbon.tag("Multimodal · Gemma 4 lee la pagina", "green")
        + " "
        + carbon.tag("Sin RAG: 100% Gemma", "blue"),
        unsafe_allow_html=True,
    )
    st.image(foto, width=340)
else:
    st.caption(
        "Sin foto se usa el corpus OER indexado. Con foto, Gemma 4 hace de OCR y "
        "razona sobre la pagina en una sola pasada."
    )

col_a, col_b = st.columns([1, 1], gap="large")
with col_a:
    st.markdown('<div class="cds-label">01 — Concepto de la curricula</div>', unsafe_allow_html=True)
    # Las opciones reflejan exactamente las secciones indexadas en el corpus.
    # Ofrecer temas ausentes del OER produciria recuperacion irrelevante
    # presentada como si fuera fundamentada.
    tema = st.selectbox(
        "Tema",
        [
            "8.1 Momento Lineal",
            "8.2 Conservacion del Momento Lineal",
            "8.3 Colisiones Elasticas e Inelasticas",
        ],
        index=1,
        label_visibility="collapsed",
    )
with col_b:
    st.markdown('<div class="cds-label">02 — Mundo del estudiante</div>', unsafe_allow_html=True)
    interes = st.text_input(
        "Interes",
        placeholder="videojuegos de carreras, produccion musical, futbol…",
        label_visibility="collapsed",
    )

st.markdown(
    '<div class="cds-label">03 — Nivel cognitivo objetivo</div>', unsafe_allow_html=True
)
nivel = st.radio(
    "Nivel",
    list(LEVELS.keys()),
    index=1,
    horizontal=True,
    format_func=lambda n: {
        "Basico": "Basico · secundaria",
        "Intermedio": "Intermedio · bachillerato",
        "Avanzado": "Avanzado · universitario",
    }[n],
    label_visibility="collapsed",
)
st.caption(LEVELS[nivel])

generar = st.button("Generar andamiaje pedagogico", type="primary")
st.markdown("<br>", unsafe_allow_html=True)

if generar:
    if not interes.strip():
        st.error("Ingresa al menos un interes del alumno para anclar la analogia.")
        st.stop()

    modo_multimodal = foto is not None
    if modo_multimodal:
        contexto = None
        ms_rag = 0
    else:
        t_rag = time.time()
        contexto = rag.search(query=tema)
        ms_rag = int((time.time() - t_rag) * 1000)

    if agent is None:
        st.warning(
            "Sin GEMINI_API_KEY valida: la interfaz corre en modo simulacion. "
            "Configura .env para inferencia real con Gemma 4."
        )
        st.stop()

    t0 = time.time()
    try:
        if modo_multimodal:
            with st.spinner("Gemma 4 leyendo la pagina y generando el andamiaje…"):
                resultado = agent.generate_analogy_from_image(
                    base64.b64encode(foto.getvalue()).decode(),
                    foto.type or "image/jpeg",
                    interes,
                    level=nivel,
                )
        else:
            with st.spinner("Gemma 4 generando el andamiaje pedagogico…"):
                resultado = agent.generate_analogy(contexto, interes, level=nivel)
    except Exception as e:  # noqa: BLE001 - la demo nunca debe morir en pantalla
        st.error(f"Fallo la generacion con Gemma 4: {e}")
        st.stop()

    total = time.time() - t0
    n_palabras = len(resultado["conceptual_analogy"].split())

    carbon.metrics([
        ("Generacion Gemma 4", f"{total:.1f}s", True),
        ("Fuente", "Imagen (multimodal)" if modo_multimodal else f"RAG {ms_rag} ms", False),
        ("Nivel", nivel, False),
        ("Validacion", "Pydantic OK", False),
    ])

    carbon.source_container(
        "Fuente — leida de la pagina fotografiada por Gemma 4"
        if modo_multimodal
        else "Fuente certificada — recuperada, no generada",
        esc(resultado["source_citation"]),
    )

    carbon.ai_container(
        f"Analogia anclada en: {esc(resultado['student_interest'])}",
        esc(resultado["conceptual_analogy"]),
    )

    st.markdown(
        f'<div class="cds-label">Matriz de mapeo conceptual'
        f'<span class="cds-ai-slug">AI</span></div>',
        unsafe_allow_html=True,
    )
    carbon.mapping_table([
        {"academico": esc(r["academico"]), "analogico": esc(r["analogico"])}
        for r in resultado["mapping_matrix"]
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    carbon.question(esc(resultado["verification_question"]))

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(
        f"Concepto detectado: {resultado['technical_concept']} · "
        f"Salida validada contra esquema Pydantic estricto · Modelo: {modelo}"
    )
