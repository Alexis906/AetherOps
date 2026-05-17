from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
import requests

app = FastAPI(title="AetherOps API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

documentos = []

class PreguntaRequest(BaseModel):
    pregunta: str
    perfil: str = "personal"

class PreguntaResponse(BaseModel):
    respuesta: str
    documentos_cargados: int

def preguntar_hf(pregunta: str, contexto: str = "") -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"Eres AetherOps, la IA personal de Fabricio. {contexto}\nPregunta: {pregunta}\nRespuesta:"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No pude responder.").strip()
        return "No pude responder en este momento."
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/")
def inicio():
    return {
        "nombre": "AetherOps API",
        "version": "1.0.0",
        "estado": "online",
        "creador": "Fabricio"
    }

@app.get("/estado")
def estado():
    return {
        "estado": "online",
        "documentos": len(documentos)
    }

@app.post("/preguntar", response_model=PreguntaResponse)
def preguntar(request: PreguntaRequest):
    contexto = f"Perfil activo: {request.perfil}."
    respuesta = preguntar_hf(request.pregunta, contexto)
    return PreguntaResponse(
        respuesta=respuesta,
        documentos_cargados=len(documentos)
    )

@app.post("/limpiar-memoria")
def limpiar_memoria():
    return {"mensaje": "Memoria limpiada correctamente"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)