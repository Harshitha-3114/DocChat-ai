import os
import fitz
import json
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
# GROQ_KEY = os.getenv("GROQ_KEY", "")
import streamlit as st
try:
    GROQ_KEY = st.secrets.get("GROQ_KEY") or os.getenv("GROQ_KEY", "")
except Exception:
    GROQ_KEY = os.getenv("GROQ_KEY", "YOUR_GROQ_KEY")



def extract_text_from_pdfs(pdf_files):
    """Returns dict: {filename: extracted_text}"""
    pdf_texts = {}
    for pdf in pdf_files:
        pdf.seek(0)
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        pdf_texts[pdf.name] = text
    return pdf_texts


def build_vector_store(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    # Runs locally — no API calls, no rate limits, free & unlimited
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    store = FAISS.from_texts(chunks, embedding=embeddings)
    return store


def build_conversation_chain(vector_store):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=GROQ_KEY,
        temperature=0.3,
    )

    answer_prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template="""You are a helpful assistant. Use the context below to answer the question.
If you don't know the answer from the context, say so honestly.
After your answer, on a new line write CITATION: followed by one short sentence saying which section/part of the document you used.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""
    )

    followup_prompt = PromptTemplate(
        input_variables=["context", "question", "answer"],
        template="""Based on the document excerpt and Q&A below, suggest exactly 3 short follow-up questions.
Return ONLY a raw JSON array of 3 strings. No markdown, no backticks, no explanation.
Example output: ["What is X?", "How does Y work?", "Why is Z important?"]

Context: {context}
Question: {question}
Answer: {answer}

JSON array:"""
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    def chain(question, chat_history):
        docs = retriever.invoke(question)
        context = "\n\n".join([d.page_content for d in docs])

        # Build history string (cap at last 10 messages to avoid context overflow)
        msgs = [m for m in chat_history if m["role"] in ("user", "assistant")]
        msgs = msgs[-10:]
        history_str = ""
        for i in range(0, len(msgs) - 1, 2):
            if msgs[i]["role"] == "user" and i + 1 < len(msgs):
                history_str += f"Human: {msgs[i]['content']}\nAI: {msgs[i+1]['content']}\n"

        # Main answer
        raw_answer = StrOutputParser().invoke(
            llm.invoke(answer_prompt.format(
                context=context, chat_history=history_str, question=question
            ))
        )

        # Split citation
        citation = ""
        if "CITATION:" in raw_answer:
            parts = raw_answer.split("CITATION:")
            answer = parts[0].strip()
            citation = parts[1].strip()
        else:
            answer = raw_answer.strip()

        # Follow-up suggestions
        suggestions = []
        try:
            raw_fu = StrOutputParser().invoke(
                llm.invoke(followup_prompt.format(
                    context=context[:1500], question=question, answer=answer[:500]
                ))
            ).strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_fu)
            if isinstance(parsed, list):
                suggestions = [s for s in parsed if isinstance(s, str)][:3]
        except Exception:
            suggestions = []

        return {
            "answer": answer,
            "citation": citation,
            "suggestions": suggestions,
            "source_chunks": [d.page_content[:300] for d in docs],
        }

    return chain