import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from core.rag import AetherOpsRAG
import os
import re

try:
    from ddgs import DDGS
except:
    from duckduckgo_search import DDGS

class AetherOpsAgente:
    def __init__(self, brain, rag: AetherOpsRAG):
        self.brain = brain
        self.rag = rag
        self.notas_path = os.path.join("data", "notas.txt")
        self.herramientas = {
            "calcular":     self._calcular,
            "hora":         self._hora_actual,
            "buscar":       self._buscar_documentos,
            "web":          self._buscar_web,
            "guardar_nota": self._guardar_nota,
            "leer_notas":   self._leer_notas,
            "ejecutar":     self._ejecutar_codigo,
        }

    def _calcular(self, expresion: str) -> str:
        try:
            resultado = eval(expresion, {"__builtins__": {}}, {})
            return f"El resultado de {expresion} es {resultado}"
        except:
            return "No pude calcular esa expresion"

    def _hora_actual(self, _: str = "") -> str:
        ahora = datetime.now()
        return f"Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}"

    def _buscar_documentos(self, pregunta: str) -> str:
        if not self.rag.tiene_documentos():
            return "No hay documentos cargados."
        resultado = self.rag.buscar(pregunta)
        return resultado if resultado else "No encontre informacion relevante."

    def _buscar_web(self, consulta: str) -> str:
        try:
            resultados = []
            with DDGS() as ddgs:
                for r in ddgs.text(consulta, max_results=2):
                    resultados.append(r)
            if not resultados:
                return "No encontre resultados."
            resumen = ""
            for i, r in enumerate(resultados, 1):
                titulo = r.get('title', '')[:60]
                cuerpo = r.get('body', '')[:150]
                resumen += f"{i}. {titulo}: {cuerpo}\n"
            return resumen
        except Exception as e:
            return f"Error buscando: {str(e)}"

    def _guardar_nota(self, nota: str) -> str:
        try:
            hora = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(self.notas_path, "a", encoding="utf-8") as f:
                f.write(f"[{hora}] {nota}\n")
            return f"Nota guardada correctamente: {nota}"
        except Exception as e:
            return f"No pude guardar la nota: {str(e)}"

    def _leer_notas(self, _: str = "") -> str:
        try:
            if not os.path.exists(self.notas_path):
                return "No hay notas guardadas aun."
            with open(self.notas_path, "r", encoding="utf-8") as f:
                contenido = f.read()
            return f"Notas guardadas:\n{contenido}" if contenido else "No hay notas."
        except:
            return "No pude leer las notas."

    def _ejecutar_codigo(self, codigo: str) -> str:
        try:
            import io
            import contextlib
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                exec(codigo, {"__builtins__": __builtins__})
            resultado = salida.getvalue()
            return f"Resultado:\n{resultado}" if resultado else "Codigo ejecutado sin salida."
        except Exception as e:
            return f"Error al ejecutar: {str(e)}"

    def _detectar_herramienta(self, pregunta: str):
        p = pregunta.lower()

        # Calculadora
        if any(w in p for w in ["cuanto es", "calcula", "suma", "resta", "multiplica", "divide"]):
            expresion = re.findall(r'[\d\+\-\*\/\.\(\)\s]+', pregunta)
            if expresion:
                exp = max(expresion, key=len).strip()
                if any(op in exp for op in ['+', '-', '*', '/']):
                    return "calcular", exp

        # Hora y fecha
        if any(w in p for w in ["hora", "fecha", "hoy", "que dia", "que hora"]):
            return "hora", ""

        # Busqueda web
        if any(w in p for w in ["busca en internet", "busca en google", "busca en la web",
                                  "que dice internet", "busca online", "noticias de",
                                  "busca informacion sobre", "busca en linea"]):
            consulta = p
            for w in ["busca en internet sobre", "busca en internet", "busca en google",
                      "busca en la web", "que dice internet sobre", "que dice internet",
                      "busca online", "noticias de", "busca informacion sobre",
                      "busca en linea"]:
                consulta = consulta.replace(w, "").strip()
            return "web", consulta if consulta else pregunta

        # Guardar nota
        if any(w in p for w in ["guarda una nota", "anota que", "guarda esto",
                                  "recuerda esto", "guarda que", "toma nota"]):
            nota = p
            for w in ["guarda una nota que", "guarda una nota", "anota que",
                      "guarda esto:", "recuerda esto:", "guarda que", "toma nota de que",
                      "toma nota que", "toma nota"]:
                nota = nota.replace(w, "").strip()
            return "guardar_nota", nota

        # Leer notas
        if any(w in p for w in ["mis notas", "que notas", "lee las notas",
                                  "cuales son mis notas", "que tengo anotado"]):
            return "leer_notas", ""

        # Ejecutar codigo
        if "```python" in pregunta:
            codigo = re.search(r'```python(.*?)```', pregunta, re.DOTALL)
            if codigo:
                return "ejecutar", codigo.group(1).strip()

        # Buscar en documentos
        if any(w in p for w in ["documento", "contrato", "pdf", "dice el",
                                  "segun el", "busca en el", "en el documento"]):
            return "buscar", pregunta

        return None, None

    def responder(self, pregunta: str, contexto: str = "") -> str:
        herramienta, parametro = self._detectar_herramienta(pregunta)

        if herramienta:
            resultado = self.herramientas[herramienta](parametro)

            # Web y notas muestran resultado directo sin pasar por el modelo
            if herramienta == "web":
                return f"[WEB] Encontre esto en internet:\n{resultado}"
            if herramienta == "leer_notas":
                return f"[NOTAS] {resultado}"
            if herramienta == "guardar_nota":
                return f"[NOTA] {resultado}"
            if herramienta == "hora":
                return f"[HORA] {resultado}"
            if herramienta == "calcular":
                return f"[CALCULAR] {resultado}"

            # Para buscar en documentos y ejecutar codigo, pasar por el modelo
            contexto_enriquecido = f"{contexto}\n\nInformacion encontrada:\n{resultado}"
            respuesta = self.brain.responder(pregunta, contexto_enriquecido)
            return f"[{herramienta.upper()}] {respuesta}"

        if self.rag.tiene_documentos():
            contexto_rag = self.rag.buscar(pregunta)
            if contexto_rag:
                contexto = contexto + "\n\nDocumentos:\n" + contexto_rag

        return self.brain.responder(pregunta, contexto)