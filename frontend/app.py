import os

import requests
import streamlit as st

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")
PAGE_OPTIONS = ["Dashboard", "Documents", "Chunks", "Chat", "Chat Stream", "Search"]
PAGE_ICONS = {
    "Dashboard": "🏠",
    "Documents": "📄",
    "Chunks": "🧩",
    "Chat": "💬",
    "Chat Stream": "▶️",
    "Search": "🔎",
}

st.set_page_config(
    page_title="Enterprise RAG Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu,
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppToolbar"],
    footer,
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    .stDeployButton,
    .stAppDeployButton,
    button[title="Deploy"],
    button[aria-label="Deploy"],
    a[title="Deploy"] {
        display: none;
    }

    :root {
        --brand-navy: #0f172a;
        --brand-blue: #2563eb;
        --brand-blue-light: #eff6ff;
        --border-color: #e2e8f0;
        --text-muted: #64748b;
        --surface: #ffffff;
        --surface-alt: #f8fafc;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: var(--surface-alt);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 0;
        padding-bottom: 3rem;
    }

    h1 {
        font-weight: 700;
        color: var(--brand-navy);
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }

    h2, h3 {
        color: var(--brand-navy);
        letter-spacing: -0.01em;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.6rem;
    }
    div.stButton {
        margin-top: 0.15rem;
    }

    /* ---------- Top header / nav bar ---------- */
    .top-header-wrap {
        position: sticky;
        top: 0;
        z-index: 999;
        background: var(--surface);
        border-bottom: 1px solid var(--border-color);
        margin: 0 -1rem 1.5rem -1rem;
        padding: 0.65rem 1rem 0 1rem;
        box-shadow: 0 1px 8px rgba(15, 23, 42, 0.04);
    }
    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--brand-navy);
        letter-spacing: -0.01em;
        padding-bottom: 0.5rem;
    }
    .brand-row .brand-mark {
        font-size: 1.3rem;
    }
    .top-nav .stButton > button {
        border: 1px solid transparent;
        background: transparent;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 0.88rem;
        border-radius: 8px 8px 0 0;
        min-height: 2.35rem;
        padding: 0 0.9rem;
        transition: background 0.15s ease, color 0.15s ease;
    }
    .top-nav .stButton > button:hover {
        background: var(--brand-blue-light);
        color: var(--brand-blue);
    }
    .top-nav-active .stButton > button {
        color: var(--brand-blue);
        border-bottom: 2px solid var(--brand-blue);
        background: var(--brand-blue-light);
    }

    /* ---------- Buttons (general) ---------- */
    .stButton > button {
        border-radius: 8px;
        min-height: 2.5rem;
        font-weight: 600;
    }
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button {
        background: var(--brand-blue);
        border: none;
    }

    /* ---------- Native bordered containers (cards / rows) ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border-color: var(--border-color) !important;
        background: var(--surface);
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        border-color: #cbd5e1 !important;
    }
    .card-icon {
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
        display: block;
    }
    .card-title {
        font-weight: 600;
        font-size: 1.02rem;
        color: var(--brand-navy);
        margin: 0 0 0.15rem 0;
    }
    .card-desc {
        font-size: 0.87rem;
        color: var(--text-muted);
        margin: 0 0 0.6rem 0;
        line-height: 1.4;
    }

    .section-divider {
        margin: 1.1rem 0 1.1rem 0;
        border: none;
        border-top: 1px solid var(--border-color);
    }

    .page-eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--brand-blue);
        margin-bottom: 0.3rem;
    }

    .empty-state {
        padding: 1.75rem 1.5rem;
        border: 1px dashed var(--border-color);
        border-radius: 10px;
        background: var(--surface);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    .doc-name {
        font-weight: 600;
        color: var(--brand-navy);
        margin: 0;
    }
    .doc-id {
        color: var(--text-muted);
        font-size: 0.8rem;
    }

    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.6rem 0.75rem;
    }
    div[data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 10px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------- Chat UI ---------- */
    .chat-thread-marker + div[data-testid="stVerticalBlockBorderWrapper"] {
        height: 480px;
        overflow-y: auto;
        padding: 0.25rem 0.4rem;
    }
    .chat-thread-marker,
    .session-strip-marker {
        display: none;
    }
    .session-strip-marker + div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.7rem;
    }
    div[data-testid="stChatMessage"] {
        background: transparent;
        padding: 0.35rem 0;
        max-width: 78%;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        margin-left: auto;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--brand-blue);
        color: #ffffff;
        border-radius: 14px 14px 3px 14px;
        padding: 0.6rem 0.85rem;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p {
        color: #ffffff;
    }
    div[data-testid="stChatMessage"]:not(:has(div[data-testid="stChatMessageAvatarUser"])) [data-testid="stChatMessageContent"] {
        background: var(--surface-alt);
        border: 1px solid var(--border-color);
        border-radius: 14px 14px 14px 3px;
        padding: 0.6rem 0.85rem;
    }
    .session-strip {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.9rem;
    }
    .session-strip-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 0.2rem;
    }
    .composer-wrap {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 0.85rem 0.95rem 0.6rem 0.95rem;
    }
    .streaming-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--brand-blue);
        background: var(--brand-blue-light);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        margin-bottom: 0.5rem;
    }
    .sources-card {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-top: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def set_page(page):
    st.session_state["page"] = page
    st.rerun()


def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(subtitle)
    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)


