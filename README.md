# 📄 DocChat AI

> Chat with your PDF documents using AI — instantly find answers, extract insights, and explore content through conversation.

🔗 **Live Demo:** [docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app](https://docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app)

---

## 📽 Demo Video

<!-- Upload your demo video below — replace the placeholder -->

https://github.com/YOUR_USERNAME/chat-with-pdf/assets/YOUR_ASSET_ID/YOUR_VIDEO_FILE.mp4

> _To add your video: go to your GitHub repo → open any Issue → drag and drop your .mp4 into the comment box → copy the generated link → paste it above replacing the placeholder. Then close the issue without submitting._

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

**3. Add your API keys**

Create a `.streamlit/secrets.toml` file:
```toml
GROQ_KEY       = "your_groq_api_key"
GEMINI_API_KEY = "your_gemini_api_key"
```

Get free keys:
- Groq → [console.groq.com](https://console.groq.com)
- Gemini → [aistudio.google.com](https://aistudio.google.com)

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
└── .streamlit/
    └── secrets.toml   # API keys — never commit this file
```

---

## 💡 How It Works

```
PDF Upload → Text Extraction (PyMuPDF)
          → Chunking (1000 chars, 200 overlap)
          → Embeddings (HuggingFace all-MiniLM-L6-v2)
          → FAISS Vector Index

User Question → Embed Question (same model)
             → Cosine Similarity Search → Top 4 chunks retrieved
             → Llama 3.3 generates answer with citation
             → 3 follow-up suggestions returned
```

---

## 📌 Resume Bullet Points

- Built an end-to-end RAG pipeline with semantic chunking, HuggingFace embeddings, and FAISS vector similarity search
- Integrated Llama 3.3 70B via Groq API for grounded answer generation with automatic source citation and follow-up suggestions
- Deployed as a production web app on Streamlit Cloud at zero infrastructure cost — live at [docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app](https://docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app)

---

## 📜 License

MIT — free to use, modify, and distribute.
