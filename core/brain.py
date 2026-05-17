import warnings
warnings.filterwarnings("ignore")
from transformers import AutoTokenizer, AutoModelForCausalLM, logging
from peft import PeftModel
import torch
logging.set_verbosity_error()

class AetherOpsBrain:
    def __init__(self):
        print("⚡ Iniciando AetherOps con modelo entrenado...")
        base_model = "Qwen/Qwen2.5-0.5B-Instruct"
        finetuned = "modelo-rlhf"

        self.tokenizer = AutoTokenizer.from_pretrained(finetuned, trust_remote_code=True)
        base = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32, device_map="cpu", trust_remote_code=True)
        self.model = PeftModel.from_pretrained(base, finetuned)
        self.historial = []
        print("✅ AetherOps listo.")

    def responder(self, pregunta: str, contexto: str) -> str:
        self.historial.append({"role": "user", "content": pregunta})
        messages = [
            {"role": "system", "content": "Eres AetherOps, la IA personal de Fabricio. Responde siempre en espanol, corto y directo.\n" + contexto}
        ] + self.historial

        texto = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(texto, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        respuesta = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        self.historial.append({"role": "assistant", "content": respuesta})

        if len(self.historial) > 10:
            self.historial = self.historial[-10:]

        return respuesta

    def limpiar_memoria(self):
        self.historial = []