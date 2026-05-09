import chromadb

DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_research"

client = chromadb.PersistentClient(path=DB_PATH)

try:
    client.delete_collection(COLLECTION_NAME)
    print("Deleted research collection:", COLLECTION_NAME)
except Exception as e:
    print("Collection not found or already deleted:", e)

client.get_or_create_collection(COLLECTION_NAME)

print("Fresh research collection created.")