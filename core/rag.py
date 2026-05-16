import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class AetherOpsRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vectorstore = None
        self.documentos_cargados = []

    def cargar_pdf(self, ruta_pdf: str) -> str:
        try:
            loader = PyPDFLoader(ruta_pdf)
            paginas = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            fragmentos = splitter.split_documents(paginas)

            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(fragmentos, self.embeddings)
            else:
                self.vectorstore.add_documents(fragmentos)

            nombre = os.path.basename(ruta_pdf)
            self.documentos_cargados.append(nombre)
            return f"✅ Cargado: {nombre} ({len(paginas)} páginas, {len(fragmentos)} fragmentos)"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def buscar(self, pregunta: str, k: int = 3) -> str:
        if self.vectorstore is None:
            return ""
        resultados = self.vectorstore.similarity_search(pregunta, k=k)
        contexto = "\n\n".join([r.page_content for r in resultados])
        return contexto

    def tiene_documentos(self) -> bool:
        return self.vectorstore is not None