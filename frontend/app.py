import os
import html

import requests
import streamlit as st
import streamlit.components.v1 as components

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
    footer,
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
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
        padding-top: 0.75rem;
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
    .app-shell-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.55rem;
    }
    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--brand-navy);
        letter-spacing: -0.01em;
        padding-bottom: 0;
    }
    .brand-row .brand-mark {
        font-size: 1.3rem;
    }
    .current-page-pill {
        color: var(--brand-blue);
        background: var(--brand-blue-light);
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        padding: 0.22rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 700;
        white-space: nowrap;
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
    .chat-layout-title {
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0.1rem 0 0.5rem 0;
    }
    .message-row {
        display: flex;
        margin: 0.55rem 0;
        width: 100%;
    }
    .message-row.user {
        justify-content: flex-end;
    }
    .message-row.assistant {
        justify-content: flex-start;
    }
    .message-bubble {
        max-width: 78%;
        padding: 0.7rem 0.9rem;
        border-radius: 14px;
        line-height: 1.45;
        font-size: 0.95rem;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
    }
    .message-row.user .message-bubble {
        background: var(--brand-blue);
        color: #ffffff;
        border-radius: 14px 14px 3px 14px;
    }
    .message-row.assistant .message-bubble {
        background: var(--surface-alt);
        border: 1px solid var(--border-color);
        border-radius: 14px 14px 14px 3px;
    }
    .message-sources {
        color: var(--text-muted);
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }
    .chat-empty {
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        text-align: center;
        border: 1px dashed var(--border-color);
        border-radius: 12px;
        background: var(--surface-alt);
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
    .stButton > button p {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    button[title^="Open chat session"],
    button[aria-label^="Open chat session"],
    button[title^="Selected chat session"],
    button[aria-label^="Selected chat session"] {
        min-height: 2.25rem !important;
        justify-content: flex-start !important;
        padding: 0 0.75rem !important;
        border-radius: 8px 0 0 8px !important;
        box-shadow: none !important;
        font-weight: 500 !important;
        background: transparent !important;
        border-color: transparent !important;
        color: var(--brand-navy) !important;
    }
    button[title^="Open chat session"]:hover,
    button[aria-label^="Open chat session"]:hover {
        background: #f8fafc !important;
        border-color: transparent !important;
        color: var(--brand-navy) !important;
    }
    button[title^="Selected chat session"],
    button[aria-label^="Selected chat session"] {
        background: var(--brand-blue-light) !important;
        border-color: #bfdbfe !important;
        color: #1d4ed8 !important;
        font-weight: 600 !important;
    }
    button[title^="Selected chat session"]:hover,
    button[aria-label^="Selected chat session"]:hover {
        background: #dbeafe !important;
        border-color: #93c5fd !important;
        color: #1d4ed8 !important;
    }
    button[title="Create chat session"],
    button[aria-label="Create chat session"],
    button[title="Refresh chat sessions"],
    button[aria-label="Refresh chat sessions"] {
        min-height: 2.15rem !important;
        border-radius: 8px !important;
        padding: 0 0.65rem !important;
        font-size: 0.86rem !important;
        box-shadow: none !important;
    }
    button[title^="Delete chat session"],
    button[aria-label^="Delete chat session"],
    button[title^="Delete selected chat session"],
    button[aria-label^="Delete selected chat session"] {
        min-height: 2.25rem !important;
        width: 2.25rem !important;
        padding: 0 !important;
        border-radius: 8px !important;
        color: var(--text-muted) !important;
        background: transparent !important;
        border-color: transparent !important;
        box-shadow: none !important;
        opacity: 0.62;
        transition: opacity 0.12s ease, background 0.12s ease, color 0.12s ease;
    }
    button[title^="Delete selected chat session"],
    button[aria-label^="Delete selected chat session"] {
        color: #1d4ed8 !important;
        opacity: 0.78;
    }
    button[title^="Delete chat session"]:hover,
    button[aria-label^="Delete chat session"]:hover,
    button[title^="Delete selected chat session"]:hover,
    button[aria-label^="Delete selected chat session"]:hover {
        color: #dc2626 !important;
        background: #fef2f2 !important;
        border-color: #fecaca !important;
        opacity: 1;
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


def deleteChatSession(sessionId):
    response, error = safe_request("DELETE", f"{API_URL}/chat/sessions/{sessionId}", timeout=60)

    if error:
        return None, error
    if not response.ok:
        return None, f"Failed to delete session ({response.status_code}): {response.text}"

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
    request_chat_scroll(state_prefix)


def append_chat_exchange(state_prefix, query, answer, citations=None):
    messages_key = f"{state_prefix}_messages"
    messages = st.session_state.get(messages_key, [])
    st.session_state[messages_key] = [
        *messages,
        {
            "role": "user",
            "content": query,
            "citations": [],
        },
        {
            "role": "assistant",
            "content": answer or "No answer returned.",
            "citations": citations or [],
        },
    ]
    request_chat_scroll(state_prefix)


def submit_chat_message():
    selected_session_id = st.session_state.get("chat_selected_session_id")
    query = (st.session_state.get("chat_query") or "").strip()

    st.session_state["chat_submit_error"] = None
    st.session_state["chat_submit_warning"] = None

    if not selected_session_id:
        st.session_state["chat_submit_warning"] = "Create or select a chat to begin."
        return
    if not query:
        st.session_state["chat_submit_warning"] = "Please enter a question."
        return

    data, error = sendChatMessage(
        query,
        selected_session_id,
        st.session_state.get("chat_top_k", 3),
        st.session_state.get("chat_document_id", ""),
        st.session_state.get("chat_filename", ""),
    )

    if error:
        st.session_state["chat_submit_error"] = error
        return

    append_chat_exchange(
        "chat",
        query,
        data.get("answer"),
        data.get("citations", []),
    )
    st.session_state["chat_query"] = ""


def select_chat_session(state_prefix, session_id):
    session_key = f"{state_prefix}_selected_session_id"
    st.session_state[session_key] = session_id
    load_session_messages(state_prefix, session_id)


def delete_selected_chat_session(state_prefix, session_id):
    selected_session_key = f"{state_prefix}_selected_session_id"
    messages_key = f"{state_prefix}_messages"
    error_key = f"{state_prefix}_sessions_error"

    _, error = deleteChatSession(session_id)

    if error:
        st.session_state[error_key] = error
        return

    if st.session_state.get(selected_session_key) == session_id:
        st.session_state[selected_session_key] = None
        st.session_state[messages_key] = []
        st.session_state[f"{state_prefix}_messages_error"] = None

    load_sessions(state_prefix)


def request_delete_chat_session(state_prefix, session_id, title):
    st.session_state[f"{state_prefix}_pending_delete_session"] = {
        "session_id": session_id,
        "title": title,
    }

    if hasattr(st, "dialog"):
        render_delete_chat_session_dialog(state_prefix)
    else:
        st.rerun()


def render_delete_chat_session_confirmation(state_prefix):
    pending_delete = st.session_state.get(f"{state_prefix}_pending_delete_session")

    if not pending_delete:
        return

    session_id = pending_delete["session_id"]
    title = pending_delete.get("title") or "New Chat"

    st.write(f'Delete "{title}"?')
    st.caption("This will remove the chat session and its messages.")

    cancel_col, delete_col = st.columns([1, 1])
    with cancel_col:
        if st.button("Cancel", key=f"{state_prefix}_cancel_delete_session", use_container_width=True):
            st.session_state.pop(f"{state_prefix}_pending_delete_session", None)
            st.rerun()
    with delete_col:
        if st.button(
            "Delete",
            key=f"{state_prefix}_confirm_delete_session",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.pop(f"{state_prefix}_pending_delete_session", None)
            delete_selected_chat_session(state_prefix, session_id)
            st.rerun()


if hasattr(st, "dialog"):
    @st.dialog("Delete chat session?")
    def render_delete_chat_session_dialog(state_prefix):
        render_delete_chat_session_confirmation(state_prefix)
else:
    def render_delete_chat_session_dialog(state_prefix):
        render_delete_chat_session_confirmation(state_prefix)


def request_chat_scroll(state_prefix):
    scroll_key = f"{state_prefix}_scroll_version"
    st.session_state[scroll_key] = st.session_state.get(scroll_key, 0) + 1


def render_chat_bottom_marker(state_prefix):
    st.markdown(f'<div data-chat-bottom="{state_prefix}"></div>', unsafe_allow_html=True)


def render_chat_scroll_script(state_prefix, force=False, placeholder=None):
    scroll_key = f"{state_prefix}_scroll_version"
    rendered_key = f"{state_prefix}_scroll_rendered_version"
    scroll_version = st.session_state.get(scroll_key, 0)

    if force or (scroll_version and st.session_state.get(rendered_key) != scroll_version):
        st.session_state[rendered_key] = scroll_version
        scroll_script = f"""
        <script>
        const markers = parent.document.querySelectorAll('[data-chat-bottom="{state_prefix}"]');
        const marker = markers[markers.length - 1];
        if (marker) {{
            const scrollParent = (node) => {{
                let current = node.parentElement;
                while (current && current !== parent.document.body) {{
                    const style = parent.getComputedStyle(current);
                    const canScroll = /(auto|scroll)/.test(style.overflowY);
                    if (canScroll && current.scrollHeight > current.clientHeight) {{
                        return current;
                    }}
                    current = current.parentElement;
                }}
                return null;
            }};
            const container = scrollParent(marker);
            if (container) {{
                container.scrollTop = container.scrollHeight;
            }} else {{
                marker.scrollIntoView({{ block: "end" }});
            }}
        }}
        </script>
        """
        if placeholder is None:
            components.html(scroll_script, height=0, width=0)
        else:
            placeholder.empty()
            with placeholder.container():
                components.html(scroll_script, height=0, width=0)


def render_session_list(state_prefix):
    session_key = f"{state_prefix}_selected_session_id"
    sessions_key = f"{state_prefix}_sessions"

    if sessions_key not in st.session_state:
        load_sessions(state_prefix)

    new_col, refresh_col = st.columns([1, 1], gap="small")
    with new_col:
        if st.button(
            "+ New Chat",
            key=f"{state_prefix}_new_session",
            use_container_width=True,
            help="Create chat session",
        ):
            with st.spinner("Creating..."):
                session, error = createChatSession()
            if error:
                st.error(error)
            else:
                load_sessions(state_prefix)
                select_chat_session(state_prefix, session["session_id"])
    with refresh_col:
        if st.button(
            "Refresh",
            key=f"{state_prefix}_refresh_sessions",
            use_container_width=True,
            help="Refresh chat sessions",
        ):
            with st.spinner("Loading..."):
                load_sessions(state_prefix)

    selected_session_id = st.session_state.get(session_key)
    sessions = st.session_state.get(sessions_key, [])
    error = st.session_state.get(f"{state_prefix}_sessions_error")

    if not hasattr(st, "dialog"):
        render_delete_chat_session_confirmation(state_prefix)

    with st.container(height=705, border=True):
        error = st.session_state.get(f"{state_prefix}_sessions_error")
        if error:
            st.error(error)
        elif not sessions:
            render_empty_state("No chats yet. Create a new chat.")
        else:
            session_ids = [session["session_id"] for session in sessions]
            if selected_session_id not in session_ids:
                selected_session_id = session_ids[0]
                select_chat_session(state_prefix, selected_session_id)

            for session in sessions:
                session_id = session["session_id"]
                title = session.get("title") or "New Chat"
                selected = session_id == selected_session_id
                row_help = (
                    f"Selected chat session: {session_id}"
                    if selected
                    else f"Open chat session: {session_id}"
                )
                session_col, delete_col = st.columns([0.86, 0.14], gap="small")
                with session_col:
                    if st.button(
                        title,
                        key=f"{state_prefix}_session_{session_id}",
                        use_container_width=True,
                        type="secondary",
                        help=row_help,
                    ):
                        select_chat_session(state_prefix, session_id)
                with delete_col:
                    if st.button(
                        "🗑",
                        key=f"{state_prefix}_delete_session_{session_id}",
                        help=(
                            f"Delete selected chat session: {session_id}"
                            if selected
                            else f"Delete chat session: {session_id}"
                        ),
                    ):
                        request_delete_chat_session(state_prefix, session_id, title)

    if selected_session_id and f"{state_prefix}_messages" not in st.session_state:
        load_session_messages(state_prefix, selected_session_id)

    return st.session_state.get(session_key)


def render_message_bubble(message):
    role = message.get("role", "assistant")
    content = html.escape(message.get("content") or "")
    css_role = "user" if role == "user" else "assistant"
    citations = message.get("citations") or []
    sources_text = ""
    if citations:
        sources_text = f'<div class="message-sources">{len(citations)} source(s)</div>'

    st.markdown(
        f"""
        <div class="message-row {css_role}">
            <div class="message-bubble">{content}{sources_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_messages(messages):
    if not messages:
        st.markdown(
            '<div class="chat-empty">No messages yet. Ask a question below to start the conversation.</div>',
            unsafe_allow_html=True,
        )
        return

    for message in messages:
        render_message_bubble(message)


def render_sources(citations):
    with st.container(border=True):
        st.markdown("**Sources used**")
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

    sessions_col, conversation_col = st.columns([1.05, 3.0], gap="small")

    with sessions_col:
        selected_session_id = render_session_list("chat")

    with conversation_col:
        top_k, document_id, filename = render_chat_options("chat")

        st.markdown('<div class="chat-layout-title">Conversation</div>', unsafe_allow_html=True)
        message_area = st.empty()

        st.text_area(
            "Message",
            height=95,
            placeholder="Ask a question about your documents",
            disabled=not selected_session_id,
            key="chat_query",
        )
        st.button(
            "Ask",
            disabled=not selected_session_id,
            type="primary",
            use_container_width=True,
            on_click=submit_chat_message,
        )

        submit_warning = st.session_state.get("chat_submit_warning")
        submit_error = st.session_state.get("chat_submit_error")
        if submit_warning:
            st.warning(submit_warning)
        if submit_error:
            st.error(submit_error)

        with message_area.container(height=570, border=True):
            if not selected_session_id:
                render_empty_state("Create or select a chat to begin.")
            else:
                message_error = st.session_state.get("chat_messages_error")
                if message_error:
                    st.error(message_error)
                else:
                    render_chat_messages(st.session_state.get("chat_messages", []))
            render_chat_bottom_marker("chat")
        render_chat_scroll_script("chat")


def stream_answer(payload):
    with requests.post(f"{API_URL}/chat/stream", json=payload, stream=True, timeout=180) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def render_chat_stream():
    page_header("Assistant", "Chat Stream", "Ask questions and stream the answer as it is generated.")

    sessions_col, conversation_col = st.columns([1.05, 3.0], gap="small")

    with sessions_col:
        selected_session_id = render_session_list("stream")

    with conversation_col:
        top_k, document_id, filename = render_chat_options("stream")

        st.markdown('<div class="chat-layout-title">Conversation</div>', unsafe_allow_html=True)
        message_container = st.container(height=570, border=True)
        with message_container:
            if not selected_session_id:
                render_empty_state("Create or select a chat to begin.")
            else:
                message_error = st.session_state.get("stream_messages_error")
                if message_error:
                    st.error(message_error)
                else:
                    render_chat_messages(st.session_state.get("stream_messages", []))
            render_chat_bottom_marker("stream")
        render_chat_scroll_script("stream")

        with st.form("stream_composer", clear_on_submit=True):
            query = st.text_area(
                "Message",
                height=95,
                placeholder="Ask a question and stream the answer",
                disabled=not selected_session_id,
            )
            stream_clicked = st.form_submit_button(
                "Stream",
                disabled=not selected_session_id,
                type="primary",
                use_container_width=True,
            )

        if stream_clicked:
            query = query.strip()
            if not query:
                st.warning("Please enter a question.")
                return

            payload = build_query_payload(query, top_k, document_id, filename, selected_session_id)
            accumulated_answer = ""

            try:
                with message_container:
                    render_message_bubble({"role": "user", "content": query})
                    answer_placeholder = st.empty()
                    render_chat_bottom_marker("stream")
                    stream_scroll_placeholder = st.empty()
                render_chat_scroll_script("stream", force=True, placeholder=stream_scroll_placeholder)

                for token in stream_answer(payload):
                    accumulated_answer += token
                    answer_placeholder.markdown(
                        f"""
                        <div class="message-row assistant">
                            <div class="message-bubble">{html.escape(accumulated_answer)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    render_chat_scroll_script("stream", force=True, placeholder=stream_scroll_placeholder)
                append_chat_exchange("stream", query, accumulated_answer)
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

current_page = st.session_state["page"]
st.markdown(
    f"""
    <div class="app-shell-header">
        <div class="brand-row"><span class="brand-mark">🧠</span> Enterprise RAG Platform</div>
        <div class="current-page-pill">{PAGE_ICONS[current_page]} {current_page}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_cols = st.columns(len(PAGE_OPTIONS), gap="small")
for column, page in zip(nav_cols, PAGE_OPTIONS):
    with column:
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
