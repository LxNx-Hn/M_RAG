# 60-query 최종 패키지 검증 보고서

## 검증 대상

- 원고: `FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`
- 표: `FINALDOCS/TABLES/TABLES_60Q.xlsx` 17개 HWP 이전용 sheet
- 그림: 프로젝트 구조·통계 10개 + 선행연구 인용 6개
- 입출력 사례: E01~E06 PNG + raw TXT
- 내부 자료 식별: `evidence_manifest_60q.json`

## 원자료 및 수치

네 영어 학술·기술 문서에 한국어 질의를 15개씩 배정해 총 60개 질의-문서 쌍을 구성하고, 8 configuration에서 480 generation record를 사용한다. 60개 질의 전체는 한국어 질의–영어 문서 검색의 cross-lingual 조건을 공유한다. 질문 유형은 질문이 요구하는 답의 성격을 기준으로 사실·정의 8개, 방법·절차 29개, 결과·비교 20개, 목적·기여 3개로 구성한다. HyDE primary 60쌍, CAD 동일 문맥 60쌍, SCD configuration-matched 240쌍, HyDE OFF 동일 문맥 SCD 120쌍을 확인한다.

핵심 결과는 HyDE answer relevancy +0.0805 [+0.0110, +0.1514], CAD faithfulness +0.0288 [-0.0367, +0.0934] (n=58), SCD HyDE-OFF same-context +0.2182 [+0.1880, +0.2487] (n=120), SCD configuration-matched +0.2289 [+0.2051, +0.2532] (n=240)이다.

## 평가 protocol

RAGAS 0.2.15, OpenAI gpt-4o judge, BAAI/bge-m3 embedding을 사용한다. 표 5-2는 SCD OFF의 영어 검색 문맥 평가와 SCD ON의 한국어 변환 평가 문맥을 두 protocol 블록으로 구분한다. Paired bootstrap은 query 단위 200,000회, seed 20260713이다. HyDE ON 조건의 configuration별 hypothetical document는 temperature=0.1, top_p=0.9 sampling으로 생성되며, 그림 5-6은 해당 실행 구조에서 관측된 조건별 기술적 대응 차이를 제시한다.

## 패키지 정합성

- `evidence_manifest_60q.json`의 source SHA-256과 실제 source artifact를 대조한다.
- source SHA-256은 내부 검증 문서인 `EXPERIMENT_60_VALIDATION.md`에서 관리한다.
- E01~E06의 query/config를 manifest와 raw evidence에서 대조한다.
- E05는 `ext_midm_001`의 CAD same-context pair를 사용한다.
- 일반 그림 caption은 16개, 표 caption은 17개이다.
- HWP copy file은 17개 workbook sheet의 탭 구분 표 블록을 포함한다.

## 최종 HWP 확인 항목

저자·학번·지도교수·제출일·승인 정보, 목차/그림목차/표목차 쪽번호, 표 넘침, 그림 크기, 수식 렌더링, 페이지 나눔은 최종 HWP에서 확인한다.
