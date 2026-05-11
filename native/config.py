import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
NATIVE_MEMORY_PATH = Path(os.getenv("BAIUGPT_NATIVE_MEMORY", DATA_DIR / "native_memory.jsonl"))
NATIVE_TRAINING_PATH = Path(os.getenv("BAIUGPT_NATIVE_TRAINING", DATA_DIR / "tubecoach_training.jsonl"))
NATIVE_ENABLED = os.getenv("BAIUGPT_NATIVE_MODE", "true").lower() in {"1", "true", "yes", "on"}
NATIVE_AUTO_ONLINE_LEARN = os.getenv("BAIUGPT_AUTO_ONLINE_LEARN", "true").lower() in {"1", "true", "yes", "on"}


def ensure_native_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NATIVE_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    NATIVE_TRAINING_PATH.parent.mkdir(parents=True, exist_ok=True)
