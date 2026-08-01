import os

import numpy as np
import requests

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"

# La familia Gemma no expone un endpoint de embeddings en Google AI Studio,
# asi que la recuperacion usa el encoder de Gemini. El razonamiento pedagogico
# -que es el producto- corre integramente en Gemma 4.
EMBED_MODEL = "gemini-embedding-001"


class EduRAG:
    """Indice vectorial en memoria sobre recursos educativos abiertos (OER).

    Se descarto ChromaDB deliberadamente: para un corpus de una decena de
    secciones, un producto punto con Numpy es exacto, tiene cero dependencias
    nativas que compilar en Windows y hace el repo clonable por un juez sin
    friccion de instalacion.
    """

    def __init__(self):
        self.documents = []
        self.embeddings = []
        # "semantic" | "keyword" -> se expone en la UI para no atribuirle al
        # sistema una capacidad que en ese momento no esta ejerciendo.
        self.mode = "keyword"
        self.last_error = None

    def _api_key(self):
        key = os.getenv("GEMINI_API_KEY")
        if not key or key == "tu_api_key_de_ai_studio_aqui":
            return None
        return key

    def _embed(self, key: str, text: str, task_type: str):
        resp = requests.post(
            f"{API_BASE}{EMBED_MODEL}:embedContent?key={key}",
            json={
                "model": f"models/{EMBED_MODEL}",
                "content": {"parts": [{"text": text}]},
                "taskType": task_type,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return np.array(resp.json()["embedding"]["values"], dtype=np.float32)

    def ingest_document(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for section in content.split("##"):
            if section.strip():
                self.documents.append("## " + section.strip())

        key = self._api_key()
        if not key:
            self.last_error = "Sin GEMINI_API_KEY: recuperacion por palabra clave."
            return

        try:
            self.embeddings = [
                self._embed(key, doc, "RETRIEVAL_DOCUMENT") for doc in self.documents
            ]
            self.mode = "semantic"
        except (requests.RequestException, KeyError) as e:
            # Antes esto caia a np.random.rand(768), lo que producia
            # recuperacion aleatoria disfrazada de busqueda semantica.
            self.embeddings = []
            self.mode = "keyword"
            self.last_error = f"Vectorizacion no disponible ({type(e).__name__}); degradado a palabra clave."

    def _keyword_search(self, query: str) -> str:
        if not self.documents:
            return "No se encontro contexto."
        q = set(query.lower().split())
        best, best_score = self.documents[0], -1
        for doc in self.documents:
            score = len(q & set(doc.lower().split()))
            if score > best_score:
                best, best_score = doc, score
        return best

    def search(self, query: str, n_results: int = 1) -> str:
        if not self.documents:
            return "No se encontro contexto."

        key = self._api_key()
        if self.mode == "semantic" and key and self.embeddings:
            try:
                q_emb = self._embed(key, query, "RETRIEVAL_QUERY")
                sims = [
                    float(np.dot(q_emb, d) / (np.linalg.norm(q_emb) * np.linalg.norm(d)))
                    for d in self.embeddings
                ]
                return self.documents[int(np.argmax(sims))]
            except (requests.RequestException, KeyError) as e:
                self.mode = "keyword"
                self.last_error = f"Busqueda semantica fallo ({type(e).__name__}); degradado a palabra clave."

        return self._keyword_search(query)
