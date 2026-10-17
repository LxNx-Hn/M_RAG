# 교수 피드백 최종 대응

이 대응 기록은 2026-10-17의49쪽 논문과 main 병합 커밋86a4a8d에서 작성했다. 이후 문체 교정으로 현재 논문은46쪽이며, 최신 쪽 위치는 DELIVERY/PAGE_MAP_60Q.json, 변경 문장은 PROSE_REVIEW.md를 따른다. 아래 전사·A→B·객체 JSON은 당시의 수정 근거로 보존한다. 국·영문초록 삭제는 별도 사용자 전달 지시이고 포스터 초록은 선택사항이다. 인준일·주심·부심·날인은 미정이다. 아래 발언·전사 요약과 관찰·추론·예상 질문은 구분한다. 초기 원본과 이전 산출물은 복구 태그 pre-finaldocs-cleanup-20261018에서 확인한다.

## 전사 전체 시간순 대조

전사 SHA-256: `6a0e4ef18df5dac10c4ab017625945f26a814ced65322a34391209f3ac34e98a`. 원음 재청취와 구분한다.

|시간|요구·맥락|현재 상태|남은 확인|
|---|---|---|---|
|00:04|몇 프로가—발언 일부|판정 제외|00:04와31:41은 실질 수정 지시를 추론하지 않음|
|00:31–01:24|RAG 정의의 검색된 문맥이 무엇인가|해결|디지털 검증 완료|
|01:24–02:50|추상적 context 대신 실체가 있는 검색 결과|해결|디지털 검증 완료|
|02:50–03:47|RAG 정의 뒤 본 연구가 너무 빨리 등장|해결|디지털 검증 완료|
|04:22–05:52|한국어-영어 언어 차이 및 필요성을 먼저 설명|해결|디지털 검증 완료|
|06:03–06:45|HyDE가 무엇이며 RAG 내 기법인가 설명|해결|디지털 검증 완료|
|06:45–07:36|선행기법 먼저, 이후 한국어 문제·연구 방법|해결|디지털 검증 완료|
|07:36–08:37|서론의 문제제기·필요·의의 설명|해결|디지털 검증 완료|
|08:37–09:02|서론은 개요, 세부는 본문; 논리 구조|해결|디지털 검증 완료|
|09:17–09:48|긴 글과 표 설명은 좌측 정렬|부분 해결|실물 인쇄·발표 거리 판독|
|09:54–09:57|숫자는 우측, 짧은 항목은 가운데 가능|부분 해결|실물 인쇄·발표 거리 판독|
|10:14–10:33|열을 같은 폭으로만 구성하지 말고 글자 길이에 따라 조정|부분 해결|실물 인쇄·발표 거리 판독|
|10:43–11:17|ON/OFF 부호의 의미 명확히|해결|디지털 검증 완료|
|11:29–11:45|description 셀 좌측 정렬|부분 해결|실물 인쇄·발표 거리 판독|
|11:49–12:13|그림의 잘린 화살표·글자 작음|부분 해결|실물 인쇄·발표 거리 판독|
|12:13–13:22|편집폭 활용·박스 안 글자 1~2pt 이상 확대|부분 해결|실물 인쇄·발표 거리 판독|
|13:24–14:33|그림·표 폭, 지나치게 넓거나 붙은 공백 조정|부분 해결|실물 인쇄·발표 거리 판독|
|14:44–15:15|문서별 질의 수 같은 단순 표보다 질의 내용 제시|해결|디지털 검증 완료|
|15:20–15:53|네 품질 지표와 한국어 지표 5개 구분|해결|디지털 검증 완료|
|15:53–16:51|질의를 임의 구성한 것이 아니라는 근거·선행 평가 방식|해결|디지털 검증 완료|
|16:59–17:29|평균값에 (표준편차) 표기|해결|디지털 검증 완료|
|17:29–17:47|네 자리 수치는 세 자리; 자릿수 정렬|해결|디지털 검증 완료|
|17:29–17:59|반복 생성 횟수 열 삭제, 불필요한 자동그림 정리|해결|디지털 검증 완료|
|18:05–18:42|분석가를 위한 그림 대신 실제 입력출력 사례를 방법 절에|해결|디지털 검증 완료|
|18:54–19:25|95% CI 그래프 정리, 표준편차로 설명|해결|디지털 검증 완료|
|19:30–20:01|평균 대응 차이 뜻과 ON/OFF 비교 명확히|해결|디지털 검증 완료|
|20:01–21:29|짝별 비교 t값·p값, SD, 유의수준 확인|해결|디지털 검증 완료|
|21:35–22:25|여덟 조건 결과를 전체표로 먼저 보여주기|해결|디지털 검증 완료|
|22:37–24:02|지표×조건의 방향과 가독성을 고려해 표 배치|해결|디지털 검증 완료|
|24:17–25:17|단일 기법 비교와 복합 조합을 구분하고 표 통합|해결|디지털 검증 완료|
|25:17–28:51|3요인 ON/OFF 완전요인실험의 전체 효과 ANOVA; 계획 대비 t|해결|디지털 검증 완료|
|29:15–29:49|긴 표를 유지하고 해석·실험 방법을 더 상세히|해결|디지털 검증 완료|
|29:49–30:49|2³ full factorial 용어, 실험 배치표, 0/1 부호|해결|디지털 검증 완료|
|31:05–31:24|큐브 장식 그림보다 실험 배치 정보에 집중|해결|디지털 검증 완료|
|31:28–31:41|1차 수정 후 재검토하겠다는 마무리 발언|판정 제외|새 수정 요구를 도출하지 않음|

## 실제 발언·관찰·추론·예상 질문

```json
{
  "source_type": "existing full transcript, 00:04–31:41; audio not replayed",
  "source_note": "Automatic-transcription errors retained in original; selected clear quotes and semantic paraphrases distinguished.",
  "additional_feedback": {
    "thesis_abstract_delete": "2026-10-17 user explicitly relayed professor instruction, attachment 6b289606 §0.1; supersedes earlier retain-abstract audit",
    "poster_abstract": "Optional, attachment §0.2; current layout retained to protect evaluation/case/result readability",
    "unknown_approval_fields": "User confirmed undecided; remain unfilled"
  },
  "observations": [
    {
      "time": "00:31~02:50",
      "actual_evidence": "02:12 “컨텍스트라는 게 실체가 있냐 이 말이야.”",
      "observed_behavior": "동일 용어의 의미를 반복 질문하고 실제 제공 대상을 확인했다.",
      "inference": "용어보다 데이터·입력의 구체적 대상을 확인하는 검토 행동으로 해석한다.",
      "expected_question": "검색 문맥은 파일·문장·입력 중 무엇인가?",
      "actual_response": "1.1의 생성 입력 정의 보존, 4.1 압축 절차를 코드 수준 대상·단어 수로 구체화"
    },
    {
      "time": "03:47~09:02",
      "actual_evidence": "03:47 연구 배경이 빠졌다는 지적, 09:02 논리 순서 요구",
      "observed_behavior": "연구자가 수행한 일에 앞서 배경·필요성·의의를 설명하도록 순서를 조정했다.",
      "inference": "문제 제기에서 방법과 기여로 이어지는 설명을 중시하는 것으로 추론한다.",
      "expected_question": "HyDE가 한국어도 평가했는데 현재 실험의 차이는 무엇인가?",
      "actual_response": "1.1의 실제 선행 평가 환경을 추가하고 동일 백본의 조합 비교로 기여를 한정"
    },
    {
      "time": "09:17~11:45",
      "actual_evidence": "09:48 “롱 텍스트는 무조건 좌측 정렬”, 09:57 “숫자는 우측 정렬”",
      "observed_behavior": "설명 열·숫자·조건 부호와 열별 내용량을 직접 확인했다.",
      "inference": "표의 의미를 정렬·너비와 함께 읽는 검토 방식으로 추론한다.",
      "expected_question": "이 숫자는 평균인가 차이인가, 단위는 무엇인가?",
      "actual_response": "14표의 정렬 정책·XLSX 셀 일치 보존, 표2-1을 대체 연구의 실제 내용과 동기화"
    },
    {
      "time": "11:49~14:33",
      "actual_evidence": "12:13 편집폭 활용·박스 내부 글자 확대,13:42 큰 공백 지적",
      "observed_behavior": "실제 출력에서 작은 도식 글자와 넓은 여백을 점검했다.",
      "inference": "자동 형식 판정보다 출력 크기의 가독성을 우선 확인하는 것으로 추론한다.",
      "expected_question": "그림의 글자·화살표가 종이에서도 읽히는가?",
      "actual_response": "13도식 재생성, 웹 출력의 고립된 그림1-1을 발견하여 1.2 강제쪽나눔 해제"
    },
    {
      "time": "14:44~16:51",
      "actual_evidence": "15:12 질문 내용의 중요성,16:11 다른 연구의 질의 구성 질문",
      "observed_behavior": "질문 수 설명에서 실제 질문 내용과 타 연구의 구성 방식으로 질문을 확장했다.",
      "inference": "데이터 생성·검증의 근거를 추적하는 행동으로 해석한다.",
      "expected_question": "질문60개가 원문으로 답변 가능한가, 왜15개인가?",
      "actual_response": "5.1에 QASPER·Sultan 방법 비교, 문서 균형 설계값, 실제 원문 대조와 미보관 기록 구분"
    },
    {
      "time": "16:59~18:42",
      "actual_evidence": "16:59 평균 괄호 속 SD·소수점3자리,18:36~42 사례 위치 점검",
      "observed_behavior": "생성 수 중복 열과 자동 결과 그림을 정리하고 결과·설계의 위치를 구분했다.",
      "inference": "같은 결과의 반복보다 표와 설명의 정보 역할을 구분하는 것으로 추론한다.",
      "expected_question": "평균표 SD와 대응 차이 SD는 같은가?",
      "actual_response": "평균(SD)3자리·중복 열 정리 보존, 5.3의 실제 입출력 예시와 부록B 배치 유지"
    },
    {
      "time": "18:54~21:29",
      "actual_evidence": "19:30 “평균 대응 차이라는 게 뭐야?”,20:01 대응 비교 t검정 제안",
      "observed_behavior": "ON/OFF의60쌍을 확인한 뒤 t·p 보고를 제안했다.",
      "inference": "표본 대응·가설을 확인한 다음 검정을 선택하는 행동으로 해석한다.",
      "expected_question": "무엇에서 무엇을 뺀 평균이며, 검정 귀무가설은 무엇인가?",
      "actual_response": "5.4에 고정 조건·질의 단위 차이·귀무가설·dz 정의 추가, 원자료 통계 재현"
    },
    {
      "time": "21:35~29:49",
      "actual_evidence": "22:08 8조건 전체표,23:37 조합 재확인,27:20~28:27 요인 효과와 ANOVA",
      "observed_behavior": "학생이8개조합을 설명하자 단순 비교에서 완전요인 분석으로 판단을 조정했다.",
      "inference": "실험 구조와 연구 질문에 맞추어 방법을 조정하는 지도 행동으로 추론한다.",
      "expected_question": "단일 비교와 주효과·상호작용은 어떤 차이가 있는가?",
      "actual_response": "전체 결과→ANOVA→대응검정 순서 보존, 품질 S별H×C와 문자·시간H×C×S의 분석 경계 명시"
    },
    {
      "time": "29:49~31:41",
      "actual_evidence": "29:49 factorial design 명시,30:25~49 조건표0/1,31:34 수정후재검토",
      "observed_behavior": "설계명·부호화·실제 조건표를 요구하고 후속 검토를 약속했다.",
      "inference": "독자가 설계 구조를 재구성할 수 있는 명시적 설명을 요구한 것으로 추론한다.",
      "expected_question": "실험8조건이 표의0/1과 실제 기록에서 일치하는가?",
      "actual_response": "3요인2수준 설계표·480기록·질의60단위 연결 재검증"
    }
  ]
}
```

