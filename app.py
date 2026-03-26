import fitz
import streamlit as st
from pipeline import extract_text_from_pdfs, build_vector_store, build_conversation_chain
import base64
from datetime import datetime

st.set_page_config(
    page_title="DocChat AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── Navbar ── */
    .navbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 16px 32px; border-bottom: 2px solid #d4a89a;
        background: #f5ebe6;
    }
    .navbar-logo {
        font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 800;
        color: #1a0a00; display: flex; align-items: center; gap: 10px;
    }
    .navbar-logo span { color: #b91c1c; }
    .navbar-badge {
        background: #fff1ee; color: #7f1d1d; border-radius: 20px;
        padding: 5px 16px; font-size: 12px; border: 1.5px solid #d4a89a;
        font-weight: 600; letter-spacing: 0.03em;
    }

    /* ── PDF tabs ── */
    .pdf-tab-row {
        display: flex; flex-wrap: wrap; gap: 6px;
        padding: 10px 14px; background: #fdf5f3;
        border-bottom: 1px solid #e8c8c0;
    }
    .pdf-tab {
        background: #ffffff; color: #7f1d1d; border-radius: 20px;
        padding: 5px 16px; font-size: 12px; cursor: pointer;
        border: 1.5px solid #d4a89a; transition: all 0.15s;
        white-space: nowrap; max-width: 200px; overflow: hidden;
        text-overflow: ellipsis; font-weight: 600;
    }
    .pdf-tab:hover { background: #fde8e4; border-color: #b91c1c; }
    .pdf-tab.active { background: #b91c1c; color: #fff; border-color: #b91c1c; }

    /* ── Upload zone ── */
    .upload-zone {
        border: 2px dashed #d4a89a; border-radius: 16px; padding: 56px 24px;
        text-align: center; background: #fdf5f3; margin: 24px 20px;
    }

    /* ── Chat header ── */
    .chat-header {
        padding: 14px 20px; border-bottom: 2px solid #e8c8c0;
        font-family: 'Playfair Display', serif; font-weight: 700;
        font-size: 18px; color: #1a0a00; background: #fdf5f3;
    }

    /* ── Citation box ── */
    .citation-box {
        background: #fff1ee; border-left: 3px solid #b91c1c;
        border-radius: 0 8px 8px 0; padding: 8px 14px;
        font-size: 12px; color: #7f1d1d; margin-top: 8px; font-weight: 600;
    }

    /* ── App background ── */
    .stApp { background: #fdf5f3 !important; }
            .stButton > button[kind="secondary"] {
    background: #fff1ee !important; 
    color: #7f1d1d !important;
    border: 1.5px solid #d4a89a !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
}
    section[data-testid="stSidebar"] { display: none; }

    /* ── Chat input ── */
    .stChatInput > div {
        border-radius: 24px !important; border: 2px solid #d4a89a !important;
        background: #ffffff !important;
    }
    .stChatInput > div:focus-within {
        border-color: #b91c1c !important;
        box-shadow: 0 0 0 3px rgba(185,28,28,0.12) !important;
    }
    .stChatInput input { color: #1a0a00 !important; font-weight: 500 !important; }

    /* ── Buttons ── */
    .stButton > button {
        background: #b91c1c !important; color: #ffffff !important;
        border: none !important; border-radius: 10px !important;
        padding: 9px 24px !important; font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.15s !important;
        box-shadow: 0 2px 8px rgba(185,28,28,0.25) !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button:hover {
        background: #991b1b !important;
        box-shadow: 0 4px 14px rgba(185,28,28,0.35) !important;
    }

    /* ── File uploader ── */
    div[data-testid="stFileUploader"] label { color: #1a0a00 !important; font-weight: 700 !important; }
    div[data-testid="stFileUploader"] section {
        background: #ffffff !important; border-color: #d4a89a !important;
        border-radius: 12px !important;
    }

    /* ── Selectbox ── */
    .stSelectbox label { color: #7f1d1d !important; font-size: 12px !important; font-weight: 700 !important; }
    .stSelectbox > div > div {
        background: #ffffff !important; color: #1a0a00 !important;
        border-color: #d4a89a !important; border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* ── Number input ── */
    .stNumberInput label { color: #7f1d1d !important; font-weight: 600 !important; font-size: 13px !important; }
    .stNumberInput input { 
        background: #ffffff !important; color: #1a0a00 !important;
        border-color: #d4a89a !important; border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* ── Chat messages ── */
    .stSpinner { color: #b91c1c !important; }
    .stChatMessage { background: transparent !important; }
    [data-testid="stChatMessageContent"] p {
    color: #1a0a00 !important; font-weight: 500 !important; line-height: 1.75 !important;
}
[data-testid="stChatMessageContent"] li {
    color: #1a0a00 !important; font-weight: 500 !important; line-height: 1.75 !important;
}
[data-testid="stChatMessageContent"] {
    color: #1a0a00 !important;
}

    /* ── Download button ── */
    .stDownloadButton > button {
        background: #fff1ee !important; color: #7f1d1d !important;
        border: 1.5px solid #d4a89a !important; border-radius: 8px !important;
        font-size: 13px !important; padding: 6px 16px !important; font-weight: 700 !important;
    }
    .stDownloadButton > button:hover { background: #fde8e4 !important; border-color: #b91c1c !important; }

    /* ── Divider line between columns ── */
    [data-testid="column"]:first-child {
        border-right: 1px solid #e8c8c0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, val in {
    "chat_history": [],
    "processed": False,
    "pdf_store": {},
    "active_pdf": None,
    "conversation": None,
    "pending_question": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-logo">📄 Doc<span>Chat</span> AI</div>
    <div class="navbar-badge">✦ Llama 3.3 · HuggingFace · Free</div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.1, 0.9], gap="small")

# ── LEFT: PDF viewer ──────────────────────────────────────────────────────────
with left:
    if not st.session_state.processed:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload up to 5 PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="visible",
        )
        if uploaded_files:
            uploaded_files = uploaded_files[:5]
            for f in uploaded_files:
                st.markdown(
                    f"<div style='background:#fff1ee;color:#7f1d1d;border:1.5px solid #d4a89a;"
                    f"border-radius:8px;padding:6px 14px;margin:4px 20px;font-size:13px;"
                    f"display:inline-block;font-weight:700;'>📄 {f.name}</div>",
                    unsafe_allow_html=True
                )
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⚡ Process & Start Chat"):
                    with st.spinner("Indexing PDFs..."):
                        texts = extract_text_from_pdfs(uploaded_files)
                        for f in uploaded_files:
                            f.seek(0)
                            pdf_bytes = f.read()
                            name_f = f.name
                            vs = build_vector_store(texts[name_f])
                            st.session_state.pdf_store[name_f] = {
                                "bytes": pdf_bytes,
                                "vector_store": vs,
                            }
                        first = list(st.session_state.pdf_store.keys())[0]
                        st.session_state.active_pdf = first
                        st.session_state.conversation = build_conversation_chain(
                            st.session_state.pdf_store[first]["vector_store"]
                        )
                        st.session_state.chat_history = []
                        st.session_state.processed = True
                    st.rerun()
        else:
            st.markdown("""
            <div class='upload-zone'>
                <div style='font-size:44px;margin-bottom:14px'>📂</div>
                <div style='font-family:Playfair Display,serif;font-weight:700;color:#1a0a00;font-size:18px;'>
                    Drop up to 5 PDFs here
                </div>
                <div style='margin-top:8px;font-size:13px;color:#7f1d1d;font-weight:500;'>
                    Each PDF gets its own index — switch between them instantly
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # PDF tab row
        names = list(st.session_state.pdf_store.keys())
        tabs_html = "<div class='pdf-tab-row'>"
        for n in names:
            active_class = "active" if n == st.session_state.active_pdf else ""
            short = n if len(n) <= 24 else n[:22] + "…"
            tabs_html += f"<div class='pdf-tab {active_class}' title='{n}'>📄 {short}</div>"
        tabs_html += "</div>"
        st.markdown(tabs_html, unsafe_allow_html=True)

        selected = st.selectbox(
            "Active PDF", options=names,
            index=names.index(st.session_state.active_pdf),
            label_visibility="collapsed",
        )
        if selected != st.session_state.active_pdf:
            st.session_state.active_pdf = selected
            st.session_state.conversation = build_conversation_chain(
                st.session_state.pdf_store[selected]["vector_store"]
            )
            st.session_state.chat_history = []
            st.rerun()

        # Render PDF as image
        pdf_bytes = st.session_state.pdf_store[st.session_state.active_pdf]["bytes"]
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)

        page_num = st.number_input(
            f"Page (1 – {total_pages})",
            min_value=1, max_value=total_pages, value=1, step=1
        ) - 1

        page = doc[page_num]
        mat = fitz.Matrix(1.8, 1.8)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("↩ Upload new PDFs"):
            st.session_state.pdf_store = {}
            st.session_state.active_pdf = None
            st.session_state.conversation = None
            st.session_state.chat_history = []
            st.session_state.processed = False
            st.rerun()

# ── RIGHT: Chat ───────────────────────────────────────────────────────────────
with right:
    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown("<div class='chat-header'>💬 Chat</div>", unsafe_allow_html=True)
    with header_right:
        if st.session_state.chat_history:
            lines = [
                f"DocChat AI — Export\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
                f"PDF: {st.session_state.active_pdf}\n", "=" * 50 + "\n"
            ]
            for msg in st.session_state.chat_history:
                role = "You" if msg["role"] == "user" else "AI"
                lines.append(f"{role}: {msg['content']}\n")
                if msg.get("citation"):
                    lines.append(f"  📌 Source: {msg['citation']}\n")
                lines.append("\n")
            st.download_button(
                label="⬇ Export",
                data="".join(lines),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
            )

    if not st.session_state.processed:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:65vh;text-align:center;gap:14px;'>
            <div style='font-size:48px'>💬</div>
            <div style='font-family:Playfair Display,serif;font-weight:700;font-size:18px;color:#1a0a00;'>
                No PDF loaded yet
            </div>
            <div style='font-size:13px;color:#7f1d1d;font-weight:500;'>
                Upload and process a PDF to start chatting
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        chat_container = st.container(height=720)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style='text-align:center;color:#7f1d1d;font-size:13px;
                            padding:52px 20px;font-weight:600;'>
                    ✅ PDF ready — ask anything about it!
                </div>
                """, unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and msg.get("citation"):
                        st.markdown(
                            f"<div class='citation-box'>📌 <b>Source:</b> {msg['citation']}</div>",
                            unsafe_allow_html=True,
                        )

        # Follow-up suggestions
        last_suggestions = []
        for msg in reversed(st.session_state.chat_history):
            if msg["role"] == "assistant" and msg.get("suggestions"):
                last_suggestions = msg["suggestions"]
                break

        if last_suggestions:
            cols = st.columns(len(last_suggestions))
            for i, suggestion in enumerate(last_suggestions):
                with cols[i]:
                    if st.button(f"💡 {suggestion}", key=f"sug_{suggestion[:30]}"):
                        st.session_state.pending_question = suggestion
                        st.rerun()

        user_question = st.chat_input("Ask anything about your PDF...")

        if st.session_state.pending_question:
            user_question = st.session_state.pending_question
            st.session_state.pending_question = None

        if user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.spinner("Thinking..."):
                result = st.session_state.conversation(
                    user_question, st.session_state.chat_history,
                )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "citation": result.get("citation", ""),
                "suggestions": result.get("suggestions", []),
            })
            st.rerun()

















