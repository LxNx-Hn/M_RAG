# 최종 제출본 가독성·인쇄 준비 검토

검토일: 2026-10-09. 시작 HEAD: `4ba2f0e495eea4dfc6dc7321bed0203924ad4b70`이며 작업 전에 origin/main과 대조했다. 이번 범위는 입출력 그림 6개의 가독성과 부록 A의 행 분할이다. 원고 MD, 초록·본문·캡션·결론의 문장, 실험 자료와 표 값은 시작 커밋과 동일하다.

## 최종 파일과 Git 기록

| 파일 | SHA-256 |
|---|---|
| `DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx` | `5bba603b26849fed9211f450b0f71e3141465d4ea5cf7d3c0e3b7b2203da55a3` |
| `DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf` | `58def5a7b86171f38c7168353185e6805cf6d5719190c8b154e2ad42ba818fdd` |

최종 PDF는 실제 웹한글 출력 **56쪽**이다. 최종 산출물 HEAD와 해당 SHA의 CI는 아래 GitHub 검증 기록에 기록한다. 보고서 자신을 포함하는 커밋의 SHA는 `git log -1 --format=%H -- FINALDOCS/VALIDATION/FINAL_PRINT_READINESS_AUDIT.md`로 확인한다. HWPX·PDF 자체의 버전 식별은 위 해시와 `DELIVERY_FILES_SHA256.json`을 사용한다.

## 입출력 그림 6개의 실제 판독성

수정 전 실제 PDF의 이미지 표시 영역을 96dpi(화면 100%), 192dpi(200%), 300dpi(A4 인쇄용)로 렌더하여 직접 읽었다. 300dpi에서 글자 획이 선명해져도 인쇄 크기의 글자가 2.96~4.96pt인 문제는 남았다. 기존 PNG는 바깥 여백이 약 8%이고, 긴 그림은 페이지 높이에 이미 맞춰 축소되어 있었다. 여백 제거·단순 확대만으로 본문 수준의 판독성을 확보하기 어려워 저장 원문에서 핵심 구간을 발췌해 같은 그림 번호의 이미지로 재조판했다.

| 사례·그림 | 기존 → 최종 PDF 쪽 | 기존 글자 크기 | 기존 판정·문제 | 최종 100% / 200% / A4 인쇄용 렌더 |
|---|---:|---:|---|---|
| E04·5-3 HyDE | 30 → 30 | 약 3.50pt | 개선 필요. 긴 양쪽 답변·HyDE 자료 때문에 조건과 평가값을 읽기 어려움 | PASS / PASS / PASS. OFF의 정보 부족 답변과 ON의 세 차원 답변, 변경된 검색 ID·문맥, 0.0000→0.8531 답변 관련성을 읽음 |
| E05·5-5 CAD | 33 → 32 | 약 4.17pt | 개선 필요. 같은 문맥의 두 답변과 점수가 세로로 과밀함 | PASS / PASS / PASS. 같은 검색 ID·세 데이터 경로·CAD ON/OFF·근거 충실도 0.8333→1.0000과 관련성 0.8261→0.8124를 읽음 |
| E02·5-7 언어 이탈 | 35 → 34 | 약 4.96pt | 개선 필요. 확대하면 판독되지만 A4 크기에서는 ID·지표가 작음 | PASS / PASS / PASS. 한국어 질문·CAD ON/SCD OFF·영어 서지형 답변·한국어 비율 0.0000을 읽음 |
| E03·5-8 SCD | 37 → 35 | 약 4.35pt | 개선 필요. 영문·혼합 답변과 동일 입력 여부의 판독에 확대가 필요함 | PASS / PASS / PASS. 같은 입력의 영어 A와 한국어가 포함된 B, SCD ON/OFF·한국어 비율 0.0000→0.7713·두 조건 평가값을 읽음 |
| E01·5-10 QA | 39 → 37 | 약 4.96pt | 개선 필요. 질문·청크 ID·검색 근거·답변의 글자가 인쇄 크기에서 작음 | PASS / PASS / PASS. Cinderella 질문·RAPTOR 근거와 계층/leaf 대비 답변·충실도 1.0000·관련성 0.9365를 읽음 |
| E06·B-1 CAD 추가 사례 | 54 → 53 | 약 2.96pt | 개선 필요. 가장 좁고 긴 표시 영역으로 질문·실패 답변·평가값의 판독이 어려움 | PASS / PASS / PASS. 같은 입력·CAD ON/OFF·저장된 실패 답변·충실도 0.9375→0.5000·관련성 0.9001→0.0000을 읽음 |