## 재심사 예상 질문18개

# 교수 재심사 예상 질문과 근거 답변 · 2026-10-17

아래 질문은 녹음에서 관찰한 검토 행동에 근거한 재심사 시뮬레이션이다. 실제 교수 발언과 동일한 문장으로 취급하지 않는다. 녹음의 표현 오류는 자동 전사의 한계로 남기고, 의미 요약을 원 발언과 구분한다.

|질문|녹음과 연결되는 근거|원고 위치|검증 가능한 답변|자료·정식 출처|실제 수정|
|---|---|---|---|---|---|
|Q1. RAG에서 검색 문맥이란 정확히 무엇인가?|00:31~02:50|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:96|검색기가 고른 문서 구간의 텍스트로, 질문과 함께 생성 모델에 제공하는 실제 입력이다. 원문 전체, 참조 답변, 생성 답변은 서로 구분한다.|[1]; backend/modules/context_compressor.py; 저장 contexts|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q2. HyDE·CAD·SCD는 각각 어떤 입력이나 점수를 바꾸는가?|06:03~07:36|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:176|HyDE는 번역·가상 문서의 임베딩으로 밀집 검색 입력을 바꾼다. BM25·재정렬은 원질의를 유지한다. CAD는 같은 생성 모델의 문맥 포함·제외 로짓을 결합한다. SCD는 이미 생성한 토큰 5개 이후 한국어·비목표 언어 토큰 로짓을 조정한다.|[2][3][4]; 그림2-2~2-4; 실험 파라미터|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q3. HyDE는 다국어 평가를 했는데 본 연구와 무엇이 다른가?|06:25~09:02|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:96|HyDE는 영어 및 한국어 포함 비영어 검색을 평가했다. 본 연구는 한국어 질의–영어 학술·기술 문서의 동일 검색·생성 백본에서 HyDE·CAD·SCD 8조합의 품질·문자 구성·시간을 비교한다. 한국어 최초 적용을 기여로 주장하는 구조를 사용하지 않는다.|[2] ACL 공식 출판; 3.3절 2³ 설계|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q4. 왜 이 세 기법을 함께 비교하는가?|03:47~09:02,27:20~28:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:96|세 기법은 밀집 검색 표현, 근거를 반영하는 디코딩, 출력 언어 토큰 조정이라는 서로 다른 단계에 개입한다. 같은 질의와 백본에서 개별 비교와 조합 효과를 연결하기 위해 완전요인설계를 사용한다.|[2][3][4]; RQ1~RQ4; 표3-1|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q5. 왜 영어 문서 네 개를 선택했는가?|14:44~16:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:368|저장된 네 문서는 RAG 개요, 근거 활용 디코딩, 계층적 검색, 한국어·영어 모델 기술을 다룬다. 문서마다 15개로 질의 수를 맞춘 고정 평가 집합이다. 무작위 문서 표본이나 광범위 문서 모집단의 대표성을 검증한 자료와는 구분하여 보고한다.|자료 D1~D4; QUERY_60_AUDIT.md; 실제 PDF 해시|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q6. 60개 질문은 어떻게 만들었는가?|14:44~16:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:368|연구자 확인 절차는 문서별 초기 질문3개→LLM 주요내용 요약→15개 내용 단위→단위별 한국어 질문1개다. 초기 질문·요약 원본은 미보관이며, 최종60문항부터 증빙을 추적한다. 문서별15개는 문서 균형을 위한 설계값이다.|QUERY_CONSTRUCTION_PROTOCOL_60Q.md; DATA_AVAILABILITY_60Q.md|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q7. 정식 선행연구에서는 질문의 질과 근거를 어떻게 확인했는가?|16:04~16:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:368|QASPER는 제목·초록을 본 질문 작성자와 별도 답변 작성자를 구분하고 전문에서 답변 가능성·답변·지지 근거를 기록했다. Sultan 등의 연구는 문서 기반 대화 생성의 답변 가능성 판단과 근거 선택을 구조화했다. 본 연구는 연구자의 최종 원문 대조를 수행한 절차로 서술한다.|[21] NAACL2021 §§2.2; [22] Findings EMNLP2024; 공식 PDF|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q8. 현재60개가 실제 원문으로 답변 가능한지 어떻게 확인했는가?|14:57~16:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:368|각 질의를 대상문서·원문 페이지·정답 근거·answerable 상태와 연결했다. 최종집합은 고유질의60개, 문서4개각15개, 근거 구간60개다. 부록A의 질문 원문과 원문 근거를 저장 PDF에서 대조한다.|APPENDIX/QUERY_60_AUDIT.md; extended_validation_literal_gt.json; 원본 PDF|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q9. 2³ 설계의 독립변수·종속변수·반복측정 단위는 무엇인가?|26:35~30:49|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:300|독립변수 H·C·S는 HyDE·CAD·SCD 적용 여부(0/1)다. 종속변수는 RAGAS 네 지표, 한국어 문자 비율, 조건 실행 시간이다. 같은 질의60개를8조건에서 측정하며 총480개다. 품질 요인 분석은 평가 문맥 언어별 H×C, 문자·시간은 H×C×S다.|표3-1; 480 생성 기록; EVALUATION_INPUT_AUDIT_60Q.json|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q10. 왜 대응 t와 ANOVA를 함께 사용하는가?|19:30~21:29,23:26~28:51|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:410|대응 t는 다른 기법을 특정 수준에 고정한 두 조건의 질의별 ON−OFF 평균 차이0을 검정한다. 반복측정 ANOVA는 다른 수준을 평균한 요인 주효과 및 상호작용을 검정한다. 가설과 비교 조건을 구분하며 질의 단위 대응 구조를 유지한다.|표5-3~5-8; analyze_factorial_60q.py; statsmodels AnovaRM 교차검증|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q11. HyDE의 +0.080점은 무엇을 의미하는가?|19:30~20:43|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:556|C0S0에서 질의별 답변 관련성 ON−OFF 차이를60개 평균한 값이다. 평균0.683→0.763이며 정확도8% 상승이라는 해석과 구분한다. 점수는 답변 기반 질문과 원질문의 임베딩 유사도로 계산된다.|표5-1·5-7; 원정밀도 paired mean·n60|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q12. Holm p=0.117을 어떻게 해석하는가?|20:43~21:29|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:556|HyDE의 네 품질 검정을 하나의 가설군으로 보정한 p다. 보정 전0.029, 보정 후0.117로0.05보다 높다. 관측한 양의 평균차이와, 가설군을 고려한 유의성 판정을 구분한다.|표5-7; t59=2.236, SD차이0.279, dz0.289|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q13. CAD의 +0.029와 p=0.393은 무엇인가?|19:30~21:29|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:556|H0S0 동일 검색 문맥에서 유효58질의의 근거 충실도 ON−OFF 평균차이다. 차이SD0.255, t57=0.862, 보정 전p0.393, Holm p1.000이다. 질의별 증가·감소와 추가 시간 비용을 함께 보고한다.|표5-7; 원문맥·검색ID 동일성60쌍; 결측2질의|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q14. SCD의 +21.8%p는 무엇이 증가했다는 뜻인가?|16:59~21:29|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:556|한글/(한글+ASCII영문자)의 비율 차이다. HyDE OFF의120쌍을 질의별CAD두상태 평균으로 묶은60표본에서+21.822%p다. 의미 정확성·자연스러움과는 측정 대상이 다르다. 전체240쌍 비교는+22.894%p다.|표5-8; t59=13.951, Holm p<0.001, dz1.801|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q15. S0와 S1의 평가 문맥 언어는 왜 다른가?|16:04~16:51,27:20~28:51와 연결한 예상 질문|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:394|저장 평가 프로토콜은 S0의 영어 문맥과 S1의 한국어 번역 문맥을 사용했다. 생성 입력은 모든 조건에서 영어이고 생성 답변은 원문 그대로 평가했다. 이 설계 경계 때문에 품질의 H×C 검정을 S별로 분리하며 S의 일반 품질효과 해석은 후속 통일 프로토콜의 확인 항목이다.|EVALUATION_INPUT_AUDIT_60Q.json; 공식 평가 runner; 표5-1주석|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q16. 실행 시간 증가에는 어떤 처리가 포함되는가?|21:35~29:49와 연결한 예상 질문|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:358|초기화 후 조건 처리 시작부터 답변 생성·메타데이터 구성 완료까지 초 단위다. 검색·재정렬·문맥 처리·생성이 포함되고 HyDE에는 번역·가상문서생성이 추가된다. 평가 API와 파일기록은 측정 이후다. CAD의 추가 로짓 계산도 포함한다.|main_generation_executor.py; duration_seconds 원자료; 표5-2·5-6|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q17. 정식 학술 문헌과 모델·기술 자료를 어떻게 구분했는가?|개념 실체·근거 추적 행동에서 확장한 예상 질문|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:680|학술 참고문헌1~22는 정식 출판 연구로 구성했다. M1·M2는 공식 모델 카드, D1~D4는 실제 평가 PDF다. CEDR와 실제MiniLM, Fan조사와 평가Gao문서, 생성Mi:dm2.0과 평가Mi:dmK2.5를 각각 구분했다.|PUBLICATION_REVIEW_20261017.md; 공식 출판·모델 카드; PDF SHA-256|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|
|Q18. 가장 명확하게 확인한 결과는 무엇인가?|27:20~28:51의 효과 질문에서 추론|MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:616|이 고정60질의 실험에서 SCD의 한국어 문자 비율 증가는 주비교·전체비교·요인분석·민감도분석에서 일관되었다. 품질의 양의평균차이는 Holm보정 후0.05보다 높은 결과와 함께 해석하고, 실행시간의 H·C주효과와 C×S상호작용을 별도로 보고한다.|6장; 표5-5~5-8; 원자료 재현; 부호순열·Wilcoxon 민감도|정의·문헌·5.1·5.4·결론 수정 또는 기존 검증 보존|


## 실제 원고 A→B36구간

# 현재→최종 원고 실제 A→B 변경 · 2026-10-17

Git 75c0e9e와 작업 원고의 실제 변경 블록 전체다. 빈 문자열은 명시적 초록 삭제 또는 새 설명 삽입을 뜻한다. 원본은 Git과 HISTORY에 보존했다.