def build_query_payload(query, top_k, document_id, filename, session_id=None):
    payload = {"query": query, "top_k": int(top_k)}
    if session_id:
        payload["session_id"] = session_id
    if document_id.strip():
        payload["document_id"] = document_id.strip()
    if filename.strip():
        payload["filename"] = filename.strip()
    return payload


def format_number(value):
    if value is None:
        return "N/A"
    return f"{float(value):.4f}"


def citation_title(citation, index):
    filename = citation.get("filename") or "Unknown file"
    chunk_index = citation.get("chunk_index", "N/A")
    distance = citation.get("distance")
    score = 1 - float(distance) if distance is not None else None
    return f"{index}. {filename} · Chunk {chunk_index} · Match {format_number(score)}"


def safe_request(method, url, **kwargs):
    """Wrap requests calls so network/timeout errors surface as UI messages
    instead of uncaught exceptions."""
    try:
        response = requests.request(method, url, **kwargs)
        return response, None
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the backend. Is the API running?"
    except requests.exceptions.Timeout:
        return None, "The request timed out. The backend may be under heavy load."
    except requests.exceptions.RequestException as exc:
        return None, f"Request failed: {exc}"


def getChatSessions():
    response, error = safe_request("GET", f"{API_URL}/chat/sessions", timeout=60)

    if error:
        return None, error
    if not response.ok:
        return None, f"Failed to load sessions ({response.status_code}): {response.text}"

    return response.json(), None


def getChatSessionMessages(sessionId):
    response, error = safe_request("GET", f"{API_URL}/chat/sessions/{sessionId}/messages", timeout=60)

    if error:
        return None, error
    if not response.ok:
        return None, f"Failed to load messages ({response.status_code}): {response.text}"

    return response.json(), None


def createChatSession():
    response, error = safe_request("POST", f"{API_URL}/chat/sessions", timeout=60)

    if error:
        return None, error
    if not response.ok:
        return None, f"Failed to create session ({response.status_code}): {response.text}"

    return response.json(), None


def sendChatMessage(query, sessionId, topK, documentId, filename):
    payload = build_query_payload(query, topK, documentId, filename, sessionId)
    response, error = safe_request("POST", f"{API_URL}/chat", json=payload, timeout=180)

    if error:
        return None, error
    if not response.ok:
        return None, f"Request failed ({response.status_code}): {response.text}"

    return response.json(), None


def render_empty_state(message):
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def render_dashboard_card(icon, title, description, target_page, button_label):
    with st.container(border=True):
        st.markdown(
            f"""
            <span class="card-icon">{icon}</span>
            <p class="card-title">{title}</p>
            <p class="card-desc">{description}</p>
            """,
            unsafe_allow_html=True,
        )
        if st.button(button_label, key=f"go-{title}", use_container_width=True):
            set_page(target_page)


