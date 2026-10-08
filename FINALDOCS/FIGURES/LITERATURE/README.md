# 제2장 문헌 그림 최종 출처·라이선스 감사

2026-10-09, 시작 HEAD `edde589b8434b3ecea919ba1143600326a10a4a6`. 최종 HWPX에서 사용한 6개 이미지와 공식 출판 자료를 대조하였다. 교체된 이전 PNG 4개는 이력 보존용이며 제출본에는 삽입하지 않는다. 그림 수 22개 체계는 유지한다.

## 최종 처리 상태

| 그림 | 저자·논문 | 실제 사용 버전·원본 번호 | 실제 PNG | 상태 |
|---|---|---|---|---|
| 2-1 | Patrick Lewis 외, *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | NeurIPS 2020, concept reference only; Figure 1 (concept only) | `fig2_1_rag_independent.png` | INDEPENDENT_DIAGRAM |
| 2-2 | Nelson F. Liu 외, *Lost in the Middle: How Language Models Use Long Contexts* | TACL 2024, 12:157–173; PDF page 2 (printed 158); Figure 1 | `fig2_2_lost_middle_tacl.png` | CC_BY_4_0 |
| 2-3 | Luyu Gao 외, *Precise Zero-Shot Dense Retrieval without Relevance Labels* | ACL 2023, 1762–1777; PDF page 2 (printed 1763); Figure 1 | `fig2_3_hyde_acl_no_logo.png` | CC_BY_4_0_ADAPTED |
| 2-4 | Weijia Shi 외, *Trusting Your Evidence: Hallucinate Less with Context-aware Decoding* | NAACL 2024 short, PDF page 1; Figure 1 | `fig2_4_cad_original.png` | CC_BY_4_0 |
| 2-5 | Bo Li 외, *Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation* | arXiv:2511.09984v1, PDF page 1; Figure 1 | `fig2_5_scd_no_logos.png` | CC_BY_4_0_ADAPTED |
| 2-6 | Shahul Es 외, *Ragas: Automated Evaluation of Retrieval Augmented Generation* | arXiv:2309.15217v2, PDF page 8; Table 2 | `fig2_6_ragas_faithfulness_original.png` | CC_BY_4_0 |

## 공식 이용 조건과 확인 범위

