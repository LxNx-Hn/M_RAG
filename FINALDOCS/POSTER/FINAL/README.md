# 질문 유형별 A1 포스터

- `M_RAG_A1_FINAL_EDITABLE.pptx`: A1 세로 594×841 mm. 글 상자와 표 6개는 PowerPoint 기본 개체이고, 파이프라인 도식과 평행좌표는 그림이다.
- `M_RAG_A1_FINAL_PRINT.pdf`, `M_RAG_A1_FINAL_PREVIEW.png`: 설치된 PowerPoint가 PPTX를 직접 렌더링한 인쇄용 PDF와 미리보기.
- `M_RAG_A1_FINAL_EDITABLE.svg`: 같은 PDF에서 만든 벡터 파일.
- `POSTER_TEXT.json`: 포스터에 배치한 모든 문구. 검사 코드가 PPTX·SVG·PDF에서 같은 문구를 확인한다.
- `poster_pipeline.png`, `poster_parallel.png`: 포스터에 넣은 도식과 평행좌표(60개 질문, 미적용·HyDE).

재생성(Windows, PowerPoint 설치 환경):

```powershell
python FINALDOCS/BUILD/build_poster.py --output FINALDOCS/POSTER/FINAL
python -m FINALDOCS.VALIDATION.package_checks --poster
```

수치는 `FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv`에서 읽어 소수 둘째 자리로 표시한다. 표는 흰 바탕이며 각 비교 범위의 최댓값만 굵게 표시하고, 처리 시간표의 굵은 값은 가장 긴 시간이다. 표준편차와 통계 검정 값은 사용하지 않는다. 실행 시간은 단일 기법(HyDE·CAD·SCD)만 제시한다.

구성: 01 연구 배경과 목적 → 02 파이프라인과 기법 적용 위치(조건 번호와 기법별 +/−) → 03 질문 60개와 평가 지표(무엇을 측정하는지와 값의 방향) → 04 질문 유형별 HyDE의 답변 관련성 → 05 기법을 더했을 때의 변화 → 06 SCD의 한국어 문자 비율 → 07 단일 기법의 처리 시간 → 08 평행좌표 → 09 결론 → 10 실제 답변에서 확인한 점 → 핵심 참고문헌.

`POSTER_SCENE.json`, `A1_COPYEDIT_MAP.json`, `PPTX_FINALIZATION_CHECKS.json`, `rebuild_exports.py`는 이전 포스터 생성 방식의 기록이며 현재 포스터에는 쓰이지 않는다. 실물 인쇄 판독은 추가 확인 대상이다.
