import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_collection(COLLECTION_NAME)


def retrieve_context(query, top_k=3):
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs = results["documents"][0]

    if not docs:
        return ""

    return "\n\n".join(docs)