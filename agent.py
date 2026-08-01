import os
import json
from typing import List, Iterator, Tuple

import requests
from pydantic import BaseModel, Field, ValidationError

# Endpoint oficial de Google AI Studio.
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"

# Variante MoE de Gemma 4: ~4B parametros activos de 26B totales.
# Elegida sobre gemma-4-31b-it (densa) porque en un aula real la inferencia
# ocurre con hardware limitado y conectividad intermitente: la latencia es
# un requisito pedagogico, no un lujo.
MODEL_FAST = "gemma-4-26b-a4b-it"
MODEL_QUALITY = "gemma-4-31b-it"


class MappingObject(BaseModel):
    academico: str = Field(description="Concepto o variable academica")
    analogico: str = Field(description="Componente de la analogia correspondiente")


class PedagogicalAnalogy(BaseModel):
    technical_concept: str = Field(description="Concepto tecnico objetivo extraido del libro de texto")
    source_citation: str = Field(description="Cita textual y numero de seccion dentro del recurso OER")
    student_interest: str = Field(description="Dominio de interes del alumno seleccionado para la analogia")
    conceptual_analogy: str = Field(description="Explicacion adaptada que mapea las leyes del concepto tecnico hacia las reglas del dominio de interes")
    # Lista plana "academico :: analogico" en lugar de un arreglo de objetos.
    # Anidar objetos dentro del esquema disparaba bucles de repeticion que
    # agotaban el presupuesto de tokens y truncaban el JSON a media cadena.
    mapping_matrix: List[str] = Field(description="Mapeo elemento a elemento, formato 'academico :: analogico'")
    verification_question: str = Field(description="Pregunta conceptual de verificacion")

    def mapping_rows(self) -> List[MappingObject]:
        rows = []
        for item in self.mapping_matrix:
            left, _, right = item.partition("::")
            if right.strip():
                rows.append(MappingObject(academico=left.strip(), analogico=right.strip()))
        return rows


# Schema declarado como dict en lugar de pasar la clase Pydantic al SDK:
# el contrato REST es estable entre versiones y no depende de que
# google-generativeai soporte la coercion de modelos Pydantic.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "technical_concept": {"type": "STRING"},
        "source_citation": {"type": "STRING"},
        "student_interest": {"type": "STRING"},
        "conceptual_analogy": {"type": "STRING"},
        "mapping_matrix": {"type": "ARRAY", "items": {"type": "STRING"}},
        "verification_question": {"type": "STRING"},
    },
    "required": [
        "technical_concept",
        "source_citation",
        "student_interest",
        "conceptual_analogy",
        "mapping_matrix",
        "verification_question",
    ],
}

# Gemma 4 en AI Studio no acepta system_instruction junto con responseSchema
# (la peticion se cuelga). El rol se anexa al prompt, que es ademas como
# Gemma fue entrenado para recibir instrucciones.
ROLE_PREAMBLE = (
    "Eres un experto en pedagogia constructivista. Explicas conceptos tecnicos "
    "mediante analogias ancladas en el mundo real del estudiante. Nunca resuelves "
    "el problema por el alumno: construyes el andamiaje para que lo resuelva solo. "
    "Basas tu respuesta UNICAMENTE en el texto fuente proporcionado."
)


# El andamiaje solo funciona si cae en la zona de desarrollo proximo del alumno:
# una analogia correcta pero calibrada al nivel equivocado no ensena nada. El
# nivel modula el prompt, nunca el esquema de salida.
LEVELS = {
    "Basico": (
        "Secundaria: usa lenguaje cotidiano, evita formulas y simbolos. "
        "La analogia debe apoyarse solo en experiencias fisicas directas."
    ),
    "Intermedio": (
        "Bachillerato: introduce la formula del concepto y vocabulario tecnico "
        "basico, siempre traducido dentro de la analogia."
    ),
    "Avanzado": (
        "Universitario: usa notacion formal, nombra las condiciones de validez "
        "y senala al menos un caso limite donde la analogia deja de sostenerse."
    ),
}


