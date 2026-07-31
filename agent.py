import os
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
import json

class MappingObject(BaseModel):
    academico: str = Field(description="Concepto o variable académica")
    analogico: str = Field(description="Componente de la analogía correspondiente")

class PedagogicalAnalogy(BaseModel):
    technical_concept: str = Field(description="Concepto técnico objetivo extraído del libro de texto")
    source_citation: str = Field(description="Cita textual y número de sección dentro del recurso OER")
    student_interest: str = Field(description="Dominio de interés del alumno seleccionado para la analogía")
    conceptual_analogy: str = Field(description="Explicación adaptada que mapea las leyes del concepto técnico hacia las reglas del dominio de interés")
    mapping_matrix: List[MappingObject] = Field(description="Mapeo explícito elemento a elemento")
    verification_question: str = Field(description="Pregunta conceptual de verificación")

class GemmaEduAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Usamos gemini-1.5-flash como proxy veloz o si hay acceso directo a Gemma via API, ajustamos el nombre del modelo.
        # Para el hackday, si queremos usar modelos Gemma en AI studio usaríamos el endpoint adecuado.
        # Asumiremos gemini-1.5-flash para la demo rápida ya que soporta Function Calling de forma nativa e impecable.
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="""Eres un diseñador instruccional riguroso. Tu objetivo es generar 
            andamiaje conceptual basado estrictamente en el texto fuente proporcionado. 
            No debes alucinar conceptos. Utiliza el contexto recuperado para crear una analogía 
            profunda basada en los intereses del estudiante."""
        )

    def generate_analogy(self, context_text: str, student_interest: str) -> dict:
        prompt = f"""
        Contexto Recuperado del Libro de Texto:
        {context_text}
        
        Interés del Estudiante:
        {student_interest}
        
        Genera una analogía pedagógica estructurada.
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=PedagogicalAnalogy,
            ),
        )
        return json.loads(response.text)
