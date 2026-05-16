import warnings
warnings.filterwarnings("ignore")
from transformers import AutoTokenizer, AutoModelForCausalLM, logging
import torch
logging.set_verbosity_error()

class AetherOpsBrain:
    def __init__(self):
        print("⚡ Iniciando AetherOps...")
        modelo = "Qwen/Qwen2.5-0.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(modelo)
        self.model = AutoModelForCausalLM.from_pretrained(
            modelo,
            torch_dtype=torch.float32,
            device_map="cpu"
        )
        self.historial = []  # ← aquí vive la memoria
        print("✅ AetherOps listo.")

    def responder(self, pregunta: str, contexto: str) -> str:
        # Agrega la pregunta nueva al historial
        self.historial.append({
            "role": "user",
            "content": pregunta
        })

        # Construye los mensajes completos con memoria
        messages = [
            {
                "role": "system",
                "content": (
                    f"Eres AetherOps, una IA asistente personal creada por Fabri. "
                    f"Responde siempre en español, de forma corta y directa. "
                    f"Usa este conocimiento base:\n{contexto}"
                )
            }
        ] + self.historial  # ← incluye toda la conversación anterior

        # Genera la respuesta
        texto = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer(texto, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        respuesta = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()

        # Guarda la respuesta en el historial
        self.historial.append({
            "role": "assistant",
            "content": respuesta
        })

        # Limita la memoria a los últimos 10 mensajes para no sobrecargar
        if len(self.historial) > 10:
            self.historial = self.historial[-10:]

        return respuesta

    def limpiar_memoria(self):
        self.historial = []