def load_sessions(state_prefix):
    sessions, error = getChatSessions()

    if error:
        st.session_state[f"{state_prefix}_sessions_error"] = error
        return

    st.session_state[f"{state_prefix}_sessions"] = sessions
    st.session_state[f"{state_prefix}_sessions_error"] = None


def load_session_messages(state_prefix, session_id):
    if not session_id:
        st.session_state[f"{state_prefix}_messages"] = []
        return

    messages, error = getChatSessionMessages(session_id)

    if error:
        st.session_state[f"{state_prefix}_messages_error"] = error
        return

    st.session_state[f"{state_prefix}_messages"] = messages
    st.session_state[f"{state_prefix}_messages_error"] = None


def render_session_strip(state_prefix):
    """Compact top strip: new chat / refresh / session picker, full width."""
    session_key = f"{state_prefix}_selected_session_id"
    sessions_key = f"{state_prefix}_sessions"

    if sessions_key not in st.session_state:
        load_sessions(state_prefix)

    st.markdown('<span class="session-strip-marker"></span>', unsafe_allow_html=True)
    with st.container(border=True):
        picker_col, new_col, refresh_col = st.columns([4, 1.1, 1.1], vertical_alignment="center")

        error = st.session_state.get(f"{state_prefix}_sessions_error")
        sessions = st.session_state.get(sessions_key, [])

        selected_session_id = None
        with picker_col:
            if error:
                st.error(error)
            elif not sessions:
                st.caption("No chat sessions yet — start a new chat.")
            else:
                session_labels = {
                    session["session_id"]: (
                        f'{session.get("title") or "New Chat"} · {session["session_id"][:8]}'
                    )
                    for session in sessions
                }
                session_ids = list(session_labels.keys())
                selected_session_id = st.session_state.get(session_key)

                if selected_session_id not in session_ids:
                    selected_session_id = session_ids[0]
                    st.session_state[session_key] = selected_session_id
                    st.session_state[f"{state_prefix}_session_select"] = selected_session_id

                selected_index = session_ids.index(selected_session_id)
                selected_session_id = st.selectbox(
                    "Chat session",
                    options=session_ids,
                    format_func=lambda session_id: session_labels[session_id],
                    index=selected_index,
                    key=f"{state_prefix}_session_select",
                    label_visibility="collapsed",
                )

                if st.session_state.get(session_key) != selected_session_id:
                    st.session_state[session_key] = selected_session_id
                    load_session_messages(state_prefix, selected_session_id)

                if f"{state_prefix}_messages" not in st.session_state:
                    load_session_messages(state_prefix, selected_session_id)

        with new_col:
            if st.button("+ New", key=f"{state_prefix}_new_session", use_container_width=True):
                with st.spinner("Creating..."):
                    session, error = createChatSession()
                if error:
                    st.error(error)
                else:
                    st.session_state[session_key] = session["session_id"]
                    st.session_state[f"{state_prefix}_session_select"] = session["session_id"]
                    load_sessions(state_prefix)
                    load_session_messages(state_prefix, session["session_id"])
                    st.rerun()

        with refresh_col:
            if st.button("Refresh", key=f"{state_prefix}_refresh_sessions", use_container_width=True):
                with st.spinner("Loading..."):
                    load_sessions(state_prefix)
                st.rerun()

    return selected_session_id


def render_chat_messages(messages):
    if not messages:
        render_empty_state("No messages yet — ask a question below to start the conversation.")
        return

    for message in messages:
        role = message.get("role", "assistant")
        content = message.get("content") or ""
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(content)
            citations = message.get("citations") or []
            if citations:
                with st.expander(f"📎 {len(citations)} source(s)"):
                    for index, citation in enumerate(citations, start=1):
                        st.caption(citation_title(citation, index))


