# 최종 A1 포스터

[인쇄 PDF](M_RAG_A1_FINAL_PRINT.pdf) · [편집 PPTX](M_RAG_A1_FINAL_EDITABLE.pptx) · [벡터 SVG](M_RAG_A1_FINAL_EDITABLE.svg)

594×841mm 세로1쪽, 표4개·159셀·88수치 우측정렬, 표시 문구209단위가 PPTX/SVG/PDF에서 일치한다. 60질의×8조건480기록의 평균SD·반복측정 ANOVA·대응 t-검정을 제시하며, p는 다중비교 보정 없는 양측 값이다. 01~08은 배경/목적→처리구조→실험설계→실제평가사례→전체결과/검정→해석→결론→학술/모델출처 순서다. 독립 초록은 선택사항으로 검토했고 사례·평가·결과 지면을 유지하도록 생략했다.

2026-10-18 문체 교정에서5개 텍스트 상자를 수정하고 PPTX·SVG·PDF를 함께 갱신했다. 통계표4개·159셀의 원래 값은 같다. [문구 대조표](../../VALIDATION/PROSE_REVIEW.md#포스터-문구-대조)에 변경 내용을 기록했다. 상세 출처는 [REFERENCES.md](../../VALIDATION/REFERENCES.md), 교수 대응·구획별 이유는 [PROFESSOR_FEEDBACK.md](../../VALIDATION/PROFESSOR_FEEDBACK.md), 실제 사례는 [증빙 명세](../../EVIDENCE/IO_CASES/PRINT_EVIDENCE_MANIFEST.json), 전체 통계는 [권위 JSON](../../DATA/TTEST_ANOVA_60Q.json)에서 확인한다.

2026-10-18 t·ANOVA 개정에서 05~07의 통계 문구와 ANOVA·대응 비교 표를 논문 표 5-3~5-5에 맞췄다. Holm 보정 p와 보정 전·후 열을 없애고 ANOVA는 보정 없는 p, 대응 비교는 p와 dz를 표시한다. 표4개·159셀·88수치 우측정렬과 01~08 배치는 유지했다. 원본은 `FINALDOCS/BUILD/build_academic_poster.mjs`에서 재생성했고, `poster_checks.py`가 표 값을 `build_ttest_anova_tables.py`의 build() 행과 대조한다. 이전 Holm 분석은 [FACTORIAL_STATISTICS_60Q.json](../../DATA/FACTORIAL_STATISTICS_60Q.json)에 이력으로 남아 있다.

```powershell
python FINALDOCS/POSTER/FINAL/rebuild_exports.py --output tmp/finaldocs/poster
```

이 명령은 현재 원본을 읽어 PDF·미리보기·7016×9933 PNG·해시·ZIP을 임시 폴더에 생성한다. 이들은 재생성 결과이므로 추적하지 않는다. PPTX 구조·재가져오기 검토는 PPTX_FINALIZATION_CHECKS.json에 보존했다. 추가 편집용 [수정 프롬프트](POSTER_REVISION_PROMPT_KO.md)도 유지한다.

실물 인쇄·발표거리·색상, 설치형 PowerPoint에서의 열기·편집은 추가 확인이 필요하다. 인쇄에는 동봉 PDF를 사용한다. 공개본은 학번을 포함하지 않으며 개인 제출본은 저장소 밖에서 관리한다.
