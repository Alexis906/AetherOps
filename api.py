from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from groq import Groq

app = FastAPI(title="AetherOps API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

perfiles = {
    "personal": "Eres AetherOps, una IA personal de Fabricio. Respondes en español, eres directo y útil.",
    "trabajo": "Eres AetherOps, asistente de trabajo de Fabricio. Ayudas con tareas profesionales en español.",
    "tecnico": "Eres AetherOps, asistente técnico de Fabricio. Eres experto en programación y tecnología."
}

class PreguntaRequest(BaseModel):
    pregunta: str
    perfil: str = "personal"

class PreguntaResponse(BaseModel):
    respuesta: str
    documentos_cargados: int

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
    return {"estado": "online", "documentos": 0}

@app.post("/preguntar", response_model=PreguntaResponse)
def preguntar(request: PreguntaRequest):
    sistema = perfiles.get(request.perfil, perfiles["personal"])
    try:
        respuesta = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": request.pregunta}
            ],
            max_tokens=1000
        )
        texto = respuesta.choices[0].message.content
    except Exception as e:
        texto = f"Error: {str(e)}"
    return PreguntaResponse(respuesta=texto, documentos_cargados=0)

@app.post("/limpiar-memoria")
def limpiar_memoria():
    return {"mensaje": "Memoria limpiada correctamente"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)