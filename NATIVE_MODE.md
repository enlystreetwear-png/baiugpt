# BaiuGPT Native Mode

BaiuGPT native mode runs locally on your PC. It does not call Claude, OpenAI, Ollama, Qwen, Llama, or any hosted model.

## Run The API

```powershell
cd D:\AIProjects\BaiuGPT
$env:BAIUGPT_NATIVE_MODE="true"
uvicorn server:app --host 0.0.0.0 --port 8000
```

Check native status:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/native/status" `
  -Headers @{ "x-api-key" = "baiu-secret-12345" }
```

If PyTorch can see your RTX 4060, `cudaAvailable` will be `true`.

## Save Feedback So BaiuGPT Learns

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/ai/native-feedback" `
  -Method Post `
  -Headers @{ "x-api-key" = "baiu-secret-12345" } `
  -ContentType "application/json" `
  -Body '{
    "niche":"Tech Reviews",
    "lang":"Tamil",
    "rating":2,
    "question":"Weekly plan was too generic",
    "badOutput":{"title":"AI smartphone features"},
    "betterOutput":{"title":"Foldable phone repair cost test for Tamil buyers"},
    "notes":"Prefer buyer decision, real proof, price, battery, camera, repair cost"
  }'
```

Feedback is saved into:

```text
data/native_memory.jsonl
data/tubecoach_training.jsonl
```

## Train BaiuGPT Weights Locally

The native dataset uses curated online source signals from:

```text
native/source_sites.json
```

These sources are used for short notes, factual signals, URLs, and source-routing examples. Do not copy full copyrighted pages into the training set.

Build a text corpus from saved examples:

```powershell
python -m native.build_training_corpus
```

Tokenize it for the current transformer:

```powershell
python -m native.tokenize_native
```

Train on your PC:

```powershell
python transformer.py
```

Choose `1 = Train`.

The model will use CUDA if PyTorch is installed with NVIDIA support.

## Recommended Next Step

The current native mode gives BaiuGPT local reasoning, feedback memory, and a training path. The next upgrade is to connect `models/baiugpt.pt` directly into `/ai/native-generate` after enough examples are collected.
