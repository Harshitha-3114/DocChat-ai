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
            iframe { border-radius: 8px; }
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .navbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 28px; border-bottom: 1px solid #e8d5b0;
        background: #f5ebe0;
    }
    .navbar-logo {
        font-family: 'Lora', serif; font-size: 20px; font-weight: 600;
        color: #1a1a1a; display: flex; align-items: center; gap: 8px;
    }
    .navbar-logo span { color: #d97706; }
    .navbar-right { display: flex; align-items: center; gap: 10px; }
    .navbar-badge {
        background: #fff8ed; color: #92400e; border-radius: 20px;
        padding: 4px 14px; font-size: 12px; border: 1px solid #e8d5b0;
        font-weight: 500;
    }

    .pdf-tab-row {
        display: flex; flex-wrap: wrap; gap: 6px;
        padding: 10px 14px; background: #fdf8f2;
        border-bottom: 1px solid #e8d5b0;
    }
    .pdf-tab {
        background: #ffffff; color: #1a1a1a; border-radius: 20px;
        padding: 5px 14px; font-size: 12px; cursor: pointer;
        border: 1.5px solid #d4a96a; transition: all 0.15s;
        white-space: nowrap; max-width: 180px; overflow: hidden;
        text-overflow: ellipsis; font-weight: 500;
    }
    .pdf-tab:hover { background: #fff3e0; border-color: #d97706; }
    .pdf-tab.active { background: #d97706; color: #fff; border-color: #d97706; font-weight: 700; }

    .upload-zone {
        border: 2px dashed #d4a96a; border-radius: 16px; padding: 52px 24px;
        text-align: center; background: #fdf8f2; margin: 24px 20px;
    }

    .chat-header {
        padding: 13px 20px; border-bottom: 1px solid #e8d5b0;
        font-family: 'Lora', serif; font-weight: 600;
        font-size: 16px; color: #1a1a1a; background: #fdf8f2;
        display: flex; justify-content: space-between; align-items: center;
    }

    .citation-box {
        background: #fff8ed; border-left: 3px solid #d97706;
        border-radius: 0 8px 8px 0; padding: 7px 12px;
        font-size: 12px; color: #92400e; margin-top: 8px; font-weight: 500;
    }

    .stApp { background: #fdf8f2 !important; }
    section[data-testid="stSidebar"] { display: none; }

    .stChatInput > div {
        border-radius: 24px !important; border: 1.5px solid #d4a96a !important;
        background: #ffffff !important;
    }
    .stChatInput > div:focus-within { border-color: #d97706 !important; box-shadow: 0 0 0 3px #fde68a55 !important; }
    .stChatInput input { color: #1a1a1a !important; font-weight: 500 !important; }

    .stButton > button {
        background: #d97706 !important; color: #ffffff !important;
        border: none !important; border-radius: 10px !important;
        padding: 8px 22px !important; font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.15s !important;
        box-shadow: 0 2px 6px rgba(217,119,6,0.3) !important;
    }
    .stButton > button:hover { background: #b45309 !important; }

    div[data-testid="stFileUploader"] label { color: #1a1a1a !important; font-weight: 600 !important; }
    div[data-testid="stFileUploader"] section { background: #ffffff !important; border-color: #d4a96a !important; border-radius: 10px !important; }

    .stSelectbox label { color: #1a1a1a !important; font-size: 12px !important; font-weight: 600 !important; }
    .stSelectbox > div > div {
        background: #ffffff !important; color: #1a1a1a !important;
        border-color: #d4a96a !important; border-radius: 8px !important;
        font-weight: 500 !important;
    }

    .stSpinner { color: #d97706 !important; }
    .stChatMessage { background: transparent !important; }
    [data-testid="stChatMessageContent"] p { color: #1a1a1a !important; font-weight: 400 !important; line-height: 1.7 !important; }

    .stDownloadButton > button {
        background: #fff8ed !important; color: #92400e !important;
        border: 1.5px solid #d4a96a !important; border-radius: 8px !important;
        font-size: 13px !important; padding: 6px 14px !important; font-weight: 700 !important;
    }
    .stDownloadButton > button:hover { background: #fde68a !important; }
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
    <div class="navbar-right">
        <div class="navbar-badge">Gemini · Llama 3.3 · Free ✨</div>
    </div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.1, 0.9], gap="small")

# ── LEFT: PDF viewer ──────────────────────────────────────────────────────────
with left:
    if not st.session_state.processed:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
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
                    f"<div style='background:#fff8ed;color:#92400e;border:1.5px solid #d4a96a;"
                    f"border-radius:6px;padding:5px 12px;margin:4px 20px;font-size:13px;display:inline-block;font-weight:600;'>"
                    f"📄 {f.name}</div>",
                    unsafe_allow_html=True
                )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
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
                <div style='font-size:40px;margin-bottom:12px'>📂</div>
                <div style='font-family:Lora,serif;font-weight:600;color:#1a1a1a;font-size:16px'>
                    Drop up to 5 PDFs here
                </div>
                <div style='margin-top:6px;font-size:13px;color:#92400e;font-weight:500'>
                    Each PDF gets its own index — switch between them instantly
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        names = list(st.session_state.pdf_store.keys())
        tabs_html = "<div class='pdf-tab-row'>"
        for n in names:
            active_class = "active" if n == st.session_state.active_pdf else ""
            short = n if len(n) <= 22 else n[:20] + "…"
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

        import fitz
        pdf_bytes = st.session_state.pdf_store[st.session_state.active_pdf]["bytes"]
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        page_num = st.number_input(
            f"Page (1–{total_pages})", min_value=1, max_value=total_pages, value=1, step=1) - 1
        page = doc[page_num]
        mat = fitz.Matrix(1.8, 1.8)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
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
            lines = [f"DocChat AI — Export\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
                     f"PDF: {st.session_state.active_pdf}\n", "=" * 50 + "\n"]
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
                    justify-content:center;height:65vh;text-align:center;gap:12px;'>
            <div style='font-size:44px'>💬</div>
            <div style='font-family:Lora,serif;font-weight:600;font-size:16px;color:#1a1a1a'>
                No PDF loaded yet
            </div>
            <div style='font-size:13px;color:#92400e;font-weight:500'>Upload and process PDFs to start chatting</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        chat_container = st.container(height=580)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style='text-align:center;color:#92400e;font-size:13px;padding:48px 20px;font-weight:500'>
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