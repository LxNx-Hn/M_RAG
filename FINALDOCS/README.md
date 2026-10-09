# 60-query RAG-Cube 졸업논문 최종 작성 패키지

최신 학교 양식 적용·출력 검토는 [2026 양식 최종 검증 보고서](VALIDATION/FINAL_SCHOOL_TEMPLATE_2026_AUDIT.md)에 기록했다. 현재 웹한글 PDF는 54쪽이며, 서론은 표시 쪽번호 1로 시작한다. 이전 감사 문서의 쪽수·편집 로그는 당시 산출물 기록이다.

이 디렉터리는 웹한글에서 편집할 HWPX 논문과 제출 전 사실 확인에 필요한 원고·표·그림·검증 자료로 구성한다.

- `MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`: 한글 이전용 단일 원고
- `MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md`: 표·그림의 HWP 배치 안내
- `MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt`: HWP 수식 입력값
- `MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt`: 본문 및 부록 A·B의 17개 표를 담은 탭 구분 원본
- `TABLES/TABLES_60Q.xlsx`: 본문 및 부록용 17개 workbook sheet
- `FIGURES/*.png`: HWP에 삽입할 10개 구조·통계 그림
- `FIGURES/LITERATURE/`: 이론적 배경에 삽입할 선행연구 인용 그림 6개
- `EVIDENCE/IO_CASES/`: 저장된 60-query artifact의 E01~E06 입출력 발췌 PNG, 원래 raw TXT, 정확한 발췌 위치·전체 답변 평가값의 인쇄용 명세
- `APPENDIX/QUERY_60_AUDIT.md`: 60개 질의 목록
- `DATA/EXPERIMENT_60_VALIDATION.md`, `DATA/evidence_manifest_60q.json`: 수치·원자료 출처 검토용
- `VALIDATION/FINAL_VALIDATION_REPORT_60Q.md`: 최종 패키지 검증 보고서
- `VALIDATION/FINAL_PROSE_AUDIT.md`: 최신 문체 전수 감사·수정·웹한글 출력·CI 기록
- `VALIDATION/FINAL_CLAIM_MAP_60Q.md`: 최종 주장-근거 연결표
- `VALIDATION/verify_finaldocs_60q.py`: 네트워크·모델 호출 없이 실행하는 제출 패키지 점검기

## 최종 실험 정의

최종 60-query 졸업논문의 실험 설정은 `experiments/configs/final_thesis_60q.yaml`을 기준으로 한다. 이 파일은 60개 평가 질의, 8개 HyDE×CAD×SCD 조건, 검색·재정렬 설정, 생성 모델과 decoding 설정, reference SCD 설정, 평가 모델과 통계 절차를 하나의 최종 configuration으로 정의한다.

질의 구성 절차는 `VALIDATION/QUERY_CONSTRUCTION_PROTOCOL_60Q.md`에 기록한다. 실험 결과의 수치와 생성 기록은 `VALIDATION/FINAL_CLAIM_MAP_60Q.md` 및 연결된 source artifact에서 추적한다.

원고의 1~6장은 HyDE·CAD·SCD를 각각 검색 표현, 동일 문맥 decoding, 출력 언어 제어 관점에서 분석한다. 현재 제출 근거는 `FINALDOCS/`의 집계 자료와 검증 문서가 해시로 연결한 source artifact로 구성한다.

## 웹한글 문서와 재생성

- `DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx`: 편집 가능한 표 17개·그림 22개·수식 10개를 담은 논문. 원본 양식의 표지 배치용 표 2개는 논문 표 번호에 포함하지 않는다.
- `DELIVERY/HWPX_BUILD_QA_REPORT.md`: 실제 구조·내용·웹한글 검증과 남은 입력 항목.
- `DELIVERY/WEB_HANCOM_CHECKLIST.md`: 웹한글 최종 확인 절차.
- `BUILD/`: 고정 버전 의존성, 자동 생성기와 독립 검사기.

```powershell
python -m pip install -r FINALDOCS/BUILD/requirements.txt
python -X utf8 FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json
python -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
```

학교 HWP 원본도 `--template`으로 지정할 수 있다. 재생성 시 기존 HWPX는 `DELIVERY/versions/`에 보존한다. 부록 A는 60개 질의 목록, 부록 B는 추가 사례와 탐색 분석이다. 그림은 구조·통계 10개, 선행연구 인용 6개, 입출력 사례 6개로 총 22개이다. 원고의 실제 장·절 명칭을 그대로 적용한다.