class GemmaEduAgent:
    def __init__(self, api_key: str, model_name: str = MODEL_QUALITY):
        self.api_key = api_key
        self.model_name = model_name

    def _build_prompt(
        self, context_text: str, student_interest: str, level: str = "Intermedio"
    ) -> str:
        return f"""{ROLE_PREAMBLE}

Nivel cognitivo objetivo: {level}. {LEVELS.get(level, '')}

Contexto Recuperado del Libro de Texto (OER):
{context_text}

Interes del Estudiante:
{student_interest}

Genera una analogia pedagogica estructurada respetando estos limites:
- conceptual_analogy: maximo 90 palabras, en segunda persona. No repitas frases.
- mapping_matrix: exactamente 4 cadenas con el formato "academico :: analogico".
- source_citation: una frase literal del contexto anterior mas su numero de seccion.
- verification_question: una sola pregunta, sin respuesta.

La brevedad es un requisito pedagogico: el docente lee esto entre clases."""

    def _payload(
        self,
        context_text: str,
        student_interest: str,
        temperature: float = 0.7,
        level: str = "Intermedio",
    ) -> dict:
        return {
            "contents": [
                {"parts": [{"text": self._build_prompt(context_text, student_interest, level)}]}
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": RESPONSE_SCHEMA,
                "temperature": temperature,
                # Acota la cola de la distribucion. Sin esto observamos
                # degeneracion intermitente (bucles de repeticion silabica)
                # que agotaban el presupuesto de tokens y truncaban el JSON.
                "topP": 0.95,
                # Una salida valida con el esquema plano pesa ~350 tokens. Este
                # techo deja holgura suficiente y, sobre todo, hace que un bucle
                # de repeticion se corte en segundos en vez de consumir medio
                # minuto antes de fallar: abarata el reintento.
                "maxOutputTokens": 900,
            },
        }

    def generate_analogy_stream(
        self, context_text: str, student_interest: str
    ) -> Iterator[Tuple[str, int]]:
        """Emite (texto_acumulado, tokens_aprox) conforme Gemma 4 genera.

        El streaming no acelera la inferencia, pero convierte una espera opaca
        en retroalimentacion continua: el primer token llega en ~1s en lugar
        de que el docente mire una pantalla vacia varios segundos.
        """
        url = f"{API_BASE}{self.model_name}:streamGenerateContent?alt=sse&key={self.api_key}"
        acc = ""
        with requests.post(
            url,
            json=self._payload(context_text, student_interest),
            stream=True,
            timeout=180,
        ) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"):
                    continue
                body = raw[5:].strip()
                if not body:
                    continue
                try:
                    chunk = json.loads(body)
                    part = chunk["candidates"][0]["content"]["parts"][0]["text"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                acc += part
                yield acc, max(1, len(acc) // 4)

    def parse(self, raw_text: str) -> dict:
        """Valida la salida de Gemma contra el esquema Pydantic.

        El responseSchema ya restringe la decodificacion, pero validar aqui
        convierte cualquier desviacion en un error explicito en vez de un
        KeyError a mitad del render.
        """
        try:
            parsed = PedagogicalAnalogy.model_validate_json(raw_text)
            data = parsed.model_dump()
            data["mapping_matrix"] = [r.model_dump() for r in parsed.mapping_rows()]
            return data
        except ValidationError as e:
            raise ValueError(f"La salida de Gemma no cumple el esquema pedagogico: {e}") from e

    def generate_analogy(
        self,
        context_text: str,
        student_interest: str,
        temperature: float = 0.7,
        level: str = "Intermedio",
    ) -> dict:
        """Genera y valida una analogia, reintentando ante degeneracion.

        La decodificacion restringida por esquema no elimina los bucles de
        repeticion estocasticos, que agotan el presupuesto de tokens y truncan
        el JSON. Un reintento a temperatura baja convierte un fallo visible en
        la demo en unos segundos extra.
        """
        url = f"{API_BASE}{self.model_name}:generateContent?key={self.api_key}"
        last_error = None
        for temp in (temperature, 0.4, 0.2):
            try:
                resp = requests.post(
                    url,
                    json=self._payload(context_text, student_interest, temp, level),
                    timeout=180,
                )
                resp.raise_for_status()
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self.parse(text)
            except (ValueError, requests.RequestException, KeyError, IndexError) as e:
                last_error = e
        raise RuntimeError(f"Gemma 4 no produjo una analogia valida: {last_error}")

    def parse_or_retry(self, raw_text: str, context_text: str, student_interest: str) -> dict:
        """Valida la salida del stream; si no cumple, regenera una vez.

        La decodificacion restringida no elimina la degeneracion estocastica.
        Un unico reintento a temperatura baja convierte un fallo visible en
        la demo en un par de segundos extra.
        """
        try:
            return self.parse(raw_text)
        except ValueError:
            return self.generate_analogy(context_text, student_interest, temperature=0.2)

    def generate_analogy_from_image(
        self,
        image_b64: str,
        mime_type: str,
        student_interest: str,
        level: str = "Intermedio",
        temperature: float = 0.7,
    ) -> dict:
        """Genera el andamiaje leyendo la foto de una pagina de libro.

        Se hace en dos pasadas de Gemma, no en una. Pedirle transcribir la
        imagen y emitir JSON restringido simultaneamente lo desestabiliza: en
        medicion, una sola pasada acertaba 1 de 4 veces, degenerando en bucles
        de repeticion que truncaban la salida. Separar percepcion de
        razonamiento -primero transcribir en texto libre, luego el camino de
        texto ya probado- devuelve la fiabilidad sin salir de Gemma.

        Importa porque el corpus real de un profesor no es un indice vectorial,
        es el libro de fisica que tiene sobre el escritorio.
        """
        transcripcion = self.read_page_image(image_b64, mime_type)
        return self.generate_analogy(
            transcripcion, student_interest, temperature=temperature, level=level
        )

    def read_page_image(self, image_b64: str, mime_type: str) -> str:
        """Pasada 1: Gemma 4 transcribe la pagina en texto libre.

        Sin esquema ni JSON. Es una tarea de percepcion pura, y el modelo la
        resuelve de forma estable justamente porque no se le pide nada mas.
        """
        url = f"{API_BASE}{self.model_name}:generateContent?key={self.api_key}"
        last_error = None
        for temp in (0.2, 0.4):
            try:
                resp = requests.post(
                    url,
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"inline_data": {"mime_type": mime_type, "data": image_b64}},
                                    {
                                        "text": "Transcribe el contenido academico de esta pagina "
                                        "de libro de texto: titulo de seccion, definiciones y "
                                        "formulas. Devuelve solo la transcripcion, sin comentarios."
                                    },
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": temp,
                            "topP": 0.95,
                            "maxOutputTokens": 600,
                        },
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                texto = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if len(texto) > 40:
                    return texto
                last_error = ValueError("transcripcion demasiado corta")
            except (requests.RequestException, KeyError, IndexError) as e:
                last_error = e
        raise RuntimeError(f"Gemma 4 no pudo leer la pagina: {last_error}")

    def warmup(self) -> bool:
        """Golpea el endpoint al abrir la app para que el primer clic del juez
        no pague el arranque en frio."""
        try:
            requests.post(
                f"{API_BASE}{self.model_name}:generateContent?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": "ok"}]}],
                    "generationConfig": {"maxOutputTokens": 1},
                },
                timeout=30,
            )
            return True
        except requests.RequestException:
            return False
