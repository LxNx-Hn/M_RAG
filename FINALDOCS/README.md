# 60-query RAG-Cube 졸업논문 최종 작성 패키지

이 디렉터리는 HWP 최종 작성과 제출 전 사실 확인에 필요한 원고·표·그림·검증 자료로 구성한다.

- `MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`: 한글 이전용 단일 원고
- `MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md`: 표·그림의 HWP 배치 안내
- `MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt`: HWP 수식 입력값
- `MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt`: 17개 workbook 표 대응표와 부록 C 탭 구분 원본
- `TABLES/TABLES_60Q.xlsx`: 본문 및 부록용 17개 workbook sheet
- `FIGURES/*.png`: HWP에 삽입할 10개 구조·통계 그림
- `FIGURES/LITERATURE/`: 이론적 배경에 삽입할 선행연구 인용 그림 6개
- `EVIDENCE/IO_CASES/`: 저장된 60-query artifact의 E01~E06 실제 입출력 PNG와 대응 raw TXT
- `APPENDIX/QUERY_60_AUDIT.md`: 60개 질의 목록
- `DATA/EXPERIMENT_60_VALIDATION.md`, `DATA/evidence_manifest_60q.json`: 수치·원자료 출처 검토용
- `VALIDATION/FINAL_VALIDATION_REPORT_60Q.md`: 최종 패키지 검증 보고서
- `VALIDATION/FINAL_CLAIM_MAP_60Q.md`: 최종 주장-근거 연결표
- `VALIDATION/verify_finaldocs_60q.py`: 네트워크·모델 호출 없이 실행하는 제출 패키지 점검기

## Canonical experiment definition

최종 60-query 졸업논문의 실험 설정은 `experiments/configs/final_thesis_60q.yaml`을 기준으로 한다. 이 파일은 60개 평가 질의, 8개 HyDE×CAD×SCD 조건, 검색·재정렬 설정, 생성 모델과 decoding 설정, reference SCD 설정, 평가 모델과 통계 절차를 하나의 최종 configuration으로 정의한다.

질의 구성 절차는 `VALIDATION/QUERY_CONSTRUCTION_PROTOCOL_60Q.md`에 기록한다. 실험 결과의 수치와 생성 기록은 `VALIDATION/FINAL_CLAIM_MAP_60Q.md` 및 연결된 source artifact에서 추적한다.

원고의 1~6장은 HyDE·CAD·SCD를 각각 검색 표현, 동일 문맥 decoding, 출력 언어 제어 관점에서 분석한다. 현재 제출 근거는 `FINALDOCS/`의 집계 자료와 검증 문서가 해시로 연결한 source artifact로 구성한다.
