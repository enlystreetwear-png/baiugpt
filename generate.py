import torch
import torch.nn as nn

# -------------------------
# Load dataset
# -------------------------

with open("dataset.txt", "r", encoding="utf-8") as f:
    text = f.read()

chars = sorted(list(set(text)))

char_to_id = {ch: i for i, ch in enumerate(chars)}
id_to_char = {i: ch for i, ch in enumerate(chars)}

vocab_size = len(chars)

# -------------------------
# Same Model Structure
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
# Load trained model
# -------------------------

device = "cuda" if torch.cuda.is_available() else "cpu"

model = SimpleModel().to(device)

model.load_state_dict(torch.load("model.pt"))

model.eval()

# -------------------------
# Generate text
# -------------------------

start_text = "h"

generated = start_text

input_ids = torch.tensor(
    [char_to_id[ch] for ch in start_text],
    dtype=torch.long
).to(device)

for _ in range(100):

    output = model(input_ids)

    last_output = output[-1]

    probs = torch.softmax(last_output, dim=0)

    next_id = torch.multinomial(probs, num_samples=1).item()

    next_char = id_to_char[next_id]

    generated += next_char

    input_ids = torch.cat([
        input_ids,
        torch.tensor([next_id]).to(device)
    ])

print(generated)