# app/config.py

TOKENIZER_PATH = "tokenizer/bpe.model"

TRAIN_DATA_PATH = "datasets/tokens/train.pt"

MODEL_DIR = "models"
MODEL_PATH = "models/baiugpt.pt"

CHECKPOINT_DIR = "models/checkpoints"

RAG_DB_PATH = "rag_db"
RAG_COLLECTION_NAME = "baiu_knowledge"

RAW_DATA_DIR = "datasets/raw"
CLEAN_DATA_DIR = "datasets/clean"

BLOCK_SIZE = 256
BATCH_SIZE = 32

N_EMBD = 384
N_HEAD = 6
N_LAYER = 6

DROPOUT = 0.2
LEARNING_RATE = 3e-4

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"