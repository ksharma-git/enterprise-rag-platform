import requests

from app.config import EMBEDDING_MODEL, OLLAMA_EMBEDDING_URL


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBEDDING_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    embedding = data["embedding"]

    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}"
        )

    return embedding
