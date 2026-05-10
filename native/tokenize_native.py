from pathlib import Path

import sentencepiece as spm
import torch

from native.config import PROJECT_ROOT


TOKENIZER_PATH = PROJECT_ROOT / "tokenizer" / "bpe.model"
CORPUS_PATH = PROJECT_ROOT / "datasets" / "native_tubecoach.txt"
TOKENS_PATH = PROJECT_ROOT / "datasets" / "tokens" / "train.pt"


def main():
    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus not found. Run: python -m native.build_training_corpus")

    sp = spm.SentencePieceProcessor()
    sp.load(str(TOKENIZER_PATH))

    text = CORPUS_PATH.read_text(encoding="utf-8")
    tokens = sp.encode(text)
    data = torch.tensor(tokens, dtype=torch.long)

    TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, TOKENS_PATH)

    print(f"Tokenized native training data: {TOKENS_PATH}")
    print(f"Total tokens: {len(data)}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")


if __name__ == "__main__":
    main()

