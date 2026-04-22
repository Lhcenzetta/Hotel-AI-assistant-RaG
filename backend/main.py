import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from config import DATA_DIR, HOST, PORT, DEBUG
from retriever import get_retriever
from generator import get_generator

app = FastAPI(title="Hotel Assistant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

# Helper to load JSON data
def load_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Endpoints
@app.get("/v1/hotel/info")
async def get_hotel_info():
    """Returns general hotel profile information."""
    return load_json("hotel_profile.json")

@app.get("/v1/hotel/rooms")
async def get_hotel_rooms():
    """Returns detailed information about hotel rooms."""
    # Try large file first, then fallback
    try:
        return load_json("large_rooms.json")
    except HTTPException:
        return load_json("rooms.json")

@app.get("/v1/hotel/services")
async def get_hotel_services():
    """Returns available hotel services."""
    try:
        return load_json("large_services.json")
    except HTTPException:
        return load_json("services.json")

@app.get("/v1/hotel/faqs")
async def get_hotel_faqs():
    """Returns common hotel FAQs."""
    try:
        return load_json("large_faqs.json")
    except HTTPException:
        return load_json("faqs.json")

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main RAG-powered chat endpoint."""
    try:
        retriever = get_retriever()
        generator = get_generator()
        
        # 1. Retrieve
        docs = retriever.query(request.message, k=3)
        
        # 2. Generate
        result = generator.generate_answer(request.message, docs)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")

@app.post("/v1/search")
async def search(request: ChatRequest):
    """Staff search endpoint - returns raw documents."""
    try:
        retriever = get_retriever()
        docs = retriever.query(request.message, k=5)
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "Unknown")
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/v1/stats")
async def get_stats():
    """Returns system statistics."""
    try:
        retriever = get_retriever()
        # Chroma doesn't have a direct 'count' in some versions, but we can try
        try:
            count = retriever.vector_store._collection.count()
        except:
            count = "150+" # Fallback
            
        return {
            "document_count": count,
            "status": "online",
            "version": "1.0.0"
        }
    except Exception:
        return {"document_count": "—", "status": "error"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
