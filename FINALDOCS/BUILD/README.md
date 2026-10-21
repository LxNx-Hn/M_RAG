# 재생성

원본 모델 실행이나 평가 API를 호출하지 않는다. 저장된 원자료에서 질문별 분석, 표, 원고를 재생성한다.

```powershell
python -m pip install -r FINALDOCS/BUILD/requirements.txt -r FINALDOCS/VALIDATION/requirements-analysis.txt
python FINALDOCS/ANALYSIS/analyze_questions.py
python FINALDOCS/ANALYSIS/review_cases.py
python FINALDOCS/BUILD/build_question_tables.py
python FINALDOCS/BUILD/build_question_manuscript.py
python FINALDOCS/ANALYSIS/plot_questions.py
python FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json --output tmp/finaldocs/thesis
python FINALDOCS/BUILD/verify_thesis_hwpx.py --file tmp/finaldocs/thesis/GRADUATION_REPORT_60Q_FINAL.hwpx
python FINALDOCS/BUILD/build_poster.py --output FINALDOCS/POSTER/FINAL
python -m FINALDOCS.VALIDATION.validate_all
```

`build_question_tables.py`는 표 정의 JSON과 XLSX를 함께 만든다(openpyxl). 표 3-1은 조건 번호와 기법별 적용 여부, 표 5-1은 8개 조건의 지표별 평균(표준편차), 표 5-2는 같은 평균을 수치, 방법, 개념과 결과 질문으로 나눈 값이다. 표 5-2는 지표 두 개씩 세 묶음으로 나누어 한 쪽에 들어가게 하며, 묶음마다 머리행 두 줄(`header_rows`)을 둔다. 평행좌표는 질문 유형마다 그림 하나이며 미적용, HyDE, CAD, SCD 조건을 위에서 아래로 쌓는다. 한컴 편집 화면 검수 기록은 `VALIDATION/EDITOR_REVIEW_20261021.json`, 이번 개정의 수정 내역은 `VALIDATION/REVISION_REPORT_20261021.md`에 있다.

실제 그림 재생성에는 Matplotlib와 맑은 고딕이 필요하며 `ANALYSIS/plot_questions.py`를 실행한다. 그림은 12개, 편집 수식은 8개, 논리 표는 6개다. `build_professor_diagrams.py`는 연구 설정과 관련 연구의 독립 도식을 만들며, Inkscape가 없으면 `--chrome "C:/Program Files/Google/Chrome/Application/chrome.exe"`로 같은 SVG를 렌더링한다. 파이프라인(그림 4-1)은 독립 SVG 원본이며 같은 방식으로 PNG를 만든다.

HWPX 표와 그림은 학교 지시대로 글자처럼 취급한다. 긴 부록 표는 첫 조각 42,000 HWPUNIT, 이후 조각 56,000 HWPUNIT 이내로 나누고 마지막 조각을 합칠 때는 60,000 HWPUNIT까지 사용한다. 모든 표 조각에 머리행을 둔다. 질문과 정답 근거의 전체 60행과 표시값은 XLSX에 직접 대조한다. 표 셀 정렬, 강조, 학교 서식을 유지한다.

한컴에서 열어 모든 페이지를 확인하고 표, 그림, 수식, 각주, 페이지 번호를 검토한다. 한컴 PDF 내보내기 후 `map_pdf_pages.py <PDF>`로 쪽 지도를 만들고, 추출이 어려운 제목은 편집 화면에서 직접 확인하여 기록한다. 같은 지도와 `--page-map`으로 목차 숫자를 채워 다시 빌드한 뒤 한컴에서 목차와 변경 페이지를 확인한다. PDF 검사로 편집 화면 검토를 대신하지 않는다.

포스터 재생성과 환경 변수는 `POSTER/FINAL/README.md`를 따른다. 검사 로그, 렌더, 내보내기 파일은 `tmp/`에 둔다. 확정된 개인 제출 정보는 저장소 밖 JSON을 `--personal-fields`로 전달하고 출력도 저장소 밖에 둔다.