|파일·행|A: 수정 전|B: 실제 수정 후|이유|
|---|---|---|---|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:18|# 국문초록 [스타일=목차제목]<br><br>검색 증강 생성(Retrieval-Augmented Generation, RAG)은 질문과 관련된 문서 구간을 검색하고 그 텍스트를 이용해 답변을 생성하는 방법이다. 한국어 질의로 영어 학술·기술 문서를 검색하는 환경에서는 검색 결과의 관련성, 답변이 근거를 반영하는 정도와 출력 언어를 함께 살펴볼 필요가 있다. 본 연구는 가상 문서 임베딩(Hypothetical Document Embeddings, HyDE), 문맥 인식 디코딩(Context-Aware Decoding, CAD), 소프트 제약 디코딩(Soft Constrained Decoding, SCD)을 같은 검색·생성 파이프라인에 적용하여 조합별 결과를 비교하였다.<br><br>영어 문서 4종에서 한국어 질의를 각각 15개씩 구성하였다. 질의 60개 각각에 세 기법의 적용 여부를 조합한 8조건을 적용하여 생성 기록 480개를 수집하였다. BGE-M3와 BM25의 검색 결과를 가중 역순위 융합으로 결합하고 CrossEncoder로 재정렬한 뒤 Mi:dm 2.0 Base Instruct로 답변을 생성하였다. 네 품질 지표는 RAG 자동 평가 프레임워크 RAGAS로 측정하고, 한국어 문자 비율은 생성 답변에서 계산하였다. 질의를 반복측정 단위로 삼아 조건별 평균과 표준편차, 요인별 주효과와 상호작용, 대응 점수 차이를 분석하였다. 품질 평가는 SCD OFF의 영어 문맥과 SCD ON의 한국어 번역 문맥을 구분하였다. 통계 검정에는 양측 유의수준 0.05와 Holm 보정을 적용하였다.<br><br>CAD와 SCD를 미적용한 HyDE 비교에서 답변 관련성의 평균 대응 점수 차이는 +0.080점이었다. 대응 t-검정은 t(59)=2.236, 보정 전 p=0.029, 네 품질 지표에 대한 보정 후 p=0.117이었다. 같은 검색 문맥에서 CAD를 비교한 근거 충실도 차이는 +0.029점, t(57)=0.862, 보정 전 p=0.393이었다. SCD의 HyDE OFF 동일 문맥 비교에서는 질의별로 두 CAD 상태의 차이를 평균하였다. 한국어 문자 비율의 평균 차이는 +21.8%p였으며, t(59)=13.951, 보정 후 p<0.001이었다. 전체 8조건의 문자 비율 분석에서도 SCD 주효과가 유의하였다. 조건 실행 시간에서는 HyDE와 CAD의 주효과 및 CAD×SCD 상호작용이 보정 후 유의하였다.<br><br>세 기법은 서로 다른 처리 단계와 평가 항목에 영향을 주었다. 본 연구는 동일한 질의와 파이프라인에서 답변 품질, 출력 언어와 실행 시간을 구분하고, 단순 비교와 요인 효과를 연결하여 조합별 특성을 제시하였다.<br><br>주제어: 검색 증강 생성, HyDE, CAD, SCD, 한국어 질의, 영어 문서, 반복측정 실험<br><br># Abstract [스타일=목차제목]<br><br>Retrieval-Augmented Generation (RAG) retrieves document passages and uses their text to generate answers. When Korean queries are used to search English academic and technical documents, retrieval relevance, grounding in retrieved evidence, and output language require separate evaluation. This study compares combinations of Hypothetical Document Embeddings (HyDE), Context-Aware Decoding (CAD), and Soft Constrained Decoding (SCD) within a fixed retrieval and generation pipeline.<br><br>Sixty Korean queries, fifteen from each of four English documents, were evaluated under all eight conditions of a two-level, three-factor design, yielding 480 generation records. The pipeline combines BGE-M3 and BM25 retrieval through weighted Reciprocal Rank Fusion (RRF), CrossEncoder reranking, and Mi:dm 2.0 Base Instruct generation. Four quality metrics were measured with the RAGAS evaluation framework, and the Korean-character ratio was computed directly from generated answers. Queries served as repeated-measures units. Quality analyses were stratified by the evaluation-context protocol: English contexts for SCD OFF and Korean-translated contexts for SCD ON. Two-sided tests used a significance level of 0.05 and Holm adjustment.<br><br>With CAD and SCD disabled, the HyDE comparison yielded a mean paired answer-relevancy difference of +0.080, t(59)=2.236, unadjusted p=0.029, and p=0.117 after adjustment across four quality metrics. The identical-context CAD comparison yielded a faithfulness difference of +0.029, t(57)=0.862, and unadjusted p=0.393. For the primary SCD comparison, the two CAD-state differences were averaged within each query under HyDE OFF. The mean Korean-character-ratio difference was +21.8 percentage points, t(59)=13.951, adjusted p<0.001. The eight-condition analysis also identified an SCD main effect on this ratio. HyDE and CAD main effects and the CAD-by-SCD interaction were significant for condition execution time after adjustment.<br><br>The comparisons distinguish changes in answer quality, output language, and execution time at different pipeline stages. Reporting simple contrasts alongside factorial effects provides an empirical account of how the three techniques behave in combination.<br><br>Keywords: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, Korean queries, English documents, repeated measures|(해당 문구 없음)|사용자가 별도로 전달한 교수 지시0.1: 학교 공식 양식에 따라 논문 초록·주제어 삭제|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:100|RAG의 검색 입력과 답변 생성 과정을 개선하기 위해 여러 기법이 제안되었다. 가상 문서 임베딩(Hypothetical Document Embeddings, HyDE)은 질의에서 생성한 가상 문서를 검색에 활용한다[2]. 문맥 인식 디코딩(Context-Aware Decoding, CAD)은 검색 문맥을 포함한 입력과 제외한 입력의 다음 토큰 점수를 결합한다[3]. 소프트 제약 디코딩(Soft Constrained Decoding, SCD)은 목표 언어에 해당하는 토큰의 점수를 조정하여 출력 언어를 제어한다[4]. 각 기법은 검색 표현, 검색 근거의 활용, 출력 언어에 개입한다. HyDE는 영어와 한국어를 포함한 다국어 검색에서 평가되었으며[2], CAD와 SCD는 각각 외부 근거의 활용과 다국어 출력의 언어 제어를 다룬다[3,4].|RAG의 검색 입력과 답변 생성 과정을 개선하기 위해 여러 기법이 제안되었다. 가상 문서 임베딩(Hypothetical Document Embeddings, HyDE)은 질의에서 생성한 가상 문서를 검색에 활용한다[2]. 문맥 인식 디코딩(Context-Aware Decoding, CAD)은 검색 문맥을 포함한 입력과 제외한 입력의 다음 토큰 점수를 결합한다[3]. 소프트 제약 디코딩(Soft Constrained Decoding, SCD)은 목표 언어에 해당하는 토큰의 점수를 조정하여 출력 언어를 제어한다[4]. 각 기법은 검색 표현, 검색 근거의 활용, 출력 언어에 개입한다. HyDE는 Contriever를 기준으로 영어 검색·질의응답·사실 확인과 한국어를 포함한 비영어 검색의 성능을 평가하였다[2]. CAD는 OPT, GPT, LLaMA와 FLAN-T5의 요약 및 지식 충돌 과제에서 근거 반영을 평가하였다[3]. SCD는 세 다국어 데이터셋과 여러 언어·모델에서 출력 언어 이탈을 분석하고 디코딩으로 제어하였다[4]. 이 결과들은 각 기법의 평가 환경에 관한 근거이며, 본 연구는 한국어 질의와 영어 학술·기술 문서의 동일 파이프라인에서 세 기법의 개별·조합 효과를 함께 검증한다.|02:12의 실체 확인 질문 및 실제 사례 근거 문장의 완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:112|RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 영어 문서 4종을 대상으로 문서별 한국어 질의 15개씩 총 60개를 구성하였다. 각 질의에는 검색 대상 문서를 지정하였다. 검색 범위는 지정 문서의 텍스트 구간이며, 질의마다 같은 8조건을 적용하여 생성 기록 480개를 분석하였다.|RAG Survey[D1], CAD[D2], RAPTOR[D3], Mi:dm K 2.5 Pro Technical Report[D4]의 영어 문서 4종을 대상으로 문서별 한국어 질의 15개씩 총 60개를 구성하였다. 각 질의에는 검색 대상 문서를 지정하였다. 검색 범위는 지정 문서의 텍스트 구간이며, 질의마다 같은 8조건을 적용하여 생성 기록 480개를 분석하였다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:158|고정 백본은 BGE-M3 밀집 검색과 BM25 희소 검색을 결합한다. 밀집 검색은 질의와 문서 구간의 의미적 유사성을 기준으로 관련 문서 구간을 검색한다. BM25는 모델명, 약어, 수치처럼 질의와 원문에 동일하게 등장하는 표현을 검색 단서로 활용하였다[5][6]. 두 검색 결과의 순위를 가중 역순위 융합(weighted Reciprocal Rank Fusion, RRF)으로 결합한다[7]. 이어 CrossEncoder가 원질의와 각 후보 구간의 관련성을 계산하여 순서를 다시 정한다[8].|고정 백본은 BGE-M3 밀집 검색과 BM25 희소 검색을 결합한다. 밀집 검색은 질의와 문서 구간의 의미적 유사성을 기준으로 관련 문서 구간을 검색한다. BM25는 모델명, 약어, 수치처럼 질의와 원문에 동일하게 등장하는 표현을 검색 단서로 활용하였다[5][6]. 두 검색 결과의 순위를 가중 역순위 융합(weighted Reciprocal Rank Fusion, RRF)으로 결합한다[7]. 문맥화된 표현을 순위 계산에 활용한 선행연구로 CEDR[8]이 있다. CEDR는 BERT의 분류 벡터와 신경 순위 모델의 상호작용 표현을 결합하였다. 본 실험의 재정렬은 MS MARCO로 학습한 MiniLM CrossEncoder[M2]를 사용한다. 한국어 원질의와 영어 후보 구간을 한 쌍으로 입력하여 관련성 점수를 계산하고, 점수 내림차순으로 후보를 정렬한다. CEDR는 문맥화된 문서 순위화의 학술적 배경이며, 실험에 사용한 모델의 정체성은 공식 모델 카드[M2]와 실행 설정으로 구분한다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:266|RAG 관련 선행연구에서는 검색기의 표현력, 여러 검색 문맥의 활용, 디코딩 제어와 검색 근거의 품질을 다루었다. Dense Passage Retrieval은 질의와 문서 구간을 각각 임베딩하여 검색하는 구조를 제시했고[11], Fusion-in-Decoder는 여러 검색 문서 구간을 각각 인코딩한 뒤 디코더에서 함께 활용하는 방식을 제안했다[12]. 긴 문맥에서는 관련 정보의 입력 위치에 따라 답변 성능이 달라지는 현상이 보고되었으며[9], Contrastive Decoding은 큰 모델과 작은 모델의 출력 로그확률 차이를 토큰 선택에 활용하였다[13]. RAPTOR는 문서 청크를 반복적으로 군집화하고 요약하여 계층적 검색 구조를 구성했다[14]. Self-RAG[15]는 검색 필요성과 생성 결과를 평가하는 방법을 제안하였다. Corrective RAG[16]는 검색된 문서의 품질을 평가하고 검색 결과를 보완하는 방법을 제안하였다.|RAG 관련 선행연구에서는 검색기의 표현력, 여러 검색 문맥의 활용, 디코딩 제어와 검색 근거의 품질을 다루었다. Dense Passage Retrieval은 질의와 문서 구간을 각각 임베딩하여 검색하는 구조를 제시했고[11], Fusion-in-Decoder는 여러 검색 문서 구간을 각각 인코딩한 뒤 디코더에서 함께 활용하는 방식을 제안했다[12]. 긴 문맥에서는 관련 정보의 입력 위치에 따라 답변 성능이 달라지는 현상이 보고되었으며[9], Contrastive Decoding은 큰 모델과 작은 모델의 출력 로그확률 차이를 토큰 선택에 활용하였다[13]. RAPTOR는 문서 청크를 반복적으로 군집화하고 요약하여 계층적 검색 구조를 구성했다[14]. Self-RAG[15]는 검색 필요성과 생성 결과를 평가하는 방법을 제안하였다. Adaptive-RAG[16]는 질문 복잡도를 예측하는 분류기를 이용해 검색 미사용, 단일 검색과 반복 검색 중 적합한 질의응답 전략을 선택하였다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:268|RAG 시스템을 정리한 조사 연구[17], 한국어와 영어를 다루는 Mi:dm 2.0 연구[18], RAG의 구성과 평가를 다룬 조사 연구[19]를 참고하여 검색 구조, 생성 구조와 언어 조건을 설정하였다. BEIR[20]와 MTEB[21]는 검색 및 임베딩 모델을 여러 데이터셋과 과제에서 평가하는 선행연구로 참고하였다. 실험 대상 문서 중 Mi:dm K 2.5 Pro는 해당 기술 보고서[22]를 사용하였다.|Zhao 외[17]는 AI 생성 콘텐츠를 위한 RAG의 검색·생성 구성과 적용 분야를 정리하였다. Fan 외[18]는 검색 증강 대규모 언어 모델 연구를 아키텍처, 학습 전략과 응용 관점에서 분류하였다. 두 조사 연구는 RAG의 구성 요소와 적용 범위를 정리하는 학술적 배경으로 사용하였다. BEIR[19]와 MTEB[20]는 검색 및 임베딩 모델을 여러 데이터셋과 과제에서 평가하는 선행연구로 참고하였다. 실제 생성 모델 Mi:dm 2.0은 공식 모델 카드[M1]로, 평가 문서 Mi:dm K 2.5 Pro는 실험 원문 자료[D4]로 관리한다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:272|표 2-1은 선행연구와 본 실험의 연결을 정리한 것이다. 앞서 설명한 Contrastive Decoding과 CAD는 대조 대상이 다르다. Contrastive Decoding은 큰 모델과 작은 모델의 출력을, CAD는 같은 모델에 문맥을 포함한 경우와 제외한 경우의 다음 토큰 분포를 대조한다. Self-RAG와 CRAG는 검색 및 근거 품질을 점검하는 관련 연구로 참고하였다.|표 2-1은 선행연구와 본 실험의 연결을 정리한 것이다. 앞서 설명한 Contrastive Decoding과 CAD는 대조 대상이 다르다. Contrastive Decoding은 큰 모델과 작은 모델의 출력을, CAD는 같은 모델에 문맥을 포함한 경우와 제외한 경우의 다음 토큰 분포를 대조한다. Self-RAG는 검색 필요성과 생성 결과의 자기평가를, Adaptive-RAG는 질문 복잡도에 따른 검색 전략 선택을 다룬다. 본 연구는 검색·생성 백본을 고정하고 검색 입력과 디코딩 제어의 조합을 비교한다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:284|Self-RAG[15], CRAG[16]	검색 및 근거 품질의 점검	검색 지표와 답변 지표를 구분하는 평가<br>RAGAS[10], BEIR[20], MTEB[21]	자동 평가와 검색·임베딩 평가	고정 문서 집합에서 질의별 대응 비교|Self-RAG[15], Adaptive-RAG[16]	자기평가 및 질문 복잡도에 따른 검색 전략 선택	고정 백본에서 입력·디코딩 조합의 효과 비교<br>RAGAS[10], BEIR[19], MTEB[20]	자동 평가와 검색·임베딩 평가	고정 문서 집합에서 질의별 대응 비교|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:348|(해당 문구 없음)|문맥 길이 관리는 선택한 구간의 공백 기준 단어 수를 합산하여 3,072단어 기준과 비교한다. ContextCompressor의 추출 방식은 질의와 각 문장에 공통으로 등장하는 단어의 비율로 문장을 정렬하고, 각 구간 단어 수의 0.5를 목표로 문장을 선택한 뒤 원래 순서를 복원하는 방식이다. 이 설정은 생성 모델에 제공할 검색 텍스트의 길이를 관리한다.|현재 원고의 실제 처리 대상·출판 근거·처리 절차를 직접 설명|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:370|RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 영어 문서를 대상으로 문서별 15개씩, 총 60개의 한국어 평가 질의를 구성하였다. 모든 질의는 한국어로 작성하고, 지정된 영어 문서에서 근거를 검색하였다.|RAG Survey[D1], CAD[D2], RAPTOR[D3], Mi:dm K 2.5 Pro Technical Report[D4]의 네 영어 문서를 대상으로 문서별 15개씩, 총 60개의 한국어 평가 질의를 구성하였다. 모든 질의는 한국어로 작성하고, 지정된 영어 문서에서 근거를 검색하였다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:374|질의 구성의 최종 검증 자료는 한국어 질의 60개, 대상 문서, 원문 페이지 및 정답 근거로 구성된다. 부록 A는 각 질의와 원문 근거의 대응 관계를 제시한다.|문서 기반 질의응답 데이터셋 QASPER[21]는 논문의 제목과 초록을 읽은 작성자가 질문을 만들고, 별도의 답변 작성자가 전문에서 답변 가능성, 답변과 지지 근거를 기록하도록 구성하였다. Sultan 외[22]는 문서에 근거한 다중 턴 대화 생성에서 답변 가능성 판정과 근거 선택을 구조화된 추론 단계로 다루었다. 두 연구는 질문과 문서 근거의 연결을 검토하는 방법론적 비교 기준이다. 본 연구의 작성은 연구자의 초기 질문과 LLM 요약을 이용한 문서별 질의 구성 절차이며, 최종 검증은 연구자가 원문 페이지와 정답 근거를 대조하는 절차다.<br><br>질의 구성의 최종 검증 자료는 한국어 질의 60개, 대상 문서, 원문 페이지 및 정답 근거로 구성된다. 문서 4종은 RAG의 개요, 근거 활용 디코딩, 계층적 검색과 한국어·영어 언어 모델 기술을 각각 다룬다. 문서별 15개는 문서별 질의 수를 같게 맞춘 설계값이며, 네 문서의 합계가 60개다. 부록 A는 각 질의와 원문 근거의 대응 관계를 제시한다.<br><br>초기 질문과 LLM 요약 대화의 작성 과정은 연구자 확인 기록으로 남아 있다. 현재 대조 가능한 증빙은 최종 질의, 원문 페이지·정답 근거와 이후 생성·평가 기록이다. 작성 절차에 관한 연구자 확인과 최종 산출물의 원문 대조는 자료 가용성 기록에서 구분한다.|16:04~16:51 질문 구성 근거에 답하도록 정식 방법론과 실제 자료 가용 범위 연결|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:404|그림 5-2는 RAPTOR 문서의 질의 ext_raptor_011에 대해 질문, 검색 근거, 생성 답변과 평가값을 연결한 예시다. 참조 답변은 원문 근거에서 구성하며, 검색 문맥과 생성 답변은 해당 조건의 저장 기록을 사용한다. 근거 충실도는 답변의 주장과 검색 문맥을, 문맥 재현율은 참조 답변과 검색 문맥을 대조한다. 각 지표가 사용하는 입력을 구분하여 결과를 해석하였다.|그림 5-2는 RAPTOR 문서의 질의 ext_raptor_011에 대해 질문, 영어 검색 근거, 참조 답변, 생성 답변과 평가값을 연결한 예시다. 검색 근거는 저장 문맥 중 원문과 고수준 요약을 함께 검색하는 이유를 설명하는 완결 문장으로 선별하였다. 해당 문장은 원문 PDF 9쪽에 있으며, 참조 답변의 Cinderella 정성 비교는 19~20쪽에서 확인하였다. 참조 답변은 원문 근거에서 구성하며, 검색 문맥과 생성 답변은 해당 조건의 저장 기록을 사용한다. 근거 충실도는 답변의 주장과 검색 문맥을, 문맥 재현율은 참조 답변과 검색 문맥을 대조한다. 각 지표가 사용하는 입력을 구분하여 결과를 해석하였다.|02:12의 실체 확인 질문 및 실제 사례 근거 문장의 완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:414|RAGAS는 평가 문맥 언어별 H×C 반복측정 ANOVA를, 한국어 문자 비율과 실행 시간은 H×C×S 반복측정 ANOVA를 적용하였다. 모든 요인은 두 수준이므로 효과별 자유도는 (1,n−1)이다. 질의별 직교 요인 대비에서 계산한 t²와 statsmodels AnovaRM의 F값을 대조하였다. 효과크기는 부분 η²로 제시하였다.|RAGAS는 평가 문맥 언어별 H×C 반복측정 ANOVA를, 한국어 문자 비율과 실행 시간은 H×C×S 반복측정 ANOVA를 적용하였다. 모든 요인은 두 수준이므로 효과별 자유도는 (1,n−1)이다. 질의별 직교 요인 대비에서 계산한 t²와 statsmodels AnovaRM의 F값을 대조하였다. 요인 주효과는 다른 요인 수준을 평균했을 때 해당 요인의 ON−OFF 차이를 뜻하며, 상호작용은 한 요인의 차이가 다른 요인 수준에 따라 달라지는지를 나타낸다. 품질의 두 요인 분석에서는 평가 문맥 언어를 고정하고 H와 C의 주효과 및 H×C 상호작용을 검정하였다. 각 효과의 귀무가설은 질의별 요인 대비의 평균이 0이라는 것이다. 효과크기는 부분 η²로 제시하며, 효과 자유도가 1일 때 F/(F+오차 자유도)로 계산하였다.|19:30~28:51의 비교 구조·가설·검정 의미와 초록 삭제 후 결론의 자기완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:416|RQ1과 RQ2는 3.3절의 조건을 고정한 양측 대응 t-검정으로 분석하고, 평균 대응 점수 차이와 차이의 SD, t, 자유도, p, Cohen dz를 보고하였다. SCD는 같은 질의의 두 CAD 상태 차이를 평균한 주 비교와 네 H·C 상태 차이를 평균한 전체 비교를 사용하였다. 두 비교 모두 검정 단위는 질의 60개다. 개별 차이와 대응 t 통계량은 다음과 같다.|RQ1과 RQ2는 3.3절의 조건을 고정한 양측 대응 t-검정으로 분석하고, 평균 대응 점수 차이와 차이의 SD, t, 자유도, p, Cohen dz를 보고하였다. SCD는 같은 질의의 두 CAD 상태 차이를 평균한 주 비교와 네 H·C 상태 차이를 평균한 전체 비교를 사용하였다. 두 비교 모두 검정 단위는 질의 60개다. 대응 t-검정의 귀무가설은 지정한 두 조건에서 질의별 ON−OFF 차이의 평균이 0이라는 것이다. 이 단순 비교는 다른 요인 수준을 고정하고, 요인 주효과는 해당 분석의 다른 요인 수준을 평균한다. Cohen dz는 평균 대응 차이를 대응 차이의 SD로 나눈 효과크기다. 개별 차이와 대응 t 통계량은 다음과 같다.|19:30~28:51의 비교 구조·가설·검정 의미와 초록 삭제 후 결론의 자기완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:618|RQ1에서 HyDE 적용 조건은 답변 관련성의 양의 평균 대응 점수 차이를 보였다. RQ2에서 같은 검색 문맥의 CAD 적용 조건도 근거 충실도의 양의 평균 차이를 보였으며, 질의별 차이는 넓게 분포하였다. 두 비교의 Holm 보정 p는 유의수준 0.05보다 높았다. 품질에 관한 적용 판단은 평균 차이와 보정 검정 결과를 함께 기준으로 삼는다.|RQ1의 C0S0 비교에서 HyDE의 답변 관련성 평균 대응 차이는 +0.080점, t(59)=2.236, 보정 전 p=0.029, Holm 보정 p=0.117이었다. RQ2의 H0S0 동일 문맥 비교에서 CAD의 근거 충실도 평균 차이는 +0.029점, t(57)=0.862, 보정 전 p=0.393, Holm 보정 p=1.000이었다. 두 품질 비교에서는 양의 평균 차이가 관찰되었으며, 보정 검정의 p는 유의수준 0.05보다 높았다. 품질에 관한 적용 판단은 평균 차이와 보정 검정 결과를 함께 기준으로 삼는다.|19:30~28:51의 비교 구조·가설·검정 의미와 초록 삭제 후 결론의 자기완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:620|RQ3에서 SCD는 같은 검색 문맥의 주 비교와 전체 비교에서 한국어 문자 사용 비중을 높였다. 두 비교의 보정 검정은 이러한 증가를 지지하였다. 이 결과는 영어 근거로 답변을 생성할 때 한국어 문자 비중을 높이는 용도로 SCD를 적용할 근거가 된다.|RQ3에서 SCD의 HyDE OFF 동일 문맥 주 비교는 한국어 문자 비율의 평균 차이 +21.822%p, t(59)=13.951, Holm 보정 p<0.001이었다. 전체 비교의 평균 차이는 +22.894%p, t(59)=18.474, Holm 보정 p<0.001이었다. 두 비교는 각각 대응쌍 120개와 240개를 질의별로 평균한 표본 60개를 사용하였다. 이 결과는 영어 근거로 답변을 생성할 때 한국어 문자 비중을 높이는 용도로 SCD를 적용할 근거가 된다.|19:30~28:51의 비교 구조·가설·검정 의미와 초록 삭제 후 결론의 자기완결성 보강|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:636|[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020. [스타일=참고문헌리스트]|[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, pp. 9459–9474, 2020. [스타일=참고문헌리스트]|현재 원고의 실제 처리 대상·출판 근거·처리 절차를 직접 설명|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:638|[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023. [스타일=참고문헌리스트]|[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023, doi: 10.18653/v1/2023.acl-long.99. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:640|[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024. [스타일=참고문헌리스트]|[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024, doi: 10.18653/v1/2024.naacl-short.69. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:642|[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026. [스타일=참고문헌리스트]|[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026, doi: 10.1609/aaai.v40i37.40417. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:646|[6] S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994. [스타일=참고문헌리스트]|[6] S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, and M. Gatford, “Okapi at TREC-3,” *Proceedings of the Third Text REtrieval Conference (TREC-3)*, NIST Special Publication 500-225, pp. 109–126, 1995 (conference 1994). [스타일=참고문헌리스트]|현재 원고의 실제 처리 대상·출판 근거·처리 절차를 직접 설명|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:648|[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009. [스타일=참고문헌리스트]|[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009, doi: 10.1145/1571941.1572114. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:650|[8] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019. [스타일=참고문헌리스트]|[8] S. MacAvaney, A. Yates, A. Cohan, and N. Goharian, “CEDR: Contextualized Embeddings for Document Ranking,” *Proceedings of SIGIR*, pp. 1101–1104, 2019, doi: 10.1145/3331184.3331317. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:652|[9] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024. [스타일=참고문헌리스트]|[9] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024, doi: 10.1162/tacl_a_00638. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:654|[10] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024. [스타일=참고문헌리스트]|[10] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024, doi: 10.18653/v1/2024.eacl-demo.16. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:656|[11] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020. [스타일=참고문헌리스트]|[11] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020, doi: 10.18653/v1/2020.emnlp-main.550. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:658|[12] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021. [스타일=참고문헌리스트]|[12] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021, doi: 10.18653/v1/2021.eacl-main.74. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:660|[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023. [스타일=참고문헌리스트]|[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023, doi: 10.18653/v1/2023.acl-long.687. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:666|[16] S.-Q. Yan et al., “Corrective Retrieval Augmented Generation,” arXiv:2401.15884, 2024. [스타일=참고문헌리스트]|[16] S. Jeong, J. Baek, S. Cho, S. J. Hwang, and J. Park, “Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity,” *Proceedings of NAACL*, pp. 7036–7050, 2024, doi: 10.18653/v1/2024.naacl-long.389. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:668|[17] P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” *Data Science and Engineering*, Vol. 11, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5. [스타일=참고문헌리스트]|[17] P. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” *Data Science and Engineering*, Vol. 11, No. 1, pp. 1–29, 2026, doi: 10.1007/s41019-025-00335-5. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:670|[18] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026. [스타일=참고문헌리스트]|[18] W. Fan et al., “A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models,” *Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining*, pp. 6491–6501, 2024, doi: 10.1145/3637528.3671470. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:672|[19] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023. [스타일=참고문헌리스트]|[19] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021. [스타일=참고문헌리스트]|현재 원고의 실제 처리 대상·출판 근거·처리 절차를 직접 설명|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:674|[20] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021. [스타일=참고문헌리스트]|[20] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023, doi: 10.18653/v1/2023.eacl-main.148. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:676|[21] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023. [스타일=참고문헌리스트]|[21] P. Dasigi, K. Lo, I. Beltagy, A. Cohan, N. A. Smith, and M. Gardner, “A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers,” *Proceedings of NAACL*, pp. 4599–4610, 2021, doi: 10.18653/v1/2021.naacl-main.365. [스타일=참고문헌리스트]|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:678|[22] KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” technical report, arXiv:2603.18788v2, 2026. [스타일=참고문헌리스트]|[22] M. A. Sultan, J. Ganhotra, and R. F. Astudillo, “Structured Chain-of-Thought Prompting for Few-Shot Generation of Content-Grounded QA Conversations,” *Findings of EMNLP*, pp. 16172–16187, 2024, doi: 10.18653/v1/2024.findings-emnlp.948. [스타일=참고문헌리스트]<br><br>## 실험 사용 모델 및 원문 자료 출처 [스타일=절(1.1)]<br><br>학술 참고문헌 [1]~[22]는 정식 출판 연구의 근거이며, 아래 모델 카드와 실험 PDF는 구현 및 평가 자료의 출처다.<br><br>[M1] KT, K-intelligence/Midm-2.0-Base-Instruct, 공식 모델 카드, https://huggingface.co/K-intelligence/Midm-2.0-Base-Instruct (확인: 2026-10-17). 실행 기록의 생성 모델 ID는 이 모델이며 답변 생성은 greedy, 최대 새 토큰 512개다. 저장 기록의 버전 정보는 모델 ID와 실행 파라미터로 구성된다. [스타일=참고문헌리스트]<br><br>[M2] Sentence Transformers, cross-encoder/ms-marco-MiniLM-L6-v2, 공식 모델 카드, https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 (확인: 2026-10-17). 실행 설정의 모델 문자열은 cross-encoder/ms-marco-MiniLM-L-6-v2이며, 원질의·후보 구간 쌍을 입력하는 CrossEncoder 재정렬에 사용하였다. [스타일=참고문헌리스트]<br><br>[D1] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997. 실험 원문: paper_nlp_rag.pdf. [스타일=참고문헌리스트]<br><br>[D2] W. Shi et al., CAD 논문[3]. 실험 원문: paper_nlp_cad.pdf. [스타일=참고문헌리스트]<br><br>[D3] P. Sarthi et al., RAPTOR 논문[14]. 실험 원문: paper_nlp_raptor.pdf. [스타일=참고문헌리스트]<br><br>[D4] KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” 기업 기술보고서, arXiv:2603.18788v2, 2026, https://arxiv.org/abs/2603.18788v2. 실험 원문: paper_midm.pdf. [스타일=참고문헌리스트]<br><br>D1~D4의 실험 PDF는 저장된 원본 바이트를 사용한다. 문서별 SHA-256과 질의·원문 페이지·정답 근거 대응은 동봉 자료 출처 검증표와 부록 A에서 제시한다.|정식 출판 서지와 실제 구현·원문 자료의 역할을 구분하고 인용 내용 동기화|
|FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md:716|참고 자료: https://arxiv.org/abs/2511.09984|참고 자료: https://ojs.aaai.org/index.php/AAAI/article/view/40417|현재 원고의 실제 처리 대상·출판 근거·처리 절차를 직접 설명|


