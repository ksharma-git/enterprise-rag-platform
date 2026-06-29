import requests

from app.config import LLM_MODEL, OLLAMA_GENERATE_URL


def ask_llama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]
