import torch
import torch.nn as nn
import torch.optim as optim

# -------------------------
# Load dataset
# -------------------------

with open("dataset.txt", "r", encoding="utf-8") as f:
    text = f.read()

chars = sorted(list(set(text)))

char_to_id = {ch: i for i, ch in enumerate(chars)}
id_to_char = {i: ch for i, ch in enumerate(chars)}

vocab_size = len(chars)

# Encode dataset
data = torch.tensor([char_to_id[ch] for ch in text], dtype=torch.long)

# -------------------------
# Create training pairs
# -------------------------

x = data[:-1]
y = data[1:]

# -------------------------
# Simple AI Model
# -------------------------

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, 32)
        self.linear = nn.Linear(32, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        x = self.linear(x)
        return x

# -------------------------
# GPU Setup
# -------------------------

device = "cuda" if torch.cuda.is_available() else "cpu"

model = SimpleModel().to(device)

x = x.to(device)
y = y.to(device)

# -------------------------
# Training
# -------------------------

optimizer = optim.Adam(model.parameters(), lr=0.01)

loss_fn = nn.CrossEntropyLoss()

for epoch in range(500):

    optimizer.zero_grad()

    output = model(x)

    loss = loss_fn(output, y)

    loss.backward()

    optimizer.step()

    if epoch % 50 == 0:
        print(f"Epoch {epoch} | Loss: {loss.item()}")

# -------------------------
# Save model
# -------------------------

torch.save(model.state_dict(), "model.pt")

print("Training complete!")