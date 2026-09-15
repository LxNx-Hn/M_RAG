# 논문 작업 기준과 문서 우선순위

이 폴더는 졸업자격실험보고서 작성에 사용하는 원문 지침과 원고를 저장한다. 아래의 구분은 이후 표·그림·본문·한글 이전본을 만들 때 계속 유지한다.

## 현재 활성 실험 기준

현재 저장된 최종 artifact는 `decoder_main_queries`의 19개 질의-대상문서 쌍, 8개 RAG-Cube 조건, 152개 생성 record다. 현재 결과를 서술하거나 그림과 표를 생성할 때에는 다음 원고와 source artifact를 사용한다.

- `../THESIS_KO_EXPANDED_HWP_READY_CLEAN.md`: 19개 질의 artifact를 근거로 한 확장 원고 기준본
- `../GRADUATION_REPORT_TRANSFER_KO.md`: 한글 양식으로 옮길 현재 작업본
- `../HWP_EQUATION_INPUTS.txt`: 한컴 한글 수식 입력기용 문자열
- `experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`: 생성 source
- `experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json`: 품질 평가 source

## 후속 60-query 확장 기준

`CODEX_MASTER_60Q_TO_HWP_WORKFLOW.md`는 60개의 질의-대상문서 쌍과 480개 생성 record가 실제로 검증된 뒤 활성화하는 실행 순서와 산출물 규격이다. 60-query artifact가 생성·검증되기 전에는 이 문서의 60/480 수치, 표 제목, 그림의 표본 수를 현재 본문에 적용하지 않는다.

60-query 확장 결과가 확정되면 현재 19개 기준 수치·표·그림·사례를 새 artifact 기반으로 일괄 교체하고, 해당 워크플로의 Stage 1부터 Stage 7 검증을 순서대로 수행한다.

## 작성 규칙

- RAG-Cube는 HyDE·CAD·SCD 적용 여부를 조합한 2×2×2 실험 구성명으로 쓴다.
- 본문은 Paper-RAG 실험 파이프라인과 실험 결과를 다루며, 웹 서비스·API·화면 기능은 넣지 않는다.
- 평균, 95% 신뢰구간, win/loss/tie, 조건별 패턴, 실제 저장 입출력 사례를 함께 제시한다.
- 한국어 문자 비율은 출력 언어 유지 지표로, 내용 품질은 대칭 평가로 각각 다룬다.
- 한글 이전본에는 `[스타일=...]` 표시를 유지하고, 수식 번호를 새로 만들지 않는다.
