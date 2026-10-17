# 최종 학술·모델·자료 출처

공식 메타데이터 영수증은 [REFERENCES.json](REFERENCES.json)에 보존한다. 현재 본문 첫 인용 순서22편, M1/M2 모델과 D1–D4 실제 실험PDF를 구분한다.

## 현재 최종 출처 목록


[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, pp. 9459–9474, 2020.

[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023, doi: 10.18653/v1/2023.acl-long.99.

[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024, doi: 10.18653/v1/2024.naacl-short.69.

[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026, doi: 10.1609/aaai.v40i37.40417.

[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 2318–2335, 2024, doi: 10.18653/v1/2024.findings-acl.137.

[6] S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, and M. Gatford, “Okapi at TREC-3,” *Proceedings of the Third Text REtrieval Conference (TREC-3)*, NIST Special Publication 500-225, pp. 109–126, 1995 (conference 1994).

[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009, doi: 10.1145/1571941.1572114.

[8] S. MacAvaney, A. Yates, A. Cohan, and N. Goharian, “CEDR: Contextualized Embeddings for Document Ranking,” *Proceedings of SIGIR*, pp. 1101–1104, 2019, doi: 10.1145/3331184.3331317.

[9] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024, doi: 10.1162/tacl_a_00638.

[10] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024, doi: 10.18653/v1/2024.eacl-demo.16.

[11] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020, doi: 10.18653/v1/2020.emnlp-main.550.

[12] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021, doi: 10.18653/v1/2021.eacl-main.74.

[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023, doi: 10.18653/v1/2023.acl-long.687.

[14] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *Proceedings of ICLR*, 2024.

[15] A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” *Proceedings of ICLR*, 2024.

[16] S. Jeong, J. Baek, S. Cho, S. J. Hwang, and J. Park, “Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity,” *Proceedings of NAACL*, pp. 7036–7050, 2024, doi: 10.18653/v1/2024.naacl-long.389.

[17] P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” *Data Science and Engineering*, Vol. 11, No. 1, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5.

[18] W. Fan et al., “A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models,” *Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining*, pp. 6491–6501, 2024, doi: 10.1145/3637528.3671470.

[19] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021.

[20] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023, doi: 10.18653/v1/2023.eacl-main.148.

[21] P. Dasigi, K. Lo, I. Beltagy, A. Cohan, N. A. Smith, and M. Gardner, “A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers,” *Proceedings of NAACL*, pp. 4599–4610, 2021, doi: 10.18653/v1/2021.naacl-main.365.

[22] M. A. Sultan, J. Ganhotra, and R. F. Astudillo, “Structured Chain-of-Thought Prompting for Few-Shot Generation of Content-Grounded QA Conversations,” *Findings of EMNLP*, pp. 16172–16187, 2024, doi: 10.18653/v1/2024.findings-emnlp.948.

## 실험 사용 모델 및 원문 자료 출처

학술 참고문헌 [1]~[22]는 정식 출판 연구의 근거이며, 아래 모델 카드와 실험 PDF는 구현 및 평가 자료의 출처다.

[M1] KT, K-intelligence/Midm-2.0-Base-Instruct, 공식 모델 카드, https://huggingface.co/K-intelligence/Midm-2.0-Base-Instruct (확인: 2026-10-17). 실행 기록의 생성 모델 ID는 이 모델이며 답변 생성은 greedy, 최대 새 토큰 512개다. 저장 기록의 버전 정보는 모델 ID와 실행 파라미터로 구성된다.

[M2] Sentence Transformers, cross-encoder/ms-marco-MiniLM-L6-v2, 공식 모델 카드, https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 (확인: 2026-10-17). 실행 설정의 모델 문자열은 cross-encoder/ms-marco-MiniLM-L-6-v2이며, 원질의·후보 구간 쌍을 입력하는 CrossEncoder 재정렬에 사용하였다.

[D1] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997. 실험 원문: paper_nlp_rag.pdf.

[D2] W. Shi et al., CAD 논문[3]. 실험 원문: paper_nlp_cad.pdf.

[D3] P. Sarthi et al., RAPTOR 논문[14]. 실험 원문: paper_nlp_raptor.pdf.

[D4] KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” 기업 기술보고서, arXiv:2603.18788v2, 2026, https://arxiv.org/abs/2603.18788v2. 실험 원문: paper_midm.pdf.

D1~D4의 실험 PDF는 저장된 원본 바이트를 사용한다. 문서별 SHA-256과 질의·원문 페이지·정답 근거 대응은 동봉 자료 출처 검증표와 부록 A에서 제시한다.


## 출판 전수 대조와 역할
# 정식 학술 출판 전수 대조 · 2026-10-17

기준: 75c0e9e의 22편. 최종 학술 참고문헌은 정식 출판 22편이며, 모델 M1·M2와 실험 PDF D1~D4는 별도 출처다. 기존 수를 맞추기 위한 유지가 아니라 두 모델·자료 항목의 역할 분리와 QASPER·Sultan의 방법론 추가 결과다.

|기존 번호|기존 A|출판 검증|최종 B|본문 변경|DOI·공식 URL|
|---|---|---|---|---|---|
|1|P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020.|정식 학술대회·학술지 출판 확인|[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, pp. 9459–9474, 2020.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html|
|2|L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023.|정식 학술대회·학술지 출판 확인|[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023, doi: 10.18653/v1/2023.acl-long.99.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2023.acl-long.99/|
|3|W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024.|정식 학술대회·학술지 출판 확인|[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024, doi: 10.18653/v1/2024.naacl-short.69.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2024.naacl-short.69/|
|4|B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026.|정식 학술대회·학술지 출판 확인|[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026, doi: 10.1609/aaai.v40i37.40417.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://ojs.aaai.org/index.php/AAAI/article/view/40417|
|5|J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 2318–2335, 2024, doi: 10.18653/v1/2024.findings-acl.137.|정식 학술대회·학술지 출판 확인|[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 2318–2335, 2024, doi: 10.18653/v1/2024.findings-acl.137.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2024.findings-acl.137/|
|6|S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994.|정식 학술대회·학술지 출판 확인|[6] S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, and M. Gatford, “Okapi at TREC-3,” *Proceedings of the Third Text REtrieval Conference (TREC-3)*, NIST Special Publication 500-225, pp. 109–126, 1995 (conference 1994).|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://trec.nist.gov/pubs/trec3/t3_proceedings.html|
|7|G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009.|정식 학술대회·학술지 출판 확인|[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009, doi: 10.1145/1571941.1572114.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://api.crossref.org/works/10.1145/1571941.1572114|
|8|R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.|기존 프리프린트와 다른 정식 논문으로 교체|[8] S. MacAvaney, A. Yates, A. Cohan, and N. Goharian, “CEDR: Contextualized Embeddings for Document Ranking,” *Proceedings of SIGIR*, pp. 1101–1104, 2019, doi: 10.1145/3331184.3331317.|2.2절을 CEDR의 BERT 분류 벡터·신경 순위 모델 설명으로 수정. 실제 구현은 M2의 MiniLM 쌍 입력 모델.|https://api.crossref.org/works/10.1145/3331184.3331317|
|9|N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024.|정식 학술대회·학술지 출판 확인|[9] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024, doi: 10.1162/tacl_a_00638.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2024.tacl-1.9/|
|10|S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024.|정식 학술대회·학술지 출판 확인|[10] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024, doi: 10.18653/v1/2024.eacl-demo.16.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2024.eacl-demo.16/|
|11|V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020.|정식 학술대회·학술지 출판 확인|[11] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020, doi: 10.18653/v1/2020.emnlp-main.550.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2020.emnlp-main.550/|
|12|G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021.|정식 학술대회·학술지 출판 확인|[12] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021, doi: 10.18653/v1/2021.eacl-main.74.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2021.eacl-main.74/|
|13|X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023.|정식 학술대회·학술지 출판 확인|[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023, doi: 10.18653/v1/2023.acl-long.687.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2023.acl-long.687/|
|14|P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *Proceedings of ICLR*, 2024.|정식 학술대회·학술지 출판 확인|[14] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *Proceedings of ICLR*, 2024.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://proceedings.iclr.cc/paper_files/paper/2024/hash/8a2acd174940dbca361a6398a4f9df91-Abstract-Conference.html|
|15|A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” *Proceedings of ICLR*, 2024.|정식 학술대회·학술지 출판 확인|[15] A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” *Proceedings of ICLR*, 2024.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://proceedings.iclr.cc/paper_files/paper/2024/hash/25f7be9694d7b32d5cc670927b8091e1-Abstract-Conference.html|
|16|S.-Q. Yan et al., “Corrective Retrieval Augmented Generation,” arXiv:2401.15884, 2024.|기존 프리프린트와 다른 정식 논문으로 교체|[16] S. Jeong, J. Baek, S. Cho, S. J. Hwang, and J. Park, “Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity,” *Proceedings of NAACL*, pp. 7036–7050, 2024, doi: 10.18653/v1/2024.naacl-long.389.|2.7절·표2-1을 질문 복잡도 분류 기반 Adaptive-RAG의 검색 전략 선택으로 수정. CRAG의 게재·철회 상태를 확정 게재로 표현하지 않음.|https://aclanthology.org/2024.naacl-long.389/|
|17|P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” *Data Science and Engineering*, Vol. 11, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5.|정식 학술대회·학술지 출판 확인|[17] P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” *Data Science and Engineering*, Vol. 11, No. 1, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://link.springer.com/article/10.1007/s41019-025-00335-5|
|18|D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026.|공식 모델·실험 PDF 출처로 분리|[M1] 공식 모델 카드[M1]|모델은 M1, 실험 원문은 D4. 학술 출판 판정과 구현·자료 출처 역할을 분리.|https://huggingface.co/K-intelligence/Midm-2.0-Base-Instruct|
|19|Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023.|기존 프리프린트와 다른 정식 논문으로 교체|[18] W. Fan et al., “A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models,” *Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining*, pp. 6491–6501, 2024, doi: 10.1145/3637528.3671470.|2.7절을 Fan 등의 아키텍처·학습 전략·응용 분류로 수정. 실제 평가의 Gao 원문 PDF는 D1로 보존.|https://api.crossref.org/works/10.1145/3637528.3671470|
|20|N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021.|정식 학술대회·학술지 출판 확인|[19] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/65b9eea6e1cc6bb9f0cd2a47751a186f-Abstract-round2.html|
|21|N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023.|정식 학술대회·학술지 출판 확인|[20] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023, doi: 10.18653/v1/2023.eacl-main.148.|원 논문 근거 보존; DOI·공식 메타데이터와 서지 대조|https://aclanthology.org/2023.eacl-main.148/|
|22|KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” technical report, arXiv:2603.18788v2, 2026.|공식 모델·실험 PDF 출처로 분리|[D4] 실험 원문 PDF[D4]|모델은 M1, 실험 원문은 D4. 학술 출판 판정과 구현·자료 출처 역할을 분리.|https://arxiv.org/abs/2603.18788v2|

## 추가한 정식 문헌

[21] P. Dasigi, K. Lo, I. Beltagy, A. Cohan, N. A. Smith, and M. Gardner, “A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers,” *Proceedings of NAACL*, pp. 4599–4610, 2021, doi: 10.18653/v1/2021.naacl-main.365.

https://aclanthology.org/2021.naacl-main.365/

[22] M. A. Sultan, J. Ganhotra, and R. F. Astudillo, “Structured Chain-of-Thought Prompting for Few-Shot Generation of Content-Grounded QA Conversations,” *Findings of EMNLP*, pp. 16172–16187, 2024, doi: 10.18653/v1/2024.findings-emnlp.948.

https://aclanthology.org/2024.findings-emnlp.948/

## 확인 범위와 접근 제한

ACM: Direct DL/DOI web fetch failed. Crossref publisher-deposited proceedings-article metadata used with CEDR author publication/code page and Fan author paper. This is a supplementary metadata path, not an assertion that ACM HTML was read.

CRAG: Direct OpenReview page shows browser challenge. No confirmed publication/withdrawal claim is made; distinct formally published Adaptive-RAG supplies the related-work comparison.

model_version: Stored experiment metadata gives generation model ID and parameters, but no weight revision SHA; current official model-card state is kept distinct from experimental revision.

## 보존한 실험 원문

|자료|파일|쪽수|SHA-256|
|---|---|---:|---|
|D1|experiments/data/source_papers/paper_nlp_rag.pdf|21|`396a0fadeb4cd40f5c8ccc36b73a0815f6cb4d7f6bfa53b6c48c1f9aba7c7e02`|
|D2|experiments/data/source_papers/paper_nlp_cad.pdf|8|`c0760ed8c79822961349589934a0b32d9ef07df85eb2fa52f90a6ee13d796deb`|
|D3|experiments/data/source_papers/paper_nlp_raptor.pdf|23|`01319e2e6e6ecfd504ee1bbda41d023f9e060bd3505ab3c161baa1d6d696cf75`|
|D4|experiments/data/source_papers/paper_midm.pdf|39|`32f9e0184f420991b0bedd9c8354d4579be5afb0db7416362a9b9f111a3b76d9`|

D1의 Gao 조사 논문은 실험에 사용한 원본 자료이며 학술 배경의 Fan 조사 논문과 구분한다. D4의 v2 기술보고서도 원문 PDF·질의 15개·정답 근거를 유지했다. 질문 원본과 모델 가중치 버전을 새로 만들어 당시 증빙으로 추가하지 않았다.
