from typing import Any, Dict

from native.config import NATIVE_AUTO_REBUILD_DATASET


def rebuild_native_dataset() -> Dict[str, Any]:
    if not NATIVE_AUTO_REBUILD_DATASET:
        return {"status": "skipped", "reason": "BAIUGPT_AUTO_REBUILD_DATASET is disabled"}

    try:
        from native.build_training_corpus import main as build_corpus
        from native.tokenize_native import main as tokenize

        build_corpus()
        tokenize()
        return {"status": "rebuilt"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}

