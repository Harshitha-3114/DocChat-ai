# 📄 DocChat AI

> Chat with your PDF documents using AI — instantly find answers, extract insights, and explore content through conversation.

![Python](https://img.shields.io/badge/Python-3.10%2B-black?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21F?style=flat-square&logoColor=black)
![AI](https://img.shields.io/badge/AI-Llama%203.3%2070B-orange?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-blue?style=flat-square)

🔗 **Live App:** [docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app](https://docchat-ai-skupcjz8kuszknxanrejqg.streamlit.app)

---

## 🎬 Demo

<!-- Drag and drop your screen recording below -->
<!-- Go to GitHub → New Issue → drag your .mp4 → cop

https://github.com/user-attachments/assets/f6602b21-0907-434f-9801-faa12db27aec

y link → paste here → close issue -->



https://github.com/user-attachments/assets/0c54bbc5-7ad4-4b37-a3a5-3c1847072e0f




---

## ✨ Features

- 📂 **Multi-PDF support** — upload up to 5 PDFs, each with its own index
- 🖥 **Side-by-side layout** — PDF viewer and chat panel visible simultaneously
- 🔍 **Semantic search** — retrieves the most relevant chunks for every question
- 📌 **Citation tracking** — every answer shows the exact source section used
- 💡 **Follow-up suggestions** — AI suggests 3 related questions after each answer
- ⬇️ **Export chat** — download full conversation as a `.txt` file
- 🆓 **100% free** — no paid APIs, no subscriptions, no database

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Llama 3.3 70B via Groq API (free tier) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (runs locally) |
| Vector Store | FAISS (in-memory) |
| PDF Parsing | PyMuPDF |
| Orchestration | LangChain |

---

## 🚀 Getting Started

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



**4. Run the app**
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
├── .env               # API keys — never commit this
└── .gitignore
```

---

## 💡 How It Works

```
PDF Upload ──► Text Extraction (PyMuPDF)
           ──► Chunking (1000 chars, 200 overlap)
           ──► Embeddings (HuggingFace all-MiniLM-L6-v2)
           ──► FAISS Vector Index

User Question ──► Embed Question (same model)
              ──► Cosine Similarity Search ──► Top 4 chunks
              ──► Llama 3.3 generates answer + citation
              ──► 3 follow-up suggestions returned
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub (without `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo
3. Under **Advanced settings → Secrets**, paste:
```toml
GROQ_KEY = "your_groq_api_key_here"
```
4. Click **Deploy** — live in ~2 minutes ✅

---


