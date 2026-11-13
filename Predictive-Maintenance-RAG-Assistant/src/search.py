
from functools import lru_cache

from src.ingest import load_machine_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Fields used for retrieval
RETRIEVAL_FIELDS = ["process_control","failure_mode","section","question","answer"]

class TfidfRetriever:
    # TF-IDF + cosine-similarity retriever

    def __init__(self, documents):
        self.documents = documents
        
        document_texts = [
            " ".join(doc.get(f) or "" for f in RETRIEVAL_FIELDS)
            for doc in documents
        ]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.document_vectors = self.vectorizer.fit_transform(document_texts)

    def search(self,query, top_k=5):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector,self.document_vectors)[0]
        top_indexes = scores.argsort()[::-1][:top_k]

        results = []
        
        for index in top_indexes:
            results.append({
                **self.documents[index],
                "score": round(float(scores[index]), 4)
            })

        return results


@lru_cache(maxsize=1)
def get_retriever():
    return TfidfRetriever(load_machine_data())


def vector_search(query,top_k = 5):
    return get_retriever().search(query,top_k=top_k)


