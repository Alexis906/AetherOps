from core.brain import AetherOpsBrain

import os

def cargar_conocimiento():
    ruta = os.path.join(os.path.dirname(__file__), "data", "knowledge.txt")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    return "AetherOps es una inteligencia artificial creada por Fabri."

CONTEXTO = cargar_conocimiento()

if __name__ == "__main__":
    brain = AetherOpsBrain()
    print("\n--- AetherOps Chatbot ---")
    print("Escribe 'salir' para terminar\n")

    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() == "salir":
            print("AetherOps: ¡Hasta luego!")
            break
        respuesta = brain.responder(pregunta, contexto)
        print(f"AetherOps: {respuesta}\n")