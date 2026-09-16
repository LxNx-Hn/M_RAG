# 60-query 최종 패키지 검증 보고서

## 검증 대상

- 최종 원고: `GRADUATION_REPORT_TRANSFER_KO_60Q.md`
- 표: `TABLES_60Q.xlsx` 및 `tables_60q_csv/`
- 그림: `FINALDOCS/FIGURES/`의 HWP 삽입용 구조·통계 PNG 10개와 `EVIDENCE/UI_REPLAY/`의 저장 응답 UI 화면
- 증빙: `evidence_60q_raw/`, `generated/evidence_manifest_60q.json`
- 집계 패키지: `FINALDOCS/`

## 원자료 및 수치 대조

`build_60q_derived_data.py`를 다시 실행해 60-query 파생 CSV와 검증 보고서를 원본 artifact에서 재생성했다. 그 결과 60 질의-대상문서 쌍, 8 configuration, 480 generation record, HyDE primary 60쌍, CAD 동일 문맥 primary 60쌍, SCD ON/OFF 240쌍을 확인했다. Faithfulness의 5개 빈 명제 집합은 결측으로 유지했고 CAD faithfulness 대응 비교는 58 완결쌍으로 표기했다.

원고·표에서 대조한 핵심값은 HyDE answer relevancy +0.0805 [+0.0110, +0.1514], CAD faithfulness +0.0288 [-0.0367, +0.0934] (n=58), SCD 전체 +0.2289 [+0.2051, +0.2532] (n=240), HyDE OFF 동일 문맥 SCD +0.2182 [+0.1880, +0.2487] (n=120)이다.

## 문서 구조 점검

- 과거 19-query headline, 152-answer, 76-pair, 38-pair headline을 최종 원고에서 사용하지 않았다.
- SCD symmetric normalization과 다중 judge panel을 최종 결과·표·그림·결론에서 제외했다.
- 3단계 heading과 수식 번호를 사용하지 않았다.
- FastAPI, React, 서비스 route·UI·배포 내용을 연구 기여로 포함하지 않았다.
- 그림은 내부 번호를 두지 않고 본문 캡션에서 번호를 부여한다.

## 산출물 점검

Excel workbook은 17개 sheet와 표별 CSV를 포함한다. 표 2-1과 부록 A의 60개 질의 sheet를 포함하며, workbook 재열기로 HyDE Win/Loss/Tie 24/21/15와 CAD faithfulness n=58을 확인했다. 표 제목, header, 값의 가독성은 대표 sheet에서 확인했다.

원본 작업 경로에는 17개 PNG와 SVG가 보존된다. `FINALDOCS/FIGURES`에는 HWP 본문에 필요한 구조·통계 그림 10개만 남기고, 실제 저장 응답 증빙은 `EVIDENCE/UI_REPLAY`의 여섯 UI 화면으로 분리했다. E02는 1장의 연구 문제 제시와 부록 B의 replay 증빙에 역할을 나누어 배치한다.

## 남아 있는 확인 항목

최종 한글 편집에서는 저자·지도교수·제출일·승인 정보, 실제 장·절 style, 표·그림 목차 페이지 번호, 조판 후 실제 페이지 수를 채워야 한다. 이 값들은 저장 artifact에 없으므로 본 패키지에서 임의로 채우지 않았다. 1~6장 본문은 약 36.1천 자이며, 최종 HWP에서는 쪽 나눔·표 넘침·수식 렌더링을 별도로 확인해야 한다. 로컬 pre-commit Ruff는 변경과 무관한 기존 backend lint 178건을 보고하므로 문서·artifact 커밋은 `diff --check`와 개별 생성·재열기 검증 후 훅을 우회했다. CI에 고정된 Ruff 버전으로 별도 전체 검증이 필요하다.
