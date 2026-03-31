from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma

def get_embedding_function():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def query_chroma(query: str, chroma_path: str, k: int = 3):
    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=get_embedding_function()
    )

    results = db.similarity_search(query, k=k)

    return results