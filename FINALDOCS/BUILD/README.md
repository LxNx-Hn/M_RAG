# 학교 양식 기반 HWPX 재생성

Python 3.11에서 `python -m pip install -r FINALDOCS/BUILD/requirements.txt`를 실행한다. 설치형 한컴오피스·COM·실험 API는 사용하지 않는다. 빌드 입력은 원고 MD, 17개 워크시트 XLSX, 삽입 지시의 PNG, 수식 원문이다.

```powershell
python -X utf8 FINALDOCS/BUILD/probe_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx
python -X utf8 FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json
python -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
python -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'
```

`--template`은 HWP/HWPX를 받는다. `--manuscript`, `--tables`, `--output`으로 입력과 출력 위치를 지정한다. 그림과 수식은 원고의 삽입 지시를 읽는다. 원본 HWP를 사용하면 변환 보고서에 누락이 있는 경우 중단한다. 이미 변환한 학교 양식을 저장소에 보존하므로 원본 Downloads 경로가 없는 환경에서도 재생성할 수 있다. 작은 시험본은 `--smoke-only`로 생성한다.

기존 출력 HWPX는 `versions/<UTC시각>/`에 보관한다. 학교 양식의 글꼴·문단·스타일 정의와 용지·단 설정을 보존하고, 생성 복사본의 예시 내용을 논문으로 교체한다. 내용이 잘못되면 예외를 발생시키며, 결측값을 0으로 채우지 않는다.

목차 번호는 실제 웹한글 PDF를 검토한 `PAGE_MAP_60Q.json`을 사용한다. 원고 해시가 바뀌거나 미확정 항목이 있으면 이 파일을 적용할 수 없다. Windows CRLF와 Git LF의 동일 텍스트는 별도 LF 해시로 확인한다. 문서 내용이나 배치를 변경하면 다음 순서로 새 페이지 지도를 만든다.

1. `--page-map`을 생략하여 초안을 생성하고 웹한글에서 PDF로 내려받는다.
2. `python -X utf8 FINALDOCS/BUILD/map_pdf_pages.py <PDF경로> --output <새 지도 경로>`를 실행한다. 이 보조 도구에는 PyMuPDF가 필요하다.
3. PDF의 모든 쪽과 제목·캡션 위치를 직접 검토한다. `unresolved` 항목은 근거를 확인하여 수동으로 해결하고 `visual_overrides`에 기록한다.
4. 새 지도를 `--page-map`으로 적용한 뒤 다시 PDF를 출력하여 목차 및 배치가 일치하는지 확인한다.

`finalize_page_map.py`의 수동 값은 2026-10-08 초기 출력본의 SHA-256에만 적용한다. 다른 PDF에는 실행을 거부한다. 새로운 출력본에 이 숫자를 복사하지 않는다. `render_pdf_qa.py`는 PyMuPDF와 Pillow로 모든 쪽과 접촉 시트를 보존한다. PDF 보조 도구는 빌드/구조 검증의 필수 의존성이 아니다.

독립 검사기는 ZIP/XML/패키지, 모든 원고 문단의 순서와 출현 횟수, 모든 표 셀과 병합, 원본 이미지 바이트·비율, 수식, 참고문헌, 학교 스타일, 60×8 생성 기록과 원자료 해시를 검사한다. 훼손 시험은 문단 중복·표 값 변경·수식 변경·그림 누락을 실제 ZIP 복사본에 주입한다. CI는 커밋된 파일과 재생성 파일을 각각 검사한다. 웹한글 편집과 PDF 조판은 브라우저에서 별도로 검증해야 한다.
