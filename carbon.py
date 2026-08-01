"""Capa de presentacion segun IBM Carbon Design System (tema Gray 100)
y su extension Carbon for AI.

Carbon for AI define un tratamiento visual explicito para el contenido
generado por un modelo: gradiente violeta-azul, borde biselado y una
etiqueta "AI" persistente. No es decoracion. Es una convencion de honestidad
de interfaz: el docente debe distinguir de un vistazo que texto proviene del
libro certificado y cual fue sintetizado por Gemma 4.
"""

import streamlit as st

# --- Tokens Carbon -----------------------------------------------------------
GRAY_100 = "#161616"  # background
GRAY_90 = "#262626"   # layer 01
GRAY_80 = "#393939"   # layer 02 / border subtle
GRAY_70 = "#525252"
GRAY_30 = "#c6c6c6"   # text secondary
GRAY_50 = "#8d8d8d"   # text helper
GRAY_10 = "#f4f4f4"   # text primary
BLUE_60 = "#0f62fe"   # interactive primary
BLUE_50 = "#4589ff"
PURPLE_50 = "#a56eff"  # extremo del gradiente AI
GREEN_40 = "#42be65"
YELLOW_30 = "#f1c21b"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, button, input, select, textarea {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

.stApp {{ background: {GRAY_100}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; max-width: 1180px; }}

/* Carbon no usa esquinas redondeadas. */
.stButton > button, .stTextInput input, .stSelectbox > div > div,
.stTextArea textarea {{
    border-radius: 0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}}

.stButton > button {{
    background: {BLUE_60}; color: #fff; border: none;
    padding: 0.9rem 1.6rem; font-weight: 400; font-size: 0.95rem;
    width: 100%; text-align: left; transition: background 70ms cubic-bezier(.2,0,.38,.9);
}}
.stButton > button:hover {{ background: #0353e9; color: #fff; }}
.stButton > button:focus {{ outline: 2px solid #fff; outline-offset: -4px; box-shadow: none; }}

.stTextInput input, .stSelectbox > div > div {{
    background: {GRAY_90} !important; border: none !important;
    border-bottom: 1px solid {GRAY_70} !important; color: {GRAY_10} !important;
}}
.stTextInput input:focus {{ outline: 2px solid {BLUE_60}; outline-offset: -2px; }}

/* --- Encabezado del producto --- */
.cds-header {{
    border-bottom: 1px solid {GRAY_80}; padding-bottom: 1.25rem; margin-bottom: 2rem;
}}
.cds-eyebrow {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.06em;
    text-transform: uppercase; color: {GRAY_50}; margin-bottom: 0.5rem;
}}
.cds-title {{ font-size: 2.1rem; font-weight: 600; color: {GRAY_10}; line-height: 1.2; }}
.cds-subtitle {{ font-size: 1.05rem; color: {GRAY_30}; font-weight: 400; margin-top: 0.4rem; }}

/* --- Etiqueta AI de Carbon for AI --- */
.cds-ai-slug {{
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: linear-gradient(90deg, {PURPLE_50}, {BLUE_50});
    color: #fff; font-family: 'IBM Plex Mono', monospace; font-weight: 600;
    font-size: 0.66rem; letter-spacing: 0.08em; padding: 0.16rem 0.5rem;
    vertical-align: middle; margin-left: 0.55rem;
}}

/* --- Contenedor de contenido generado por IA --- */
.cds-ai-container {{
    position: relative; background:
        linear-gradient(180deg, rgba(165,110,255,0.10) 0%, rgba(69,137,255,0.03) 42%, rgba(38,38,38,0) 78%),
        {GRAY_90};
    border-left: 2px solid {PURPLE_50};
    padding: 1.4rem 1.6rem; margin-bottom: 1rem;
}}
.cds-ai-container::after {{
    content: ''; position: absolute; left: 0; bottom: 0; height: 2px; width: 100%;
    background: linear-gradient(90deg, {PURPLE_50}, rgba(69,137,255,0));
}}

/* --- Contenedor de fuente certificada (sin gradiente: no es IA) --- */
.cds-source-container {{
    background: {GRAY_90}; border-left: 2px solid {GRAY_70};
    padding: 1.1rem 1.4rem; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem; color: {GRAY_30}; line-height: 1.6; margin-bottom: 1rem;
}}

.cds-label {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.06em;
    text-transform: uppercase; color: {GRAY_50}; margin-bottom: 0.55rem;
}}
.cds-body {{ color: {GRAY_10}; font-size: 1rem; line-height: 1.6; }}

/* --- Tira de metricas --- */
.cds-metrics {{ display: flex; gap: 1px; background: {GRAY_80}; margin-bottom: 1.5rem; }}
.cds-metric {{ flex: 1; background: {GRAY_90}; padding: 0.9rem 1.1rem; }}
.cds-metric-label {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.06em;
    text-transform: uppercase; color: {GRAY_50};
}}
.cds-metric-value {{
    font-size: 1.35rem; font-weight: 600; color: {GRAY_10}; margin-top: 0.2rem;
    font-family: 'IBM Plex Mono', monospace;
}}
.cds-metric-value.ai {{
    background: linear-gradient(90deg, {PURPLE_50}, {BLUE_50});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}

/* --- Etiqueta de estado --- */
.cds-tag {{
    display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem;
    padding: 0.16rem 0.55rem; letter-spacing: 0.04em;
}}
.cds-tag.green {{ background: rgba(66,190,101,0.16); color: {GREEN_40}; }}
.cds-tag.yellow {{ background: rgba(241,194,27,0.16); color: {YELLOW_30}; }}
.cds-tag.blue {{ background: rgba(15,98,254,0.20); color: {BLUE_50}; }}

/* --- Tabla estructural --- */
.cds-table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
.cds-table th {{
    background: {GRAY_80}; color: {GRAY_10}; text-align: left; padding: 0.72rem 1rem;
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.02em;
}}
.cds-table td {{
    background: {GRAY_90}; padding: 0.72rem 1rem; color: {GRAY_30};
    font-size: 0.88rem; border-bottom: 1px solid {GRAY_80};
}}
.cds-table td.map-to {{ color: {GRAY_10}; }}

/* --- Pregunta de verificacion --- */
.cds-question {{
    background: {GRAY_90}; border-left: 2px solid {BLUE_60};
    padding: 1.15rem 1.4rem; color: {GRAY_10}; font-size: 1rem; line-height: 1.55;
}}

/* --- Streaming --- */
.cds-stream {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: {GRAY_30};
    background: {GRAY_90}; border-left: 2px solid {PURPLE_50}; padding: 1rem 1.2rem;
    white-space: pre-wrap; word-break: break-all; max-height: 190px; overflow: hidden;
    line-height: 1.5;
}}
.cds-caret {{
    display: inline-block; width: 8px; height: 15px; background: {PURPLE_50};
    vertical-align: text-bottom; animation: cds-blink 1s step-end infinite;
}}
@keyframes cds-blink {{ 50% {{ opacity: 0; }} }}

section[data-testid="stSidebar"] {{
    background: {GRAY_90}; border-right: 1px solid {GRAY_80};
}}
section[data-testid="stSidebar"] .cds-label {{ margin-top: 1.1rem; }}
hr {{ border-color: {GRAY_80}; }}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, subtitle: str, eyebrow: str):
    st.markdown(
        f"""<div class="cds-header">
            <div class="cds-eyebrow">{eyebrow}</div>
            <div class="cds-title">{title}<span class="cds-ai-slug">AI</span></div>
            <div class="cds-subtitle">{subtitle}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def metrics(items):
    """items: lista de (label, value, es_ai)"""
    cells = "".join(
        f'<div class="cds-metric"><div class="cds-metric-label">{lab}</div>'
        f'<div class="cds-metric-value{" ai" if ai else ""}">{val}</div></div>'
        for lab, val, ai in items
    )
    st.markdown(f'<div class="cds-metrics">{cells}</div>', unsafe_allow_html=True)


def ai_container(label: str, body: str):
    st.markdown(
        f"""<div class="cds-ai-container">
            <div class="cds-label">{label}<span class="cds-ai-slug">AI</span></div>
            <div class="cds-body">{body}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def source_container(label: str, body: str):
    st.markdown(
        f'<div class="cds-label">{label}</div>'
        f'<div class="cds-source-container">{body}</div>',
        unsafe_allow_html=True,
    )


def mapping_table(rows):
    body = "".join(
        f'<tr><td>{r["academico"]}</td><td class="map-to">{r["analogico"]}</td></tr>'
        for r in rows
    )
    st.markdown(
        f"""<table class="cds-table">
            <thead><tr><th>Concepto academico (OpenStax)</th>
            <th>Anclaje en el mundo del estudiante</th></tr></thead>
            <tbody>{body}</tbody></table>""",
        unsafe_allow_html=True,
    )


def question(text: str):
    st.markdown(
        f'<div class="cds-label">Pregunta de verificacion metacognitiva'
        f'<span class="cds-ai-slug">AI</span></div>'
        f'<div class="cds-question">{text}</div>',
        unsafe_allow_html=True,
    )


def stream_view(text: str, tokens: int) -> str:
    tail = text[-620:]
    return (
        f'<div class="cds-label">Gemma 4 generando &mdash; {tokens} tokens</div>'
        f'<div class="cds-stream">{tail}<span class="cds-caret"></span></div>'
    )


def tag(text: str, color: str = "blue") -> str:
    return f'<span class="cds-tag {color}">{text}</span>'
