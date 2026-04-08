"""
모든 모델을 사전 다운로드하는 스크립트
GPU 서버에서 앱 실행 전 한 번 실행하세요.

Usage:
    python scripts/download_models.py
    python scripts/download_models.py --skip-llm  # LLM 제외 (CPU 환경)
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Download all required models")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM download (CPU environment)")
    args = parser.parse_args()

    print("=" * 60)
    print("M-RAG Model Downloader")
    print("=" * 60)

    # 1. Embedding model
    print("\n[1/3] Downloading BGE-M3 embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-m3")
        test = model.encode(["hello world"])
        print(f"  OK — dimension: {test.shape[1]}")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # 2. Reranker model
    print("\n[2/3] Downloading reranker model...")
    try:
        from sentence_transformers import CrossEncoder
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        score = reranker.predict([("query", "document")])
        print(f"  OK — test score: {score[0]:.4f}")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # 3. LLM
    if args.skip_llm:
        print("\n[3/3] Skipping LLM download (--skip-llm)")
    else:
        print("\n[3/3] Downloading MIDM-2.0-Base-Instruct...")
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                "K-intelligence/Midm-2.0-Base-Instruct",
                trust_remote_code=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                "K-intelligence/Midm-2.0-Base-Instruct",
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )
            print(f"  OK — device: {next(model.parameters()).device}")
            del model, tokenizer
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"  FAILED: {e}")
            print("  (GPU with 24GB+ VRAM required)")

    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
