def normalize_keyword_score(keyword_results):
    if not keyword_results:
        return {}

    max_score = max(float(row["keyword_score"]) for row in keyword_results)

    if max_score == 0:
        return {}

    return {
        str(row["id"]): float(row["keyword_score"]) / max_score
        for row in keyword_results
    }


def hybrid_merge(vector_results, keyword_results, top_k: int = 5):
    merged = {}

    keyword_scores = normalize_keyword_score(keyword_results)

    for row in vector_results:
        chunk_id = str(row["id"])
        distance = row["distance"]
        vector_score = max(0.0, float(1.0 - distance))

        merged[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": str(row["document_id"]),
            "filename": row["filename"],
            "chunk_text": row["chunk_text"],
            "chunk_index": row["chunk_index"],
            "chunk_metadata": row["chunk_metadata"],
            "distance": row["distance"],
            "vector_score": vector_score,
            "keyword_score": 0.0,
        }

    for row in keyword_results:
        chunk_id = str(row["id"])
        keyword_score = keyword_scores.get(chunk_id, 0.0)

        if chunk_id not in merged:
            merged[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": str(row["document_id"]),
                "filename": row["filename"],
                "chunk_text": row["chunk_text"],
                "chunk_index": row["chunk_index"],
                "chunk_metadata": row["chunk_metadata"],
                "distance": None,
                "vector_score": 0.0,
                "keyword_score": keyword_score,
            }
        else:
            merged[chunk_id]["keyword_score"] = keyword_score

    for item in merged.values():
        item["hybrid_score"] = item["vector_score"] * 0.7 + item["keyword_score"] * 0.3

    return sorted(
        merged.values(),
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )[:top_k]
