from groq import Groq

class AetherOpsBrain:
    def __init__(self):
        import os
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama3-70b-8192"
        self.perfiles = {
            "personal": "Eres AetherOps, una IA personal de Fabricio. Respondes en español, eres directo y útil.",
            "trabajo": "Eres AetherOps, asistente de trabajo de Fabricio. Ayudas con tareas profesionales en español.",
            "tecnico": "Eres AetherOps, asistente técnico de Fabricio. Eres experto en programación y tecnología."
        }
        print("✅ AetherOps con Groq listo.")

    def preguntar(self, pregunta: str, perfil: str = "personal", contexto: str = "") -> str:
        sistema = self.perfiles.get(perfil, self.perfiles["personal"])
        
        mensajes = [{"role": "system", "content": sistema}]
        
        if contexto:
            mensajes.append({
                "role": "user", 
                "content": f"Contexto de documentos:\n{contexto}\n\nPregunta: {pregunta}"
            })
        else:
            mensajes.append({"role": "user", "content": pregunta})
        
        respuesta = self.client.chat.completions.create(
            model=self.model,
            messages=mensajes,
            max_tokens=1000
        )
        
        return respuesta.choices[0].message.content