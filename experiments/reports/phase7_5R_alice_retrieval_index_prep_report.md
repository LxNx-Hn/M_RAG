[Summary]
- phase: Phase 7.5R - Alice retrieval data/index preparation for smoke retry
- readiness before: ready_for_phase7_5_retry_with_patch
- readiness after: ready_for_phase7_5_retry_with_explicit_user_approval
- files created: /tmp/index_bge_for_smoke.py; experiments/reports/phase7_5R_alice_retrieval_index_prep_report.md; runtime copy at /home/elicer/mrag_runtime/data/paper_nlp_bge.pdf; runtime vector/BM25 data under /home/elicer/mrag_runtime/chroma_db
- files modified: /home/elicer/mrag_runtime/chroma_db; experiments/reports/phase7_5R_alice_retrieval_index_prep_report.md
- commit made: no

[Source PDF]
- source path: experiments/data/source_papers/paper_nlp_bge.pdf
- exists: yes
- valid PDF: yes, header starts with %PDF-
- size: 754673 bytes, about 737K by ls

[Runtime Data]
- MRAG_DATA_DIR: /home/elicer/mrag_runtime/data
- MRAG_CHROMA_DIR: /home/elicer/mrag_runtime/chroma_db
- PDF copied to runtime data: yes, /home/elicer/mrag_runtime/data/paper_nlp_bge.pdf
- existing vector store before indexing: previous Phase 7.5 smoke observed context_available=false and 0 chunks for paper_nlp_bge; MRAG_CHROMA_DIR contained only a small chroma.sqlite3 shell before preparation

[Indexing]
- method used: temporary direct vector-store indexer because backend API upload namespaces collections as user_id__collection_name and smoke expects local_gt__papers
- script used: /tmp/index_bge_for_smoke.py
- collection: local_gt__papers
- doc_id: paper_nlp_bge
- chunks indexed: 82
- OpenAI used: no
- RAGAS used: no
- GT regenerated: no

[Verification]
- local_gt__papers exists: yes
- paper_nlp_bge chunk count sample: 5 sample chunks returned; collection total count 82
- context available for smoke: yes, vector-store doc_id filter now returns chunks for paper_nlp_bge
- issues: ONNX Runtime printed CPU affinity warnings during import/model initialization; indexing completed successfully despite these warnings

[Safety]
- tuning run: no
- main experiment run: no
- Phase 7.5 smoke run: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query splits modified: no
- commit made: no

[Decision]
- ready_for_phase7_5_retry_with_explicit_user_approval

[Next Step]
- whether Phase 7.5 retry can start: yes, after explicit user approval
- exact smoke retry scope:
  - 1 tuning query
  - current_defaults
  - hyde_off__no_decoder_control
  - K-intelligence/Midm-2.0-Base-Instruct
  - OpenAI/RAGAS off
  - GT regeneration off
