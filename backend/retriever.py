from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma
from config import CHROMA_PATH, EMBEDDING_MODEL

class HotelRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = self._load_vector_store()

    def _load_vector_store(self):
        """Loads the ChromaDB vector store."""
        if not CHROMA_PATH.exists():
            # If the database doesn't exist, we will need to run the rag_pipeline.py later,
            # but for now, we'll try to initialize or handle gracefully.
            raise FileNotFoundError(f"ChromaDB not found at {CHROMA_PATH}. Please run rag_pipeline.py first.")
            
        return Chroma(
            persist_directory=str(CHROMA_PATH),
            embedding_function=self.embeddings
        )

    def query(self, text: str, k: int = 3):
        """Queries the vector store for relevant documents."""
        results = self.vector_store.similarity_search(text, k=k)
        return results

# Singleton instance for the application
retriever = None

def get_retriever():
    global retriever
    if retriever is None:
        retriever = HotelRetriever()
    return retriever