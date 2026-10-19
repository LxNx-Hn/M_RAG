# 최종 산출물 재생성과 검증

원고·표 XLSX·현재13그림과11수식이 입력이다. 학교2026 HWP 원본과 변환 HWPX를 DELIVERY에 보존한다. 생성 모델/평가를 새로 호출하지 않고 저장된 자료에서 재현한다.

```powershell
python -m pip install -r FINALDOCS/BUILD/requirements.txt -r FINALDOCS/VALIDATION/requirements-statistics.txt
python -m FINALDOCS.VALIDATION.validate_all
python FINALDOCS/BUILD/build_thesis_hwpx.py --template FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx --page-map FINALDOCS/DELIVERY/PAGE_MAP_60Q.json --output tmp/finaldocs/thesis
python FINALDOCS/BUILD/verify_thesis_hwpx.py --file tmp/finaldocs/thesis/GRADUATION_REPORT_60Q_FINAL.hwpx
python FINALDOCS/BUILD/render_pdf_qa.py FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf --output tmp/finaldocs/pages
python FINALDOCS/POSTER/FINAL/rebuild_exports.py --output tmp/finaldocs/poster
```

HWPX가 조판 엔진을 대신하지 않는다. 내용이나 배치를 바꿨다면 새 HWPX를 한컴독스 웹에서 열어 PDF로 출력하고 모든 쪽을 검토한다. `map_pdf_pages.py <PDF> --output <임시지도>`로 실제 쪽을 찾고, 추출되지 않는 제목은 페이지에서 읽어 근거를 남긴 뒤 목차를 재빌드한다. 2026-10-19 교수 피드백·문체 개정본을 한컴독스 웹에서 출력한 최신 PDF는 47쪽이다. 변하지 않은 문서에 과거 쪽 보정값을 적용하지 않는다. 통계표는 `python FINALDOCS/VALIDATION/analyze_ttest_anova_60q.py` 다음 `python FINALDOCS/BUILD/build_ttest_anova_tables.py`로 JSON·XLSX·원고용 블록을 갱신한다.

개인 제출본은 저장소 밖 JSON을 `--personal-fields`로 전달하고 출력도 저장소 밖에 둔다. 확정된 성명·학번·소속·지도교수·제출일만 사용하며 미정인 인준·심사위원·날인은 입력하지 않는다.

`build_professor_diagrams.py`는 현재7개 개념/흐름 도식을, `build_print_evidence.py`는 저장된6개 실제 사례를 만든다. 사용 폰트·Inkscape 차이는 재렌더 결과를 바꿀 수 있어 기존 제출 그림을 자동 덮어쓰지 않는다. 실행 후 결과·폰트·해시를 검토해 의도한 교체만 반영한다. 각 생성기 명령의 `--help` 및 코드에서 입력을 확인한다.

`build_statistics_tables.mjs`와 `build_academic_poster.mjs`는 Artifact Tool 런타임에서 실행한다. 포스터는 `--output <임시폴더>`가 필수이고 개인 제출본에는 `--personal-fields <로컬JSON>`을 추가한다. 표 입력은 DATA/THESIS_TABLES_60Q.json이다. 최종 편집 파일은 먼저당사 프레젠테이션 도구의 패키지·편집 객체·재가져오기 검사를 통과한 원본이다. 문체 교정한 포스터는 기존 객체를 편집하고 PPTX 재가져오기와 SVG/PDF 문구 대조를 거쳤다.

검사 결과·본문 추출·PDF 페이지 PNG·연락표·300dpi 포스터·ZIP은 tmp로 생성한다. 거대한 HISTORY 복사본과 날짜별 검사 로그는 Git에 추가하지 않는다. 장·절·표·그림에 학교 명명 스타일을 적용하고, 긴 설명은 왼쪽·숫자는 오른쪽·조건/머리글은 가운데 정렬한다.
