# 📄 DocChat AI

> Chat with your PDF documents using AI — instantly find answers, extract insights, and explore content through conversation.

🔗 **Live Demo:** [docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app](https://docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app)

---

## 📽 Demo Video



https://github.com/YOUR_USERNAME/chat-with-pdf/assets/YOUR_ASSET_ID/YOUR_VIDEO_FILE.mp4


---

## ✨ Features

- **Multi-PDF support** — upload up to 5 PDFs, each with its own index
- **Side-by-side layout** — PDF viewer and chat panel visible simultaneously
- **Smart retrieval** — finds the most relevant chunks using semantic search
- **Citation tracking** — every answer shows the exact source section used
- **Follow-up suggestions** — AI suggests 3 related questions after each answer
- **Export chat** — download your full conversation as a `.txt` file
- **100% free** — no paid APIs, no subscriptions, no database required

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Llama 3.3 70B via Groq API (free tier) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (runs locally) |
| Vector Store | FAISS (in-memory, no external DB) |
| PDF Parsing | PyMuPDF |
| Orchestration | LangChain |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/chat-with-pdf.git
cd chat-with-pdf
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file in the project root:
```
GROQ_KEY=your_groq_api_key_here
```

Get a free Groq key → [console.groq.com](https://console.groq.com)



**4. Run**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 📁 Project Structure

```
chat-with-pdf/
├── app.py             # Streamlit UI — layout, styling, chat logic
├── pipeline.py        # RAG core — chunking, embeddings, retrieval, LLM
├── requirements.txt
├── .env               # API key — never commit this
└── .gitignore
```

---

## 💡 How It Works

```
PDF Upload → Text Extraction (PyMuPDF)
          → Chunking (1000 chars, 200 overlap)
          → Embeddings (HuggingFace all-MiniLM-L6-v2, runs locally)
          → FAISS Vector Index

User Question → Embed Question (same model)
             → Cosine Similarity Search → Top 4 chunks retrieved
             → Llama 3.3 70B generates answer with citation
             → 3 follow-up suggestions returned
```

---

## ☁️ Deploying to Streamlit Cloud

1. Push code to GitHub (without `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo
3. Under **Advanced settings → Secrets**, add:
```toml
GROQ_KEY = "your_groq_api_key_here"
```
4. Click **Deploy** — live in ~2 minutes

