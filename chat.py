import chromadb
from sentence_transformers import SentenceTransformer

# =========================
# RAG SETTINGS
# =========================

DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_knowledge"

# =========================
# LOAD EMBEDDING MODEL
# =========================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =========================
# LOAD VECTOR DATABASE
# =========================

client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

# =========================
# RAG SEARCH
# =========================

def search_rag(query, top_k=3):
    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs = results["documents"][0]

    return docs

# =========================
# SIMPLE RAG ANSWER
# =========================

def answer_from_rag(user_question):
    docs = search_rag(user_question)

    context = "\n\n".join(docs)

    # clean output length
    answer = context[:1200]

    return answer

# =========================
# CHAT LOOP
# =========================

print("\nBaiuGPT RAG Chat Started")
print("Type 'exit' to quit\n")

while True:
    user = input("You: ")

    if user.lower() == "exit":
        break

    answer = answer_from_rag(user)

    print("\nBaiuGPT:")
    print(answer)
    print()