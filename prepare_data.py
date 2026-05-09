import torch
import sentencepiece as spm

# Load tokenizer
sp = spm.SentencePieceProcessor()
sp.load("bpe.model")

# Load dataset
with open("data/stories.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Encode text
tokens = sp.encode(text)

# Convert to tensor
data = torch.tensor(tokens, dtype=torch.long)

# Save tokens
torch.save(data, "train.pt")

print("Dataset tokenized!")
print("Total tokens:", len(data))