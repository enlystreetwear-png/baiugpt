from sentence_transformers import SentenceTransformer
import chromadb
import os

# =====================================
# SETTINGS
# =====================================

RAW_DATA_FOLDER = "raw_data"
DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_knowledge"

# =====================================
# CHECK RAW DATA FOLDER
# =====================================

if not os.path.exists(RAW_DATA_FOLDER):

    os.makedirs(RAW_DATA_FOLDER)

    print(f"Created folder: {RAW_DATA_FOLDER}")
    print("Put text files inside raw_data/")
    exit()

# =====================================
# LOAD ALL TEXT FILES
# =====================================

all_text = ""

files = os.listdir(RAW_DATA_FOLDER)

if len(files) == 0:

    print("No files found in raw_data/")
    exit()

print("\nLoading files...\n")

for filename in files:

    path = os.path.join(
        RAW_DATA_FOLDER,
        filename
    )

    # only txt files
    if filename.endswith(".txt"):

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                text = f.read()

                all_text += text + "\n"

                print(f"Loaded: {filename}")

        except Exception as e:

            print(f"Failed: {filename}")
            print(e)

# =====================================
# CHECK TEXT
# =====================================

if len(all_text.strip()) == 0:

    print("No text loaded!")
    exit()

print(f"\nTotal characters: {len(all_text)}")

# =====================================
# SPLIT INTO CHUNKS
# =====================================

chunk_size = 500
chunks = []

for i in range(0, len(all_text), chunk_size):

    chunk = all_text[i:i + chunk_size]

    if len(chunk.strip()) > 50:

        chunks.append(chunk)

print(f"Total chunks: {len(chunks)}")

# =====================================
# LOAD EMBEDDING MODEL
# =====================================

print("\nLoading embedding model...\n")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================
# CREATE CHROMA DATABASE
# =====================================

print("Opening database...\n")

client = chromadb.PersistentClient(
    path=DB_PATH
)

# =====================================
# DELETE OLD COLLECTION
# =====================================

try:

    client.delete_collection(
        COLLECTION_NAME
    )

    print("Old collection deleted.")

except:

    print("No old collection found.")

# =====================================
# CREATE NEW COLLECTION
# =====================================

collection = client.create_collection(
    name=COLLECTION_NAME
)

print(f"Created collection: {COLLECTION_NAME}")

# =====================================
# CREATE EMBEDDINGS
# =====================================

print("\nCreating embeddings...\n")

embeddings = model.encode(
    chunks,
    show_progress_bar=True
).tolist()

# =====================================
# STORE INTO DATABASE
# =====================================

print("\nSaving to database...\n")

collection.add(

    embeddings=embeddings,

    documents=chunks,

    ids=[str(i) for i in range(len(chunks))]
)

# =====================================
# VERIFY DATABASE
# =====================================

collections = client.list_collections()

print("\nCollections in DB:")

for c in collections:

    print("-", c.name)

# =====================================
# FINISHED
# =====================================

print("\nRAG database built successfully!")
print(f"Saved at: {DB_PATH}")
print(f"Collection name: {COLLECTION_NAME}")