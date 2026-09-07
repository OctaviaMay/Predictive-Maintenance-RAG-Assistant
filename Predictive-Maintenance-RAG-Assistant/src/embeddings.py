from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm

EMBEDDER_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# embedding query question
def embed_question(query_question):
    # encode query question
    query_vector = EMBEDDER_MODEL.encode(query_question)

    # get vector string(encoded string)
    query_vector_str ='[' + ','.join(str(x) for x in query_vector) + ']'

    return query_vector_str


# embedding loaded documents
def embed_batch(documents):
    doc_texts = [doc['question'] + ' ' + doc['answer'] for doc in documents]
    batch_size = 50
    batch_vectors = []

    for i in tqdm(range(0, len(doc_texts), batch_size)):
        batch = doc_texts[i:i + batch_size]
        batch_vector = EMBEDDER_MODEL.encode(batch)
        batch_vectors.extend(batch_vector)

    return batch_vectors