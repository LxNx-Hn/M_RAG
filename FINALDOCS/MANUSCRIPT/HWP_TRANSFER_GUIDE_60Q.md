# 60-query 한글(HWP) 이전 가이드

이 문서는 `GRADUATION_REPORT_TRANSFER_KO_60Q.md`를 학교 HWP 양식에
옮길 때 사용하는 삽입·스타일 대응표다. 원고의 수치, 답변, 문맥은
수정하지 않는다. 표 제목은 표 위에, 그림 캡션은 그림 아래에 둔다.

## 문서 순서와 스타일

1. 표지, 국문초록, 영문초록, 목차, 그림목차, 표목차는 학교 양식의
   기존 스타일을 사용한다.
2. 원고의 `[스타일=장제목]`, `[스타일=절제목]`, `[스타일=본문]`,
   `[스타일=표제목]`, `[스타일=그림제목]`, `[스타일=참고문헌]` marker에
   맞춰 HWP의 기존 스타일을 적용한다.
3. 장 시작 전에는 새 쪽을 넣고, 표가 분리되면 표 제목과 첫 행이
   같은 쪽에 남도록 한다.
4. 본문은 학교 양식의 10pt와 150~160% 줄간격을 유지한다. 원고 본문
   1장~6장에는 초록·목차·참고문헌·부록을 포함하지 않는다.

## 표 삽입 대응

각 항목은 `[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=<sheet> | 한글 표로 복사]`로 처리한다.

| 본문 위치 | Sheet | 표 제목 |
|---|---|---|
| 3.1 | T3-1_Requirements | 연구 및 실험 요구사항 |
| 3.3 | T3-2_RAG-Cube | RAG-Cube 8개 조건 |
| 3.3 | T3-3_Factor_Position | 실험 요인별 적용 위치와 비교 단위 |
| 4.1 | T4-1_Environment | 실험 실행 환경 |
| 4.1 | T4-2_Backbone | 고정 Paper-RAG backbone |
| 4.3 | T4-3_Runtime | 조건별 평균 생성시간 |
| 4.3 | T4-4_Record_Fields | generation record 주요 필드 |
| 5.1 | T5-1_Dataset | 4개 문서와 60개 질의 분포 |
| 5.3 | T5-2_Config_Scores | 8개 configuration 평균 품질 |
| 5.4 | T5-3_HyDE | HyDE primary 통제 비교 |
| 5.5 | T5-4_CAD | CAD primary 동일 문맥 비교 |
| 5.6 | T5-5_SCD_Config | SCD configuration별 언어 결과 |
| 5.6 | T5-6_SCD_Paired | SCD matched-pair summary |
| 부록 C | Appendix_Paper | 문서별 탐색 집계 |
| 부록 C | Appendix_QueryType | 질문 유형별 탐색 집계 |

## 그림 삽입 대응

아래 항목은 `[그림삽입: FINALDOCS/FIGURES/<filename>.png | 권장폭=본문폭 90% | 정렬=가운데]`로 처리한다.
번호는 그림 파일 내부가 아니라 HWP 그림 제목에서 부여한다.

| 본문 위치 | PNG 파일 | 그림 제목 |
|---|---|---|
| 1장 | fig1_1_research_setting.png | 한국어 질의 기반 영어 학술문서 RAG 연구 환경 |
| 1장 | fig1_2_language_drift_case_a.png | 영어 문맥에서 관찰된 저장 언어 이탈 사례 A |
| 1장 | fig1_3_language_drift_case_b.png | 영어 문맥에서 관찰된 저장 언어 이탈 사례 B |
| 3장 | fig3_1_rag_cube.png | HyDE·CAD·SCD RAG-Cube 8개 조건 |
| 4장 | fig4_1_pipeline.png | 고정 Paper-RAG backbone 실행 흐름 |
| 4장 | fig4_2_artifact_flow.png | generation·evaluation·analysis artifact 흐름 |
| 5.2 | fig5_0_evaluation_design.png | 60-query 평가 및 대응 비교 설계 |
| 5.3 | fig5_1_quality_matrix.png | configuration별 평균 품질 지표 |
| 5.4 | fig5_2_primary_forest.png | HyDE·CAD primary contrast와 신뢰구간 |
| 5.6 | fig5_3_scd_language.png | SCD의 한국어 문자 비율 변화 |
| 5.7 | fig5_4_normal_answer.png | 저장된 정상 QA 사례 |
| 5.7 | fig5_5_scd_language_pair.png | 동일 문맥 SCD OFF·ON 사례 |
| 5.7 | fig5_6_hyde_retrieval_pair.png | HyDE 검색 변경 사례 |
| 5.7 | fig5_7_cad_pair.png | 동일 문맥 CAD positive 사례 |
| 5.7 | fig5_8_cad_lower_case.png | 동일 문맥 CAD trade-off 사례 |
| 5.8 | fig5_9_hyde_cad_strata.png | HyDE·CAD strata별 변화 |
| 5.5 | fig5_10_runtime.png | configuration별 생성 시간 |

## 실제 응답 UI 삽입

아래 파일은 기존 `cli/evidence_replay.py` UI가 60-query 저장 artifact를
read-only로 재현한 화면이다. 답변·점수·문맥을 새로 생성하거나 편집한
이미지가 아니다. 부록 B에는 여섯 화면을 모두 넣고, 본문 1장에는 E02,
5장에는 E01·E03·E04·E05·E06을 각각 필요 위치에 넣는다.

| UI 화면 | 파일 |
|---|---|
| Normal QA | `FINALDOCS/EVIDENCE/UI_REPLAY/E01_normal_qa.png` |
| Language drift | `FINALDOCS/EVIDENCE/UI_REPLAY/E02_language_drift.png` |
| SCD same-context rescue | `FINALDOCS/EVIDENCE/UI_REPLAY/E03_scd_rescue.png` |
| HyDE retrieval change | `FINALDOCS/EVIDENCE/UI_REPLAY/E04_hyde_retrieval_change.png` |
| CAD positive pair | `FINALDOCS/EVIDENCE/UI_REPLAY/E05_cad_positive_same_context.png` |
| CAD trade-off pair | `FINALDOCS/EVIDENCE/UI_REPLAY/E06_cad_tradeoff_same_context.png` |

## 수식

`HWP_EQUATION_INPUTS_60Q.txt`의 각 블록을 HWP 수식 입력기에 그대로
입력한다. 수식에는 장·절 번호를 붙이지 않는다. RAG의 검색/생성 관계,
weighted RRF, CAD score, SCD token score, Korean-character ratio를 이
순서로 배치한다.

## 최종 전송 검토

- 모든 표 제목이 표 위에 있는지 확인한다.
- 모든 그림 제목이 그림 아래에 있는지 확인한다.
- 표·그림 번호와 목차를 HWP 필드 갱신 후 다시 확인한다.
- 5장 수치가 `EXPERIMENT_60_VALIDATION.md` 및 workbook과 일치하는지 확인한다.
- UI 화면의 `Contexts identical`, `Retrieved IDs identical`, `Reranked IDs identical` 표시는
  본문 설명과 일치하는지 확인한다.
