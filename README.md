# Atlas Breeze Hotel & Spa - AI Concierge Assistant

A premium, RAG-powered (Retrieval-Augmented Generation) AI concierge system for the Atlas Breeze Hotel & Spa. This project combines a modern, luxurious frontend with a robust FastAPI backend to provide guests with real-time, accurate information about hotel services, rooms, and local recommendations.

![Atlas Breeze Hotel Hero](frontend/assets/hero.png)

## 🌟 Key Features

- **AI Concierge**: A context-aware chatbot powered by Google Gemini and RAG, trained on hotel-specific data (rooms, services, FAQs).
- **Dynamic Room Showcase**: Beautifully rendered room cards with details on capacity, pricing, and amenities.
- **Exclusive Services**: Interactive display of hotel services like spa treatments and dining options.
- **Premium UI/UX**: Responsive design with a luxury aesthetic, featuring glassmorphism, smooth animations, and a curated color palette.
- **Real-time Retrieval**: Uses ChromaDB and HuggingFace embeddings to retrieve the most relevant information for guest queries.

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Orchestration**: [LangChain](https://www.langchain.com/)
- **LLM**: [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)

### Frontend
- **Structure**: HTML5 Semantic Elements
- **Styling**: Vanilla CSS3 (Custom Design System)
- **Logic**: Vanilla JavaScript (ES6+)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- A Google API Key (for Gemini)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lhcenzetta/Hotel-AI-assistant-RaG.git
   cd Hotel-AI-assistant-RaG
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the Project

1. **Build the Vector Database**:
   Run the RAG pipeline to process hotel data and populate the vector store.
   ```bash
   python backend/rag_pipeline.py
   ```

2. **Start the Backend API**:
   ```bash
   python backend/main.py
   ```
   The API will be available at `http://localhost:8000`. You can view the automated docs at `http://localhost:8000/docs`.

3. **Launch the Frontend**:
   Simply open `frontend/index.html` in your web browser.

## 📁 Project Structure

```text
/
├── backend/                # FastAPI application logic
│   ├── chromadb/           # Persistent vector store (gitignored)
│   ├── main.py             # API endpoints and entry point
│   ├── rag_pipeline.py     # Data ingestion and vector store building
│   ├── retriever.py        # Information retrieval logic
│   ├── generator.py        # Response generation via Gemini
│   └── config.py           # Configuration and environment loading
├── data/                   # Hotel knowledge base (JSON files)
│   ├── rooms.json          # Room types and pricing
│   ├── services.json       # Spa and dining services
│   └── faqs.json           # Common guest questions
├── frontend/               # Web interface
│   ├── index.html          # Main landing page
│   ├── styles.css          # Premium styling
│   └── app.js              # Frontend logic and API integration
├── .env                    # Secret keys (not tracked by git)
└── requirements.txt        # Python dependencies
```

## 📝 License

This project is for demonstration purposes. All rights reserved.

---
*Created with ❤️ for the Atlas Breeze Hotel & Spa.*
