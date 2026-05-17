import json
import os
from datetime import datetime

FEEDBACK_PATH = os.path.join("data", "feedback.json")

def guardar_feedback(pregunta: str, respuesta: str, puntuacion: int, comentario: str = ""):
    datos = []
    if os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except:
                datos = []

    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pregunta": pregunta,
        "respuesta": respuesta,
        "puntuacion": puntuacion,
        "comentario": comentario
    }
    datos.append(entrada)

    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def cargar_feedback():
    if not os.path.exists(FEEDBACK_PATH):
        return []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def estadisticas_feedback():
    datos = cargar_feedback()
    if not datos:
        return {"total": 0, "promedio": 0, "buenos": 0, "malos": 0}
    total = len(datos)
    promedio = sum(d["puntuacion"] for d in datos) / total
    buenos = sum(1 for d in datos if d["puntuacion"] >= 4)
    malos = sum(1 for d in datos if d["puntuacion"] <= 2)
    return {
        "total": total,
        "promedio": round(promedio, 2),
        "buenos": buenos,
        "malos": malos
    }

def exportar_dataset_entrenamiento():
    datos = cargar_feedback()
    buenos = [d for d in datos if d["puntuacion"] >= 4]
    ruta = os.path.join("data", "rlhf_dataset.jsonl")
    with open(ruta, "w", encoding="utf-8") as f:
        for d in buenos:
            prompt = f"### Instruccion:\n{d['pregunta']}\n\n### Respuesta:\n{d['respuesta']}"
            f.write(json.dumps({"text": prompt}, ensure_ascii=False) + "\n")
    return len(buenos), ruta