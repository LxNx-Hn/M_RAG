# 60-query RAG-Cube 졸업논문 최종 작성 패키지

이 디렉터리는 HWP 최종 작성과 제출 전 사실 확인에 필요한 원고·표·그림·증빙·검증 자료로 구성한다.

- `MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`: 한글 이전용 단일 원고
- `MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md`: 표·그림·증빙 화면의 HWP 배치 안내
- `MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt`: HWP 수식 입력값
- `MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt`: 한글 표 변환용 탭 구분 원본
- `TABLES/TABLES_60Q.xlsx`: 본문과 부록의 17개 표가 들어 있는 단일 workbook
- `FIGURES/*.png`: HWP에 삽입할 10개 구조·통계 그림
- `APPENDIX/QUERY_60_AUDIT.md`: 60개 질의 목록
- `DATA/EXPERIMENT_60_VALIDATION.md`, `DATA/evidence_manifest_60q.json`: 수치·원자료 출처 검토용
- `VALIDATION/FINAL_VALIDATION_REPORT_60Q.md`: 최종 패키지 검증 보고서
- `VALIDATION/FINAL_CLAIM_MAP_60Q.md`: 최종 주장-근거 연결표
- `VALIDATION/verify_finaldocs_60q.py`: 네트워크·모델 호출 없이 실행하는 제출 패키지 점검기

원고의 1~6장은 HyDE·CAD·SCD를 각각 검색 표현, 동일 문맥 decoding, 출력 언어 제어 관점에서 분석한다. 현재 제출 근거는 `FINALDOCS/`의 집계 자료와 검증 문서가 해시로 연결한 source artifact로 구성한다.
