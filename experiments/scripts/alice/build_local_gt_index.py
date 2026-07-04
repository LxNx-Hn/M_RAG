"""Build the bare `local_gt__papers` retrieval index on a GPU host.

Mirrors the backend upload pipeline exactly (PDFParser -> SectionDetector ->
Chunker -> Embedder -> VectorStore.add_chunks) and then fits the BM25 index,
writing the BARE collection name that the experiment runners read (the API
path namespaces collections per-user; experiment adapters do not).

Reads the checked-in source paper PDFs only. No GT generation, no OpenAI,
no RAGAS, no query generation.

Usage (on Alice, venv active, HF_HOME/MRAG_CHROMA_DIR exported):
    # full corpus (all checked-in source papers), fresh collection:
    python experiments/scripts/alice/build_local_gt_index.py --reset
    # single paper:
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

DEFAULT_PDF_DIR = ROOT / "data" / "source_papers"
DEFAULT_COLLECTION = "local_gt__papers"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        action="append",
        default=None,
        help="Specific PDF(s) to index; defaults to every PDF in --pdf-dir.",
    )
    parser.add_argument("--pdf-dir", default=str(DEFAULT_PDF_DIR))
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop the collection first so the rebuild is clean.",
    )
    args = parser.parse_args()

    pdf_paths = (
        [Path(p) for p in args.pdf]
        if args.pdf
        else sorted(Path(args.pdf_dir).glob("*.pdf"))
    )
    if not pdf_paths:
        print(f"REFUSED: no source PDFs found in {args.pdf_dir}")
        return 2
    missing = [p for p in pdf_paths if not p.exists()]
    if missing:
        print(f"REFUSED: source PDF not found: {missing}")
        return 2

    from modules.chunker import Chunker
    from modules.embedder import Embedder
    from modules.hybrid_retriever import HybridRetriever
    from modules.pdf_parser import PDFParser
    from modules.section_detector import SectionDetector
    from modules.vector_store import VectorStore

    store = VectorStore()
    if args.reset:
        name = store._sanitize_name(args.collection)
        try:
            store.client.delete_collection(name)
            print(f"reset: dropped collection {name}")
        except Exception as exc:  # noqa: BLE001
            print(f"reset: nothing to drop ({type(exc).__name__})")

    parser_mod = PDFParser()
    detector = SectionDetector()
    chunker = Chunker()
    embedder = Embedder()

    total = 0
    for pdf_path in pdf_paths:
        doc = parser_mod.parse(str(pdf_path))
        doc = detector.detect(doc)
        chunks = chunker.chunk_document(doc)
        print(f"doc_id={doc.doc_id} chunks={len(chunks)}")
        if not chunks:
            print(f"REFUSED: chunker produced no chunks for {pdf_path}.")
            return 2
        embeddings = embedder.embed_texts([c.content for c in chunks])
        store.add_chunks(args.collection, chunks, embeddings)
        total += len(chunks)

    retriever = HybridRetriever(store, embedder)
    retriever.fit_bm25(args.collection)

    collection = store.get_or_create_collection(args.collection)
    print(
        f"collection={args.collection} docs={len(pdf_paths)} count={collection.count()} (added {total})"
    )
    print(f"bm25_available={retriever.has_bm25_for_collection(args.collection)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
