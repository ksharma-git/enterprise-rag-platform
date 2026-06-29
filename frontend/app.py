import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Enterprise RAG Platform")
st.caption(f"API: {API_URL}")

upload_tab, chat_tab, documents_tab, chunks_tab = st.tabs([
    "Upload File",
    "Chat",
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
    top_k = st.number_input("Top K", min_value=1, max_value=20, value=3)

    if st.button("Ask", disabled=not query.strip()):
        response = requests.post(
            f"{API_URL}/chat",
            json={"query": query, "top_k": top_k},
            timeout=180,
        )

        if response.ok:
            data = response.json()
            st.write(data.get("answer"))
            st.json(data.get("citations", []))
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
        st.write(f"{document['filename']} - {document['id']}")

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