## 이전39개 표·그림의 개별 대응

```json
{
  "그림": [
    {
      "old_number": "1-1",
      "old_title": "한국어 질의와 영어 학술 및 기술 문서를 사용하는 RAG 실험 환경",
      "current_location": "그림1-1 재작성",
      "reason": "한국어 질문→영어 근거→생성 답변과 세 기법의 역할을 본문폭 독립 도식으로 보여준다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        8
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-1",
      "old_title": "RAG의 검색기–생성기 구조",
      "current_location": "그림2-1 독립도식",
      "reason": "RAG 검색기와 생성기, 실제 제공 텍스트와 출력 답변의 실체를 구분한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        9
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-2",
      "old_title": "긴 문맥에서 관련 정보 위치에 따른 성능 변화",
      "current_location": "2.2 본문 설명",
      "reason": "입력 위치 효과는2.2의 문헌 설명으로 통합하고 조합 실험의 핵심 도식에 지면을 배분한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-3",
      "old_title": "HyDE의 가상 문서 기반 검색 구조",
      "current_location": "그림2-2 독립도식",
      "reason": "가상 문서 생성→임베딩→실제 문서 검색의 순서와 본 실험의 번역·원질의 경로를 명시한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        11
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-4",
      "old_title": "Context-Aware Decoding의 분포 대조 구조",
      "current_location": "그림2-3 독립도식",
      "reason": "같은 모델의 문맥 포함/제외 로짓을 각각 계산한 뒤 결합하는 두 경로를 구분한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        12
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-5",
      "old_title": "다국어 RAG의 출력 언어 이탈 사례",
      "current_location": "그림2-4 독립도식",
      "reason": "언어 이탈은2.5 설명과 SCD 토큰 조정 구조 및 실제 부록 사례로 연결하여 개념 예시의 중복을 줄였다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        13
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "2-6",
      "old_title": "RAGAS의 근거 충실도 높음/낮음 예시",
      "current_location": "5.3 그림5-2 실제 평가 사례",
      "reason": "일반 지표 예시를 실제 저장된 질문·근거·생성·평가값 사례로 연결하여 평가 방법의 검증성을 높였다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        23
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "3-1",
      "old_title": "HyDE, CAD, SCD를 조합한 RAG-Cube 8개 조건",
      "current_location": "표3-1 0/1 요인설계",
      "reason": "장식 큐브를0/1 설계표로 대체해 통계 분석에 쓰는8조건의 부호를 직접 읽게 했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        16
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-1",
      "old_title": "고정 Paper-RAG 백본 실행 흐름",
      "current_location": "그림4-1 구현 흐름",
      "reason": "검색·융합·재정렬·생성 경로와 CAD후SCD 순서를 확대하고 이번에 도식 경계 잘림을 고쳤다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        19
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-2",
      "old_title": "생성 기록–평가–대응 분석 흐름",
      "current_location": "그림5-1 평가 절차로 통합",
      "reason": "생성 기록과 평가 입력 연결은 방법절 그림5-1에서 반복측정 단위·프로토콜별 분석과 함께 설명한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        22
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-1",
      "old_title": "60개 질의 평가 및 HyDE, CAD, SCD의 대응 비교 설계",
      "current_location": "그림5-1 평가 절차로 통합",
      "reason": "질의60개를8조건에서 반복측정하고480기록을 지표별 검정으로 연결하는 실험 절차를 제시한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        22
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-2",
      "old_title": "평가 프로토콜별 RAG-Cube 조건 평균",
      "current_location": "표5-1 평균(SD)",
      "reason": "평균 히트맵 대신 표5-1에서 실제 수치·SD와 S별 평가 프로토콜을 동시에 읽는다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        25
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-3",
      "old_title": "HyDE 적용에 따른 검색 문맥 및 답변 변화 사례",
      "current_location": "부록 그림B-2",
      "reason": "정성 사례는 부록B-2로 옮겨 결과 전체표의 흐름을 유지하면서 원문 증빙을 보존한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        44
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-4",
      "old_title": "HyDE와 CAD의 주 대응 비교",
      "current_location": "표5-7 대응 t",
      "reason": "신뢰구간 그림 대신 표5-7의 t(df)·차이SD·Holm·dz로 대응 검정의 근거를 제시한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        28
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-5",
      "old_title": "동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례",
      "current_location": "부록 그림B-3",
      "reason": "같은 검색 문맥의 CAD 전후 답변은 부록B-3에 보존하여 전체 평균과 개별 사례를 구분한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        45
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-6",
      "old_title": "RAG-Cube 조건별 평균 실행 시간",
      "current_location": "표5-2 실행 시간 평균(SD)",
      "reason": "실행 시간은 표5-2 평균/SD 및 표5-6 요인 검정으로 제시하여 분포와 효과를 함께 읽는다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        26
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-7",
      "old_title": "SCD OFF 조건의 출력 언어 이탈 사례",
      "current_location": "부록 그림B-4",
      "reason": "영어 중심 출력의 실제 기록은 부록B-4에 남겨 문자 비중 지표의 구체 예시로 사용한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        45
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-8",
      "old_title": "동일 검색 문맥에서 SCD 적용 전후 출력 언어 변화 사례",
      "current_location": "부록 그림B-5",
      "reason": "SCD 전후 언어 변화는 부록B-5에 보존하고 주 비교120쌍과 전체240쌍의 범위를 명시한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        46
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-9",
      "old_title": "SCD의 한국어 문자 비율 변화",
      "current_location": "표5-5·5-8 요인/대응 검정",
      "reason": "SCD 신뢰구간 그래프를 표5-8의%p·t·Holm으로 정리하여 질의 단위 검정과 단위를 드러낸다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        27
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-10",
      "old_title": "질문, 검색 근거, 생성 답변과 평가 결과 예시",
      "current_location": "그림5-2 방법절 실제사례",
      "reason": "질문·검색·생성·평가 예시를5.3 방법절로 옮겨 결과표 전에 지표별 입력의 관계를 설명한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        23
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-11",
      "old_title": "HyDE와 CAD의 조건군별 근거 충실도 및 답변 관련성 평균 대응 차이",
      "current_location": "부록 표B-1·B-2 조건군 분석",
      "reason": "조건군 차이의 보조 시각화를 요인 검정과 부록 탐색표에 연결하고 원자료·과거 그림은Git에 보존한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        47
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "B-1",
      "old_title": "동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 추가 사례",
      "current_location": "부록 그림B-1",
      "reason": "평균과 다른 CAD 감소 사례를 보존하여 같은 문맥에서 주장·근거가 어떻게 바뀌는지 확인한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        43
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    }
  ],
  "표": [
    {
      "old_number": "2-1",
      "old_title": "관련 연구와 본 실험의 연결",
      "current_location": "표2-1",
      "reason": "기법의 기능 나열을 본 연구가 실제로 비교하는 질문과 연결하여 선행연구와 평가의 관계를 명확히 했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        15
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "3-1",
      "old_title": "연구 및 실험 요구사항",
      "current_location": "3.1 요구사항 문장",
      "reason": "요구사항을3.1 본문에 통합하여 같은 실험 목적의 중복 표를 줄였다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "3-2",
      "old_title": "RAG-Cube 8개 조건",
      "current_location": "표3-1 완전요인설계",
      "reason": "요인 H·C·S의0/1과8조건을 직접 대응시켜 완전요인 분석의 입력 구조를 명확히 했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        16
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "3-3",
      "old_title": "실험 요인별 적용 위치와 비교 단위",
      "current_location": "3.2·3.3 적용위치/분석단위 문장",
      "reason": "적용 단계와 비교 단위를3.2·3.3의 처리 순서 및 단순/요인 효과 정의와 함께 설명한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-1",
      "old_title": "실험 실행 환경",
      "current_location": "표4-1 공통환경",
      "reason": "모델·기법·설정·단위를 같은 환경표에서 확인하도록 통합했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        18
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-2",
      "old_title": "고정 Paper-RAG 백본",
      "current_location": "표4-1·4.2 통합",
      "reason": "백본의 설정은 표4-1, 실제 경로는 그림4-1로 나누어 표의 중복을 줄였다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        18
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-3",
      "old_title": "실험 조건별 실행 시간",
      "current_location": "표5-2 평균(SD)",
      "reason": "실행 시간은 구현 설명과 구분되는 측정 결과여서5장으로 이동하고 질의별 SD를 제시했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        26
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "4-4",
      "old_title": "생성 기록의 주요 필드",
      "current_location": "4.3 기록필드 문장",
      "reason": "필드의 역할과 기록 시점을4.3 본문에서 설명하여 재현에 필요한 연결 키와 시간 범위를 유지했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-1",
      "old_title": "4개 문서별 질의 구성",
      "current_location": "5.1 문서별15개 설명",
      "reason": "모두 문서별15개인 수량은5.1 문장으로 제시하고 질문 내용·원문 근거에 지면을 배분했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-2",
      "old_title": "SCD 평가 프로토콜별 RAG-Cube 조건 평균",
      "current_location": "표5-1 평균(SD)",
      "reason": "전체8조건의 평균(SD)을 한 표에서 제시하고 S0/S1 평가 문맥 언어를 그룹으로 구분했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        25
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-3",
      "old_title": "HyDE 주 비교 결과",
      "current_location": "표5-7 통합",
      "reason": "HyDE 평균 차이를 대응 t(df),차이SD,보정전후p,dz와 연결해 통계적 해석 범위를 제시했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        28
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-4",
      "old_title": "CAD 동일 문맥 주 비교 결과",
      "current_location": "표5-7 통합",
      "reason": "CAD의 같은 문맥 비교를 HyDE와 같은 표 형식으로 정리하여 유효n=58과 변동성을 드러냈다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        28
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-5",
      "old_title": "SCD 조합별 한국어 문자 비율 변화",
      "current_location": "표5-1·5-5·5-8 전체평균/요인/차이",
      "reason": "SCD 비율 변화의 단위를%p로 표시하고120/240쌍을 질의별n=60으로 묶은 검정을 보고한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        25
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "5-6",
      "old_title": "SCD 대응쌍 분석 요약",
      "current_location": "표5-8 질의별 대응 검정",
      "reason": "중복 SCD 대응 요약을 표5-8의 주/전체 비교로 통합하여 쌍 수와 검정 단위를 함께 설명했다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        28
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "A-1",
      "old_title": "60개 질의–대상 문서 쌍",
      "current_location": "표A-1",
      "reason": "질의마다 대상 문서·유형·원문 페이지·정답 근거를 결합해60개 질문의 답변 가능성을 추적한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        35
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "B-1",
      "old_title": "문서별 탐색 분석",
      "current_location": "표B-1",
      "reason": "문서별 평균 대응 차이(SD)와 유효n을 제시하여 네 고정 문서의 변동을 탐색적으로 읽는다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        47
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    },
    {
      "old_number": "B-2",
      "old_title": "질문 유형별 탐색 분석",
      "current_location": "표B-2",
      "reason": "유형별 평균 대응 차이(SD)와 유효n을 제시하고8/29/20/3의 불균형을 명시한다.",
      "preservation": "원래 커밋 d4931ec와 HISTORY 유지",
      "current_pages": [
        49
      ],
      "verified_current_evidence": [
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "VALIDATION/REEXAM_OBJECT_LAYOUT_20261017.json"
      ],
      "state": "수정·이동·통합 상태 재검증; 원본 Git 보존",
      "remaining": "실물 인쇄 확인"
    }
  ]
}
```

