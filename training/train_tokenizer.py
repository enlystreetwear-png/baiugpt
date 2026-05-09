import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input='dataset.txt',
    model_prefix='bpe',
    vocab_size=8000,
    model_type='bpe',
    character_coverage=1.0
)

print("Tokenizer trained!")