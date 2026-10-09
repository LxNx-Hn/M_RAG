# 졸업논문 문장 교정 및 최종 출력 검토

검토일: 2026-10-10. 기준 커밋은 `2e6a96a915f246a2f1bf215db9f53f11e84970a5`이다. 국문초록, Abstract, 1~6장, 그림 설명, 참고문헌 뒤 출처 안내와 부록 설명을 수정하고 실제 웹한글에서 HWPX를 열어 PDF를 내보냈다. 최종 출력은 55쪽이며, 서론부터 표시 쪽번호 1~47로 이어진다. 이전 감사 문서의 쪽수는 당시 산출물 기록이다.

## 문체에서 확인한 문제와 수정

사용자가 제공한 원문 A·수정안 B와 직접적인 학술 문체를 기준으로 86개 원고 문단·행을 변경했다. 수정·재수정을 포함한 작업 기록은 148건이다. 이는 서로 다른 문장 148개를 뜻하지 않는다. 최종 원고의 문장·제목·목차·캡션 등을 포함한 검토 단위는 532개이다. 각 단위의 판단과 변경 전후 문장은 [전수 검토 기록](PROSE_SENTENCE_REVIEW.json)에 남겼다.

이번 원고에서 확인한 문제는 다음과 같다. 특정 단어의 등장만으로 생성형 AI 문장이라고 판정하지 않고, 문장이 실제로 전달하는 정보와 앞뒤 문단의 관계를 확인했다.

| 확인한 문장 패턴 | 수정 기준 |
|---|---|
| 수치를 설명한 뒤 같은 뜻을 추상적인 평가 문장으로 반복함 | 결과와 비교 조건을 남기고 중복 해석을 제거함 |
| ‘기반’, ‘관점’, ‘구성’, ‘적용’을 이어 붙여 동작이 흐려짐 | 무엇을 검색하고 계산하고 비교했는지 동사로 설명함 |
| 각 장에서 연구 목적·분석 지표·기법 소개를 같은 구조로 반복함 | 처음 필요한 정의와 실제 분석을 남기고 중복 예고를 줄임 |
| 실제 수행한 평가와 후속 평가 제안을 같은 시제로 표현함 | 수행한 절차와 관찰 결과는 과거형으로, 후속 평가는 제안으로 표현함 |
| 연구 범위를 부정하거나 방어하는 문장으로 설명함 | 실제 비교 조건과 지표가 측정하는 대상을 직접 서술함 |

예를 들어 CAD 설명의 ‘단일 분포보다 실행 비용이 증가할 수 있다’는 일반적인 예측을 다음과 같이 바꿨다.

> CAD는 생성 단계마다 두 분포를 계산한다. 5.5절에서는 이에 따른 생성 시간과 근거 충실도·답변 관련성의 대응 차이, 질의별 증가·감소 분포를 분석하였다.

HyDE 결과의 ‘검색 경로 전체의 결과로 해석해야 한다’는 독자에게 해석을 요구하는 표현을 다음과 같이 고쳤다.

> HyDE의 답변 관련성 변화에는 질의 번역, 가상 문서 생성과 검색 문맥 선택의 변화가 함께 반영되어 있다.

결론의 후속 평가도 실제 수행 여부를 드러내도록 정리했다.

> 고유명사·인용·전문용어의 보존 여부는 후속 사람 평가의 항목으로 제안한다.

지표 감소, 신뢰구간, 동일 문맥 조건처럼 실험 해석에 필요한 비교 표현은 유지했다. 남은 부정·대조 표현 후보 21개는 사실 전달 여부를 문맥에서 다시 확인했다. 질의 구성에 LLM을 사용한 사실과 5개 faithfulness 결측값도 유지했다.

## 수치·출처 보존

- 60질의×8조건의 생성 기록 480개, SCD 상태 대응 240쌍과 동일 문맥 H0 120쌍을 구분했다. H1의 HyDE 독립 표본 추출에 따른 문맥 변화 설명도 유지했다.
- 원고의 코드 블록 28개, 참고문헌 22개와 수식 10개를 기준 커밋과 대조하여 동일함을 확인했다. 표 17개와 XLSX 셀 1,092개를 HWPX에서 독립적으로 검사했다.
- 실험 자료·표·그림·입출력 발췌 등 40개 파일을 기준 커밋과 대조했다. [보존 검증 기록](NATURAL_PROSE_QA/SOURCE_PRESERVATION.json)에 해시를 남겼다.
- 참고문헌의 원문은 그대로 두고, HWPX 표시에서만 Markdown의 짝지어진 별표를 제거했다. 인용 번호와 참고문헌 순서는 유지했다.
- 검색·생성·평가 실험과 서비스 코드는 변경하거나 재실행하지 않았다.

