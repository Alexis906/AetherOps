import tkinter as tk
from tkinter import scrolledtext
import threading
import os
from core.brain import AetherOpsBrain

PERFILES_DIR = os.path.join(os.path.dirname(__file__), "data", "perfiles")
HISTORIAL_PATH = os.path.join(os.path.dirname(__file__), "data", "historial.txt")

def cargar_perfil(nombre):
    ruta = os.path.join(PERFILES_DIR, f"{nombre}.txt")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    return "AetherOps es una IA creada por Fabricio."

def listar_perfiles():
    if not os.path.exists(PERFILES_DIR):
        return ["personal"]
    return [f.replace(".txt","") for f in os.listdir(PERFILES_DIR) if f.endswith(".txt")]

def guardar_historial(perfil, usuario, respuesta):
    with open(HISTORIAL_PATH, "a", encoding="utf-8") as f:
        from datetime import datetime
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{hora}] [{perfil}]\nTú: {usuario}\nAetherOps: {respuesta}\n\n")

BG       = "#080c14"
BG2      = "#0f1623"
ACCENT   = "#00e5ff"
ACCENT2  = "#7b2fff"
TXT      = "#e0e8f0"
TXT2     = "#5a7a99"
FONT     = ("Consolas", 10)

class AetherOpsUI:
    def __init__(self):
        self.brain = None
        self.ventana = tk.Tk()
        self.perfil_actual = tk.StringVar(value="personal")
        self.ventana.title("AetherOps")
        self.ventana.geometry("680x580")
        self.ventana.configure(bg=BG)
        self.ventana.resizable(False, False)
        self._construir_ui()
        threading.Thread(target=self._cargar_brain, daemon=True).start()

    def _construir_ui(self):
        # Header
        header = tk.Frame(self.ventana, bg=BG2, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="⚡", font=("Consolas", 20),
                 bg=BG2, fg=ACCENT).pack(side=tk.LEFT, padx=(20,6), pady=10)
        tk.Label(header, text="AETHER", font=("Consolas", 18, "bold"),
                 bg=BG2, fg=ACCENT).pack(side=tk.LEFT)
        tk.Label(header, text="OPS", font=("Consolas", 18, "bold"),
                 bg=BG2, fg=ACCENT2).pack(side=tk.LEFT)

        tk.Button(
            header, text="🗑 Limpiar",
            font=("Consolas", 8), bg=BG2, fg=TXT2,
            relief="flat", bd=0,
            activebackground=BG, activeforeground=ACCENT,
            command=self._limpiar_memoria
        ).pack(side=tk.RIGHT, padx=16)

        # Barra de perfiles
        perfiles_bar = tk.Frame(self.ventana, bg="#0a1020", height=36)
        perfiles_bar.pack(fill=tk.X)
        perfiles_bar.pack_propagate(False)

        tk.Label(perfiles_bar, text="PERFIL:",
                 font=("Consolas", 8), bg="#0a1020", fg=TXT2).pack(side=tk.LEFT, padx=(16,8), pady=8)

        self.botones_perfil = {}
        for perfil in listar_perfiles():
            btn = tk.Button(
                perfiles_bar, text=perfil.upper(),
                font=("Consolas", 8, "bold"),
                bg="#0a1020", fg=TXT2,
                relief="flat", bd=0, padx=10,
                activebackground=ACCENT2, activeforeground=TXT,
                command=lambda p=perfil: self._cambiar_perfil(p)
            )
            btn.pack(side=tk.LEFT, pady=4)
            self.botones_perfil[perfil] = btn

        self._resaltar_perfil("personal")

        tk.Frame(self.ventana, bg=ACCENT, height=1).pack(fill=tk.X)

        # Chat
        self.chat = scrolledtext.ScrolledText(
            self.ventana, wrap=tk.WORD,
            bg=BG, fg=TXT, font=FONT,
            state="disabled", bd=0,
            padx=16, pady=12,
            selectbackground=ACCENT2
        )
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.tag_config("user",    foreground=ACCENT,    font=("Consolas", 10, "bold"))
        self.chat.tag_config("bot",     foreground="#a0f0c0", font=FONT)
        self.chat.tag_config("sistema", foreground=TXT2,      font=("Consolas", 9, "italic"))
        self.chat.tag_config("label",   foreground=ACCENT2,   font=("Consolas", 10, "bold"))
        self.chat.tag_config("perfil",  foreground=ACCENT,    font=("Consolas", 9, "bold"))

        tk.Frame(self.ventana, bg=ACCENT2, height=1).pack(fill=tk.X)

        # Input
        bottom = tk.Frame(self.ventana, bg=BG2, height=56)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)

        self.status = tk.Label(bottom, text="● Iniciando...",
                               font=("Consolas", 8), bg=BG2, fg=TXT2)
        self.status.pack(side=tk.BOTTOM, anchor=tk.W, padx=16, pady=(0,4))

        frame_input = tk.Frame(bottom, bg=BG2)
        frame_input.pack(fill=tk.X, padx=12, pady=(8,0))

        self.entrada = tk.Entry(
            frame_input, font=("Consolas", 11),
            bg="#141e2e", fg=TXT,
            insertbackground=ACCENT,
            relief="flat", bd=0
        )
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0,10))
        self.entrada.bind("<Return>", lambda e: self._enviar())
        self.entrada.config(state="disabled")

        self.boton = tk.Button(
            frame_input, text="ENVIAR →",
            font=("Consolas", 9, "bold"),
            bg=ACCENT, fg=BG, relief="flat", bd=0,
            activebackground=ACCENT2, activeforeground=TXT,
            command=self._enviar, padx=14, pady=7
        )
        self.boton.pack(side=tk.RIGHT)
        self.boton.config(state="disabled")

    def _resaltar_perfil(self, perfil):
        for nombre, btn in self.botones_perfil.items():
            if nombre == perfil:
                btn.config(bg=ACCENT2, fg=TXT)
            else:
                btn.config(bg="#0a1020", fg=TXT2)

    def _cambiar_perfil(self, perfil):
        self.perfil_actual.set(perfil)
        self._resaltar_perfil(perfil)
        if self.brain:
            self.brain.limpiar_memoria()
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"\n  ⚡ Perfil cambiado a: ", "sistema")
        self.chat.insert(tk.END, f"{perfil.upper()}\n", "perfil")
        self.chat.config(state="disabled")
        self.chat.see(tk.END)

    def _cargar_brain(self):
        self._mensaje_sistema("  Cargando modelo de IA...")
        self.brain = AetherOpsBrain()
        self._mensaje_sistema("  Modelo listo.\n")
        self.status.config(text="● Online", fg="#00ff88")
        self.entrada.config(state="normal")
        self.boton.config(state="normal")
        self.entrada.focus()

    def _mensaje_sistema(self, texto):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{texto}\n", "sistema")
        self.chat.config(state="disabled")
        self.chat.see(tk.END)

    def _limpiar_memoria(self):
        if self.brain:
            self.brain.limpiar_memoria()
            self._mensaje_sistema("🗑 Memoria limpiada — nueva conversación.")

    def _enviar(self):
        pregunta = self.entrada.get().strip()
        if not pregunta or not self.brain:
            return
        self.entrada.delete(0, tk.END)
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"\n  Tú  ", "label")
        self.chat.insert(tk.END, f"→ {pregunta}\n", "user")
        self.chat.config(state="disabled")
        self.boton.config(state="disabled")
        self.status.config(text="● Pensando...", fg=ACCENT)
        threading.Thread(target=self._responder, args=(pregunta,), daemon=True).start()

    def _responder(self, pregunta):
        perfil = self.perfil_actual.get()
        contexto = cargar_perfil(perfil)
        respuesta = self.brain.responder(pregunta, contexto)
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"  AetherOps  ", "label")
        self.chat.insert(tk.END, f"→ {respuesta}\n", "bot")
        self.chat.config(state="disabled")
        self.chat.see(tk.END)
        self.boton.config(state="normal")
        self.status.config(text="● Online", fg="#00ff88")
        guardar_historial(perfil, pregunta, respuesta)

    def iniciar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = AetherOpsUI()
    app.iniciar()