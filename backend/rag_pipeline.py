import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma
import os
import shutil

DATA_DIR = "/Users/lait-zet/Desktop/Hotel-AI-assistant-RaG/data"

def load_hotel_profile(path: str | Path) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    d = json.loads(file_path.read_text(encoding="utf-8"))

    text = (
        f"Hotel: {d['hotel_name']}\n"
        f"Location: {d['location']}\n"
        f"Description: {d['description']}\n"
        f"Amenities: {', '.join(d.get('amenities', []))}\n"
        f"Contact: {json.dumps(d.get('contact', {}), ensure_ascii=False)}"
    )

    return [{
        "id": "hotel_profile",
        "source": "hotel_profile",
        "text": text,
        "metadata": d
    }]


def load_faqs(path: str | Path) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    items = json.loads(file_path.read_text(encoding="utf-8"))
    chunks = []
    for item in items:
        text = f"FAQ Q: {item['question']}\nFAQ A: {item['answer']}"
        chunks.append({
            "id": f"faq_{item['faq_id']}",
            "source": "faqs",
            "text": text,
            "metadata": item,
        })
    return chunks


def load_knowledge_base(path: str | Path) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    items = json.loads(file_path.read_text(encoding="utf-8"))
    chunks = []
    for item in items:
        text = f"Topic: {item['title']}\n{item['content']}"
        chunks.append({
            "id": item["doc_id"],
            "source": "knowledge_base",
            "text": text,
            "metadata": item,
        })
    return chunks


def load_rooms(path: str | Path) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    items = json.loads(file_path.read_text(encoding="utf-8"))
    chunks = []
    for item in items:
        text = (
            f"Room Type: {item['room_type']}\n"
            f"Capacity: {item['capacity']} guests\n"
            f"Price: €{item['price_per_night_eur']} per night\n"
            f"View: {item['view']}\n"
            f"Breakfast Included: {'Yes' if item['breakfast_included'] else 'No'}"
        )
        if item.get("features"):
            text += f"\nFeatures: {', '.join(item['features'])}"

        chunks.append({
            "id": item["room_id"],
            "source": "rooms",
            "text": text,
            "metadata": item,
        })
    return chunks


def load_services(path: str | Path) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    items = json.loads(file_path.read_text(encoding="utf-8"))
    chunks = []
    for item in items:
        text = (
            f"Service: {item['service_name']}\n"
            f"Price: €{item['price_eur']}\n"
            f"Description: {item['description']}"
        )
        chunks.append({
            "id": item["service_id"],
            "source": "services",
            "text": text,
            "metadata": item,
        })
    return chunks


def build_chunks() -> list[dict]:
    chunks = []
    seen_ids = set()

    def add(new_chunks):
        for c in new_chunks:
            if c["id"] not in seen_ids:
                seen_ids.add(c["id"])
                chunks.append(c)

    add(load_hotel_profile(f"{DATA_DIR}/hotel_profile.json"))
    add(load_faqs(f"{DATA_DIR}/large_faqs.json"))
    add(load_knowledge_base(f"{DATA_DIR}/large_knowledge_base.json"))
    add(load_rooms(f"{DATA_DIR}/large_rooms.json"))
    add(load_services(f"{DATA_DIR}/large_services.json"))

    return chunks



def make_metadata_safe(metadata: dict) -> dict:
    safe = {}

    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, list):
            safe[key] = value
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_key = f"{key}_{sub_key}"
                if isinstance(sub_value, (str, int, float, bool)) or sub_value is None:
                    safe[flat_key] = sub_value
                elif isinstance(sub_value, list):
                    safe[flat_key] = sub_value
                else:
                    safe[flat_key] = json.dumps(sub_value, ensure_ascii=False)
        else:
            safe[key] = json.dumps(value, ensure_ascii=False)

    return safe


def chunks_to_documents(chunks: list[dict]) -> list[Document]:
    documents = []

    for chunk in chunks:
        metadata = {
            "id": chunk["id"],
            "source": chunk["source"],
        }

        metadata.update(make_metadata_safe(chunk["metadata"]))

        documents.append(
            Document(
                page_content=chunk["text"],
                metadata=metadata
            )
        )

    return documents


def get_embedding_function():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def add_to_chroma(documents, chroma_path):
    # Reset DB to avoid duplicates
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=get_embedding_function()
    )

    db.add_documents(documents)
    db.persist()

    return db


if __name__ == "__main__":
    docs = chunks_to_documents(build_chunks())

    chroma_path = "/Users/lait-zet/Desktop/Hotel-AI-assistant-RaG/backend/chroma_db"

    db = add_to_chroma(docs, chroma_path)

    print(f"Stored {len(docs)} documents in ChromaDB")