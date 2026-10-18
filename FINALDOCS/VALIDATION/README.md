# 최종 검증과 근거

한 번에 실행: `python -m FINALDOCS.VALIDATION.validate_all`. 결과는 `tmp/finaldocs/validation/VALIDATION_RESULT.json`에 성공·실패·추가 확인 필요를 구분해 기록한다. 오류가 발생하면 종료코드1이며 통과로 대체하지 않는다.

|책임|구현·자료|검출 범위|
|---|---|---|
|논문 내용·표·출처|manuscript_checks.py, verify_finaldocs_60q.py, TEXT_REVIEW.json|표15/1236셀·그림13·수식11·초록부재·문헌/모델/자료 인용·문장·배치 연결|
|HWPX·학교 양식|../BUILD/verify_thesis_hwpx.py, layout_checks.py|22개 학교 스타일·문단 순서·실제 셀/그림/수식·서론 쪽번호·표지/심사란|
|통계·원자료|analyze_ttest_anova_60q.py, ../BUILD/build_ttest_anova_tables.py, verify_statistics_reproduction.py, print_evidence_checks.py|60질의/480기록/1915유효값/5결측·평균SD·대응t·38 반복측정 ANOVA 효과·효과크기·실제 사례. 본문 표는 TTEST_ANOVA_60Q.json에서 재생성하며, verify_statistics_reproduction.py는 이력 분석(FACTORIAL_STATISTICS_60Q.json)을 재현한다|
|포스터|../BUILD/poster_checks.py, poster_alignment.py, package_checks.py|A1·4편집표159셀/88숫자우측정렬·209문구 PPTX/SVG/PDF 일치·출처|
|제출 패키지|package_checks.py, ARTIFACT_MANIFEST.json|원자료/제출 파일 해시·51쪽 페이지 지도·누락·A1 규격|

`PROSE_REVIEW.md`는 본문 전수 교열·96후보 판정·전체 문장 A→B·문단 재구성·최종 해시, `CURRENT_AUDIT.md`는 현재 판정, `PROFESSOR_FEEDBACK.md`는 전사·추가 메모·관찰/추론·실제 A→B·39개 이전 객체·27개 현재 객체·예상질문18개, `REFERENCES.md/.json`은 출판 검증, `RESEARCH_PROVENANCE.md`는 질의 작성과 자료 가용성·주장 근거다.

`CLEANUP_FILES.csv`는 기준1242파일의 처리·원래SHA·의존 참조·복구 경로를 담는다. `CLEANUP_REPORT.md`는 전후 규모와 검사 기능 대응이다. 이전 파일 복원은 `git show pre-finaldocs-cleanup-20261018:<경로>`로 내용을 확인한 뒤 `git restore --source pre-finaldocs-cleanup-20261018 -- <경로>`로 필요한 파일만 복원한다.

2026-10-18 금지 기준 A→B 전수 교열의 1문장 1행 대조표는 `AB_FULL_REVIEW_20261018.md`, 수정·검증 보고는 `FINAL_REVISION_REPORT_20261018.md`에 있다. 두 문서는 작업 기록이며 논문 본문과 분리한다.
