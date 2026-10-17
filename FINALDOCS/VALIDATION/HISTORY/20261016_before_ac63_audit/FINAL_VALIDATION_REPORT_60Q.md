# 60-query 최종 패키지 검증 보고서

## 검증 대상

- 원고: `FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`
- 표: `FINALDOCS/TABLES/TABLES_60Q.xlsx` 17개 HWP 이전용 sheet
- 그림: 구조·통계 10개 + 선행연구 인용 6개 + 입출력 사례 6개 = 논문 그림 22개
- 입출력 사례: E01~E06 PNG + raw TXT
- 내부 자료 식별: `evidence_manifest_60q.json`

## 원자료 및 수치

네 영어 학술·기술 문서에 한국어 질의를 15개씩 배정해 총 60개 질의-문서 쌍을 구성하고, 8 configuration에서 480 generation record를 사용한다. 60개 질의 전체는 한국어 질의–영어 문서 검색의 cross-lingual 조건을 공유한다. 질문 유형은 질문이 요구하는 답의 성격을 기준으로 사실·정의 8개, 방법·절차 29개, 결과·비교 20개, 목적·기여 3개로 구성한다. HyDE primary 60쌍, CAD 동일 문맥 60쌍, SCD configuration-matched 240쌍, HyDE OFF 동일 문맥 SCD 120쌍을 확인한다.

핵심 결과는 HyDE answer relevancy +0.0805 [+0.0110, +0.1514], CAD faithfulness +0.0288 [-0.0367, +0.0934] (n=58), SCD HyDE-OFF same-context +0.2182 [+0.1880, +0.2487] (n=120), SCD configuration-matched +0.2289 [+0.2051, +0.2532] (n=240)이다.

## 평가 protocol

RAGAS 0.2.15, OpenAI gpt-4o 평가 모델, BAAI/bge-m3 임베딩을 사용한다. 표 5-2는 SCD OFF의 영어 검색 문맥 평가와 SCD ON의 한국어 변환 평가 문맥을 구분한다. 대응 부트스트랩은 질의 단위 200,000회, seed 20260713이다. HyDE ON의 조건별 가상 문서는 temperature=0.1, top_p=0.9 샘플링으로 생성되며, 그림 5-11은 이 실행 구조에서 관측된 조건별 기술적 대응 차이를 제시한다. 그림 5-6은 생성 시간이다.

## 패키지 정합성

- `evidence_manifest_60q.json`의 source SHA-256과 실제 source artifact를 대조한다.
- source SHA-256은 내부 검증 문서인 `EXPERIMENT_60_VALIDATION.md`에서 관리한다.
- E01~E06의 query/config를 manifest와 raw evidence에서 대조한다.
- E05는 `ext_midm_001`의 CAD same-context pair를 사용한다.
- 논문 그림 번호는 22개, 표 번호는 17개이다. 목차 항목과 본문 캡션은 각각 대조한다.
- E04→그림 5-3, E05→5-5, E02→5-7, E03→5-8, E01→5-10, E06→B-1이다. E번호는 내부 파일 식별자이다.
- Windows의 `core.autocrlf=true` 체크아웃에서는 원본 SHA-256과 정확히 일치하는 CRLF→LF 바이트도 허용하며, 적용 파일명을 검증 로그에 기록한다. 결과값이나 원자료를 재작성하지 않는다.
- HWP copy file은 17개 workbook sheet의 탭 구분 표 블록을 포함한다.

## 실행 검증 및 HWPX 산출물

2026-10-08에 `python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py`를 실행해 종료 코드 0과 PASS를 확인했다. 실제 출력은 `DELIVERY/LOGS/finaldocs.log`에 보존한다. HWPX의 독립 검사는 `BUILD/verify_thesis_hwpx.py`로 수행하며 결과와 웹한글 확인 범위는 `DELIVERY/HWPX_BUILD_QA_REPORT.md`에 기록한다.

## 최종 웹한글 확인 항목

최종 HWPX를 웹한글에서 열고 57쪽 PDF를 내보내어 목차 쪽번호, 표·그림·수식과 페이지 배치를 확인했다. 남은 저자·학번·지도교수·제출일·승인 정보 입력과 편집 후 목차 갱신 절차는 `DELIVERY/WEB_HANCOM_CHECKLIST.md`에 기록한다.
