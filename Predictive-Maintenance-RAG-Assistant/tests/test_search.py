from src.search import TfidfRetriever, get_retriever

DOCS = [
    {"id": "a", "section": "Tool Wear Failure", "question": "What causes tool wear?", "answer": "Long cutting time."},
    {"id": "b", "section": "Power Failure", "question": "What causes power failure?", "answer": "Torque times speed out of range."},
]


def test_returns_top_k():
    results = TfidfRetriever(DOCS).search("tool wear", top_k=1)
    assert len(results) == 1


def test_most_relevant_first():
    results = TfidfRetriever(DOCS).search("power failure torque", top_k=2)
    assert results[0]["id"] == "b"
    assert results[0]["score"] >= results[1]["score"]


def test_real_knowledge_base_loads():
    results = get_retriever().search("symptoms of tool wear failure", top_k=5)
    assert len(results) == 5
    assert all("answer" in r for r in results)