최종 6개 모두 실제 PDF 표시 폭은 약 403.92pt, PNG 폭은 2,000px, 그림 본문 글자는 48px이므로 물리 크기는 **약 9.694pt**이다. 100%에서 질문·질의 ID·설정·검색 ID·근거 발췌·답변 발췌·평가값을 판독했고, 200%와 300dpi에서 줄바꿈·문자 획·누락·잘림을 확인했다. 실물 프린터 출력 시험은 수행하지 않았으며, 인쇄 판정은 PDF의 A4 크기와 렌더에 대한 결과이다.

최종 판독용 이미지 18개는 `PRINT_COMPARISON/E01~E06-{100,200,print300}.png`에 있다. `PDF_PRINT_CHECKS.json`은 실제 이미지 영역·글자 크기·페이지를 기록한다. PDF에 포함된 그림의 RGB 픽셀은 최종 원본 PNG와 6개 모두 일치한다.

## 발췌와 평가값의 원자료 대조

`PRINT_EXCERPT_PLAN.json`은 원문 필드, 0부터 시작하는 시작/끝 문자 위치(끝 제외), 문맥 인덱스와 정확한 발췌 문자열을 담는다. 발췌가 저장 원문과 다르면 생성과 검증이 실패한다. 문맥 번호와 검색 ID는 각각 저장 필드로 표시하며 두 순서를 임의로 연결하지 않았다. 그림에는 검색 ID 앞 2개와 전체 8개임을 표시하고, 전체 검색·재정렬 ID는 `PRINT_EVIDENCE_MANIFEST.json`에 보존했다.

질문·설정 이름·HyDE/CAD/SCD ON/OFF·RAGAS 네 지표·전체 답변의 한국어 문자 비율은 원래 생성/평가 기록에서 읽었다. 평가지표를 발췌 문자열로 다시 산출하지 않았다. `[…]`는 발췌 경계를 나타낸다. 저장 답변의 오답, 영어 서지 문자열, E06의 `breath`와 실패 출력도 그대로 표시했다. E04의 정보 부족 표현은 저장 답변을 인용한 부분이며, 원고에 새로 쓴 논문 문장이 아니다.

기존 `cli/render_evidence_figures.py`, raw TXT 6개, 생성 JSONL, 평가 JSON, 질의 파일, 실험 설정은 유지했다. 신규 실험·모델 실행·API 호출은 수행하지 않았다. `SOURCE_PRESERVATION.json`은 원고·XLSX·문헌 출처 기록·조판 정책·원래 raw TXT를 시작 커밋과 대조한 해시이다.

## 부록 A의 행 분할과 모든 셀

기존 51쪽 위쪽에는 앞 쪽 행의 질문·근거가 질의 ID 없이 이어졌고, 52쪽 위쪽에는 `track1_0016`의 근거 뒷부분이 나머지 빈 셀과 이어졌다. 페이지를 따로 읽으면 질의와 근거의 연결이 분명하지 않았다. 기존 51·52쪽은 `appendix-before-page-51.png`, `appendix-before-page-52.png`로 보존했다.

