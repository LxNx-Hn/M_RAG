# 60-query 결과 반영을 위한 원고 피드백

## 적용 기준

최종 원고의 실험 결과는 4개 대상 문서에 연결된 60개 한국어 질의-문서 쌍과 8개 RAG-Cube 조건의 480개 저장 generation record를 기준으로 작성한다. 기존 19-query 원고는 문체와 장 구성의 참고자료이며, 최종 본문·표·그림·결론의 수치 근거로 사용하지 않는다.

원자료와 파생 결과의 완결성은 `generated/EXPERIMENT_60_VALIDATION.md`에서 확인한다. RAGAS 점수는 1,920 metric cell 중 1,915개가 저장되어 있으며, faithfulness의 5개 빈 명제 집합은 누락값으로 그대로 보존한다. 따라서 faithfulness 대응 비교의 표본 수는 비교별로 명시한다.

## 원고에서 교체할 핵심 서술

### 실험 규모와 설계

실험 대상은 4개 영어 학술·기술 문서와 문서별 15개씩의 한국어 질의로 구성한다. 같은 60개 질의-문서 쌍에 HyDE, CAD, SCD의 ON/OFF 조합 8개를 적용하여 480개 답변을 생성한다. RAG-Cube는 세 기존 기법을 독립 이진 요인으로 배열한 비교 명칭이며, 새 알고리즘이나 일반적 최적화 프레임워크로 표현하지 않는다.

### HyDE 해석

HyDE의 주 비교에서 answer relevancy 평균 변화는 +0.0805이고 95% CI는 [+0.0110, +0.1514]이다. 이는 60개 대응 질의에서 가장 명확하게 관찰된 품질 지표 변화다. Faithfulness는 평균 +0.0436이나 95% CI가 [-0.0262, +0.1153]이므로 질의별 방향의 이질성을 함께 제시한다. Context precision은 -0.0343, context recall은 0.0000이며 context recall은 52/60이 practical tie다. 따라서 검색 표현을 확장한 결과가 모든 retrieval·answer 지표를 동일 방향으로 움직인다고 서술하지 않고, answer-level 관련성과 retrieval 측정값의 차이를 함께 해석한다.

### CAD 해석

CAD의 주 비교는 동일 검색 문맥을 공유하는 대응쌍이다. Faithfulness는 점수가 완결된 58쌍에서 평균 +0.0288, 95% CI [-0.0367, +0.0934]이고, answer relevancy는 60쌍에서 -0.0073, 95% CI [-0.0855, +0.0719]이다. Context precision과 context recall의 평균 변화도 각각 -0.0092와 -0.0167이다. 이 결과는 하나의 공통 품질 순위를 만들기보다, 문맥 기반 decoding의 지표별 방향·조합별 패턴·저장 응답 사례를 함께 검토하도록 한다. HyDE ON strata에서 faithfulness와 context precision이 양의 방향인 조합 패턴, 그리고 H1C1S0의 최고 faithfulness도 보조적으로 제시할 수 있다.

### SCD 해석

SCD의 직접 목표는 영어 근거 문맥 아래 한국어 출력 유지다. 240개 ON/OFF 대응쌍에서 한국어 문자 비율 평균 변화는 +0.2289, 95% CI [+0.2051, +0.2532]이며 증가·감소·동률은 219/10/11이다. HyDE OFF에서 문맥이 같은 120개 대응쌍에서도 변화는 +0.2182, 95% CI [+0.1880, +0.2487]이다. 이 두 비교를 SCD의 가장 안정적인 직접 결과로 제시한다.

## 최종 원고에서 제외할 내용

- 19-query, 152-answer, 76-pair, 38-pair를 최종 headline 또는 결과 표본으로 쓰지 않는다.
- SCD symmetric normalization, 영어·한국어 정규화 비교, gpt-4o와 gpt-4.1 다중 judge 패널을 최종 결과·그림·표·결론에 포함하지 않는다.
- FastAPI, React, A-F route, 웹 UI, API 및 배포 내용을 연구 기여나 시스템 구현 장에 포함하지 않는다.
- 모든 기법을 ON으로 설정할수록 성능이 상승한다는 서술을 사용하지 않는다.

## 원고의 종합 메시지

세 기법을 모두 적용할수록 성능이 높아지는 구조가 아니라, 검색 관련성·근거 충실도·출력 언어 유지라는 목적에 따라 유리한 configuration이 달라진다. 이 문장은 8개 configuration 평균과 HyDE·CAD의 통제 비교, SCD의 대응 언어 분석을 함께 가리킬 때만 사용한다.

## 근거 파일

- `generated/EXPERIMENT_60_VALIDATION.md`
- `generated/RESULT_REVIEW_60Q.md`
- `generated/hyde_primary_60q.csv`
- `generated/cad_primary_60q.csv`
- `generated/scd_language_summary_60q.csv`
- `generated/rag_cube_config_scores_60q.csv`
