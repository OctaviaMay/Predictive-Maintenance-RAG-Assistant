

from src.ingest import load_machine_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def vector_search(query, top_k=5):
    # load machine data
    documents = load_machine_data()

    SECTION_FILTER = None

    documents_eval = [
        doc for doc in documents
        if SECTION_FILTER is None or doc["section"] == SECTION_FILTER
    ]
    # Fields used for retrieval
    document_texts = [
    " ".join([
        doc.get("process_control") or "",
        doc.get("failure_mode") or "",
        doc.get("section") or "",
        doc.get("question") or "",
        doc.get("answer") or ""
    ])
    for doc in documents_eval
    ]
    vectorizer = TfidfVectorizer(stop_words="english")
    document_vectors = vectorizer.fit_transform(document_texts)

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        document_vectors
    )[0]

    top_indexes = scores.argsort()[::-1][:top_k]

    results = []

    for index in top_indexes:
        results.append({
            **documents_eval[index],
            "score": round(float(scores[index]), 4)
        })

    return results
