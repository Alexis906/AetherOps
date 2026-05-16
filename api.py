from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil

from core.brain import AetherOpsBrain
from core.rag import AetherOpsRAG

app = FastAPI(title="AetherOps API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("⚡ Iniciando AetherOps API...")
brain = AetherOpsBrain()
rag = AetherOpsRAG()
print("✅ AetherOps API lista.")

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
    return {
        "estado": "online",
        "documentos": len(rag.documentos_cargados),
        "lista_documentos": rag.documentos_cargados
    }

@app.post("/preguntar", response_model=PreguntaResponse)
def preguntar(request: PreguntaRequest):
    perfil_path = os.path.join("data", "perfiles", f"{request.perfil}.txt")
    contexto = ""
    if os.path.exists(perfil_path):
        with open(perfil_path, "r", encoding="utf-8") as f:
            contexto = f.read()

    if rag.tiene_documentos():
        contexto_rag = rag.buscar(request.pregunta)
        if contexto_rag:
            contexto += "\n\nInformacion de documentos:\n" + contexto_rag

    respuesta = brain.responder(request.pregunta, contexto)
    return PreguntaResponse(
        respuesta=respuesta,
        documentos_cargados=len(rag.documentos_cargados)
    )

@app.post("/cargar-pdf")
async def cargar_pdf(archivo: UploadFile = File(...)):
    temp_path = f"temp_{archivo.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(archivo.file, f)
    resultado = rag.cargar_pdf(temp_path)
    os.remove(temp_path)
    return {
        "mensaje": resultado,
        "documentos_totales": len(rag.documentos_cargados)
    }

@app.post("/limpiar-memoria")
def limpiar_memoria():
    brain.limpiar_memoria()
    return {"mensaje": "Memoria limpiada correctamente"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)