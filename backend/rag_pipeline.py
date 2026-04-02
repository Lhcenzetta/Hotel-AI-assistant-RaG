import json
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma
from config import DATA_DIR, CHROMA_PATH, EMBEDDING_MODEL

def load_json_file(path: Path) -> dict:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def build_hotel_profile_chunk(d: dict) -> list[dict]:
    if not d: return []
    text = (
        f"Hotel: {d['hotel_name']}\n"
        f"Location: {d['location']}\n"
        f"Description: {d['description']}\n"
        f"Amenities: {', '.join(d.get('amenities', []))}\n"
        f"Contact: {json.dumps(d.get('contact', {}), ensure_ascii=False)}"
    )
    return [{"id": "hotel_profile", "source": "hotel_profile", "text": text, "metadata": d}]

def build_faq_chunks(items: list) -> list[dict]:
    chunks = []
    for item in items:
        text = f"FAQ Q: {item['question']}\nFAQ A: {item['answer']}"
        chunks.append({"id": f"faq_{item['faq_id']}", "source": "faqs", "text": text, "metadata": item})
    return chunks

def build_knowledge_chunks(items: list) -> list[dict]:
    chunks = []
    for item in items:
        text = f"Topic: {item['title']}\n{item['content']}"
        chunks.append({"id": item["doc_id"], "source": "knowledge_base", "text": text, "metadata": item})
    return chunks

def build_room_chunks(items: list) -> list[dict]:
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
        chunks.append({"id": item["room_id"], "source": "rooms", "text": text, "metadata": item})
    return chunks

def build_service_chunks(items: list) -> list[dict]:
    chunks = []
    for item in items:
        text = f"Service: {item['service_name']}\nPrice: €{item['price_eur']}\nDescription: {item['description']}"
        chunks.append({"id": item["service_id"], "source": "services", "text": text, "metadata": item})
    return chunks

def make_metadata_safe(metadata: dict) -> dict:
    safe = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, (list, dict)):
            # Special case for Langchain/Chroma: flatten or stringify
            safe[key] = json.dumps(value, ensure_ascii=False)
        else:
            safe[key] = str(value)
    return safe

def get_all_chunks() -> list[dict]:
    all_chunks = []
    
    # Load and build from all JSON files
    hotel_profile = load_json_file(DATA_DIR / "hotel_profile.json")
    if hotel_profile: all_chunks.extend(build_hotel_profile_chunk(hotel_profile))
    
    faqs = load_json_file(DATA_DIR / "large_faqs.json") or load_json_file(DATA_DIR / "faqs.json")
    if faqs: all_chunks.extend(build_faq_chunks(faqs))

    kb = load_json_file(DATA_DIR / "large_knowledge_base.json") or load_json_file(DATA_DIR / "knowledge_base.json")
    if kb: all_chunks.extend(build_knowledge_chunks(kb))

    rooms = load_json_file(DATA_DIR / "large_rooms.json") or load_json_file(DATA_DIR / "rooms.json")
    if rooms: all_chunks.extend(build_room_chunks(rooms))

    services = load_json_file(DATA_DIR / "large_services.json") or load_json_file(DATA_DIR / "services.json")
    if services: all_chunks.extend(build_service_chunks(services))

    return all_chunks

def rebuild_db():
    print("Building chunks...")
    chunks = get_all_chunks()
    
    documents = []
    for chunk in chunks:
        metadata = {"id": chunk["id"], "source": chunk["source"]}
        metadata.update(make_metadata_safe(chunk["metadata"]))
        documents.append(Document(page_content=chunk["text"], metadata=metadata))

    print(f"Creating vector store at {CHROMA_PATH} with {len(documents)} documents...")
    
    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH)
    )
    db.persist()
    print("Database built successfully.")

if __name__ == "__main__":
    rebuild_db()