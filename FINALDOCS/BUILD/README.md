# 학교 양식 HWPX 재생성과 검증

입력은 원고 MD, 14개 워크시트 XLSX, 삽입 그림 13개, 편집 가능한 수식 11개다. 참고문헌은 22편이다. 학교 양식의 글꼴·문단·명명 스타일·용지·단 정의를 보존한다. 표 셀은 머리글·짧은 조건을 가운데, 숫자를 오른쪽, 긴 설명을 왼쪽에 정렬한다. 목차 점선을 유지한다.

```powershell
python -m pip install -r FINALDOCS/BUILD/requirements.txt
python -m pip install -r FINALDOCS/VALIDATION/requirements-statistics.txt
python -X utf8 FINALDOCS/VALIDATION/verify_statistics_reproduction.py
python -X utf8 FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json
python -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
python -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'
python -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p 'test_*.py'
```

`--output`으로 출력 폴더를 지정한다. 개인 제출본은 저장소 밖의 JSON을 `--personal-fields`로 전달한다. 이름·학번·소속·지도교수·제출일은 확인된 값만 사용하고 미정인 인준·심사위원 항목은 입력 칸으로 유지한다. 공개본은 개인 필드를 비운다. 기존 출력은 `versions/`에 보관한다.

## 웹한글 출력과 목차

1. `--page-map` 없이 초안을 만들고 웹한글에서 열어 PDF로 내려받는다.
2. `python -X utf8 FINALDOCS/BUILD/map_pdf_pages.py <PDF> --output <지도 JSON>`으로 쪽 지도를 만든다.
3. 모든 쪽을 렌더링해 검토하고, 텍스트 추출이 불가능한 윤곽선 제목은 실제 페이지에서 읽어 `visual_overrides`에 기록한다.
4. 그 지도를 `--page-map`으로 적용하고 PDF를 다시 내려받아 목차 번호·본문 번호·표와 그림 배치를 대조한다.

원고와 배치 코드의 해시가 달라지거나 미확정 항목이 있으면 페이지 지도를 적용할 수 없다. Windows CRLF와 Git LF 차이는 LF 정규화 해시로 확인한다. 과거 출력본의 수동 쪽번호를 새 문서에 복사하지 않는다. 현재는 초록 없는49쪽이며 전면부 경계는 목차다. 표 5-2·5-4, 표 B-2와 절 B.2 앞 쪽나눔은 실제 웹 출력에서 발견한 제목 분리를 교정한 배치다. 절1.2의 이전 강제 쪽나눔은 고립된 서론 그림을 해소하기 위해 해제했다. 단순 포매팅 후에는 AST와 재빌드 HWPX의 모든 텍스트·배치·이미지·식별자 참조 그래프가 동일함을 독립 대조한 `formatting_equivalence` 기록도 보존한다.

## 자료와 도식

60개 질의·480개 생성의 통계 권위 파일은 `DATA/FACTORIAL_STATISTICS_60Q.json`이다. 반복측정 단위·완전 대응 결측 처리·Holm 가설군·탐색적 분석 지위를 함께 기록한다. 원자료는 변경하지 않는다.

`build_professor_diagrams.py`는 RAG·HyDE·CAD·SCD의 독립 개념도와 연구 설정·평가 흐름·파이프라인을 SVG와 PNG로 만든다. 문헌 그림의 개념 출처·작성 주체·이미지 해시는 `FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json`에 기록한다. 이전 원문 그림은 이력에 유지한다.

`build_statistics_tables.mjs`와 `build_academic_poster.mjs`는 Artifact Tool을 사용한다. 후자는 `--output <폴더>`가 필수이고 공개본을 기본으로 만든다. 제출본은 `--personal-fields <로컬 JSON>`을 추가한다. 통계 표 입력은 `DATA/THESIS_TABLES_60Q.json`이다.

독립 검사기는 패키지·XML, 원고 전체 문단 순서·출현 횟수, 1,229개 표 셀과 병합·정렬, 원본 이미지 바이트·비율, 수식, 인용·참고문헌, 학교 양식 정의를 검사한다. 훼손 시험은 실제 문서 사본에 값 변경·누락·중복·정렬 오류를 주입한다. 구조 검사와 웹한글의 실제 조판 검증을 구분한다.
