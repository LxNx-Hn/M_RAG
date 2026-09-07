# 졸업논문 요청사항 대조 및 검토 기록

검토 대상은 `output/application_study/`의 제출 원고, 이전용 TXT, 그림, 앱 문서, PPT와 발표 메모이다. 본 문서는 작성·검토 기록이며 논문 본문에 포함하지 않는다.

## 요청사항 대조

| 요청 | 반영 및 확인 |
|---|---|
| 학부 졸업논문, 적용 실험 범위 | 초록·1.2절·결론을 영어 학술논문에 대한 한국어 질의응답의 기존 기법 적용 실험으로 정리 |
| 문제→원인→목적→연구 요약의 자연스러운 흐름 | 1.1절에 LLM·RAG, 근거 활용 문제, 언어 차이, 기법 적용 이유, 실험 요약을 연결 |
| CAD는 일반 RAG에도 유용한 기존 기법 | 2.3절에서 Shi 등의 문맥 활용 기법으로 설명하고 해당 응용의 검증 대상으로 한정 |
| 새 알고리즘처럼 보이지 않는 기여 서술 | HyDE·CAD·SCD의 원 제안자를 명시하고 본 연구의 역할을 적용·비교로 기술 |
| 기술 목록보다 완결된 한국어 문장 | 초록·서론·선행연구·해석을 서술형으로 교정; 표에는 비교 가능한 내용만 유지 |
| 다른 저장소와 기존 글 참고 | M_RAG의 기존 국문 원고·README 및 KT-10 README의 구체적 기능 중심 설명을 참고; 작성자 고유 문체를 완벽히 재현했다고 주장하지 않음 |
| 일본어 논문 한 편 | JHARS 원문을 확인하여 RAG의 잔여 환각 근거로 사용; 한·영 검색 손실의 직접 증거로 확대하지 않음 |
| 초반의 간단한 가로형 다이어그램 | 그림 1-1, PPT 6장에 질문→검색→LLM→답변과 HyDE·CAD·SCD 개입 위치 표시 |
| 앱 기능·파이프라인을 별도 문서로 작성 | `앱_기능과_파이프라인.md`에 A–F·기능·코드 근거 정리 |
| HWP 및 두 PDF 모두 참고 | HWP의 장·절, 유스케이스/명세, 아키텍처/클래스/순서도, 구현·실험 결과, 표/그림 위치 반영. 논문 PDF의 서론·초록/참고문헌 구성을 참고. 발표 PDF의 흰 바탕·장 순서·4:3 형식을 참고 |
| HWP는 직접 이전, 분량·발표 시간 제한 없음 | UTF-8 TXT와 PNG/SVG, 이전 안내 제공; PPT는 목차·참고문헌을 포함해 14장 |
| 원고에는 최종 실험 상태만 | 최종 reference_scd α=1.1, β=0.9, Tstart=5와 최종 점수만 서술 |
| 추가 실험 최소화 | 새 답변 생성·번역·채점 호출 없이 보존 자료를 재계산 |

## 재검토에서 고친 내용

- 실험 도식에 섞였던 사용자·관리자·API·A 파이프라인을 제거하고 실제 `main_generation_executor`와 모듈 관계로 갱신했다. 파일을 삭제하지 않고 내용을 수정했다.
- HyDE 가상 문서의 sampling(temperature 0.1, top_p 0.9)과 최종 답변의 greedy를 구분했다. 재정렬 뒤 위치 재배치와 추출형 압축도 구현에 맞춰 설명했다.
- 152건 중 RAG 개요 논문 5질문×8조건의 40건은 BM25 후보가 없고 나머지 112건은 후보 8개였다는 실행 기록을 반영했다. 원인은 확인되지 않았으므로 추정하지 않았다.
- SCD 평가의 생성 후 정규화, 동일 제공자의 두 평가 모델, 한국어 답변 번역 빈도 23/38과 11/38을 한계에 포함했다.
- 실험 대상 문서의 Mi:dm K 2.5 Pro와 생성 모델 Mi:dm 2.0 Base를 구분했다.
- 초기 실행 보고서에만 명시된 A100 80GB 세부 규격을 최종 생성 기록의 하드웨어 정보로 단정하지 않고, 확인 가능한 Alice Cloud GPU 실행으로 기술했다.
- 이전 수치 검증기는 기존 `THESIS.md`와 `THESIS_KO.md`를 대상으로 했다. 새 `verify_application_study.py`는 제출 원고의 표 전체·TXT 동기화·참고문헌 순서·그림 링크·최종 매개변수를 직접 검사하고 SCD 대칭 평가도 재계산한다.
- SVG의 XML 검사에 더해 PNG 렌더링을 직접 확인했다. PPT는 14장을 모두 확인하고 가로형 도식의 화살표 방향을 수정했다. PPTX 구조 검사 통과를 PowerPoint에서의 직접 실행 확인과 동일시하지 않는다.