부록 A에만 네이티브 표 `pageBreak=TABLE`을 적용하여 셀을 나누지 않고 행 전체를 다음 쪽으로 이동하도록 바꿨다. 9pt 글자 크기, 열 폭, 모든 셀 내용, 병합과 반복 머리글을 유지했다. 다른 표의 분할 속성은 그대로이다. TABLE의 의미는 [HWPX XML 명세를 정리한 작성자 자료](https://github.com/imsebeom/hwpx2/blob/main/references/xml-structure.md)와 대조한 뒤 실제 웹한글 출력으로 확인했다.

최종 부록 A는 **45~52쪽**이며 모든 쪽에 머리글을 반복한다. 60개의 질의 ID가 정확히 한 번씩 나타나고, 각각의 질문·대상 문서·유형·원문 페이지·근거가 같은 행에 있다. `verify_print_pdf.py`는 PDF의 표 경계와 실제 글자 좌표를 읽어 **360개 셀 전체가 XLSX와 일치**함을 확인했다. 공백과 PDF의 대시·따옴표 표현만 정규화하며 값·단어·순서를 생략하지 않는다. 최종 `track1_0016`은 50쪽의 한 행에 질문과 근거를 모두 담는다. 셀 잘림이나 다음 쪽의 ID 없는 근거 잔여 행은 없다. 최종 50~52쪽 상세 렌더와 모든 행 좌표를 보존했다.

## 새 쪽번호와 변경 전후 비교

| 구역 | 기존 57쪽 PDF | 최종 56쪽 PDF |
|---|---|---|
| 표지·인준·초록 | 1~4 | 1~4 |
| 목차·그림목차·표목차 | 5~8 | 5~8, 실제 새 위치로 갱신 |
| 서론~5.4 도입 | 9~29 | 9~29 |
| 5.5 / 5.6 / 5.7 / 5.8 / 5.9 | 32 / 34 / 38 / 39 / 40 | 31 / 33 / 36 / 37 / 38 |
| 결론 | 42~43 | 40~41 |
| 참고문헌 / 그림 자료 이용 정보 | 44~45 / 46 | 42~43 / 44 |
| 부록 A | 47~53 | 45~52 |
| 부록 B / B.2 | 54 / 55 | 53 / 54 |

이전 PDF와 같은 번호의 쪽을 비교하면 **1~4·9~29의 25쪽은 픽셀까지 동일**하고, 5~8·30~56은 목차 또는 배치·내용 위치가 달라졌다. 기존 57쪽의 마지막 표 내용은 최종 56쪽으로 이동했으며 삭제하지 않았다. 전체 쪽수를 고정하거나 여백·글꼴을 축소하지 않았다.

최종본과 쪽번호 산정용 웹한글 PDF 56쪽을 비교하면 **51쪽이 픽셀까지 동일**하다. 차이는 목차 5~8쪽과 E03 문맥 발췌를 완결한 35쪽이다. 35쪽의 이미지 크기와 표·캡션 위치는 같고 추가 텍스트 높이 증가가 없다. `PAGE_COMPARISON.json`에 쪽별 결과를 기록했다. 픽셀 비교는 양쪽 PDF를 새 렌더 문맥에서 열어 같은 조건으로 실행했다.

최종 56쪽 전체를 렌더하고 접촉 시트 5개를 직접 검토했다. 수정 그림 6개는 18개 상세 렌더로, 부록 A 8쪽은 전체 행과 반복 머리글로 검토했다. 목차·장절 제목·39개 표/그림 캡션의 실제 위치를 대조했다. PDF에서 장절 제목 일부가 텍스트 추출되지 않아 제목 위치는 렌더와 본문 문단 앵커를 함께 사용했다. 잘림, 겹침, 그림/캡션 분리, 표 머리글 누락, 새 빈 쪽은 발견되지 않았다. 전체 렌더는 `tmp/print_final/qa`, 보존한 접촉 시트와 상세 증빙은 `PRINT_COMPARISON/`에 있다.

## 학교 양식·학술 내용·개체 보존

학교 원본의 19개 스타일, 글꼴, 용지·여백·단 설정과 표지 배치용 표 2개를 보존했다. 본문 문단 형식과 `layout_policy.py`도 시작 커밋과 같다. 원고 전체 MD의 LF 기준 SHA-256은 `d96f5870ca702404c442f08c8df912d3c59fd97ac6e79866686f870df59e4a50`으로 동일하다.

독립 검사 결과: 원고 문단 333개 순서·출현 횟수, XLSX 셀 1,092개, 논문 표 17개, 그림 22개, 네이티브 수식 10개, 참고문헌 22편, 60질의×8조건=480생성 기록을 유지했다. 문헌 그림 6개와 출처·라이선스 기록, 구조·통계 그림 10개는 유지하고 입출력 PNG 6개만 재조판했다. 제목·그림 번호·캡션·실험 주장은 원고와 같다.

HyDE 답변 관련성 +0.0805, CAD 근거 충실도 +0.0288, SCD 동일 문맥 한국어 비율 +0.2182와 전체 +0.2289, 각 신뢰구간·표본 수·대응쌍 기준을 보존했다. 원자료 7개 해시 대조는 통과했으며 19질의 결과를 섞지 않았다. HWPX의 표·수식·글자 문단은 편집 가능한 네이티브 개체이다.

## 표지·제출·인준 미입력 항목

`SUBMISSION_PERSONAL_FIELDS.md`를 전부 읽고 입력 위치를 확인했다. 이번 사용자 요청에 확정 값이 없어 **학생명, 학번, 소속 학과, 소속 대학·캠퍼스, 지도교수, 제출일, 인준일, 심사위원, 제출연도 9개 항목은 미입력**이다. 1~2쪽의 입력 위치와 학교 배치를 유지했다. 심사위원 서명·날인도 학교 절차에 따라 필요하다. 계정 이름이나 다른 파일의 개인정보를 전용하지 않았고 개인정보를 채운 파일을 GitHub에 게시하지 않았다.

실제 값을 입력한 뒤 1~2쪽 반복 위치·줄바꿈과 인준 공간을 확인하고 저장·재열기·PDF 내보내기를 다시 수행해야 한다. 본문 쪽이 이동하면 목차도 갱신한다.

## 웹한글 열기·출력 및 실제 검사

최종 HWPX와 바이트가 같은 `GRADUATION_REPORT_60Q_PRINT_FINAL.hwpx`를 한컴독스에 업로드하고 실제 웹한글 편집기로 열었다. 「파일 → PDF로 다운로드」로 출력한 파일을 최종 PDF로 보존했다. 웹한글 30쪽의 질문·조건·답변·평가값 표시와 56쪽 수를 확인했다. 화면 증빙은 `DELIVERY/WEB_PRINT_REVIEW.png`이다. 중간 초안의 내보내기를 최종 검증으로 대신하지 않았다.

```powershell
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p "test_*.py"
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/BUILD -p "test_*.py"
python -X utf8 FINALDOCS/BUILD/verify_print_pdf.py
.venv-hwpx/Scripts/python.exe -X utf8 -m compileall -q FINALDOCS/BUILD FINALDOCS/VALIDATION
git diff --check
```

모두 실행하여 통과했다. VALIDATION 27개·BUILD 13개, 합계 **40개 회귀 시험**을 통과했다. 발췌 위조·평가값 변경·질의 변경·그림 해시 변경·부록 셀 분할 복귀를 주입하는 시험을 포함한다. 변경 Python 파일의 Ruff·Black 검사도 통과했다. 실제 명령·출력·종료 코드는 `DELIVERY/LOGS/print-local-checks.txt`에 기록한다.

추가 PDF 검사에서 처음에는 내용 스트림 순서의 혼합 문자 추출을 사용해 캡션/셀 비교가 실패했다. 실제 글자 좌표 순서로 비교하도록 수정하고 원본 360개 셀 및 최종 그림 6개 픽셀의 일치를 확인했다. 실패를 무시하거나 0으로 대체하지 않았다. 이 검사 도구에는 PyMuPDF·Pillow가 필요하며 웹한글 렌더 자체를 대체하지 않는다.

첫 커밋 시 로컬 훅은 전역 Python의 Ruff 0.16.0을 사용하여 백엔드 검사에서 실패했다. CI가 지정한 Ruff 0.13.0을 포함한 `.venv-hwpx` 환경에서 백엔드 Ruff·Black을 실행하여 모두 통과했고, 동일 환경으로 커밋 훅도 통과했다. 백엔드 코드나 훅 설정은 변경하지 않았다.

## 실제 변경 파일

- `BUILD/build_thesis_hwpx.py`, `verify_thesis_hwpx.py`, `test_hwpx_validation.py`: 부록 A 행 분할·검증·훼손 회귀 시험.
- `BUILD/build_print_evidence.py`, `verify_print_pdf.py`: 원문 발췌 인쇄 조판, 실제 PDF 그림·표 검사.
- `VALIDATION/print_evidence_checks.py`, `test_print_evidence.py`, `verify_finaldocs_60q.py`: 원자료·발췌·지표 검증과 5개 추가 시험.
- `EVIDENCE/IO_CASES/E01~E06` PNG 6개, `PRINT_EXCERPT_PLAN.json`, `PRINT_EVIDENCE_MANIFEST.json`.
- 최종 HWPX·PDF·build JSON·쪽번호 지도·파일 해시 목록·독립 구조/추출 결과·웹한글 화면 증빙·이번 실행 로그.
- 이 보고서, `PRINT_COMPARISON/`의 쪽 비교·원문 보존·PDF 셀/그림 검사·렌더 증빙, `FINALDOCS/README.md`, `BUILD/README.md`.

기존 미추적 DOCX, DOCX 빌더와 `tmp/`는 이번 커밋에 포함하지 않는다. 이전 파일과 기록은 보존한다.

## GitHub 검증 기록

최종 산출물 HEAD는 `4e142cde877d3209c50d1abf6667733c40f03ebd`이며 origin/main에 push했다. 해당 전체 SHA와 일치하는 다음 세 실행이 모두 **completed / success**이다.

- [CI: 백엔드·프런트엔드 검사, 시험 및 Docker 빌드](https://github.com/LxNx-Hn/M_RAG/actions/runs/37837007866)
- [Thesis HWPX validation: 논문 원자료·HWPX 검증](https://github.com/LxNx-Hn/M_RAG/actions/runs/37837007899)
- [Publish Backend Image: 백엔드 이미지 빌드·게시](https://github.com/LxNx-Hn/M_RAG/actions/runs/37837007939)

실행 ID·전체 HEAD·상태·결론은 `DELIVERY/LOGS/print-ci-artifacts.json`에 보존했다. 이 보고서와 실행 기록을 반영하는 후속 커밋은 논문 파일을 변경하지 않는다. 후속 커밋의 CI도 완료 후 최종 사용자 보고에 전체 결과를 제시한다.

## 제출 판단

**논문 본문·인쇄 가독성·편집 개체·웹한글 출력의 제출 준비 검토는 통과했다.** 행정 제출에는 9개 개인/소속/날짜 항목의 확정 입력과 학교가 요구하는 서명·인준이 남아 있다. 웹한글 PDF는 출처 URL을 표시하지만 URI 링크 주석을 생성하지 않는 기존 특성이 있어 주소를 선택·복사하여 사용한다. 최종 HWPX에는 기존 7개 네이티브 하이퍼링크를 유지했다.
