import os
import sys
import json
import subprocess
import streamlit as st

# Add src to sys.path
sys.path.append("src")
from rag import OrganicRAG
from utils import format_pages

# 1. Page Configuration
st.set_page_config(
    page_title="BioLeaf AI | Organic Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Aesthetics & CSS (Glassmorphic Emerald Theme)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E2E8F0;
}

/* Background gradient */
.stApp {
    background: radial-gradient(circle at 15% 15%, #0D2216 0%, #08130C 50%, #040906 100%);
    background-attachment: fixed;
}

/* Hero Header Card */
.hero-container {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 20px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 1.02rem;
    margin-top: 6px;
    margin-bottom: 12px;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
}
.badge-emerald {
    background: rgba(16, 185, 129, 0.2);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
.badge-amber {
    background: rgba(245, 158, 11, 0.2);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Sidebar styles */
[data-testid="stSidebar"] {
    background: rgba(10, 19, 14, 0.88) !important;
    border-right: 1px solid rgba(16, 185, 129, 0.18);
    backdrop-filter: blur(18px);
}

/* Metric / Stat box */
.stat-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    margin-bottom: 10px;
}
.stat-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: #10B981;
}
.stat-lbl {
    font-size: 0.78rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Starter Prompts Box */
.prompts-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #34D399;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* Custom styled buttons */
div.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.08);
    color: #E2E8F0;
    transition: all 0.25s ease-in-out;
}
div.stButton > button:hover {
    border-color: #10B981;
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: #FFFFFF;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

/* Citation card */
.source-card {
    background: rgba(18, 30, 23, 0.6);
    border-left: 3px solid #10B981;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# 3. Load RAG Instance
@st.cache_resource
def get_rag():
    return OrganicRAG()

rag = get_rag()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Helper to rebuild vector DB
def rebuild_vector_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rebuild_script = os.path.join(base_dir, "rebuild_db.py")
    venv_py = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
    py_exec = venv_py if os.path.exists(venv_py) else sys.executable
    res = subprocess.run([py_exec, rebuild_script], capture_output=True, text=True)
    rag.reload_db()
    return res.stdout



# 4. Sidebar Workspace
with st.sidebar:
    st.markdown("### 🌱 BioLeaf Control Panel")
    st.caption("AI-Powered Organic Farming Intelligence")

    st.markdown("---")

    # Knowledge Base Stats
    stats = rag.get_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-val">{stats['total_chunks']}</div>
                <div class="stat-lbl">Indexed Chunks</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col2:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        pdf_count = len([f for f in os.listdir(data_dir) if f.endswith(".pdf")]) if os.path.exists(data_dir) else 0
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-val">{pdf_count}</div>
                <div class="stat-lbl">PDF Manuals</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Dynamic RAG Controls
    st.markdown("#### ⚙️ Retrieval Parameters")
    top_k = st.slider("Source Chunks (Top K)", min_value=1, max_value=10, value=5, help="Number of document passages to retrieve")
    temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.1, step=0.05, help="Lower = strict facts, Higher = creative")

    st.markdown("---")

    # Document Uploader & Indexer
    st.markdown("#### 📄 Document Manager")
    uploaded_file = st.file_uploader("Upload New Organic Farming PDF", type=["pdf"])
    if uploaded_file is not None:
        save_path = os.path.join(data_dir, uploaded_file.name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded `{uploaded_file.name}`!")

    if st.button("🔄 Rebuild Vector Database", use_container_width=True):
        with st.spinner("Processing documents & re-indexing ChromaDB..."):
            log_output = rebuild_vector_db()
            st.success("Vector DB successfully rebuilt!")
            st.rerun()

    st.markdown("---")

    # Chat Export & Reset
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.session_state.messages:
            chat_md = "# BioLeaf AI Chat History\n\n"
            for msg in st.session_state.messages:
                role = "User" if msg["role"] == "user" else "BioLeaf Assistant"
                chat_md += f"### {role}\n{msg['content']}\n\n"
            st.download_button(
                "📥 Export",
                data=chat_md,
                file_name="bioleaf_chat_history.md",
                mime="text/markdown",
                use_container_width=True
            )


# 5. Hero Banner Header
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">
            <span>🌱 BioLeaf Organic Farming AI</span>
        </div>
        <div class="hero-subtitle">
            Instant expert answers powered by Retrieval-Augmented Generation & Gemini 3.6 Flash.
        </div>
        <div>
            <span class="badge badge-emerald">🟢 RAG Active</span>
            <span class="badge badge-emerald">📚 Chroma Vector DB</span>
            <span class="badge badge-amber">⚡ Gemini 3.6 Flash</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 6. Quick Starter Chips (if no conversation yet)
if not st.session_state.messages:
    st.markdown('<div class="prompts-title">💡 Starter Questions & Frequent Topics:</div>', unsafe_allow_html=True)
    chip_cols = st.columns(2)

    starter_prompts = [
        ("🌾 How do I make high-quality organic compost?", "Compost preparation steps"),
        ("🐛 What are effective natural pest control methods?", "Pest management strategies"),
        ("🧪 How to improve soil fertility without chemicals?", "Soil enrichment techniques"),
        ("📜 What are the key rules for organic certification?", "Certification requirements")
    ]

    for idx, (prompt_text, subtitle) in enumerate(starter_prompts):
        col = chip_cols[idx % 2]
        if col.button(prompt_text, key=f"starter_{idx}", use_container_width=True):
            st.session_state.pending_prompt = prompt_text
            st.rerun()


# 7. Render Conversation History
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🧑‍🌾" if msg["role"] == "user" else "🌱"):
        st.markdown(msg["content"])

        # Show sources for assistant response
        if msg["role"] == "assistant" and msg.get("sources"):
            pages_str = format_pages(msg.get("pages", []))
            with st.expander(f"📚 Retrieved Sources ({pages_str})", expanded=False):
                for src_idx, src in enumerate(msg["sources"], 1):
                    conf = src.get("confidence", 85)
                    conf_class = "conf-high" if conf >= 75 else "conf-med"
                    file_name = src.get("file", "Manual")

                    st.markdown(
                        f"""<div class="source-card">
                            <b>Chunk {src_idx}</b> | File: <code>{file_name}</code> | Page {src['page']} | Match Confidence: <span class="{conf_class}">{conf}%</span>
                        </div>""",
                        unsafe_allow_html=True
                    )
                    st.caption(src["text"])

        # Show follow-up question chips
        if msg["role"] == "assistant" and msg.get("follow_ups"):
            st.markdown("**Suggested Follow-ups:**")
            f_cols = st.columns(len(msg["follow_ups"]))
            for f_idx, f_question in enumerate(msg["follow_ups"]):
                if f_cols[f_idx].button(f"🔍 {f_question}", key=f"fu_{msg_idx}_{f_idx}"):
                    st.session_state.pending_prompt = f_question
                    st.rerun()


# 8. Handle User Input
user_input = st.chat_input("Ask any question about organic farming, crops, soil health...")

# Override input if pending prompt exists from a clicked chip button
if st.session_state.pending_prompt:
    user_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🌾"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant", avatar="🌱"):
        with st.spinner("Searching organic farming knowledge base..."):
            try:
                res = rag.ask(user_input, top_k=top_k, temperature=temperature)
                answer = res["answer"]
                sources = res.get("sources", [])
                pages = res.get("pages", [])
                follow_ups = res.get("follow_ups", [])

                st.markdown(answer)

                if sources:
                    pages_str = format_pages(pages)
                    with st.expander(f"📚 Retrieved Sources ({pages_str})", expanded=False):
                        for src_idx, src in enumerate(sources, 1):
                            conf = src.get("confidence", 85)
                            conf_class = "conf-high" if conf >= 75 else "conf-med"
                            file_name = src.get("file", "Manual")
                            st.markdown(
                                f"""<div class="source-card">
                                    <b>Chunk {src_idx}</b> | File: <code>{file_name}</code> | Page {src['page']} | Match Confidence: <span class="{conf_class}">{conf}%</span>
                                </div>""",
                                unsafe_allow_html=True
                            )
                            st.caption(src["text"])

                # Store assistant response in session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "pages": pages,
                    "follow_ups": follow_ups
                })

                if follow_ups:
                    st.rerun()

            except Exception as e:
                err_msg = f"An error occurred while processing your request: `{str(e)}`"
                st.error(err_msg)