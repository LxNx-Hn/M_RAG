# 최종 A1 포스터

[인쇄 PDF](M_RAG_A1_FINAL_PRINT.pdf) · [편집 PPTX](M_RAG_A1_FINAL_EDITABLE.pptx) · [벡터 SVG](M_RAG_A1_FINAL_EDITABLE.svg)

594×841mm 세로1쪽, 표4개·159셀·88수치 우측정렬, 표시 문구209단위가 PPTX/SVG/PDF에서 일치한다. 60질의×8조건480기록의 평균SD·반복측정 ANOVA·대응 검정·Holm을 제시한다. 01~08은 배경/목적→처리구조→실험설계→실제평가사례→전체결과/검정→해석→결론→학술/모델출처 순서다. 독립 초록은 선택사항으로 검토했고 사례·평가·결과 지면을 유지하도록 생략했다.

2026-10-18 문체 교정에서5개 텍스트 상자를 수정하고 PPTX·SVG·PDF를 함께 갱신했다. 통계표4개·159셀의 원래 값은 같다. [문구 대조표](../../VALIDATION/PROSE_REVIEW.md#포스터-문구-대조)에 변경 내용을 기록했다. 상세 출처는 [REFERENCES.md](../../VALIDATION/REFERENCES.md), 교수 대응·구획별 이유는 [PROFESSOR_FEEDBACK.md](../../VALIDATION/PROFESSOR_FEEDBACK.md), 실제 사례는 [증빙 명세](../../EVIDENCE/IO_CASES/PRINT_EVIDENCE_MANIFEST.json), 전체 통계는 [권위 JSON](../../DATA/FACTORIAL_STATISTICS_60Q.json)에서 확인한다.

```powershell
python FINALDOCS/POSTER/FINAL/rebuild_exports.py --output tmp/finaldocs/poster
```

이 명령은 현재 원본을 읽어 PDF·미리보기·7016×9933 PNG·해시·ZIP을 임시 폴더에 생성한다. 이들은 재생성 결과이므로 추적하지 않는다. PPTX 구조·재가져오기 검토는 PPTX_FINALIZATION_CHECKS.json에 보존했다. 추가 편집용 [수정 프롬프트](POSTER_REVISION_PROMPT_KO.md)도 유지한다.

실물 인쇄·발표거리·색상, 설치형 PowerPoint에서의 열기·편집은 추가 확인이 필요하다. 인쇄에는 동봉 PDF를 사용한다. 공개본은 학번을 포함하지 않으며 개인 제출본은 저장소 밖에서 관리한다.
