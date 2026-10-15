# M-RAG 졸업논문·포스터 최종 패키지

현재 기준은 [교수 피드백 반영 감사](VALIDATION/PROFESSOR_FINAL_AUDIT_20261016.md)다. 제목은 **한국어 질의로 영어 학술·기술 문서를 검색하는 RAG에서의 HyDE·CAD·SCD 조합 실험**이다.

- [공개 HWPX](DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx) / [웹한글 출력 PDF](DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf)
- [A1 포스터·프롬프트·배포 묶음](POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/README.md)
- [원고](MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md) / [표 14개 XLSX](TABLES/TABLES_60Q.xlsx)
- [최종 주장과 수치 근거](VALIDATION/FINAL_CLAIM_MAP_60Q.md) / [전체 통계 JSON](DATA/FACTORIAL_STATISTICS_60Q.json)
- [최신 원고 변경 A→B 16구간](VALIDATION/PROFESSOR_PROSE_AB_20261016.md) / [전체 538단위 문장 검토](VALIDATION/PROSE_SENTENCE_REVIEW.json)
- [질의 작성·보관 범위](VALIDATION/QUERY_CONSTRUCTION_PROTOCOL_60Q.md) / [60개 질의 근거](APPENDIX/QUERY_60_AUDIT.md)
- [자료 가용성 기록](VALIDATION/DATA_AVAILABILITY_60Q.md)
- [22편 문헌 출처 대조](VALIDATION/REFERENCE_RECHECK_20261016.md)
- [재생성과 검사 방법](BUILD/README.md)

논문은 표 14개·그림 13개·편집 가능한 수식 11개·참고문헌 22편이다. 학교 표지 배치용 표 2개는 논문 표 수에 포함하지 않는다. PDF는 47쪽이며 서론부터 표시 쪽번호 1~39이다. 목차 점선과 학교 명명 스타일을 유지한다. 공개본은 개인 정보 입력 칸을 유지하며, 확인된 개인 정보를 넣은 제출본은 로컬 다운로드 폴더에 보관한다.

60개 질의×8조건의 생성 480건과 평가 점수는 원자료 그대로 사용한다. 현재 통계는 평균(SD), 질의 단위 반복측정 ANOVA, 대응 비교와 Holm 보정이다. 부트스트랩 기록은 보조 분석으로 유지한다. 최종 질의·원문 페이지·정답 근거를 저장 자료와 대조하며, 작성 자료의 보존 상태는 자료 가용성 기록에 제시한다.

이번 재검토의 기준은 `10578fb2b31df3001bdf7b6dd1d9027cde41334f`다. 변경은 `codex/positive-academic-final-20261016`에서 검토하며 main 병합은 별도 검토 대상으로 둔다.

`HISTORY/` 및 이전 날짜의 감사 파일은 해당 단계의 이력이다. 현재 결과와 파일 판정은 위 최신 감사·해시·CI 기록을 따른다. 실제 인쇄 가독성과 PowerPoint 설치 프로그램 실행 여부는 디지털 구조·출력 검사와 구분해 보고한다.
