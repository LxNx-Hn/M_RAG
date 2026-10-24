# 60문항 질문별 분석

원래 생성, 검색, 평가 기록을 그대로 읽어 질문과 조건으로 연결한다. 결과는 조건별 원점수의 평균과 표준편차, 같은 평균의 질문 유형별 값, 미적용 대비 질문별 변화로 정리한다. 중앙값과 통계 검정은 사용하지 않는다.

## 질문 유형

분석 유형은 정답의 형태와 내용으로 정한 세 가지다.

| 유형 | 질문 수 | 기준 |
|---|---:|---|
| 수치 질문 | 18 | 정답이 점수, 비율, 개수, 설정값 같은 수치 (`answer_form`이 수치형) |
| 방법 질문 | 25 | 서술형이며 원분류가 방법 및 절차 |
| 개념과 결과 질문 | 17 | 서술형이며 원분류가 사실 및 정의, 결과 및 비교, 목적 및 기여 |

원분류 네 유형(8, 29, 20, 3개)은 `question_type` 열에 그대로 보존한다. 원분류는 목적 및 기여가 3개이고 결과 및 비교 20개에 수치 질문 12개와 서술 질문 8개가 섞여 있어, 답변에 필요한 작업(수치 옮기기, 과정 설명, 개념과 결과 해석)에 맞춘 세 유형으로 다시 묶었다. 질문별 근거는 `QUESTION_CLASSIFICATION_60Q.csv`의 `group_basis` 열에 있다.

## 비교 규칙

- 근거 충실도, 문맥 정밀도, 문맥 재현율은 검색 결과를 쓰므로 같은 평가 언어의 조건끼리만 비교한다(SCD 미적용은 영어 검색 결과, SCD 적용은 한국어 번역 검색 결과). 미적용 대비 비교에서 SCD 조건은 답변 관련성, 한국어 문자 비율, 처리 시간만 계산하며 `evaluation_language`는 `질문과 답변`이다.
- 기법 하나를 추가한 비교(예: HyDE에서 HyDE+CAD)는 같은 평가 언어 안에서 계산한다.
- 처리 시간은 각 생성 실행의 첫 기록(track1_0009, ext_rag_001)을 모든 조건에서 뺀 58개 질문으로 계산한다.
- 점수 차이 0.05 초과는 오름, −0.05 미만은 내림, 사이는 비슷함이다. 처리 시간은 1초 경계다.
- 두 조건 중 한쪽의 답변 관련성이 0이면 해당 질문은 오르내림 집계에서 빼고 `ZERO_RELEVANCY_AUDIT.json`에서 관련성 0점의 생성과 해소로 센다. 0점은 평가 모델의 판정값이며, 실제 답변의 내용은 5.7절 사례처럼 따로 대조한다. 원점수 표의 평균에는 0점을 포함한다.
- 근거 충실도 결측 5개(CAD 2개, SCD 3개)는 해당 조건의 평균과 대응 비교에서 뺀다.

## 자료

- `QUERY_LEVEL_RESULTS.csv`: 60×8개 실행, 질문 유형과 원분류.
- `CONDITION_SUMMARY.csv`: 조건별, 유형별 평균, 표준편차, 0점 개수.
- `QUERY_LEVEL_DELTAS.csv`: 미적용 대비 비교와 기법 추가 비교의 질문별 차이.
- `QUESTION_TYPE_SUMMARY.csv`: 비교별 평균 변화와 오른, 내린, 비슷한 질문 수. 전체, 질문 유형, 원분류, 문서, 질문 유형과 문서의 조합(`group_document`) 등으로 집계한다.
- `FIGURE_HIGHLIGHTS.json`: 평행좌표에서 색으로 표시한 질문(유형과 기법마다 가장 크게 오르거나 내린 질문).
- `CASE_REVIEW_PLAN.json`, `REVIEWED_CASES.json`, `CASE_EXCERPTS.json`: 5.7절과 부록 B의 9개 사례, 저장 기록과 대조하는 근거 검사 37개, 답변 발췌.
- `CONTEXT_IDENTITY_AUDIT.json`, `SOURCE_PAGE_AUDIT.json`, `RAW_PRESERVATION.json`: 입력 구간 동일성, 원문 페이지, 원자료 보존 확인.

## 재현

```powershell
python FINALDOCS/ANALYSIS/analyze_questions.py
python FINALDOCS/ANALYSIS/review_cases.py
python FINALDOCS/ANALYSIS/plot_questions.py
python FINALDOCS/VALIDATION/verify_question_analysis.py --analysis-only
```

평행좌표는 유형마다 그림 하나이며 미적용, HyDE, CAD, SCD 조건을 위에서 아래로 쌓는다. 회색 선은 질문별 원점수, 색 선(오른 질문은 ▲, 내린 질문은 ▼ 표식)은 미적용 대비 HyDE의 답변 관련성, CAD의 근거 충실도, SCD의 한국어 문자 비율이 가장 크게 오르거나 내린 질문이며 점선은 그 질문의 미적용 점수다. 0점과 결측은 그림에서만 선을 끊는다. 처리 시간은 초 단위이므로 표에서 제시한다.
