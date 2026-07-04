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
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu,
    footer,
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"],
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
        padding-top: 1.75rem;
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

    /* Tighten default Streamlit block spacing */
    [data-testid="stVerticalBlock"] {
        gap: 0.6rem;
    }
    div.stButton {
        margin-top: 0.15rem;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] .stButton > button {
        justify-content: flex-start;
        border: 1px solid transparent;
        background: transparent;
        color: var(--brand-navy);
        font-weight: 500;
        border-radius: 8px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--border-color);
        background: var(--brand-blue-light);
        color: var(--brand-blue);
    }
    /* ---------- Buttons ---------- */
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

    /* ---------- Native bordered containers (used for cards & item rows) ---------- */
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


def build_query_payload(query, top_k, document_id, filename):
    payload = {"query": query, "top_k": int(top_k)}
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


def render_sources(citations):
    st.subheader("Sources Used")
    st.caption("Retrieved document chunks used to generate this answer.")

    if not citations:
        render_empty_state("No sources were returned for this answer.")
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

    query = st.text_area("Question", height=120, placeholder="e.g. What are the key findings in the Q3 report?")
    col1, col2, col3 = st.columns(3)
    top_k = col1.number_input("Top K", min_value=1, max_value=20, value=3, key="chat_top_k")
    document_id = col2.text_input("Document ID (optional)", key="chat_document_id")
    filename = col3.text_input("Filename (optional)", key="chat_filename")

    if st.button("Ask", disabled=not query.strip(), use_container_width=True, type="primary"):
        with st.spinner("Generating answer..."):
            response, error = safe_request(
                "POST",
                f"{API_URL}/chat",
                json=build_query_payload(query, top_k, document_id, filename),
                timeout=180,
            )

        if error:
            st.error(error)
        elif response.ok:
            data = response.json()
            st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
            st.subheader("Answer")
            st.write(data.get("answer", "No answer returned."))
            render_sources(data.get("citations", []))
        else:
            st.error(f"Request failed ({response.status_code}): {response.text}")


def stream_answer(payload):
    with requests.post(f"{API_URL}/chat/stream", json=payload, stream=True, timeout=180) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def render_chat_stream():
    page_header("Assistant", "Chat Stream", "Ask questions and stream the answer as it is generated.")

    query = st.text_area(
        "Question",
        height=120,
        placeholder="e.g. Summarize the uploaded policy document",
        key="stream_query",
    )
    col1, col2, col3 = st.columns(3)
    top_k = col1.number_input("Top K", min_value=1, max_value=20, value=3, key="stream_top_k")
    document_id = col2.text_input("Document ID (optional)", key="stream_document_id")
    filename = col3.text_input("Filename (optional)", key="stream_filename")

    if st.button("Stream Answer", disabled=not query.strip(), use_container_width=True, type="primary"):
        payload = build_query_payload(query, top_k, document_id, filename)
        st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
        st.subheader("Answer")

        try:
            st.write_stream(stream_answer(payload))
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
# App shell
# --------------------------------------------------------------------------
if "page" not in st.session_state or st.session_state["page"] not in PAGE_OPTIONS:
    st.session_state["page"] = "Dashboard"

with st.sidebar:
    brand_icon, brand_text = st.columns([1, 5], vertical_alignment="center")
    with brand_icon:
        st.markdown("### 🧠")
    with brand_text:
        st.markdown("### Enterprise RAG")

    st.divider()

    for page in PAGE_OPTIONS:
        label = f"{PAGE_ICONS[page]}  {page}"
        if st.button(label, key=f"nav-{page}", use_container_width=True):
            set_page(page)

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
