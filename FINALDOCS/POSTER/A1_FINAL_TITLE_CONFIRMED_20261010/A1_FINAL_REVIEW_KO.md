# A1 포스터 본문 교정 및 출력 동기화

**원제목 유지:** 한국어 질의–영어 학술·기술 문서 RAG에서의 HyDE·CAD·SCD 조합 실험

본문 및 조판 교정 128곳. 제목과 결과 수치를 유지하고 좌표와 글자 크기를 조정하였다. 참고문헌 22편과 사례 전체는 동봉 파일에 보존하였다.
SVG와 PPTX에서 원문 A를 수정문 B로 교체한 뒤, PDF와 PNG를 수정된 SVG에서 출력하였다.

| 번호 | 원문 A | 수정문 B |
|---|---|---|
|1|문종건 · [학번] · 동국대학교 WISE 캠퍼스 컴퓨터공학과 · 지도교수 김진석 · 2026.10.15|문종건 · 동국대학교 WISE 캠퍼스 컴퓨터공학과 · 지도교수 김진석 · 2026.10.15|
|2|01 연구 배경과 선행연구: 한국어 질의–영어 문서|01 연구 배경과 선행연구|
|3|03 RAG-Cube 실험 설계: 같은 질의에 8조건 적용|03 RAG-Cube 실험 설계|
|4|04 평가 방법: 답변 품질과 출력 언어의 대응 비교|04 평가 방법|
|5|05 실험 결과: 세 기법의 적용 전후 변화|05 실험 결과|
|6|06 실제 출력: 질의별 적용 전후 비교|06 실제 출력: 개선과 감소 사례|
|7|07 결론: 기법별 결과와 조건 선택|07 결론|
|8|한국어 질문으로 영어 문서를 검색할 때의 쟁점|한국어 질의로 영어 문서를 검색하는 RAG|
|9|한국어 질문과 영어 원문의 표현 차이에 따른 검색 결과 비교|한국어 질의로 영어 문서를 검색했을 때의 검색 결과 분석|
|10|근거 충실도와 한국어 문자 비율을 각각 측정|답변 품질과 한국어 문자 비율을 각각 측정|
|11|HyDE의 검색 결과, CAD의 답변 품질, SCD의 출력 언어 비교|HyDE의 검색, CAD의 생성, SCD의 출력 언어 비교|
|12|관련 연구: DPR[11], FiD[12], 긴 문맥[9], Self-RAG와 CRAG[15,16]||
|13|같은 문맥에서 CAD 적용 전후 답변 품질과 실행 시간은 어떻게 달라지는가|같은 문맥에서 CAD 적용 전후 답변 품질과
실행 시간은 어떻게 달라지는가|
|14|답변 품질, 한국어 문자 비율과 실행 시간으로 어떤 조건을 선택하는가|평가 목적에 따라 답변 품질, 한국어 문자 비율과
실행 시간을 어떻게 비교할 것인가|
|15|관련 문맥을 검색하고 생성 모델에 입력하여 답변 생성|검색 문맥을 생성 모델에 입력하여 답변 생성
검색 및 생성 모델은 모든 조건에서 고정|
|16|Paper-RAG의 검색과 생성 모델은 모든 조건에서 고정||
|17|한국어 질의를 영어로 번역해 가상 문서를 생성하고 벡터화|영어 번역 질의로 가상 문서 생성 후 밀집 검색
BM25와 재정렬은 원래 한국어 질의 사용|
|18|가상 문서 벡터로 밀집 검색, BM25와 재정렬은 한국어 질의 사용||
|19|같은 모델에서 문맥을 포함한 입력과 제외한 입력의 로짓 계산|문맥 포함·제외 입력의 로짓을 가중 결합
(1+α)z_ctx - αz_noctx, α=0.5|
|20|로짓을 (1+α)z_ctx - αz_noctx로 가중 결합||
|21|한국어와 다른 언어 토큰의 로짓에 각각 계수를 곱함|한국어 로짓×1.1, 다른 언어×0.9
중립 토큰과 첫 5토큰 유지|
|22|한국어 로짓×1.1, 다른 언어×0.9. 중립 토큰과 첫 5토큰 유지||
|23|초기 질문 3개로 표현과 범위 설정 → LLM으로 각 문서 주요 내용 요약|초기 질문 3개로 범위 설정, 문서별 주요 내용 요약
요약 내용을 15개 단위로 나누어 질의 작성
→ 총 60개 질의의 원문 근거 확인|
|24|요약 15개 단위에서 질의 작성 → 문서별 15개, 총 60개 근거 확인||
|25|BGE-M3 + BM25 / RRF 가중치 0.6/0.4, k=60|BGE-M3 + BM25, RRF 가중치 0.6/0.4, k=60|
|26|cross-encoder/ms-marco-MiniLM-L-6-v2 / K-intelligence/Midm-2.0-Base-Instruct|MiniLM-L-6-v2 / Midm-2.0-Base-Instruct|
|27|검색 8개, 재정렬 8개, 문맥 5개; 청크 최대 512, 중첩 64, 최소 50단어|검색 8개, 재정렬 8개, 문맥 5개 / 512단어, 중첩 64|
|28|문맥 3,072단어 초과 시 압축(0.5); 탐욕적 디코딩, 최대 512토큰|문맥 3,072단어 초과 시 압축 / 탐욕적 디코딩, 512토큰|
|29|생성 답변이 질문의 요구에 대응하는 정도|답변이 질문의 요구에 대응하는 정도|
|30|정답에 필요한 근거가 검색 문맥에 포함된 정도|정답의 근거가 검색 문맥에 포함된 정도|
|31|영어 문맥을 gpt-4o로 한국어 번역한 뒤 RAGAS 평가|영어 문맥을 gpt-4o로 한국어 번역하여 평가|
|32|비교 조건과 목적|비교 조건|
|33|검색과 재정렬 청크 ID, 최종 문맥 동일|검색 청크와 최종 문맥 동일|
|34|60쌍, 충실도 58쌍|60쌍
충실도 58쌍|
|35|주 비교 HyDE OFF 동일 문맥 / 전체 H/C 상태 일치|HyDE OFF 동일 문맥 / H·C 상태 일치|
|36|120 / 240쌍|주 120쌍
전체 240쌍|
|37|비교 조건(쌍수)|비교 조건|
|38|HyDE 답변 관련성|HyDE
답변 관련성|
|39|CAD와 SCD OFF, 60쌍|CAD·SCD OFF
60쌍|
|40|CAD 근거 충실도|CAD
근거 충실도|
|41|HyDE와 SCD OFF, 58쌍|HyDE·SCD OFF
58쌍|
|42|SCD 한국어 비율|SCD
한국어 비율|
|43|HyDE OFF 동일 문맥, 120쌍|HyDE OFF 동일 문맥
주 비교 120쌍|
|44|HyDE와 CAD 상태 일치, 240쌍|H·C 상태 일치
전체 240쌍|
|45|HyDE의 다른 지표: 충실도 +0.0436, 정밀도 -0.0343, 재현율 0||
|46|CAD 두 지표의 95% 구간은 0 포함. 관련성 -0.0073 [-0.0855, +0.0719]|CAD 신뢰구간은 0 포함|
|47|질의, 답변, 검색 문맥과 참조 답변으로 품질 평가. 한국어 문자 비율 별도 측정|RAGAS[10] 0.2.15: gpt-4o / 관련성 임베딩 BGE-M3|
|48|RAGAS[10] 0.2.15: 평가 gpt-4o, 답변 관련성 임베딩 BGE-M3||
|49|답변 생성에는 영어 문맥을 사용하며, 저장된 답변은 그대로 평가|생성에는 영어 문맥 사용. 저장 답변을 그대로 평가.|
|50|SCD ON/OFF의 RAGAS 평균은 평가 문맥 언어가 달라 각각 제시|SCD의 RAGAS 평균은 평가 문맥 언어별로 제시.|
|51|HyDE OFF의 동일 문맥 120쌍을 주 비교로 사용. 전체 240쌍도 집계||
|52|한글과 ASCII 영문자 수로 계산. 논문명과 모델명의 영어 표기도 포함||
|53|RAGAS 평가값 1,920개 중 1,915개 유효. 근거 충실도 5개 결측|평가값 1,920개 중 1,915개 유효, 충실도 5개 결측|
|54|평균 변화는 ON - OFF, 질의 단위 대응 부트스트랩 200,000회|ON − OFF / 95% CI: 대응 부트스트랩 200,000회|
|55|문서 4종 고정, seed=20260713. 질의 단위 95% 신뢰구간||
|56|HyDE ext_midm_004 (문맥 변경)|CAD track1_0012 (동일 문맥)|
|57|한국어 멀티턴 대화 데이터의 설계 차원 3가지|H0C0S0 → H0C1S0: 충실도 0.9375→0.5|
|58|H0C0S0 → H1C0S0|OFF “외부 지식 활용의 우수성” / ON “위 내용 참조”|
|59|관련성 0→0.8531, 재현율 0→1|SCD ext_midm_005 (동일 문맥)|
|60|OFF “구체적인 정보를 확인할 수 없습니다”|H1C0S0 → H1C0S1: 한국어 문자 비율 0→0.7713|
|61|ON “상호작용 구조” 등 세 기준 제시|S0 “tasks such as math problems”|
|62|CAD ext_midm_001 (동일 문맥)|S1 “우리는 정기적인 간격으로”|
|63|Mi:dm K 2.5 Pro 데이터 확보 경로|이 SCD 사례는 전체 240쌍에 포함. 주 비교는 H0 120쌍.|
|64|H0C0S0 → H0C1S0||
|65|충실도 0.8333→1, 관련성 0.8261→0.8124||
|66|라이선스 자료, 상업 이용 가능 공개 자료, 자체 합성 자료||
|67|ON “라이선스 취득 전용 데이터셋”||
|68|CAD track1_0012 (동일 문맥)||
|69|RAG가 지식 집약적 작업에 유리한 이유||
|70|충실도 0.9375→0.5, 관련성 0.9001→0||
|71|OFF “외부 지식 활용의 우수성”||
|72|ON “위 내용 참조”||
|73|SCD ext_midm_005 (동일 문맥)||
|74|Fusion SFT의 비추론(non-reasoning) 학습 목적||
|75|H1C0S0 → H1C0S1||
|76|한국어 문자 비율 0→0.7713||
|77|S0 “tasks such as math problems”||
|78|S1 “우리는 정기적인 간격으로”||
|79|CAD 사례는 동일 문맥 비교. SCD 사례는 답변 언어의 변화 비교||
|80|HyDE ON의 SCD 사례는 전체 240쌍에 포함. 주 비교는 HyDE OFF 120쌍||
|81|08 참고문헌|08 주요 참고문헌|
|82|[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” Advances|[1] Lewis et al. RAG. NeurIPS, 2020.|
|83|in Neural Information Processing Systems, Vol. 33, 2020.|[2] Gao et al. HyDE. ACL, 2023.|
|84|[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” Proceedings of ACL,|[3] Shi et al. Context-Aware Decoding. NAACL, 2024.|
|85|pp. 1762–1777, 2023.|[4] Li et al. Language Drift and SCD. AAAI, 2026.|
|86|[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,”|[5] Chen et al. M3-Embedding. ACL Findings, 2024.|
|87|Proceedings of NAACL, pp. 783–791, 2024.|[10] Es et al. RAGAs. EACL Demonstrations, 2024.|
|88|[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation:|전체 22편과 모델 출처: 동봉 참고문헌 파일 및 졸업논문|
|89|Characterization and Decoding-Time Mitigation,” Proceedings of the AAAI Conference on Artificial||
|90|Intelligence, Vol. 40, No. 37, pp. 31519–31526, 2026.||
|91|[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text||
|92|Embeddings Through Self-Knowledge Distillation,” Findings of the Association for Computational||
|93|Linguistics: ACL 2024, pp. 2318–2335, 2024, doi: 10.18653/v1/2024.findings-acl.137.||
|94|[6] S. E. Robertson et al., “Okapi at TREC-3,” Text REtrieval Conference, 1994.||
|95|[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet||
|96|and Individual Rank Learning Methods,” Proceedings of SIGIR, pp. 758–759, 2009.||
|97|[8] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.||
|98|[9] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” Transactions of||
|99|the Association for Computational Linguistics, Vol. 12, pp. 157–173, 2024.||
|100|[10] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” Proceedings||
|101|of EACL System Demonstrations, pp. 150–158, 2024.||
|102|[11] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,”||
|103|Proceedings of EMNLP, pp. 6769–6781, 2020.||
|104|[12] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open||
|105|Domain Question Answering,” Proceedings of EACL, pp. 874–880, 2021.||
|106|[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,”||
|107|Proceedings of ACL, pp. 12286–12312, 2023.||
|108|[14] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,”||
|109|Proceedings of ICLR, 2024.||
|110|[15] A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,”||
|111|[16] S.-Q. Yan et al., “Corrective Retrieval Augmented Generation,” arXiv:2401.15884, 2024.||
|112|[17] P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” Data||
|113|Science and Engineering, Vol. 11, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5.||
|114|[18] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026.||
|115|[19] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,”||
|116|arXiv:2312.10997, 2023.||
|117|[20] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information||
|118|Retrieval Models,” Proceedings of NeurIPS Datasets and Benchmarks Track, 2021.||
|119|[21] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” Proceedings of EACL, pp.||
|120|2014–2037, 2023.||
|121|[22] KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” technical report, arXiv:2603.18788v2, 2026.||
|122|HyDE 적용 후 답변 관련성이 평균 +0.0805 증가|HyDE 적용 후 답변 관련성 평균 +0.0805|
|123|CAD 근거 충실도 평균 대응 차이 +0.0288. 95% 신뢰구간은 0 포함|CAD 근거 충실도 평균 +0.0288, 신뢰구간은 0 포함|
|124|H0S0에서 CAD 조건 실행 시간은 20.792초에서 63.867초로 증가|H0S0의 CAD 실행 시간: 20.792초 → 63.867초|
|125|SCD 한국어 문자 비율은 HyDE OFF 동일 문맥 120쌍에서 평균 +0.2182 증가|SCD: H0 동일 문맥 120쌍에서 한국어 비율 +0.2182|
|126|답변 관련성, 근거 충실도, 한국어 문자 비율과 실행 시간으로 조건 선택|평가 목적에 따라 답변 품질, 한국어 비율과 시간 비교|
|127|평가 범위: 영어 문서 4종, 한국어 질의 60개, 생성 모델 1종과 자동 평가|영어 문서 4종, 한국어 질의 60개, 생성 모델 1종|
|128|질의 유형: 사실 및 정의 8, 방법 및 절차 29, 결과 및 비교 20, 목적 및 기여 3||

## 동기화 검증
- 승인 제목 두 줄 유지; 52pt 제목, 18pt 본문, 16pt 그림 설명과 주요 참고문헌
- PPTX의 최종 교정문 128건 일치; 이번 재빌드에서 교체한 원문 0건
- PDF는 A1 비율의 단일 페이지
- 300dpi PNG는 7016 × 9933 픽셀
- PDF SHA-256: 114d1557f159bcbf96fc7fe9b53882818a1ee83e55f0e307212de1f4e59d6b04
- 실제 인쇄소의 색상과 재단은 현장 확인 필요
