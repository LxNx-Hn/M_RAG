"""Build the bare `local_gt__papers` retrieval index on a GPU host.

Mirrors the backend upload pipeline exactly (PDFParser -> SectionDetector ->
Chunker -> Embedder -> VectorStore.add_chunks) and then fits the BM25 index,
writing the BARE collection name that the experiment runners read (the API
path namespaces collections per-user; experiment adapters do not).

Reads the checked-in source paper PDFs only. No GT generation, no OpenAI,
no RAGAS, no query generation.

Usage (on Alice, venv active, HF_HOME/MRAG_CHROMA_DIR exported):
    python experiments/scripts/alice/build_local_gt_index.py \
        --pdf experiments/data/source_papers/paper_nlp_bge.pdf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # experiments/
REPO = ROOT.parent
BACKEND_DIR = REPO / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

DEFAULT_PDF = ROOT / "data" / "source_papers" / "paper_nlp_bge.pdf"
DEFAULT_COLLECTION = "local_gt__papers"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"REFUSED: source PDF not found: {pdf_path}")
        return 2

    from modules.chunker import Chunker
    from modules.embedder import Embedder
    from modules.hybrid_retriever import HybridRetriever
    from modules.pdf_parser import PDFParser
    from modules.section_detector import SectionDetector
    from modules.vector_store import VectorStore

    doc = PDFParser().parse(str(pdf_path))
    doc = SectionDetector().detect(doc)
    chunks = Chunker().chunk_document(doc)
    print(f"doc_id={doc.doc_id} chunks={len(chunks)}")
    if not chunks:
        print("REFUSED: chunker produced no chunks.")
        return 2

    embedder = Embedder()
    embeddings = embedder.embed_texts([c.content for c in chunks])
    print(f"embeddings shape={getattr(embeddings, 'shape', None)}")

    store = VectorStore()
    store.add_chunks(args.collection, chunks, embeddings)

    retriever = HybridRetriever(store, embedder)
    retriever.fit_bm25(args.collection)

    collection = store.get_or_create_collection(args.collection)
    print(f"collection={args.collection} count={collection.count()}")
    print(f"bm25_available={retriever.has_bm25_for_collection(args.collection)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
