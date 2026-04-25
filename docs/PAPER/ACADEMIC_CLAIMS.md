# M-RAG 학술 기여 정리

- 기준일 2026-04-26
- 목적 논문 본문과 발표 자료에서 주장 가능한 범위를 현재 코드 기준으로 고정

## C1 라우트 기반 모듈형 학술 문서 QA 구조

- 주장 질의 의도에 따라 파이프라인을 분기하는 모듈형 RAG 구조를 제시
- 근거 파일 `backend/modules/query_router.py`
- 근거 파일 `backend/pipelines/pipeline_a_simple_qa.py`
- 근거 파일 `backend/pipelines/pipeline_b_section.py`
- 근거 파일 `backend/pipelines/pipeline_c_compare.py`
- 근거 파일 `backend/pipelines/pipeline_d_citation.py`
- 근거 파일 `backend/pipelines/pipeline_e_summary.py`
- 근거 파일 `backend/pipelines/pipeline_f_quiz.py`
- 본문 포인트 단일 검색 경로가 아니라 질문 유형별 조합 경로를 가진다는 점

## C2 하이브리드 검색과 재정렬을 결합한 학술 QA 검색 스택

- 주장 Dense 임베딩, BM25, RRF, reranker, context compression을 결합한 검색 스택을 제공
- 근거 파일 `backend/modules/embedder.py`
- 근거 파일 `backend/modules/hybrid_retriever.py`
- 근거 파일 `backend/modules/reranker.py`
- 근거 파일 `backend/modules/context_compressor.py`
- 본문 포인트 검색 품질 개선을 단일 벡터 검색이 아니라 단계적 검색 조합으로 다룸

## C3 CAD SCD 기반 생성 제어의 통합 적용

- 주장 환각 억제와 언어 이탈 억제를 위한 디코딩 제어를 한국어 학술 QA 흐름에 통합
- 근거 파일 `backend/modules/generator.py`
- 근거 파일 `backend/modules/cad_decoder.py`
- 근거 파일 `backend/modules/scd_decoder.py`
- 본문 포인트 검색 단계와 독립된 생성 단계 제어를 별도 기여로 분리해서 서술

## C4 재현 가능한 로컬 실험 경로와 결과 표 자동화

- 주장 로컬 환경에서 반복 실행 가능한 실험 파이프라인과 표 생성 경로를 제공
- 근거 파일 `backend/evaluation/ablation_study.py`
- 근거 파일 `backend/evaluation/decoder_ablation.py`
- 근거 파일 `backend/evaluation/run_track1.py`
- 근거 파일 `backend/evaluation/run_track2.py`
- 근거 파일 `backend/scripts/master_run.py`
- 근거 파일 `backend/scripts/results_to_markdown.py`
- 본문 포인트 모델 설명만이 아니라 실행과 결과 정리 경로까지 묶인다는 점

## 주장할 때 주의할 표현

- SOTA 라는 표현은 검증 전 사용하지 않음
- 프로덕션 완성이라는 표현은 보안 운영 문서와 분리
- 외부 서비스 전반과의 우열 비교는 정량 근거가 있을 때만 사용
- 미완료 실험 항목은 기대 효과가 아니라 향후 과제로 분리
