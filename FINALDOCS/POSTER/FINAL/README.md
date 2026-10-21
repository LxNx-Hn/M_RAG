# 질문 유형별 A1 포스터

- `M_RAG_A1_FINAL_EDITABLE.pptx`: A1 세로 594×841 mm. 글 상자와 표 5개는 PowerPoint 기본 개체이고, 파이프라인 도식과 평행좌표는 그림이다.
- `M_RAG_A1_FINAL_PRINT.pdf`, `M_RAG_A1_FINAL_PREVIEW.png`: 설치된 PowerPoint가 PPTX를 직접 렌더링한 인쇄용 PDF와 미리보기.
- `M_RAG_A1_FINAL_EDITABLE.svg`: 같은 PDF에서 만든 벡터 파일. `svg_export.py`가 SVG 내 PNG의 픽셀과 메타데이터를 보존하여 압축 스트림만 다시 기록한다.
- `POSTER_TEXT.json`: 포스터에 배치한 모든 문구. 검사 코드가 PPTX, SVG, PDF에서 같은 문구를 확인한다.
- `poster_pipeline.png`, `poster_parallel.png`: 포스터에 넣은 도식과 방법 질문 25개의 평행좌표(미적용, HyDE, CAD, SCD).

재생성(Windows, PowerPoint 설치 환경):

```powershell
python FINALDOCS/BUILD/build_poster.py --output FINALDOCS/POSTER/FINAL
python -m FINALDOCS.VALIDATION.package_checks --poster
```

구성: 01 연구 배경과 목적 → 02 파이프라인과 실험 조건(조건 번호, 기법별 +와 −, 품질 평가 근거) → 03 질문 60개와 평가 지표 → 04 조건별 평균 점수 → 05 질문 유형별 평균 점수 → 06 단일 기법의 처리 시간 → 07 방법 질문 25개의 조건별 원점수 평행좌표 → 08 결론 → 09 실제 답변에서 확인한 점 → 핵심 참고문헌.

수치는 `FINALDOCS/ANALYSIS/CONDITION_SUMMARY.csv`와 `QUESTION_TYPE_SUMMARY.csv`에서 읽어 소수 둘째 자리로 표시한다. 조건 순서는 논문과 같다(1 미적용, 2 HyDE, 3 CAD, 4 SCD, 5 HyDE+CAD, 6 HyDE+SCD, 7 CAD+SCD, 8 HyDE+CAD+SCD). 표는 흰 바탕이며 열마다 최댓값만 굵게 표시하고, 처리 시간표의 굵은 값은 가장 긴 시간이다. 표준편차와 통계 검정 값은 넣지 않고, 실행 시간은 단일 기법만 제시한다. 문구에는 가운뎃점, 화살표, 콜론 설명을 쓰지 않으며 `poster_checks.py`가 이를 검사한다.

평행좌표는 질문마다 점수가 평균 주위로 크게 흩어지고, 평균에서 멀리 떨어진 질문을 찾아 그 질문의 유형에 맞는 기법을 고르자는 녹취(01:01~01:07)의 의도를 따른다. 0점과 결측값에서는 선을 끊는다.

`POSTER_SCENE.json`, `A1_COPYEDIT_MAP.json`, `PPTX_FINALIZATION_CHECKS.json`, `rebuild_exports.py`는 이전 포스터 생성 방식의 기록이며 현재 포스터에는 쓰이지 않는다. 실물 인쇄 판독은 추가 확인 대상이다.