def render_sources(citations):
    st.markdown('<div class="sources-card">', unsafe_allow_html=True)
    st.markdown("**Sources used**")
    st.caption("Retrieved document chunks used to generate this answer.")

    if not citations:
        render_empty_state("No sources were returned for this answer.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for index, citation in enumerate(citations, start=1):
        distance = citation.get("distance")
        score = 1 - float(distance) if distance is not None else None
        chunk_text = citation.get("chunk_text") or ""
        preview = chunk_text[:350] + "..." if len(chunk_text) > 350 else chunk_text

        with st.expander(citation_title(citation, index), expanded=index == 1):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Match Score", format_number(score))
            col2.metric("Distance", format_number(distance))
            col3.metric("Chunk Index", citation.get("chunk_index", "N/A"))
            col4.metric("Filename", citation.get("filename") or "N/A")

            st.markdown("**Document ID**")
            st.code(citation.get("document_id", "N/A"))

            st.markdown("**Chunk ID**")
            st.code(citation.get("chunk_id", "N/A"))

            st.markdown("**Preview**")
            if preview:
                st.write(preview)
            else:
                st.caption("Chunk text was not returned by the API.")

            if chunk_text:
                st.markdown("**Full Chunk Text**")
                st.text_area(
                    "Full chunk text",
                    value=chunk_text,
                    height=180,
                    label_visibility="collapsed",
                    key=f"citation-text-{citation.get('chunk_id', index)}",
                )
    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_options(state_prefix, default_top_k=3):
    """Collapsed-by-default retrieval options, keeps the composer clean."""
    with st.expander("⚙️ Retrieval options (Top K, document/filename filters)"):
        col1, col2, col3 = st.columns(3)
        top_k = col1.number_input(
            "Top K", min_value=1, max_value=20, value=default_top_k, key=f"{state_prefix}_top_k"
        )
        document_id = col2.text_input("Document ID (optional)", key=f"{state_prefix}_document_id")
        filename = col3.text_input("Filename (optional)", key=f"{state_prefix}_filename")
    return top_k, document_id, filename


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def render_dashboard():
    page_header(
        "Overview",
        "Enterprise RAG Platform",
        "A production-inspired Retrieval-Augmented Generation platform built with "
        "FastAPI, PostgreSQL + pgvector, Ollama, hybrid search, and Streamlit.",
    )

    cards = [
        ("📤", "Upload Documents", "Add PDF, text, or markdown files to the enterprise knowledge base.", "Documents", "Open Upload"),
        ("📚", "Documents Library", "Review uploaded documents and remove documents when needed.", "Documents", "Open Library"),
        ("🧩", "Chunk Explorer", "Inspect extracted chunks stored for retrieval and generation.", "Chunks", "Open Chunks"),
        ("💬", "Chat Assistant", "Ask questions and review source citations used in each answer.", "Chat", "Open Chat"),
        ("▶️", "Chat Stream", "Ask questions and watch the answer render as it arrives.", "Chat Stream", "Open Stream"),
        ("🔎", "Search", "Run hybrid retrieval with optional document and filename filters.", "Search", "Open Search"),
    ]

    for row_start in range(0, len(cards), 3):
        columns = st.columns(3, gap="medium")
        for column, card in zip(columns, cards[row_start:row_start + 3]):
            with column:
                render_dashboard_card(*card)


def render_documents():
    page_header("Knowledge Base", "Documents", "Upload files and manage the document library.")

    st.subheader("Upload Documents")
    upload_col, meta_col = st.columns([2, 1])
    with upload_col:
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md"])
    with meta_col:
        uploaded_by = st.text_input("Uploaded by", value="kamal")

    if st.button("Upload", disabled=uploaded_file is None, use_container_width=True):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"uploaded_by": uploaded_by}
        with st.spinner("Uploading and processing document..."):
            response, error = safe_request(
                "POST", f"{API_URL}/documents/upload", files=files, data=data, timeout=120
            )

        if error:
            st.error(error)
        elif response.ok:
            st.success(f"'{uploaded_file.name}' uploaded successfully.")
            with st.expander("Response details"):
                st.json(response.json())
        else:
            st.error(f"Upload failed ({response.status_code}): {response.text}")

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
    st.subheader("Documents Library")

    lib_col1, lib_col2 = st.columns([1, 5])
    with lib_col1:
        load_clicked = st.button("Refresh", use_container_width=True)

    if load_clicked:
        with st.spinner("Loading documents..."):
            response, error = safe_request("GET", f"{API_URL}/documents", timeout=60)

        if error:
            st.error(error)
        elif response.ok:
            st.session_state["documents"] = response.json()
        else:
            st.error(f"Failed to load documents ({response.status_code}): {response.text}")

    documents = st.session_state.get("documents", [])
    if not documents:
        render_empty_state("No documents loaded yet. Click **Refresh** to fetch the library.")
        return

    for document in documents:
        with st.container(border=True):
            row_col1, row_col2 = st.columns([5, 1])
            with row_col1:
                st.markdown(f'<p class="doc-name">{document.get("filename", "Unnamed document")}</p>', unsafe_allow_html=True)
                st.markdown(f'<span class="doc-id">ID: {document.get("id", "N/A")}</span>', unsafe_allow_html=True)
            with row_col2:
                if st.button("Delete", key=f"delete-{document['id']}", use_container_width=True):
                    with st.spinner("Deleting..."):
                        response, error = safe_request(
                            "DELETE", f"{API_URL}/documents/{document['id']}", timeout=60
                        )
                    if error:
                        st.error(error)
                    elif response.ok:
                        st.session_state["documents"] = [
                            item for item in st.session_state["documents"]
                            if item["id"] != document["id"]
                        ]
                        st.rerun()
                    else:
                        st.error(f"Delete failed ({response.status_code}): {response.text}")


