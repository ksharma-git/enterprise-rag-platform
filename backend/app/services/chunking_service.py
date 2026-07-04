import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_paragraphs(text: str) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def fixed_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def split_long_paragraph(
    paragraph: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        candidate = f"{current_chunk} {sentence}".strip()

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = f"{overlap_text} {sentence}".strip()

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def paragraph_aware_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    paragraphs = split_into_paragraphs(text)

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            long_chunks = split_long_paragraph(paragraph, chunk_size, overlap)
            chunks.extend(long_chunks)
            continue

        candidate = f"{current_chunk}\n\n{paragraph}".strip()

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            chunks.append(current_chunk.strip())

            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = f"{overlap_text}\n\n{paragraph}".strip()

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
