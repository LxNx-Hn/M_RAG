# 60-query 최종 패키지 검증 보고서

## 검증 대상

- 최종 원고: `GRADUATION_REPORT_TRANSFER_KO_60Q.md`
- 표: `FINALDOCS/TABLES/TABLES_60Q.xlsx`의 17개 HWP 이전용 sheet
- 집계 패키지: `FINALDOCS/`

## 원자료 및 수치 대조

`FINALDOCS/DATA/evidence_manifest_60q.json`에 기록된 저장 generation·evaluation·analysis artifact의 해시를 대조했다. 그 결과 60 질의-대상문서 쌍, 8 configuration, 480 generation record, HyDE primary 60쌍, CAD 동일 문맥 primary 60쌍, SCD ON/OFF 240쌍을 확인했다. Faithfulness의 5개 빈 명제 집합은 결측으로 유지했고 CAD faithfulness 대응 비교는 58 완결쌍으로 표기했다.

원고·표에서 대조한 핵심값은 HyDE answer relevancy +0.0805 [+0.0110, +0.1514], CAD faithfulness +0.0288 [-0.0367, +0.0934] (n=58), SCD 전체 +0.2289 [+0.2051, +0.2532] (n=240), HyDE OFF 동일 문맥 SCD +0.2182 [+0.1880, +0.2487] (n=120)이다.

## 문서 구조 점검

- 최종 원고의 실험 범위는 60-query·480 generation 기준으로 통일했다.
- 결과·표·그림·결론은 60-query primary artifact와 통제 비교를 기준으로 구성했다.
- 문서 구조는 장·절 heading과 본문 caption numbering으로 구성했다.
- 연구 내용은 HyDE·CAD·SCD의 실험 설계, 구현, 정량 결과와 사례 분석에 맞췄다.
- 그림 번호는 본문 caption에서 부여한다.
- 본문 서술은 연구가 수행한 내용과 관찰된 결과를 중심으로 정리하고, 범위·한계는 표본과 평가 조건을 사실형으로 제시한다.

## 산출물 점검

Excel workbook은 17개 HWP 이전용 sheet를 포함한다. 표 2-1과 부록 A의 60개 질의 sheet를 포함하며, workbook 재열기로 HyDE Win/Loss/Tie 24/21/15와 CAD faithfulness n=58을 확인했다. 표 제목, header, 값의 가독성은 대표 sheet에서 확인했다.

## 최종 HWP 확인 항목

최종 한글 편집 단계에서 저자·지도교수·제출일·승인 정보, 실제 장·절 style, 표·그림 목차 페이지 번호, 조판 후 실제 페이지 수를 입력·확인한다. 쪽 나눔, 표 넘침, 그림 크기와 수식 렌더링도 최종 HWP에서 확인한다. validator는 원고의 구조·수치·표·그림·참고문헌·증빙 경로와 핵심 수식의 정합성을 검사한다.

로컬 pre-commit Ruff는 기존 backend lint 178건을 보고했다. 문서·artifact 검증은 `diff --check`와 개별 생성·재열기 검증을 사용했고, 전체 Python lint는 CI에 고정된 Ruff 버전 기준으로 별도 확인한다.