def render_chunks():
    page_header("Knowledge Base", "Chunks", "Explore document chunks available for retrieval.")

    if st.button("Load Chunks", use_container_width=False):
        with st.spinner("Loading chunks..."):
            response, error = safe_request("GET", f"{API_URL}/chunks", timeout=60)

        if error:
            st.error(error)
        elif response.ok:
            st.session_state["chunks"] = response.json()
        else:
            st.error(f"Failed to load chunks ({response.status_code}): {response.text}")

    chunks = st.session_state.get("chunks")
    if chunks is None:
        render_empty_state("Click **Load Chunks** to inspect the indexed document text.")
    elif not chunks:
        render_empty_state("No chunks found. Upload a document to populate the index.")
    else:
        st.caption(f"{len(chunks)} chunk(s) loaded")
        st.dataframe(chunks, use_container_width=True)


def render_chat():
    page_header("Assistant", "Chat", "Ask questions against your uploaded document knowledge base.")

    selected_session_id = render_session_strip("chat")

    st.markdown('<span class="chat-thread-marker"></span>', unsafe_allow_html=True)
    with st.container(border=True):
        if selected_session_id:
            message_error = st.session_state.get("chat_messages_error")
            if message_error:
                st.error(message_error)
            else:
                render_chat_messages(st.session_state.get("chat_messages", []))
        else:
            render_empty_state("Select or create a chat session to begin.")

    top_k, document_id, filename = render_chat_options("chat")

    with st.container(border=True):
        query = st.text_area(
            "Question",
            height=90,
            placeholder="e.g. What are the key findings in the Q3 report?",
            key="chat_query",
            label_visibility="collapsed",
        )
        ask_col, spacer_col = st.columns([1, 4])
        with ask_col:
            ask_clicked = st.button(
                "Ask ➤",
                disabled=not query.strip() or not selected_session_id,
                use_container_width=True,
                type="primary",
            )

    if ask_clicked:
        with st.spinner("Generating answer..."):
            data, error = sendChatMessage(query, selected_session_id, top_k, document_id, filename)

        if error:
            st.error(error)
        else:
            load_session_messages("chat", selected_session_id)
            render_sources(data.get("citations", []))
            st.rerun()