## 2026-10-17 당시27개 객체의 배치·판독 기록

아래 쪽별 PNG 경로는 당시 검사 위치다. 정리 후 이미지는 `python FINALDOCS/BUILD/render_pdf_qa.py <PDF> --output tmp/finaldocs/pages`로 재생성한다.

```json
{
  "pdf_pages": 49,
  "objects": [
    {
      "kind": "표",
      "number": "2-1",
      "caption": "선행연구의 접근과 본 연구의 비교 질문",
      "caption_line": 79,
      "physical_page": 15,
      "printed_page": 9,
      "body_reference_lines": [],
      "purpose": "선행연구의 접근과 본 연구의 비교 질문",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "Official publication verification; CEDR/Adaptive-RAG/Fan/QASPER/Sultan distinctions",
      "sheet": "T2-1_Related_Work",
      "font_pt": 9.0,
      "column_widths_pt": [
        93.54,
        136.07,
        195.61
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-15.png"
    },
    {
      "kind": "표",
      "number": "3-1",
      "caption": "HyDE·CAD·SCD의 3요인 2수준 실험 조건",
      "caption_line": 80,
      "physical_page": 16,
      "printed_page": 10,
      "body_reference_lines": [],
      "purpose": "HyDE·CAD·SCD의 3요인 2수준 실험 조건",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T3-1_Factorial_Design",
      "font_pt": 9.0,
      "column_widths_pt": [
        195.6,
        76.53,
        76.53,
        76.56
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-16.png"
    },
    {
      "kind": "표",
      "number": "4-1",
      "caption": "검색·재정렬·생성 단계의 모델과 공통 실행 설정",
      "caption_line": 81,
      "physical_page": 18,
      "printed_page": 12,
      "body_reference_lines": [],
      "purpose": "검색·재정렬·생성 단계의 모델과 공통 실행 설정",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T4-1_Environment",
      "font_pt": 9.0,
      "column_widths_pt": [
        85.04,
        178.59,
        161.59
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-18.png"
    },
    {
      "kind": "표",
      "number": "5-1",
      "caption": "평가 문맥 언어별 8조건의 품질 및 한국어 문자 비율 평균(SD)",
      "caption_line": 82,
      "physical_page": 25,
      "printed_page": 19,
      "body_reference_lines": [],
      "purpose": "평가 문맥 언어별 8조건의 품질 및 한국어 문자 비율 평균(SD)",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-1_Mean_SD",
      "font_pt": 9.0,
      "column_widths_pt": [
        70.87,
        70.87,
        70.87,
        70.87,
        70.87,
        70.87
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-25.png"
    },
    {
      "kind": "표",
      "number": "5-2",
      "caption": "8조건의 질의별 조건 실행 시간 평균과 표준편차",
      "caption_line": 83,
      "physical_page": 26,
      "printed_page": 20,
      "body_reference_lines": [],
      "purpose": "8조건의 질의별 조건 실행 시간 평균과 표준편차",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-2_Runtime_SD",
      "font_pt": 9.0,
      "column_widths_pt": [
        141.74,
        141.74,
        141.74
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-26.png"
    },
    {
      "kind": "표",
      "number": "5-3",
      "caption": "SCD OFF 영어 평가 문맥의 품질 지표 H×C 반복측정 ANOVA",
      "caption_line": 84,
      "physical_page": 26,
      "printed_page": 20,
      "body_reference_lines": [],
      "purpose": "SCD OFF 영어 평가 문맥의 품질 지표 H×C 반복측정 ANOVA",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-3_Quality_S0",
      "font_pt": 9.0,
      "column_widths_pt": [
        93.54,
        51.02,
        51.02,
        55.27,
        55.27,
        59.53,
        59.57
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-26.png"
    },
    {
      "kind": "표",
      "number": "5-4",
      "caption": "SCD ON 한국어 번역 평가 문맥의 품질 지표 H×C 반복측정 ANOVA",
      "caption_line": 85,
      "physical_page": 27,
      "printed_page": 21,
      "body_reference_lines": [],
      "purpose": "SCD ON 한국어 번역 평가 문맥의 품질 지표 H×C 반복측정 ANOVA",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-4_Quality_S1",
      "font_pt": 9.0,
      "column_widths_pt": [
        93.54,
        51.02,
        51.02,
        55.27,
        55.27,
        59.53,
        59.57
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-27.png"
    },
    {
      "kind": "표",
      "number": "5-5",
      "caption": "한국어 문자 비율의 H×C×S 반복측정 ANOVA",
      "caption_line": 86,
      "physical_page": 27,
      "printed_page": 21,
      "body_reference_lines": [],
      "purpose": "한국어 문자 비율의 H×C×S 반복측정 ANOVA",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-5_Factorial",
      "font_pt": 9.0,
      "column_widths_pt": [
        70.87,
        70.87,
        70.87,
        70.87,
        70.87,
        70.87
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-27.png"
    },
    {
      "kind": "표",
      "number": "5-6",
      "caption": "조건 실행 시간의 H×C×S 반복측정 ANOVA",
      "caption_line": 87,
      "physical_page": 27,
      "printed_page": 21,
      "body_reference_lines": [],
      "purpose": "조건 실행 시간의 H×C×S 반복측정 ANOVA",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-6_Factorial",
      "font_pt": 9.0,
      "column_widths_pt": [
        70.87,
        70.87,
        70.87,
        70.87,
        70.87,
        70.87
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-27.png"
    },
    {
      "kind": "표",
      "number": "5-7",
      "caption": "HyDE·CAD 단순 비교의 품질 대응 점수 차이와 검정 결과",
      "caption_line": 88,
      "physical_page": 28,
      "printed_page": 22,
      "body_reference_lines": [],
      "purpose": "HyDE·CAD 단순 비교의 품질 대응 점수 차이와 검정 결과",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-7_Paired_Quality",
      "font_pt": 9.0,
      "column_widths_pt": [
        97.8,
        23.38,
        89.29,
        68.03,
        42.52,
        51.02,
        53.18
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-28.png"
    },
    {
      "kind": "표",
      "number": "5-8",
      "caption": "SCD 한국어 문자 비율의 질의별 평균 대응 차이(%p)와 검정 결과",
      "caption_line": 89,
      "physical_page": 28,
      "printed_page": 22,
      "body_reference_lines": [],
      "purpose": "SCD 한국어 문자 비율의 질의별 평균 대응 차이(%p)와 검정 결과",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "T5-8_Paired_Language",
      "font_pt": 9.0,
      "column_widths_pt": [
        97.8,
        23.38,
        89.29,
        68.03,
        42.52,
        51.02,
        53.18
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-28.png"
    },
    {
      "kind": "표",
      "number": "A-1",
      "caption": "60개 한국어 질의의 대상 문서·유형·원문 페이지 및 정답 근거",
      "caption_line": 90,
      "physical_page": 35,
      "printed_page": 29,
      "body_reference_lines": [],
      "purpose": "60개 한국어 질의의 대상 문서·유형·원문 페이지 및 정답 근거",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "Appendix_Queries",
      "font_pt": 9.0,
      "column_widths_pt": [
        46.77,
        123.31,
        51.02,
        42.52,
        21.26,
        140.34
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-35.png"
    },
    {
      "kind": "표",
      "number": "B-1",
      "caption": "문서별 HyDE·CAD 대응 점수 차이의 평균(SD)",
      "caption_line": 91,
      "physical_page": 47,
      "printed_page": 41,
      "body_reference_lines": [],
      "purpose": "문서별 HyDE·CAD 대응 점수 차이의 평균(SD)",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "Appendix_Paper",
      "font_pt": 9.0,
      "column_widths_pt": [
        85.04,
        85.04,
        85.04,
        85.04,
        85.06
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-47.png"
    },
    {
      "kind": "표",
      "number": "B-2",
      "caption": "질문 유형별 HyDE·CAD 대응 점수 차이의 평균(SD)",
      "caption_line": 92,
      "physical_page": 49,
      "printed_page": 43,
      "body_reference_lines": [],
      "purpose": "질문 유형별 HyDE·CAD 대응 점수 차이의 평균(SD)",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "자체 실험 원자료",
      "sheet": "Appendix_QueryType",
      "font_pt": 9.0,
      "column_widths_pt": [
        85.04,
        85.04,
        85.04,
        85.04,
        85.06
      ],
      "alignment": "긴 설명 LEFT, 수치/df RIGHT, 조건/요인부호 CENTER, 머리글 CENTER",
      "current_review_evidence": "REEXAM_QA/page-49.png"
    },
    {
      "kind": "그림",
      "number": "1-1",
      "caption": "한국어 질의와 영어 학술·기술 문서를 사용하는 RAG 실험 환경",
      "caption_line": 63,
      "physical_page": 8,
      "printed_page": 2,
      "body_reference_lines": [],
      "purpose": "한국어 질의와 영어 학술·기술 문서를 사용하는 RAG 실험 환경",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/FIGURES/fig1_1_research_setting.png",
      "width_pt": 425.22,
      "height_pt": 148.83,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.921800000000001,
      "current_review_evidence": "REEXAM_QA/page-08.png"
    },
    {
      "kind": "그림",
      "number": "2-1",
      "caption": "RAG의 검색기–생성기 구조",
      "caption_line": 64,
      "physical_page": 9,
      "printed_page": 3,
      "body_reference_lines": [],
      "purpose": "RAG의 검색기–생성기 구조",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json; 각 그림 아래 작성자·개념 출처 한 문장과 참고문헌 뒤 이용 정보 유지",
      "source_image": "FINALDOCS/FIGURES/LITERATURE/fig2_1_rag_independent.png",
      "width_pt": 425.22,
      "height_pt": 153.61,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.394266666666667,
      "current_review_evidence": "REEXAM_QA/page-09.png"
    },
    {
      "kind": "그림",
      "number": "2-2",
      "caption": "HyDE의 가상 문서 기반 검색 구조",
      "caption_line": 65,
      "physical_page": 11,
      "printed_page": 5,
      "body_reference_lines": [],
      "purpose": "HyDE의 가상 문서 기반 검색 구조",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json; 각 그림 아래 작성자·개념 출처 한 문장과 참고문헌 뒤 이용 정보 유지",
      "source_image": "FINALDOCS/FIGURES/LITERATURE/fig2_2_hyde_independent.png",
      "width_pt": 425.22,
      "height_pt": 172.39,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.921800000000001,
      "current_review_evidence": "REEXAM_QA/page-11.png"
    },
    {
      "kind": "그림",
      "number": "2-3",
      "caption": "CAD의 문맥 포함·제외 로짓 결합",
      "caption_line": 66,
      "physical_page": 12,
      "printed_page": 6,
      "body_reference_lines": [],
      "purpose": "CAD의 문맥 포함·제외 로짓 결합",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json; 각 그림 아래 작성자·개념 출처 한 문장과 참고문헌 뒤 이용 정보 유지",
      "source_image": "FINALDOCS/FIGURES/LITERATURE/fig2_3_cad_independent.png",
      "width_pt": 425.22,
      "height_pt": 200.74,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.449333333333335,
      "current_review_evidence": "REEXAM_QA/page-12.png"
    },
    {
      "kind": "그림",
      "number": "2-4",
      "caption": "SCD의 토큰 그룹별 로짓 조정",
      "caption_line": 67,
      "physical_page": 13,
      "printed_page": 7,
      "body_reference_lines": [],
      "purpose": "SCD의 토큰 그룹별 로짓 조정",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json; 각 그림 아래 작성자·개념 출처 한 문장과 참고문헌 뒤 이용 정보 유지",
      "source_image": "FINALDOCS/FIGURES/LITERATURE/fig2_4_scd_independent.png",
      "width_pt": 425.22,
      "height_pt": 212.61,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.921800000000001,
      "current_review_evidence": "REEXAM_QA/page-13.png"
    },
    {
      "kind": "그림",
      "number": "4-1",
      "caption": "한국어 질의의 검색·융합·재정렬 및 답변 생성 흐름",
      "caption_line": 68,
      "physical_page": 19,
      "printed_page": 13,
      "body_reference_lines": [],
      "purpose": "한국어 질의의 검색·융합·재정렬 및 답변 생성 흐름",
      "digital_review": "SVG crop padded by6 units each side; full border/arrow visible in Web Hancom PDF physical page20. Text unchanged.",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/FIGURES/fig4_1_pipeline.png",
      "width_pt": 425.22,
      "height_pt": 218.81112500000003,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.874293675981114,
      "current_review_evidence": "REEXAM_QA/page-19.png"
    },
    {
      "kind": "그림",
      "number": "5-1",
      "caption": "질의별 생성 기록과 평가값을 연결하는 대응 비교 절차",
      "caption_line": 69,
      "physical_page": 22,
      "printed_page": 16,
      "body_reference_lines": [],
      "purpose": "질의별 생성 기록과 평가값을 연결하는 대응 비교 절차",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/FIGURES/fig5_0_evaluation_design.png",
      "width_pt": 425.22,
      "height_pt": 245.74,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 9.449333333333335,
      "current_review_evidence": "REEXAM_QA/page-22.png"
    },
    {
      "kind": "그림",
      "number": "5-2",
      "caption": "RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시",
      "caption_line": 70,
      "physical_page": 23,
      "printed_page": 17,
      "body_reference_lines": [],
      "purpose": "RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png",
      "width_pt": 425.22,
      "height_pt": 253.86,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-23.png"
    },
    {
      "kind": "그림",
      "number": "B-1",
      "caption": "동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 사례",
      "caption_line": 71,
      "physical_page": 43,
      "printed_page": 37,
      "body_reference_lines": [],
      "purpose": "동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 사례",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E06_cad_tradeoff_same_context.png",
      "width_pt": 425.22,
      "height_pt": 422.46,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-43.png"
    },
    {
      "kind": "그림",
      "number": "B-2",
      "caption": "HyDE 적용에 따른 검색 문맥 및 답변 변화 사례",
      "caption_line": 72,
      "physical_page": 44,
      "printed_page": 38,
      "body_reference_lines": [],
      "purpose": "HyDE 적용에 따른 검색 문맥 및 답변 변화 사례",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png",
      "width_pt": 425.22,
      "height_pt": 383.55,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-44.png"
    },
    {
      "kind": "그림",
      "number": "B-3",
      "caption": "동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례",
      "caption_line": 73,
      "physical_page": 45,
      "printed_page": 39,
      "body_reference_lines": [],
      "purpose": "동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png",
      "width_pt": 425.22,
      "height_pt": 357.61,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-45.png"
    },
    {
      "kind": "그림",
      "number": "B-4",
      "caption": "SCD 미적용 조건의 영어 중심 출력 사례",
      "caption_line": 74,
      "physical_page": 45,
      "printed_page": 39,
      "body_reference_lines": [],
      "purpose": "SCD 미적용 조건의 영어 중심 출력 사례",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png",
      "width_pt": 425.22,
      "height_pt": 240.89,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-45.png"
    },
    {
      "kind": "그림",
      "number": "B-5",
      "caption": "SCD 적용 전후 한국어 문자 비율 변화 사례",
      "caption_line": 75,
      "physical_page": 46,
      "printed_page": 40,
      "body_reference_lines": [],
      "purpose": "SCD 적용 전후 한국어 문자 비율 변화 사례",
      "digital_review": "표·그림 본문 연결, 캡션 및 렌더에서 잘림/겹침/글자 판독 확인",
      "physical_print": "추가 확인 필요",
      "spacing": "학교 캡션·본문 스타일 적용; 전체쪽 렌더 확인",
      "source_record": "빌드 입력 이미지 및 독립 도식 출처 기록",
      "source_image": "FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png",
      "width_pt": 425.22,
      "height_pt": 422.46,
      "alignment": "본문폭, 가운데, 원본 비율",
      "minimum_internal_font_pt": 10.20528,
      "current_review_evidence": "REEXAM_QA/page-46.png"
    }
  ],
  "review_date": "2026-10-17",
  "pdf_sha256": "9025c6901914d00d0b0ce624f01d8d9d50026af787815827d7c62164dbab5b8d"
}
```

