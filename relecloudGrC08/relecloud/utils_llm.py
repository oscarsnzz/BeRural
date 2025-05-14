from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle
from .models import Pueblo
import requests
import os

modelo_embedding = SentenceTransformer("all-MiniLM-L6-v2")

def recuperar_contexto(pregunta, k=3):
    pregunta_emb = modelo_embedding.encode([pregunta])
    index = faiss.read_index("relecloud/faiss_index.index")

    with open("relecloud/id_map.pkl", "rb") as f:
        id_map = pickle.load(f)

    D, I = index.search(np.array(pregunta_emb), k)
    ids_encontrados = [id_map[i] for i in I[0]]

    pueblos = Pueblo.objects.filter(id__in=ids_encontrados)
    return "\n".join([f"{p.name}: {p.descripcion}" for p in pueblos])

def llamar_llm_openrouter(contexto, pregunta):
    import json

    prompt = f"""
    Eres un asistente experto en zonas rurales y pueblos de España.
    Responde únicamente con base en el contexto proporcionado, sin inventar información externa. 
    Incluye, si están disponibles, detalles sobre la comunidad autónoma, los servicios del pueblo, sus actividades e incentivos.
    Si hay valoraciones de usuarios o comentarios, resume brevemente lo que dicen.
    Si no tienes información suficiente, responde claramente que no se dispone de datos.

    === CONTEXTO ===
    {contexto}

    === PREGUNTA ===
    {pregunta}

    === RESPUESTA DEL ASISTENTE ===
    """
    

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct:free",  # o cualquier otro gratuito
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "max_tokens": 512
        }
    )

    resultado = response.json()
    if "choices" not in resultado:
        print("❌ Error:", resultado)
        return "Lo siento, hubo un error al generar la respuesta."

    return resultado["choices"][0]["message"]["content"].strip()
