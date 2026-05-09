import sentencepiece as spm

# Train SentencePiece tokenizer
spm.SentencePieceTrainer.train(

    input='data/stories.txt',

    model_prefix='bpe',

    vocab_size=8000,

    character_coverage=1.0,

    model_type='bpe'
)

print("Tokenizer trained!")