## 추가 메모의 원래63개 요구 추적

요구 문구와 출처만 보존하고 당시 완료 판정은 승계하지 않는다. 현재 학교 지시가 우선하므로 논문 초록은 삭제, 포스터 초록은 선택사항이며 실물 인쇄는 미검증이다. 각 요구의 현재 결과는 위 최종 대응·배치·A→B와 CURRENT_AUDIT.md에서 확인한다.

|ID|요구|피드백 출처|
|---|---|---|
|AC-01|제목은 연구 대상, 실험 요인 및 평가 목적을 명확하게 전달한다.|추가 메모|
|AC-02|논문 국문초록과 영문초록의 연구 대상·방법·통계 결과를 일치시킨다.|추가 메모|
|AC-03|포스터 초록 영역 삭제 상태를 유지한다.|추가 메모|
|AC-04|RAG 최초 등장에 정식 명칭과 작동 원리를 설명한다.|교수 녹취 및 추가 메모|
|AC-05|“검색 문맥”은 생성 모델에 제공하는 실제 검색 결과 텍스트를 가리키도록 정의한다.|교수 녹취 및 추가 메모|
|AC-06|서론은 RAG → 선행기법 → 교차언어 문제 → 연구 필요성 → 연구 목적 순서를 따른다.|교수 녹취 및 추가 메모|
|AC-07|HyDE·CAD·SCD의 최초 등장에 정식 명칭과 기능을 설명한다.|교수 녹취 및 추가 메모|
|AC-08|Paper-RAG 최초 등장에 자체 검색·생성 파이프라인의 정의를 제시한다.|교수 녹취 및 추가 메모|
|AC-09|영어 문서를 이용한 RAG의 선행연구 결과와 한국어 질의–영어 문서 환경의 연구 필요성을 연결한다. 선행연구의 실제 평가 언어와 결과는 원 논문을 기준으로 기술한다.|추가 메모|
|AC-10|서론에서 연구 질문, 연구 필요성 및 연구 의의를 전달한다.|교수 녹취 및 추가 메모|
|AC-11|세부 수식과 구현 파라미터는 이론적 배경 및 방법 절에 배치한다.|교수 녹취 및 추가 메모|
|AC-12|연구 질문별 측정 지표와 통계 검정의 대응을 명시한다.|교수 녹취 및 추가 메모|
|AC-13|모든 문장의 주어와 측정 대상을 구체적으로 작성한다.|추가 메모|
|AC-14|표의 긴 텍스트는 좌측 정렬한다.|교수 녹취 및 추가 메모|
|AC-15|표의 설명 열은 좌측 정렬한다.|교수 녹취 및 추가 메모|
|AC-16|모든 수치와 통계량은 우측 정렬한다.|교수 녹취 및 추가 메모|
|AC-17|짧은 조건 코드와 0/1 요인 부호는 중앙 정렬한다.|교수 녹취 및 추가 메모|
|AC-18|텍스트의 양에 따라 열 너비를 비대칭으로 구성한다.|교수 녹취 및 추가 메모|
|AC-19|표의 가로·세로 배치 및 비교축을 데이터 유형에 맞게 결정한다.|교수 녹취 및 추가 메모|
|AC-20|표 제목에는 평가 대상, 비교 조건, 제시된 통계량을 포함한다.|추가 메모|
|AC-21|반복되는 생성 횟수 열을 정리한다.|교수 녹취 및 추가 메모|
|AC-22|문장으로 충분히 설명되는 단순 목록표를 정리한다.|교수 녹취 및 추가 메모|
|AC-23|큐브 그림을 0/1 완전요인설계표로 대체한다.|교수 녹취 및 추가 메모|
|AC-24|중복되는 결과 그래프와 히트맵을 정리한다.|교수 녹취 및 추가 메모|
|AC-25|다이어그램 내부 글자 크기를 실제 인쇄 크기에 맞춰 확대한다.|교수 녹취 및 추가 메모|
|AC-26|박스 안에서 글자의 크기와 여백이 조화를 이루도록 조정한다.|교수 녹취 및 추가 메모|
|AC-27|그림의 폭과 높이를 본문 편집 영역에 맞게 조정한다.|교수 녹취 및 추가 메모|
|AC-28|불필요한 큰 여백과 박스 사이의 빈 공간을 정리한다.|교수 녹취 및 추가 메모|
|AC-29|화살표, 연결선, 글꼴 및 수식의 렌더링을 확인한다.|교수 녹취 및 추가 메모|
|AC-30|표·그림·캡션·절 제목 사이의 간격을 확인한다.|교수 녹취 및 추가 메모|
|AC-31|60개 질의의 작성 방법과 원문 근거 확인 절차를 설명한다.|교수 녹취 및 추가 메모|
|AC-32|질의의 실제 내용과 대표적인 질문 사례를 제시한다.|교수 녹취 및 추가 메모|
|AC-33|질의 구성의 최종 증빙 자료와 연구자 작성 절차 설명을 구분한다.|추가 메모|
|AC-34|다섯 핵심 평가 지표의 정의를 제시한다.|교수 녹취 및 추가 메모|
|AC-35|각 지표에서 높은 점수가 의미하는 측정 특성을 설명한다.|교수 녹취 및 추가 메모|
|AC-36|`0.700`, `+0.080`, `+0.218` 등 실제 수치의 의미와 단위를 설명한다.|추가 메모|
|AC-37|평가 지표와 실험 환경을 명확한 순서로 제시한다.|교수 녹취 및 추가 메모|
|AC-38|대표적인 질문·검색 근거·생성 답변·평가 결과를 실험 방법에서 제시한다.|교수 녹취 및 추가 메모|
|AC-39|8조건 전체 결과표를 제시한다.|추가 메모|
|AC-40|조건별 결과는 평균(표본표준편차)로 표시한다.|교수 녹취 및 추가 메모|
|AC-41|소수점은 세 자리로 통일한다.|교수 녹취 및 추가 메모|
|AC-42|신뢰구간 중심의 설명을 표준편차와 통계 검정 중심의 설명으로 정리한다.|교수 녹취 및 추가 메모|
|AC-43|“평균 변화량” 등 해석이 모호한 표현을 “평균 대응 점수 차이”처럼 정확하게 수정한다.|교수 녹취 및 추가 메모|
|AC-44|ON/OFF 비교에는 질의별 대응 검정값과 유효 표본 수를 제시한다.|교수 녹취 및 추가 메모|
|AC-45|대응 t-검정의 t값, 자유도, p값 및 필요 시 효과크기를 제시한다.|교수 녹취 및 추가 메모|
|AC-46|3요인 2수준 완전요인설계의 주효과 및 상호작용을 분석한다.|교수 녹취 및 추가 메모|
|AC-47|실험 조건표는 H·C·S의 0/1 부호를 사용한다.|교수 녹취 및 추가 메모|
|AC-48|단일 기법 비교와 전체 조합 분석을 구분한다.|교수 녹취 및 추가 메모|
|AC-49|ANOVA와 대응 t-검정이 검증하는 가설을 구분한다.|교수 녹취 및 추가 메모|
|AC-50|결과표를 먼저 제시하고, 이후 통계 결과와 해석을 연결한다.|교수 녹취 및 추가 메모|
|AC-51|실험 방법의 설명이 실제 구현 및 평가 기록과 일치하도록 한다.|교수 녹취 및 추가 메모|
|AC-52|결측, 평가 문맥 언어, 샘플링, 실행 시간의 측정 범위를 명시한다.|교수 녹취 및 추가 메모|
|AC-53|포스터의 독립 초록 영역 삭제 상태를 유지한다.|추가 메모|
|AC-54|포스터 01에서 문제 배경과 연구 필요성을 구체적으로 제시한다.|추가 메모|
|AC-55|포스터 02에서 데이터 흐름과 기법의 적용 위치를 크게 표시한다.|교수 녹취 및 추가 메모|
|AC-56|포스터 03은 0/1 실험 설계표 중심으로 구성한다.|교수 녹취 및 추가 메모|
|AC-57|포스터 04는 지표 정의 → 점수 의미 → 실제 평가 사례 → 실험 환경 → 통계 방법 순서로 구성한다.|추가 메모|
|AC-58|포스터 05는 전체 결과표 → ANOVA → 대응 t-검정 순서로 구성한다.|추가 메모|
|AC-59|포스터 06은 05의 통계 결과를 해석하는 역할에 집중한다.|추가 메모|
|AC-60|포스터 07은 연구 질문의 결과와 실제 적용상 의미를 제시한다.|추가 메모|
|AC-61|포스터 08은 핵심 참고문헌만 간결하게 제시한다.|추가 메모|
|AC-62|포스터 표의 숫자·SD·t·F·p값과 작은 주석의 가독성을 확인한다.|추가 메모|
|AC-63|A1 실물 출력 크기에서 내부 글자와 표 내용을 확인한다.|추가 메모|
