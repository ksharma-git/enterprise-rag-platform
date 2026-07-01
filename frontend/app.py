import os

import requests
import streamlit as st

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Enterprise RAG Platform", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1180px; padding-top: 2rem; }
    div[data-testid="stTabs"] button { font-weight: 600; }
    div[data-testid="stVerticalBlock"] > div:has(.rag-card) {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        background: #ffffff;
    }
    .rag-card { font-size: 0.9rem; color: #475569; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Enterprise RAG Platform")
st.caption(f"API: {API_URL}")


def build_query_payload(query, top_k, document_id, filename):
    payload = {"query": query, "top_k": int(top_k)}
    if document_id.strip():
        payload["document_id"] = document_id.strip()
    if filename.strip():
        payload["filename"] = filename.strip()
    return payload

upload_tab, chat_tab, search_tab, documents_tab, chunks_tab = st.tabs([
    "Upload File",
    "Chat",
    "Search",
    "Documents",
    "Chunks",
])

with upload_tab:
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md"])
    uploaded_by = st.text_input("Uploaded by", value="kamal")

    if st.button("Upload", disabled=uploaded_file is None):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"uploaded_by": uploaded_by}
        response = requests.post(f"{API_URL}/documents/upload", files=files, data=data, timeout=120)

        if response.ok:
            st.success("Uploaded")
            st.json(response.json())
        else:
            st.error(response.text)

with chat_tab:
    query = st.text_area("Question")
    col1, col2, col3 = st.columns(3)
    top_k = col1.number_input("Top K", min_value=1, max_value=20, value=3, key="chat_top_k")
    document_id = col2.text_input("Document ID", key="chat_document_id")
    filename = col3.text_input("Filename", key="chat_filename")

    if st.button("Ask", disabled=not query.strip()):
        response = requests.post(
            f"{API_URL}/chat",
            json=build_query_payload(query, top_k, document_id, filename),
            timeout=180,
        )

        if response.ok:
            data = response.json()
            st.markdown('<div class="rag-card">Answer</div>', unsafe_allow_html=True)
            st.write(data.get("answer"))
            st.markdown('<div class="rag-card">Citations</div>', unsafe_allow_html=True)
            st.json(data.get("citations", []))
        else:
            st.error(response.text)

with search_tab:
    search_query = st.text_area("Search query")
    col1, col2, col3 = st.columns(3)
    search_top_k = col1.number_input("Top K", min_value=1, max_value=20, value=5, key="search_top_k")
    search_document_id = col2.text_input("Document ID", key="search_document_id")
    search_filename = col3.text_input("Filename", key="search_filename")

    if st.button("Search", disabled=not search_query.strip()):
        response = requests.post(
            f"{API_URL}/search",
            json=build_query_payload(search_query, search_top_k, search_document_id, search_filename),
            timeout=120,
        )

        if response.ok:
            st.dataframe(response.json().get("results", []), use_container_width=True)
        else:
            st.error(response.text)

with documents_tab:
    if st.button("Load Documents"):
        response = requests.get(f"{API_URL}/documents", timeout=60)

        if response.ok:
            st.session_state["documents"] = response.json()
        else:
            st.error(response.text)

    for document in st.session_state.get("documents", []):
        st.markdown(
            f"<div class='rag-card'><strong>{document['filename']}</strong><br>{document['id']}</div>",
            unsafe_allow_html=True,
        )

        if st.button("Delete", key=f"delete-{document['id']}"):
            response = requests.delete(f"{API_URL}/documents/{document['id']}", timeout=60)

            if response.ok:
                st.success("Deleted")
                st.session_state["documents"] = [
                    item for item in st.session_state["documents"]
                    if item["id"] != document["id"]
                ]
                st.rerun()
            else:
                st.error(response.text)

with chunks_tab:
    if st.button("Load Chunks"):
        response = requests.get(f"{API_URL}/chunks", timeout=60)

        if response.ok:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(response.text)