## 학교 양식과 출력

2026 학교 양식의 용지, 여백, 글꼴, 문단·목차·참고문헌 스타일을 보존했다. 표 4-2와 부록 표 B-1은 캡션과 표가 함께 시작하도록 페이지 배치를 조정했다. 실제 웹한글 PDF의 표·그림 39개 위치와 HWPX 목차 77개 항목의 쪽번호를 대조했다.

55쪽 전체를 렌더링해 확인했다. 원본 발췌 그림 6개는 PDF의 삽입 픽셀과 원본이 일치했으며, 환산 글자 크기는 약 9.69pt로 9pt 기준을 충족했다. 부록 A의 60개 질문·360개 셀과 반복 표 머리글도 확인했다. [출력 검사](NATURAL_PROSE_QA/PRINT_READABILITY/PDF_PRINT_CHECKS.json), [쪽수 검토](NATURAL_PROSE_QA/FINAL_PAGINATION.json), [전체 쪽 미리보기](NATURAL_PROSE_QA/contact-01.jpg)에 근거를 남겼다. 나머지 미리보기는 같은 폴더의 contact-13·25·37·49이다.

공개 검증본과 개인정보를 입력한 다운로드 폴더의 제출본은 3~55쪽이 픽셀 단위로 동일하다. 제출본 표지 1~2쪽은 별도로 렌더링해 성명·학번·학과·지도교수·제출일의 배치와 표시를 확인했다. 인준일·주심·부심은 원래 입력 칸을 남겼다. [두 출력본 비교](NATURAL_PROSE_QA/PUBLIC_PRIVATE_COMPARISON.json)에는 개인정보 값 대신 검사한 항목만 기록했다.

## 실행한 검증

다음 검사는 모두 통과했다. 문서 검증 테스트는 합계 41개이다.

```powershell
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p 'test_*.py'
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
python -X utf8 FINALDOCS/BUILD/verify_print_pdf.py --output FINALDOCS/VALIDATION/NATURAL_PROSE_QA/PRINT_READABILITY
.venv-hwpx/Scripts/python.exe -m ruff check FINALDOCS/BUILD FINALDOCS/VALIDATION --exclude build_hwp_transfer_docx.py
.venv-hwpx/Scripts/python.exe -m black --check FINALDOCS/BUILD/build_thesis_hwpx.py FINALDOCS/BUILD/verify_thesis_hwpx.py FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -m compileall -q FINALDOCS/BUILD FINALDOCS/VALIDATION
git diff --check
```

개인정보 입력본도 별도 경로를 지정해 HWPX 구조·내용 검사를 통과했다. 원고 검증기의 기존 글자 수 하한은 장·절 구조와 필수 실험 근거 확인으로 바꿨다. 모든 6개 장·29개 절의 설명, 5.7절의 실제 사례·값·그림, 6.2절의 핵심 결과와 120/240쌍 구분을 검사하므로 반복 문장으로 분량을 채울 필요가 없다.

해당 변경 커밋의 원격 CI 결과와 최종 SHA는 GitHub 워크플로 기록 및 완료 보고에서 확인한다. 기존 미추적 DOCX, DOCX 생성기와 tmp 파일은 이번 변경에 포함하지 않는다. 개인정보를 입력한 제출본은 공개 저장소에 포함하지 않는다.

## 남은 입력과 사용 범위

인준일과 주심·부심 성명은 아직 정해지지 않아 입력 칸이 남아 있다. 확정 후 이를 입력하면 해당 표지의 출력 상태를 다시 확인하면 된다. 현재 쪽번호는 이번 55쪽 웹한글 출력에 맞춘 값이므로 본문 분량이나 배치를 추가로 바꾸면 목차도 다시 확인해야 한다.

이번 교정의 판정 근거는 문장의 자연스러움, 정보 전달, 실험 사실 및 출력 상태이다. 생성형 AI 탐지 점수나 저자 판정 결과를 완료 근거로 사용하지 않았다.
