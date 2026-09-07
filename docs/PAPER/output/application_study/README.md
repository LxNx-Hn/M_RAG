# 졸업논문 산출물 안내

제출 원고의 기준 파일은 `졸업논문_적용실험_교정본.md`이며, HWP에 옮길 때는 `졸업논문_한글이전용.txt`와 `한글양식_이전안내.txt`를 사용한다.

| 파일 | 용도 |
|---|---|
| 졸업논문_적용실험_교정본.md | 표·그림 참조를 포함한 교정 기준 원고 |
| 졸업논문_한글이전용.txt | HWP 복사용 본문 |
| figures/ | 그림 1-1, 3-1~3-4의 SVG·PNG와 그림 5-1 조회 화면 PNG |
| 앱_기능과_파이프라인.md | 논문과 분리한 앱 기능·코드 경로 설명 |
| 졸업논문_발표요약.pptx | 4:3 비율의 14장 발표 자료 |
| PPT_요약과_발표메모.txt | 슬라이드별 발표 메모 |

원고와 PPT의 실험 서술은 최종 `reference_scd` 조건과 보존된 최종 결과만 사용한다.

재검토 내역과 근거는 [요청사항 검토 기록](../../APPLICATION_STUDY_REVIEW.md)에 정리했다. 작성 과정의 초안은 제출 원고에 포함하지 않는다.

재검증은 저장소 루트에서 `python -X utf8 docs/PAPER/scripts/verify_application_study.py`로 실행한다. 원고 수정 뒤 TXT를 맞추려면 `--sync-text`를 사용한다. 그림은 `build_application_figures.py`, PPT는 `build_application_presentation.mjs`로 다시 만들 수 있다. Node 스크립트는 Codex 번들 런타임을 사용하며 다른 환경에서는 `ARTIFACT_RUNTIME_ROOT`와 `PRESENTATIONS_SKILL_DIR`을 지정한다.
