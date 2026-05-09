from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_collection(
    "baiugpt"
)

query = "What is artificial intelligence?"

embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[embedding],
    n_results=3
)

print(results["documents"][0])