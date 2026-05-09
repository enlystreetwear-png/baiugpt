import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import sentencepiece as spm

# =====================================
# DEVICE
# =====================================
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

# =====================================
# PATHS
# =====================================
TOKENIZER_PATH = "tokenizer/bpe.model"
TRAIN_DATA_PATH = "datasets/tokens/train.pt"

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "baiugpt.pt")

os.makedirs(MODEL_DIR, exist_ok=True)

# =====================================
# LOAD TOKENIZER
# =====================================
sp = spm.SentencePieceProcessor()
sp.load(TOKENIZER_PATH)

vocab_size = sp.get_piece_size()

print(f"Vocab size: {vocab_size}")

# =====================================
# LOAD TOKENIZED DATA
# =====================================
if os.path.exists(TRAIN_DATA_PATH):

    data = torch.load(TRAIN_DATA_PATH)

    print(f"Training tokens loaded: {len(data)}")

else:

    data = None

    print("train.pt not found")
    print("Chat mode only")

# =====================================
# GPT HYPERPARAMETERS
# =====================================
block_size = 256
batch_size = 32

n_embd = 384
n_head = 6
n_layer = 6

dropout = 0.2

learning_rate = 3e-4

# =====================================
# BATCHING
# =====================================
def get_batch():

    ix = torch.randint(
        len(data) - block_size - 1,
        (batch_size,)
    )

    x = torch.stack([
        data[i:i + block_size]
        for i in ix
    ])

    y = torch.stack([
        data[i + 1:i + block_size + 1]
        for i in ix
    ])

    return x.to(device), y.to(device)

# =====================================
# SELF ATTENTION
# =====================================
class CausalSelfAttention(nn.Module):

    def __init__(self):

        super().__init__()

        self.n_head = n_head
        self.head_size = n_embd // n_head

        self.qkv = nn.Linear(
            n_embd,
            3 * n_embd
        )

        self.proj = nn.Linear(
            n_embd,
            n_embd
        )

        self.dropout = nn.Dropout(dropout)

        self.register_buffer(
            "mask",
            torch.tril(
                torch.ones(
                    block_size,
                    block_size
                )
            )
        )

    def forward(self, x):

        B, T, C = x.shape

        qkv = self.qkv(x)

        q, k, v = qkv.split(C, dim=2)

        q = q.view(
            B,
            T,
            self.n_head,
            self.head_size
        ).transpose(1, 2)

        k = k.view(
            B,
            T,
            self.n_head,
            self.head_size
        ).transpose(1, 2)

        v = v.view(
            B,
            T,
            self.n_head,
            self.head_size
        ).transpose(1, 2)

        att = q @ k.transpose(-2, -1)

        att = att / (self.head_size ** 0.5)

        att = att.masked_fill(
            self.mask[:T, :T] == 0,
            float("-inf")
        )

        att = F.softmax(att, dim=-1)

        att = self.dropout(att)

        out = att @ v

        out = out.transpose(1, 2).contiguous()

        out = out.view(B, T, C)

        out = self.proj(out)

        return out

# =====================================
# FEED FORWARD
# =====================================
class MLP(nn.Module):

    def __init__(self):

        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                n_embd,
                4 * n_embd
            ),

            nn.GELU(),

            nn.Linear(
                4 * n_embd,
                n_embd
            ),

            nn.Dropout(dropout)
        )

    def forward(self, x):

        return self.net(x)

# =====================================
# TRANSFORMER BLOCK
# =====================================
class Block(nn.Module):

    def __init__(self):

        super().__init__()

        self.ln1 = nn.LayerNorm(n_embd)

        self.attn = CausalSelfAttention()

        self.ln2 = nn.LayerNorm(n_embd)

        self.mlp = MLP()

    def forward(self, x):

        x = x + self.attn(self.ln1(x))

        x = x + self.mlp(self.ln2(x))

        return x

# =====================================
# GPT MODEL
# =====================================
class GPT(nn.Module):

    def __init__(self):

        super().__init__()

        self.tok_emb = nn.Embedding(
            vocab_size,
            n_embd
        )

        self.pos_emb = nn.Embedding(
            block_size,
            n_embd
        )

        self.blocks = nn.Sequential(

            *[
                Block()
                for _ in range(n_layer)
            ]

        )

        self.ln_f = nn.LayerNorm(n_embd)

        self.head = nn.Linear(
            n_embd,
            vocab_size
        )

    def forward(self, idx):

        B, T = idx.shape

        tok = self.tok_emb(idx)

        pos = self.pos_emb(
            torch.arange(
                T,
                device=device
            )
        )

        x = tok + pos

        x = self.blocks(x)

        x = self.ln_f(x)

        logits = self.head(x)

        return logits

# =====================================
# INIT MODEL
# =====================================
model = GPT().to(device)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=learning_rate
)

# =====================================
# LOAD EXISTING MODEL
# =====================================
if os.path.exists(MODEL_PATH):

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=device
        )
    )

    print("Loaded existing model")

# =====================================
# GENERATION
# =====================================
@torch.no_grad()
def generate(
    start_text="Hello",
    max_new_tokens=200,
    temperature=0.8,
    top_k=20
):

    model.eval()

    start_ids = sp.encode(start_text)

    context = torch.tensor(
        [start_ids],
        dtype=torch.long,
        device=device
    )

    for _ in range(max_new_tokens):

        idx_cond = context[:, -block_size:]

        logits = model(idx_cond)

        logits = logits[:, -1, :]

        logits = logits / temperature

        topk_logits, topk_idx = torch.topk(
            logits,
            top_k
        )

        probs = F.softmax(
            topk_logits,
            dim=-1
        )

        next_token = torch.multinomial(
            probs,
            1
        )

        next_id = topk_idx.gather(
            -1,
            next_token
        )

        context = torch.cat(
            [context, next_id],
            dim=1
        )

    tokens = context[0].tolist()

    text = sp.decode(tokens)

    return text

# =====================================
# TRAINING
# =====================================
def train_model(total_steps=20000):

    if data is None:

        print("No training data found")
        return

    model.train()

    for step in range(total_steps):

        xb, yb = get_batch()

        logits = model(xb)

        B, T, C = logits.shape

        loss = F.cross_entropy(

            logits.view(B * T, C),

            yb.view(B * T)

        )

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        if step % 100 == 0:

            print(
                f"Step {step} | Loss: {loss.item():.4f}"
            )

        if step % 1000 == 0:

            checkpoint_path = os.path.join(
                MODEL_DIR,
                f"checkpoint_{step}.pt"
            )

            torch.save(
                model.state_dict(),
                checkpoint_path
            )

            print(f"Saved: {checkpoint_path}")

    torch.save(
        model.state_dict(),
        MODEL_PATH
    )

    print("\nModel saved!")

# =====================================
# MAIN
# =====================================
if __name__ == "__main__":

    mode = input(
        "\nChoose mode:\n"
        "1 = Train\n"
        "2 = Chat\n\n"
        "Enter: "
    )

    # =========================
    # TRAIN MODE
    # =========================
    if mode == "1":

        train_model()

        print("\nSample Generation:\n")

        print(generate("The"))

    # =========================
    # CHAT MODE
    # =========================
    elif mode == "2":

        print("\nBaiuGPT Chat Started")
        print("Type 'exit' to quit\n")

        while True:

            prompt = input("You: ")

            if prompt.lower() == "exit":
                break

            response = generate(
                prompt,
                max_new_tokens=120
            )

            print("\nBaiuGPT:", response)
            print()

    else:

        print("Invalid mode")