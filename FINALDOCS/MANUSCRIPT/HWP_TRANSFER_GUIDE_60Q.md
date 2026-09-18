# 60-query 한글(HWP) 이전 가이드

이 문서는 `GRADUATION_REPORT_TRANSFER_KO_60Q.md`를 학교 HWP 양식에
옮길 때 사용하는 삽입·스타일 대응표다. 원고의 수치·답변·문맥을 유지한
상태로 HWP 배치를 수행한다. 표 제목은 표 위에, 그림 캡션은 그림 아래에 둔다.

## 문서 순서와 스타일

1. 표지, 국문초록, 영문초록, 목차, 그림목차, 표목차는 학교 양식의
   기존 스타일을 사용한다.
2. 원고의 `[스타일=논문제목]`, `[스타일=장(1.)]`, `[스타일=절(1.1)]`,
   `[스타일=본문]`, `[스타일=표제목]`, `[스타일=그림제목]`,
   `[스타일=참고문헌제목]`, `[스타일=참고문헌리스트]`, `[스타일=부록제목]`
   marker에 맞춰 HWP의 기존 스타일을 적용한다. 목차·표/그림목차는
   `[스타일=목차리스트(장)]`, `[스타일=목차리스트(절)]`, `[스타일=표/그림리스트]`를 사용한다.
3. 장 시작 전에는 새 쪽을 넣고, 표가 분리되면 표 제목과 첫 행이
   같은 쪽에 남도록 한다.
4. 본문은 학교 양식의 10pt와 150~160% 줄간격을 유지한다. 본문 분량과
   조판은 1장~6장을 기준으로 확인하고, 초록·목차·참고문헌·부록은 별도 구성한다.

## 표 삽입 대응

각 항목은 `[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=<sheet> | 한글 표로 복사]`로 처리한다.

| 본문 위치 | Sheet | 표 제목 |
|---|---|---|
| 2.7 | T2-1_Related_Work | 관련 연구와 본 실험의 연결 |
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
| 부록 A | Appendix_Queries | 60개 질의-대상문서 쌍 |
| 부록 B | Appendix_Paper | 문서별 탐색 집계 |
| 부록 B | Appendix_QueryType | 질문 유형별 탐색 집계 |

표 5-2 아래에는 다음 주석을 함께 배치한다: `SCD ON 품질 지표는 한국어로 변환된 평가 context를 사용한 configuration-level 기술통계이며, SCD의 주 효과 평가는 표 5-5와 표 5-6의 Korean-character ratio 대응 비교를 사용한다.`

부록 C의 실험 자료 식별 정보는 원고와 `HWP_COPYPASTE_TABLES_60Q.txt`의 탭 구분 블록을 사용한다.

## 그림 삽입 대응

아래 항목은 `[그림삽입: FINALDOCS/FIGURES/<filename>.png | 권장폭=본문폭 90% | 정렬=가운데]`로 처리한다.
번호는 HWP 그림 제목에서 부여한다.

| 본문 위치 | PNG 파일 | 그림 제목 |
|---|---|---|
| 1장 | fig1_1_research_setting.png | 한국어 질의 기반 영어 학술문서 RAG 연구 환경 |
| 2.1 | LITERATURE/fig2_1_rag_original.png | RAG의 retriever–generator 구조 — Lewis et al.[1], Fig. 1 |
| 2.2 | LITERATURE/fig2_2_lost_middle_original.png | 관련 정보 위치에 따른 long-context 성능 변화 — Liu et al.[12], Fig. 1 |
| 2.3 | LITERATURE/fig2_3_hyde_original.png | HyDE의 hypothetical-document retrieval 구조 — Gao et al.[2], Fig. 1 |
| 2.4 | LITERATURE/fig2_4_cad_original.png | Context-Aware Decoding의 분포 대조 구조 — Shi et al.[3], Fig. 1 |
| 2.5 | LITERATURE/fig2_5_scd_language_drift_original.png | 다국어 RAG의 language drift 사례 — Li et al.[4], Fig. 1 |
| 2.6 | LITERATURE/fig2_6_ragas_faithfulness_original.png | RAGAS high/low faithfulness 예시 — Es et al.[9], Table 2 |
| 3장 | fig3_1_rag_cube.png | HyDE·CAD·SCD RAG-Cube 8개 조건 |
| 4장 | fig4_1_pipeline.png | 고정 Paper-RAG backbone 실행 흐름 |
| 4장 | fig4_2_artifact_flow.png | generation·evaluation·analysis artifact 흐름 |
| 5.2 | fig5_0_evaluation_design.png | 60-query 평가 및 대응 비교 설계 |
| 5.3 | fig5_1_quality_matrix.png | configuration별 평균 품질 지표 |
| 5.4 | fig5_2_primary_forest.png | HyDE·CAD primary contrast와 신뢰구간 |
| 5.6 | fig5_3_scd_language.png | SCD의 한국어 문자 비율 변화 |
| 5.8 | fig5_9_hyde_cad_strata.png | HyDE·CAD strata별 변화 |
| 5.5 | fig5_10_runtime.png | configuration별 생성 시간 |

## 대표 입출력 사례 삽입

`FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06은 최종 60-query의 실제 질문·생성 답변·검색 근거·평가값을 함께 제시하는 입출력 사례다. 2장은 선행연구 원문 그림으로 개념을 설명하고, 5장은 본 연구의 입출력 사례를 정량 결과와 연결한다. E04는 5.4절의 HyDE retrieval 변화, E05는 5.5절의 CAD 동일 문맥 faithfulness 차이, E02와 E03은 5.6절에서 각각 SCD OFF의 출력 언어 이탈과 SCD 적용 후 output-language control을 보여준다. E01은 5.7절의 기본 입출력 사례이며, E06은 CAD의 반대 방향 trade-off 사례로 부록 B에 배치한다. `raw/*.txt`는 각 PNG의 텍스트 원본이다.

| 위치 | 파일 | 용도 |
|---|---|---|
| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 근거·답변 변화 사례 |
| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 근거 충실도 차이 사례 |
| 5.6 | E02_language_drift.png | SCD OFF 출력 언어 이탈 관찰 사례 |
| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 언어 이탈 완화 사례 |
| 5.7 | E01_normal_qa.png | 기본 질문·검색·답변·평가 사례 |
| 부록 B | E06_cad_tradeoff_same_context.png | CAD 동일 문맥 trade-off 사례 |
| 부록 B | E01~E06 | 전체 대표 입출력 사례 |


## 수식

`HWP_EQUATION_INPUTS_60Q.txt`의 각 블록을 HWP 수식 입력기에 그대로
입력한다. 수식은 장·절 번호 없이 배치한다. RAG의 검색/생성 관계,
weighted RRF, CAD score, SCD token score, Korean-character ratio를 이
순서로 배치한다.

## 최종 HWP 배치

- 모든 표 제목은 표 위에 배치한다.
- 모든 그림 제목은 그림 아래에 배치한다.
- 표·그림 번호와 목차는 HWP 필드 갱신 결과를 반영한다.
- 표가 쪽을 넘을 때 제목과 첫 행을 같은 쪽에 두고, 부록 A의 60행 표는 이어지는 표로 처리한다.
- 수식은 HWP 수식 입력기의 렌더링 결과로 배치한다.
- 5장 수치는 `EXPERIMENT_60_VALIDATION.md` 및 workbook의 값과 동일하게 유지한다.
