import google.generativeai as genai
import numpy as np
import os

class EduRAG:
    def __init__(self, persist_directory="./mock_db"):
        self.documents = []
        self.embeddings = []
        
    def ingest_document(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        sections = content.split("##")
        for section in sections:
            if section.strip():
                doc_text = "## " + section.strip()
                self.documents.append(doc_text)
                
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "tu_api_key_de_ai_studio_aqui":
            genai.configure(api_key=api_key)
            try:
                response = genai.embed_content(
                    model="models/embedding-001",
                    content=self.documents,
                    task_type="retrieval_document"
                )
                self.embeddings = response['embedding']
            except Exception as e:
                print("Error de API al vectorizar:", e)
                self.embeddings = [np.random.rand(768) for _ in self.documents]
        else:
            # Mock de embeddings si no hay API Key (para que la app no truene)
            self.embeddings = [np.random.rand(768) for _ in self.documents]
            
    def search(self, query: str, n_results: int = 1) -> str:
        if not self.documents:
            return "No se encontró contexto."
            
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "tu_api_key_de_ai_studio_aqui":
            try:
                query_response = genai.embed_content(
                    model="models/embedding-001",
                    content=query,
                    task_type="retrieval_query"
                )
                query_emb = query_response['embedding']
                
                # Similitud Coseno con Numpy
                similarities = []
                for doc_emb in self.embeddings:
                    # A dot B / (norm A * norm B)
                    sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
                    similarities.append(sim)
                    
                best_idx = np.argmax(similarities)
                return self.documents[best_idx]
            except Exception as e:
                print("Error en búsqueda semántica:", e)
                
        # Fallback simple
        for doc in self.documents:
            if query.lower() in doc.lower():
                return doc
        return self.documents[0] if self.documents else "No hay contexto."
