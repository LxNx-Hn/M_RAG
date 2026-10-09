# 2026 학교 양식 적용 및 최종 출력 검증

검토일: 2026-10-10. 수정 전 근거는 [학교 양식 재검증](SCHOOL_FORMAT_RECHECK_2026.md)이다. 이전 감사 문서와 페이지 번호는 각 작업 당시의 기록이며, 현재 출력은 이 보고서와 `DELIVERY/PAGE_MAP_60Q.json`을 기준으로 확인한다.

## 변경과 판정

학교 최신 공지 첨부의 `붙임 2. 졸업논문보고서 양식_2026_스타일적용.hwp`를 변환하여 원본 표지·인준 배치를 복원했다. 22개 원본 스타일 정의, 용지·여백·단을 보존하고 본문·제목·캡션·표·그림의 실제 문단/글자 적용값을 원본 이름 스타일에 맞췄다. 이전 조판 정책의 간격·글자 크기 덮어쓰기는 제거했다. 표 내용에도 원본 `표내용` 스타일을 적용한다.

국문·영문 제목과 주심·부심 칸이 있는 두 번째 표지를 사용한다. 공개본은 입력 표시를 유지한다. 사용자가 확정한 소속·성명·학번·지도교수·제출일은 다운로드 폴더의 개인 제출본에 적용했다. 실제 입력에는 원본 표지 셀의 검정 글자 run을 사용한다. 인준일, 주심·부심 성명, 실제 날인은 미정이다. 개인 값과 개인 제출 파일은 저장소에 포함하지 않는다.

서론에서 쪽번호를 1로 다시 시작한다. 실제 웹한글 PDF는 **54쪽**, 서론은 **물리 9쪽 / 표시 1쪽**, 본문 표시는 **1~46쪽**이다. 목차는 표시 쪽번호를 사용하고, PDF 검사기는 물리 페이지를 사용한다. 장 1~6은 물리 9, 11, 18, 21, 24, 38쪽에서 시작한다. 39개 표·그림 캡션과 장·절 위치를 대조했으며, 자동 추출되지 않는 제목은 렌더를 직접 확인하여 명시적 보정 기록을 남겼다. 짧은 표 3-3, 절 5.9와 6.3의 시작을 다음 쪽으로 옮겨 표 분할과 절 제목의 고립을 해소했다. 목차 항목에는 이 쪽 나눔을 적용하지 않는다.

참고문헌을 첫 인용 순서 1~22로 정렬했다. 이전 9→10, 10→11, 11→12, 12→9를 원고 인용·서지 목록·그림 출처 명세·관련 검사기에 함께 적용했다. 본문은 인용 번호를 역변환하여 수정 전 문자열과 일치함을 확인했고, 22편 서지 텍스트를 개별 대조했다. 방어형 문장을 새로 추가하거나 본문을 재작성하지 않았다. XLSX, 원자료, 원래 입출력 TXT, E01~E06와 나머지 그림의 바이트/정규화 해시가 수정 전 HEAD와 일치한다.

## 실제 출력 검증

- 공개 일반본과 개인 제출본 모두 웹한글에서 열어 PDF로 내보냈다. 총 54쪽이며 **3~54쪽은 두 파일의 픽셀이 모두 같다**. 차이는 두 표지에 한정된다.
- 개인 정보는 HWPX 표지 XML에서 정확한 문자열로 확인하고, PDF 두 표지 렌더에서 눈으로 재검토했다. 표지 PDF 글꼴은 텍스트 추출을 지원하지 않는 부분이 있어 추출 문자열 검사를 대신 통과 처리하지 않았다.
- 전체 54쪽 렌더를 검토했다. 목차·캡션·절 시작과 표 분할 수정 결과를 확인했다.
- E01~E06 6개 입출력 이미지는 PDF에 포함된 픽셀이 원본과 같고, 인쇄 글자 크기는 약 9.694pt다. 100%, 200%, 300dpi 이미지가 제공된다. 질문·조건·검색 근거·답변 발췌·평가값을 판독했다.
- 부록 A는 60개 질의의 360개 셀을 XLSX와 대조했다. 질의 행은 쪽 경계에서 나뉘지 않고, 표 머리글이 반복된다.
- 구조 검사: 순서가 맞는 본문 324문단, 논문 표 17개(표지 배치 표 2개 별도), 그림 22개, 편집 가능한 수식 10개, 참고문헌 22편, 60질의×8조건=480기록. 원고 앞부분의 9개 표지 메타 항목은 학교 원본 표지에 반영하고 본문 순서 검사에서 별도로 취급한다.

근거: [PDF 검사](SCHOOL_2026_QA/PDF_PRINT_CHECKS.json), [개인본과 공개본 비교](SCHOOL_2026_QA/PUBLIC_PRIVATE_BODY_COMPARISON.json), [원자료 보존](SCHOOL_2026_QA/SOURCE_PRESERVATION.json), [쪽번호 지도](../DELIVERY/PAGE_MAP_60Q.json), `SCHOOL_2026_QA/contact-*.jpg` 및 `E01~E06` 확대 렌더.

## 실행 검사

```powershell
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p 'test_*.py'
python -X utf8 FINALDOCS/BUILD/map_pdf_pages.py <실제 웹한글 PDF> --output <검토용 지도>
python -X utf8 FINALDOCS/BUILD/verify_print_pdf.py --pdf FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf --output FINALDOCS/VALIDATION/SCHOOL_2026_QA
python -m compileall -q FINALDOCS/BUILD FINALDOCS/VALIDATION
```

회귀 테스트는 BUILD 14개, VALIDATION 27개로 총 41개다. 서론 쪽번호 재시작이 훼손되면 독립 검사에서 실패하는 테스트를 추가했다. 수정 Python 파일의 Ruff·Black 및 Git 공백 검사를 수행한다. GitHub의 CI, Thesis HWPX validation, Publish backend image는 공개본 변경을 푸시한 HEAD에서 확인하며 결과를 완료 응답에 보고한다. 논문 양식·검사기 수정이므로 모델 호출이나 추가 실험은 수행하지 않았다.

## 남은 제출 항목

인준일·심사위원·실제 날인은 결정 이후 입력해야 한다. 이 파일은 심사·날인 완료를 의미하지 않는다. 포스터는 사용자 요청에 따라 직접 수정하지 않고, 다운로드 폴더에 A1 재배치·작성자 정보·최신 출처 번호·수치 보존·판독성 검사를 포함한 수정 프롬프트와 학교 A1 PPTX를 제공했다. 실제 수정된 A1 포스터 PPT/PDF는 아직 만들어지지 않았다. 실물 인쇄 시험은 수행하지 않았다.
