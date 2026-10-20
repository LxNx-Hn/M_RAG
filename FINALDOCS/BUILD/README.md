# 재생성

원본 모델 실행이나 평가 API를 호출하지 않는다. 저장된 원자료에서 질문별 분석·표·원고를 재생성한다.

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

`build_question_tables.py`는 표 정의 JSON과 XLSX를 함께 만든다(openpyxl). 관련성 비교는 양쪽 조건 모두 0점이 아닌 질문으로 계산한다. 평행좌표는 기법별 60개 질문을 네 유형으로 나누고 여섯 지표를 표시한다. 모든 지표의 0점과 결측값은 표시할 때만 비운다. 처리 시간은 0~180초의 별도 역방향 축이며 원자료의 초 단위를 유지한다. 결과표는 비교마다 병합된 묶음 행과 질문 유형 4개·전체 60개 행으로 구성한다. 한컴 편집 화면 검수 기록은 `VALIDATION/EDITOR_REVIEW_20261020.json`, GPT 편집본 검토와 수정 내역은 `VALIDATION/REVIEW_GPT_FINAL_20261020.md`에 있다.

실제 그림 재생성에는 Matplotlib와 맑은 고딕이 필요하며 `ANALYSIS/plot_questions.py`를 실행한다. 그림은 11개, 편집 수식은 8개, 논리 표는 9개다. `build_professor_diagrams.py`는 연구 설정과 관련 연구의 독립 도식을 만든다. 파이프라인은 독립 SVG 원본이며 평가 설계·입출력 예시·평행좌표는 질문 분석 생성기가 관리한다.

HWPX 표와 그림은 학교 지시대로 글자처럼 취급한다. 긴 부록 표는 첫 조각 42,000 HWPUNIT, 이후 조각 56,000 HWPUNIT 이내로 나누고 마지막 조각을 합칠 때는 60,000 HWPUNIT까지 사용한다. 모든 표 조각에 머리행을 둔다. 질문·정답 근거의 전체 60행과 표시값은 XLSX에 직접 대조한다. 표 셀 정렬·강조·학교 서식을 유지한다.

한컴에서 열어 모든 페이지를 확인하고 표·그림·수식·각주·페이지 번호를 검토한다. 한컴 PDF 내보내기 후 `map_pdf_pages.py <PDF>`로 쪽 지도를 만들고, 추출이 어려운 제목은 편집 화면에서 직접 확인하여 기록한다. 같은 지도와 `--page-map`으로 목차 숫자를 채워 다시 빌드한 뒤 한컴에서 목차와 변경 페이지를 확인한다. PDF 검사로 편집 화면 검토를 대신하지 않는다.

포스터 재생성·환경 변수는 `POSTER/FINAL/README.md`를 따른다. 검사 로그·렌더·내보내기는 `tmp/`에 둔다. 확정된 개인 제출 정보는 저장소 밖 JSON을 `--personal-fields`로 전달하고 출력도 저장소 밖에 둔다.
