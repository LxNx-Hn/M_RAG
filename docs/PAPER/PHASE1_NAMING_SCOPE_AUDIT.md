# PHASE 1 명칭·범위 감사

## 판정 기준

- `KEEP`: 저장소명, 코드 경로, 실험 artifact, 또는 범위가 정확한 문장으로 유지한다.
- `RENAME_TO_RAG_CUBE`: 2×2×2 조합 실험을 가리키는 연구 명칭을 RAG-Cube로 쓴다.
- `REWRITE_GENERICALLY`: 연구 범위를 과장하지 않는 일반 표현으로 바꾼다.
- `REMOVE_FROM_THESIS`: 서비스 구현을 연구 기여처럼 보이게 하는 본문 표현·RQ·표를 제거한다.
- `APPENDIX_ONLY`: 보존은 필요하지만 논문 본문이 아니라 별도 앱 문서, 증거 원본, 또는 생성 산출물에 둔다.

RAG-Cube는 HyDE, CAD, SCD를 독립적인 이진 요인으로 둔 2×2×2 실험 구성을 가리킨다.

## 본문 원고

| 위치 | 기존 역할 | 판정 | PHASE 1 처리 |
|---|---|---|---|
| `THESIS.md`, `THESIS_KO.md` 제목 | M-RAG 및 시스템 구현을 연구명으로 제시 | `REWRITE_GENERICALLY` | 한국어 질의-영어 학술논문 RAG의 HyDE·CAD·SCD 조합 실험으로 바꿈 |
| 두 원고 초록의 M-RAG·FastAPI·React·A-F 문장 | 서비스 기능을 연구 대상으로 제시 | `REMOVE_FROM_THESIS` | 세 이진 요인과 RAG-Cube 정의로 축소; 초록 전문은 PHASE 4에서 재검토 |
| 두 원고 서론의 연구/서비스 계층 문장 | 서비스와 실험을 하나의 기여로 결합 | `REWRITE_GENERICALLY` | 실험과 결과 해석만 연구 범위로 명시 |
| `THESIS.md` 3.2의 M-RAG 결합 표현 | 고정 검색 구성의 설명 | `REWRITE_GENERICALLY` | fixed backbone으로 변경 |
| 두 원고 RQ5 | A-F 구현을 연구 질문으로 제시 | `REMOVE_FROM_THESIS` | 삭제; RQ1-RQ4는 실험 대비와 직접 대응 |
| 두 원고 6절, `system_overview.svg` 인용 | 연구·서비스 이중 구조 | `RENAME_TO_RAG_CUBE` | 6절을 RAG-Cube 실험 개요로 바꾸고 요인 설계를 인용 |
| 두 원고 12절과 A-F 표 | 서비스 구현 및 경로 정책 | `REMOVE_FROM_THESIS` | 장과 표를 제거하고 이후 장 번호를 앞당김 |
| 두 원고 논의·한계·결론의 M-RAG/서비스 문장 | 서비스의 구조·운영을 연구 결과로 연결 | `REWRITE_GENERICALLY` | 요인별 분석, 실험 한계, 조합별 동작으로 한정 |

## 논문 보조 문서와 그림

| 위치 | 판정 | PHASE 1 처리 또는 이유 |
|---|---|---|
| `docs/PAPER/README.md` | `REWRITE_GENERICALLY` | RAG-Cube 실험 문서와 별도 앱 문서를 구분 |
| `FIGURE_CAPTIONS.md` E01의 M-RAG | `REWRITE_GENERICALLY` | 저장된 한국어 질의-영어 근거 응답 사례로 변경 |
| `EVIDENCE_SCREENSHOT_PLAN.md` C16-C17 | `APPENDIX_ONLY` | A-F 증거를 별도 앱 문서용으로 명시; 논문 본문 절 참조 제거 |
| `figures/system_overview.svg` | `APPENDIX_ONLY` | 서비스 구조도이므로 삭제하지 않고 본문 인용만 제거; PHASE 2에서 RAG-Cube 도식으로 대체 |
| `figures/factorial_design.svg` | `KEEP` | 현재 2×2×2 요인 설계의 임시 본문 도식; PHASE 2에서 cube 도식으로 교체 여부를 결정 |
| `figures/evidence/raw/E01-E08`의 `M-RAG Experimental Result` | `KEEP` | 저장된 증거의 원문 표기이므로 사후 변경하지 않음 |
| `output/application_study/졸업논문_적용실험_교정본.md` | `KEEP` | 이미 기존 기법의 적용·비교로 범위를 제한한 제출용 역사 산출물; 현 PHASE의 본문 재작성 대상이 아님 |
| `scripts/build_submission_docs.py`의 M-RAG 제목·서비스 도식 레이블 | `APPENDIX_ONLY` | 역사적 DOCX 생성기와 생성물의 표기다. 새 논문 구조 확정 뒤 PHASE 3에서 새 출력 계열을 만들지 결정 |

## 저장소·서비스·초안의 예외

| 위치 | 판정 | 이유 |
|---|---|---|
| 루트 `README.md`의 M-RAG, `M_RAG` 경로, 코드 import·배포 경로 | `KEEP` | 저장소와 코드의 역사적 이름이며 논문 실험명으로 바꾸지 않음 |
| 루트 `README.md`의 A-F 기능 설명 | `KEEP` | 제품 README의 서비스 문서이며 논문 본문이 아님 |
| `GUIDE_ORIGINAL.md`, `DOC_SYNC_PLAN_35.md`, `PPT_*`, `LIMITATIONS_AND_FUTURE_WORK.md` | `APPENDIX_ONLY` | 기존 가이드·발표·앱/후속 작업 자료다. 현재 논문 본문으로 인용하지 않음 |
| `ABSTRACT_INTRO_KO_DRAFT.txt`, `RELATED_WORK_APPLICATION_KO_DRAFT.txt`, `JAPANESE_REFERENCE_INSERT_KO.txt`, `figures/application_*.mmd/svg` | `KEEP` | 작업 전부터 미추적이던 사용자 초안/자산이다. PHASE 4-6에서 승인된 문단을 고를 때만 다룬다 |

## 남은 언어 검수 대상

`제안`, `새로운`, `개선`, `향상`, `최적`, `framework`, `architecture`, `integrated`, `proposed`, `novel`, `enhanced`, `optimized`는 PHASE 4-12에서 각 문장의 외부 인용 또는 실험 artifact 근거를 다시 붙여 판정한다. 인용문·원 논문의 원문·저장된 evidence raw 텍스트는 이 규칙의 수정 대상이 아니다.
