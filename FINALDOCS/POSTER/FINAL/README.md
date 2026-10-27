# 질문 유형별 A1 포스터

- `M_RAG_A1_FINAL_EDITABLE.pptx`: A1 세로 594×841 mm. 글 상자와 표 2개(04 평가 지표 정의표, 05 가로 결과표)는 PowerPoint 기본 개체이고, 파이프라인 도식, 예시 질문 그림, 평행좌표는 그림이다.
- `M_RAG_A1_FINAL_PRINT.pdf`, `M_RAG_A1_FINAL_PREVIEW.png`: 설치된 PowerPoint가 PPTX를 직접 렌더링한 인쇄용 PDF와 미리보기.
- `M_RAG_A1_FINAL_EDITABLE.svg`: 같은 PDF에서 만든 벡터 파일. `svg_export.py`가 SVG 내 PNG의 픽셀과 메타데이터를 보존하여 압축 스트림만 다시 기록한다.
- `POSTER_TEXT.json`: 포스터에 배치한 모든 문구. 검사 코드가 PPTX, SVG, PDF에서 같은 문구를 확인한다.
- `poster_mechanism.png`, `poster_parallel.png`: 포스터에 넣은 예시 질문 그림(`FINALDOCS/ANALYSIS/plot_questions.py`의 `example_mechanism`, 논문 그림 4-2와 같은 원본)과 방법 질문 25개의 평행좌표(미적용, HyDE, CAD, SCD 네 패널을 전체 폭 한 줄로 배치). `poster_pipeline.png`는 02의 파이프라인 도식이다.

제목 아래 학과, 학번, 이름, 지도교수 줄은 공개본에서 [학과] [학번] [이름], 지도교수 [지도교수]로 둔다. 개인 제출본은 저장소 밖 `personal_fields.json`을 `--personal-fields`로 전달하고 출력도 저장소 밖에 둔다.

재생성(Windows, PowerPoint 설치 환경):

```powershell
python FINALDOCS/BUILD/build_poster.py --output FINALDOCS/POSTER/FINAL
python FINALDOCS/BUILD/build_poster.py --layout a --output FINALDOCS/POSTER/VARIANT_A
python -m FINALDOCS.VALIDATION.package_checks --poster
```

제출용 B 구성(`FINAL`, 기본값 `--layout b`): 왼쪽 01 연구 배경과 목적, 오른쪽 02 파이프라인, 03 예시 질문으로 본 단독 기법의 작동(전체 폭 그림, 패널마다 미적용과 단독 적용 조건 비교), 04 질문과 평가(왼쪽 질문과 평가 조건, 오른쪽 평가 지표 정의표), 05 질문 유형별 평균 점수(전체 폭 가로 표), 06 방법 질문 25개의 원점수 평행좌표(전체 폭, 네 조건 패널 한 줄), 07 결론(전체 폭 두 열), 맨 아래 한 줄 참고문헌. 2026-10-21 교수 피드백(그림 중심, 기법별 제안자와 기본 아이디어, 예시 질문의 처리 과정)에 따라 단일 기법 처리 시간 표와 조건별 평균 표를 뺐다. 2026-10-27 교수 피드백에 따라 04에 다섯 지표의 측정 내용과 값의 방향을 정의표로 되살리고(논문 5.2절의 정의, 05 표와 같은 지표 이름과 순서), 질문 이름만으로는 내용과 시사점을 알기 어려운 08 실제 답변 사례를 뺐다. 같은 날 06 그림이 작다는 의견에 따라 06과 07을 각각 전체 폭으로 펼쳐 평행좌표 패널의 세로 높이를 약 두 배로 키웠다.

02 그림은 질문 "Mi:dm K 2.5 Pro 모델의 파라미터 수는 몇 개입니까?"(정답 근거 32B parameters, 원문 2쪽)의 저장된 실행 기록에서 HyDE 가상 구간과 검색 구간, 미적용과 CAD 답변의 수치, 미적용과 SCD 답변의 인용 문장, 세 점수 변화를 읽어 그린다. 사용한 원문과 값은 `FINALDOCS/ANALYSIS/EXAMPLE_MECHANISM.json`에 남기며, 임베딩 점의 위치와 후보 단어의 글자 크기는 원리를 보인 개념도다. 표의 수치는 `FINALDOCS/ANALYSIS/CONDITION_SUMMARY.csv`에서 읽어 소수 둘째 자리로 표시한다. 조건 순서는 논문과 같다(1 미적용, 2 HyDE, 3 CAD, 4 SCD, 5 HyDE+CAD, 6 HyDE+SCD, 7 CAD+SCD, 8 HyDE+CAD+SCD). 05는 다섯 지표를 각각 수치, 방법, 개념과 결과 질문으로 나눈 전체 폭의 가로 표다(논문 표 5-2의 품질 지표와 한국어 문자 비율). 근거 충실도, 문맥 정밀도, 문맥 재현율은 SCD 미적용 조건(영어 검색 결과)과 적용 조건(한국어 번역 검색 결과) 안에서 각각 최댓값을 굵게 표시하고, 답변 관련성과 한국어 문자 비율은 여덟 조건 중 최댓값을 굵게 표시한다. 표시값이 같으면 함께 굵게 표시한다. 표준편차와 통계 검정 값은 넣지 않는다. 문구에는 가운뎃점, 화살표, 콜론 설명을 쓰지 않으며 `poster_checks.py`가 이를 검사한다.

평행좌표는 질문마다 점수가 평균 주위로 크게 흩어지고, 평균에서 멀리 떨어진 질문을 찾아 그 질문의 유형에 맞는 기법을 고르자는 녹취(01:01~01:07)의 의도를 따른다. 0점과 결측값에서는 선을 끊는다.

이전 포스터 생성 방식의 기록(`POSTER_SCENE.json`, `A1_COPYEDIT_MAP.json`, `PPTX_FINALIZATION_CHECKS.json`, `POSTER_REVISION_PROMPT_KO.md`, `rebuild_exports.py`)은 `FINALDOCS/VALIDATION/HISTORY/20261024_legacy_poster_and_audit/POSTER_FINAL/`로 옮겼다. 실물 인쇄 판독은 추가 확인 대상이다.

비교용 A 구성(`FINALDOCS/POSTER/VARIANT_A`, `--layout a`)은 파이프라인 도식 없이 01을 두 열 글머리표로 두고 02 예시 질문 그림부터 06 결론까지 같은 내용과 같은 표 기준을 쓴다. 두 구성 모두 `package_checks --poster`가 검사한다.