def stream_answer(payload):
    with requests.post(f"{API_URL}/chat/stream", json=payload, stream=True, timeout=180) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def render_chat_stream():
    page_header("Assistant", "Chat Stream", "Ask questions and stream the answer as it is generated.")

    selected_session_id = render_session_strip("stream")

    st.markdown('<span class="chat-thread-marker"></span>', unsafe_allow_html=True)
    with st.container(border=True):
        if selected_session_id:
            message_error = st.session_state.get("stream_messages_error")
            if message_error:
                st.error(message_error)
            else:
                render_chat_messages(st.session_state.get("stream_messages", []))
        else:
            render_empty_state("Select or create a chat session to begin.")

    top_k, document_id, filename = render_chat_options("stream")

    with st.container(border=True):
        query = st.text_area(
            "Question",
            height=90,
            placeholder="e.g. Summarize the uploaded policy document",
            key="stream_query",
            label_visibility="collapsed",
        )
        ask_col, spacer_col = st.columns([1, 4])
        with ask_col:
            stream_clicked = st.button(
                "Stream ➤",
                disabled=not query.strip() or not selected_session_id,
                use_container_width=True,
                type="primary",
            )

    if stream_clicked:
        payload = build_query_payload(query, top_k, document_id, filename, selected_session_id)

        st.markdown('<span class="streaming-badge">🟢 Streaming answer…</span>', unsafe_allow_html=True)
        with st.chat_message("assistant"):
            try:
                st.write_stream(stream_answer(payload))
                load_session_messages("stream", selected_session_id)
                st.rerun()
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is the API running?")
            except requests.exceptions.Timeout:
                st.error("The request timed out. The backend may be under heavy load.")
            except requests.exceptions.HTTPError as exc:
                response = exc.response
                detail = response.text if response is not None else str(exc)
                status_code = response.status_code if response is not None else "unknown"
                st.error(f"Stream failed ({status_code}): {detail}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Stream failed: {exc}")


def render_search():
    page_header("Assistant", "Search", "Run retrieval with optional metadata filters.")

    search_query = st.text_area("Search query", height=120, placeholder="Enter keywords or a natural-language query")
    col1, col2, col3 = st.columns(3)
    top_k = col1.number_input("Top K", min_value=1, max_value=20, value=5, key="search_top_k")
    document_id = col2.text_input("Document ID (optional)", key="search_document_id")
    filename = col3.text_input("Filename (optional)", key="search_filename")

    if st.button("Search", disabled=not search_query.strip(), use_container_width=True, type="primary"):
        with st.spinner("Searching..."):
            response, error = safe_request(
                "POST",
                f"{API_URL}/search",
                json=build_query_payload(search_query, top_k, document_id, filename),
                timeout=120,
            )

        if error:
            st.error(error)
        elif response.ok:
            results = response.json().get("results", [])
            st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
            if results:
                st.caption(f"{len(results)} result(s)")
                st.dataframe(results, use_container_width=True)
            else:
                render_empty_state("No results matched your query.")
        else:
            st.error(f"Search failed ({response.status_code}): {response.text}")


# --------------------------------------------------------------------------
# App shell — header nav (replaces sidebar)
# --------------------------------------------------------------------------
if "page" not in st.session_state or st.session_state["page"] not in PAGE_OPTIONS:
    st.session_state["page"] = "Dashboard"

st.markdown(
    '<div class="brand-row"><span class="brand-mark">🧠</span> Enterprise RAG Platform</div>',
    unsafe_allow_html=True,
)

nav_cols = st.columns(len(PAGE_OPTIONS), gap="small")
for column, page in zip(nav_cols, PAGE_OPTIONS):
    with column:
        is_active = st.session_state["page"] == page
        st.markdown(
            f'<div class="{"top-nav-active" if is_active else "top-nav"}">',
            unsafe_allow_html=True,
        )
        label = f"{PAGE_ICONS[page]}  {page}"
        if st.button(label, key=f"nav-{page}", use_container_width=True):
            set_page(page)
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state["page"] == "Dashboard":
    render_dashboard()
elif st.session_state["page"] == "Documents":
    render_documents()
elif st.session_state["page"] == "Chunks":
    render_chunks()
elif st.session_state["page"] == "Chat":
    render_chat()
elif st.session_state["page"] == "Chat Stream":
    render_chat_stream()
else:
    render_search()
