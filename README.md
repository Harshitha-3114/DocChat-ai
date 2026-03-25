# 📄 Chat with PDF — RAG App

A full RAG (Retrieval-Augmented Generation) pipeline that lets you upload PDFs and chat with them using Google Gemini's free API.

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: Google Gemini 1.5 Flash (free tier)
- **Embeddings**: Gemini embedding-001
- **Vector Store**: FAISS (local, no external DB needed)
- **PDF Parsing**: PyMuPDF
- **Orchestration**: LangChain

## Setup

### 1. Clone and install
```bash
git clone https://github.com/yourusername/chat-with-pdf
cd chat-with-pdf
pip install -r requirements.txt
```

### 2. Get a free Gemini API key
Go to https://aistudio.google.com → Get API Key (free, no credit card)

### 3. Add your key to .env
```
GEMINI_API_KEY=your_key_here
```

### 4. Run
```bash
streamlit run app.py
```

## How it works
1. **Ingest**: PDFs are parsed with PyMuPDF and split into 1000-char chunks (200 char overlap)
2. **Embed**: Each chunk is embedded using Gemini's embedding model into a 768-dim vector
3. **Index**: Vectors are stored in a local FAISS index (in-memory)
4. **Query**: User question is embedded → cosine similarity search → top 4 chunks retrieved
5. **Generate**: Gemini 1.5 Flash answers using retrieved chunks as context
6. **Memory**: LangChain ConversationBufferMemory maintains multi-turn chat history

## Features
- Multi-PDF support
- Conversational memory (follow-up questions work)
- Source chunk transparency (see exactly what context was used)
- Fully local vector store — no Pinecone/Weaviate needed

## Resume talking points
- Implemented end-to-end RAG pipeline with semantic chunking and vector similarity search
- Reduced hallucination by grounding LLM responses in retrieved document context
- Built conversational memory layer enabling multi-turn Q&A over private documents
- Deployed with Streamlit; zero infrastructure cost using FAISS in-memory vector store