RAG: [NeurIPS 공식 FAQ](https://neurips.cc/FAQ)는 저작권을 저자가 보유하고 NeurIPS에 비독점 이용 허락을 준다고 설명한다. [정식 논문](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)과 PDF, arXiv 공개 조건에서 제3자에게 적용되는 일반 그림 재사용 허락을 확인하지 못하였다. 확인되지 않은 법적 예외를 적용하지 않고, 검색·문맥·생성을 설명하는 독립 데이터 흐름 도식을 제작하였다. 원 그림의 예시, 색상, 도형 배치와 문구를 복제하지 않았으며 원 논문은 개념 근거로 인용하였다. 별도 허락 요청이나 저자에게 메시지를 보내지 않았다.

Liu: [TACL 정식 PDF](https://aclanthology.org/2024.tacl-1.9.pdf)의 첫 쪽(인쇄 157쪽)에 © 2024 ACL 및 CC-BY 4.0 고지가 있다. [MIT Press 정식 페이지](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long)는 도구에서 열리지 않아 ACL이 배포하는 동일 DOI의 정식 출판 PDF를 근거로 사용하였다. arXiv 그림 1과 출판 PDF 2쪽(인쇄 158쪽)의 그림 1을 대조하였다. 20개 문서 위치, Accuracy 축, 1st/5th/10th/15th/20th 표기, GPT-3.5-turbo-0613 및 closed-book 범례, U자 곡선과 약 56.1% 기준선이 일치한다. 출판본의 위치·조판·크기는 다르므로 파일 바이트 동일성을 주장하지 않는다. PNG는 출판본의 도표만 다시 발췌하였다. 별도의 원자료 수치 파일을 복원하거나 추정하지 않았다.

Gao: [ACL 2023 정식 PDF](https://aclanthology.org/2023.acl-long.99.pdf)와 [ACL 공식 저작권 안내](https://aclanthology.org/faq/copyright/)를 확인하였다. ACL의 2016년 이후 자료에는 CC BY 4.0이 적용되며 제3자 자료는 제외된다는 고지를 구별하였다. 두 버전의 그림 1에서 질문 3개, 지시문, 생성 문서, 실제 문서, GPT→Contriever 흐름, 화살표, 색상 범례와 예시가 일치한다. 원 영어 캡션은 arXiv판의 GPT-3에서 정식판의 InstructGPT로 달라졌다. 영어 원 캡션을 제외하고 정식 출판본의 도식·범례만 발췌하였다.

HyDE의 OpenAI 로고는 별도 권리 요소다. [공식 브랜드 안내](https://openai.com/brand/)는 로고와 상표의 권리 및 사용 조건을 제시한다. 이 학위논문의 제3자 로고 사용 허락을 독립적으로 확정하지 않고, PDF의 로고 영역만 같은 배경색으로 덮은 후 그림을 렌더링하였다. 최종 PNG에는 로고가 없으며 GPT라는 방법 설명 표기·모든 연결 화살표·예시는 유지하였다. 로고 생략과 잘라내기를 출처 문단에 명시하였다. ACL 라이선스가 OpenAI 로고의 권리를 부여한다고 주장하지 않는다.

Shi: NAACL 2024 정식 출판 PDF 그림 1, Li: arXiv:2511.09984v1 그림 1, Es: arXiv:2309.15217v2 표 2를 다시 대조하였다. [SCD arXiv 라이선스 링크](https://arxiv.org/abs/2511.09984v1)와 [RAGAS arXiv 라이선스 링크](https://arxiv.org/abs/2309.15217v2)는 CC BY 4.0을 가리킨다. 기존 잘라내기 좌표로 렌더링한 결과는 각 기존 PNG와 SHA-256이 정확히 같았다. CAD·RAGAS 발췌 영역은 변경하지 않았다. SCD의 확대 검토에서 OpenAI·Ollama 로고를 확인하여 최종 발췌에서는 두 로고를 생략하고 제목 상단을 포함하도록 범위를 보완하였다. 질의·문맥·추론·언어 이탈 예시와 처리 화살표는 유지하였다. RAGAS는 원본이 표 2라는 사실을 유지하였다.

[CC BY 4.0 조건](https://creativecommons.org/licenses/by/4.0/)에 따라 저자·논문은 본문 인용번호와 참고문헌 및 아래 버전 기록으로 연결하고, 원본 객체 번호·PDF 위치·라이선스 링크·잘라내기와 로고 생략을 본문 그림 아래에 표시하였다. 법률상 예외나 모든 잠재적 제3자 권리를 일괄 확정하는 법률 의견은 아니다. 최종 삽입 이미지에서 이전의 재사용 근거 미확정 3건은 독립 도식/정식 출판본 발췌로 처리하였다.

## 버전·무결성 기록

`SUBMISSION_PROVENANCE.json`은 6개 이미지의 PDF URL·정확한 버전·PDF 및 PNG SHA-256·처리 상태·본문 출처 문단을 보존한다. 검증기는 최종 삽입 파일, 해시, 출처 및 라이선스 누락을 실패로 처리한다.

`FINALDOCS/BUILD/build_submission_literature.py`는 검토한 PDF의 SHA-256을 먼저 확인한 후 2-2·2-3·2-5를 렌더링하며 네트워크를 호출하지 않는다. 원본 PDF는 공식 URL에서 내려받아 로컬 작업 폴더에서 검토하였다.

| 그림 | PDF SHA-256 | PNG SHA-256 | 대조 결과 |
|---|---|---|---|
| 2-1 | `720f67eb41aa49995d5fcf3d24ac7efe431fbe08ce109b14b5a9fa4d4ebe2f8b` | `c238c249a437150fe7056fc5500d8d00f4b58c70cf1e30ba8add9117c574b7c8` | 원본 배치·도형·문구를 복사하지 않은 2행 데이터 흐름 도식 |
| 2-2 | `f37f6fabe0fe0d8c73b67579cd115dbf14e282cfb7b7af655ae8109638402c9b` | `49f2ca11bd2cbd8763f98f6bb32e8ad948c567a7d09d0470bc60049f837196cc` | 도표 영역만 발췌; 제목·축·범례·20개 위치의 곡선·폐쇄형 기준선 일치. 원 캡션은 정식 본문 캡션으로 분리 |
| 2-3 | `cfc80c2ae284e1a3f36b4cec65122cc06707ac8088f107e43b328906305f609d` | `ffa24e76a1667c1071719e3e4fd4599bd51188c264a89ba9c700a14e20e3fda2` | 도식·예시·색상 범례·GPT/Contriever 표기는 일치. 원 캡션은 GPT-3→InstructGPT로 달라짐. 도식 부분만 발췌하고 OpenAI 로고 생략 |
| 2-4 | `aa1863d571122cda6143861e7f103f22cb47a82b80039392b6f22c31dbd3b355` | `bbb7077db374b7b7508230285fa0702bdb37cabd2ef7c4499b0d6b57ab8ba407` | 재추출 PNG가 기존 PNG와 SHA-256 일치; 잘라낸 영역 내 표기 변경 없음 |
| 2-5 | `1b93d4477ff4e12d936447c2a9f0ee7b55cda56556cfc0094897baf2be3d67ca` | `577b520f6ef85ecf2d19079b0c9a1fd4e60ca7e19a7d8c56d976ed6ad8587608` | 기존 영역 재추출은 기존 PNG와 해시 일치. 최종 사용 이미지에서는 제목 상단을 포함하도록 잘라내기 범위를 보완하고 OpenAI·Ollama 로고만 생략; 질의·문맥·추론 및 언어 이탈 예시 유지. |
| 2-6 | `6c24762a3f277fd120ed1adf34b01420ecf92f18ff6d1b5435fa0a09cb804ecb` | `9480668b571b721d57690d0d02c8e3f41397293ba16ddd3f088d5f543d64ddae` | 재추출 PNG가 기존 PNG와 SHA-256 일치; 원본 표를 이미지로 발췌 |

시각 대조 기록: `FINALDOCS/VALIDATION/LITERATURE_COMPARISON/figure2-2_comparison.png`, `figure2-3_comparison.png`.

## 이전 발췌 기록 — 최종 사용 파일은 위 표를 따름

| File | Source | Source PDF | Page (1-based) | SHA-256 |
|---|---|---|---:|---|
| `fig2_1_rag_original.png` | Lewis et al. [1], Figure 1 | https://arxiv.org/pdf/2005.11401 | 2 | `b2279192b7087f9db474ae883fff991eb778e7d80e4ee658670b3f8c03a28e3e` |
| `fig2_2_lost_middle_original.png` | Liu et al. [12], Figure 1 | https://arxiv.org/pdf/2307.03172 | 1 | `64196278730bece7124299ea3527419e561823ad3f339549c759357ff21c289a` |
| `fig2_3_hyde_original.png` | Gao et al. [2], Figure 1 | https://arxiv.org/pdf/2212.10496 | 2 | `61a374032013a3a246f1347871ec6c5ff24a3cf8e06ce44d63d0a29fa6b65a5f` |
| `fig2_4_cad_original.png` | Shi et al. [3], Figure 1 | https://aclanthology.org/2024.naacl-short.69.pdf | 1 | `bbb7077db374b7b7508230285fa0702bdb37cabd2ef7c4499b0d6b57ab8ba407` |
| `fig2_5_scd_language_drift_original.png` | Li et al. [4], Figure 1 | https://arxiv.org/pdf/2511.09984 | 1 | `6d212c2592d74a45727b0a6fb161da0dccc9e4b23358906c4eba7bb454b2741b` |
| `fig2_6_ragas_faithfulness_original.png` | Es et al. [9], Table 2 | https://arxiv.org/pdf/2309.15217 | 8 | `9480668b571b721d57690d0d02c8e3f41397293ba16ddd3f088d5f543d64ddae` |