## 근거 파일

- 생성: `experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`
- HyDE/CAD 점수: `experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json` 중 SCD-off 행
- SCD 언어 분석: `experiments/results/analysis/reference_scd_language_adherence.json`
- SCD 대칭 분석: `experiments/results/analysis/reference_scd_symmetric_gpt4o.json`, `reference_scd_symmetric_gpt41_2025_04_14.json`
- 정규화·한계: `experiments/reports/reference_scd_symmetric_input_audit.md`, `reference_scd_symmetric_cross_judge_report.md`
- 실행 경로: `experiments/runners/main_generation_executor.py`, `backend/modules/query_expander.py`, `reranker.py`, `context_compressor.py`, `scd_decoder.py`
- 질문 분할: `experiments/data/query_splits/decoder_main_queries.json`
- JHARS 원문: https://www.anlp.jp/proceedings/annual_meeting/2025/pdf_dir/Q2-17.pdf
- 기법 원문·서지: https://aclanthology.org/2023.acl-long.99/ , https://aclanthology.org/2024.naacl-short.69/ , https://doi.org/10.1609/aaai.v40i37.40417

## 검증 방법

저장소 루트에서 다음 검사를 수행한다. 수치 재계산은 저장 자료만 읽으며 모델/API를 호출하지 않는다.

```powershell
python -X utf8 docs/PAPER/scripts/verify_current_thesis_results.py
python -X utf8 docs/PAPER/scripts/verify_application_study.py
python -m ruff check docs/PAPER/scripts/build_application_figures.py docs/PAPER/scripts/verify_application_study.py
python -m py_compile docs/PAPER/scripts/build_application_figures.py docs/PAPER/scripts/verify_application_study.py
git diff --cached --check
```

PPT 생성기는 번들 artifact-tool의 패키지·레이아웃·글꼴 검사와 재가져오기 검사를 수행한다. 최종 검증 영수증과 미리보기는 로컬 `tmp/application_review/`에 두며 제출·커밋 대상에 포함하지 않는다. 서비스 코드는 수정하지 않으며 푸시된 커밋의 GitHub CI와 이미지 빌드 결과를 별도로 확인한다.

커밋 전 백엔드 검사에서 로컬 Ruff 0.16.0과 CI의 고정 버전 0.13.0 사이에 검사 결과 차이가 있었다. 임시 가상환경에 CI 버전을 설치해 `python -m ruff check backend`를 실행했으며 통과했다. Black 26.3.1의 백엔드 49개 파일 검사도 통과했다. 커밋 훅은 비활성화하지 않고 동일한 가상환경을 선택해 실행한다.

## 제출자가 채울 정보와 확인 범위

저자·지도교수·제출일·인준 및 최종 페이지 번호는 원본 HWP에서 입력한다. HWP의 글꼴·문단 스타일은 변경하지 않았다. 1.1절의 실제 1쪽 분량과 최종 표·그림 배치는 HWP로 이전한 뒤 확인해야 한다. PDF 예시의 고유 연구 내용과 작성자 정보는 본문에 복사하지 않았다.

질문 19개의 최초 작성자와 최초 작성·사람 검토 절차는 저장 자료만으로 완전히 확인되지 않았다. 원고는 확인된 질문·대상 문서·근거 구절·분할 구성만 서술한다. 이번 문서 작업은 웹 앱의 전체 기능 실행 시험이나 사용자 효과 평가를 대신하지 않는다.
