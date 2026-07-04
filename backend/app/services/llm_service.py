import json

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


def ask_llama_stream(prompt: str):
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2
            }
        },
        stream=True,
        timeout=120,
    )

    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode("utf-8"))

        if "response" in data:
            yield data["response"]

        if data.get("done"):
            break
