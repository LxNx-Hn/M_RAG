"""
Download runtime models used by the local M-RAG stack.

Usage:
    python scripts/download_models.py
    python scripts/download_models.py --skip-llm
    python scripts/download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import GENERATION_MODEL


def main() -> None:
    parser = argparse.ArgumentParser(description="Download all required models")
    parser.add_argument(
        "--skip-llm", action="store_true", help="Skip LLM download"
    )
    parser.add_argument(
        "--llm-model",
        default=GENERATION_MODEL,
        help="LLM model name to cache locally",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("M-RAG Model Downloader")
    print("=" * 60)

    print("\n[1/3] Downloading BGE-M3 embedding model...")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("BAAI/bge-m3")
        test = model.encode(["hello world"])
        print(f"  OK - dimension: {test.shape[1]}")
    except Exception as exc:
        print(f"  FAILED: {exc}")
        raise SystemExit(1) from exc

    print("\n[2/3] Downloading reranker model...")
    try:
        from sentence_transformers import CrossEncoder

        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        score = reranker.predict([("query", "document")])
        print(f"  OK - test score: {score[0]:.4f}")
    except Exception as exc:
        print(f"  FAILED: {exc}")
        raise SystemExit(1) from exc

    if args.skip_llm:
        print("\n[3/3] Skipping LLM download (--skip-llm)")
    else:
        print(f"\n[3/3] Downloading {args.llm_model}...")
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                args.llm_model,
                trust_remote_code=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                args.llm_model,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )
            print(f"  OK - device: {next(model.parameters()).device}")
            del model, tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception as exc:
            print(f"  FAILED: {exc}")
            if "Base" in args.llm_model and "Mini" not in args.llm_model:
                print("  Base model usually needs a 24GB+ GPU")
            else:
                print("  Mini model usually needs a 12GB-class GPU")
            raise SystemExit(1) from exc

    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
