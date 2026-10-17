# 최종 검토 기록 · 논문·포스터 · 2026-10-16

## A. Git 기준점

- 실제 작업 시작 main·origin/main: `10578fb2b31df3001bdf7b6dd1d9027cde41334f`.
- 교수 피드백 이전 비교 기준: `d4931ec76f591016b2601561d17fbd37ac2a833a`. 해당 감사·A→B는 `HISTORY/20261016_before_positive_revision/`에 보존한다.
- 작업 브랜치: `codex/positive-academic-final-20261016`. main 병합은 최종 검토 대상으로 둔다.
- 시작 시 tracked 변경 0개. 기존 untracked `_render_fonts/`, XLSX inspect 로그, `VALIDATION/build_hwp_transfer_docx.py`, `tmp/`는 보존하고 커밋에서 제외한다.
- 수정 완료 커밋과 원격 CI는 이 문서를 포함하는 브랜치 HEAD 및 PR 체크에 연결한다. 최종 HEAD·CI URL·원격 일치 기록은 로컬 제출 폴더의 `FINAL_GIT_CI_RECEIPT_20261016.json`과 완료 보고에서 확인한다. 커밋 자신의 SHA를 본문에 삽입하는 순환 참조는 사용하지 않는다.

변경 파일 목록은 `CHANGED_FILES_20261016.txt`에 기록한다.

## B. 교수 피드백 반영 결과

### 논문

| 위치 | 실제 문제 | 적용한 수정 | 검증 근거 |
|---|---|---|---|
| 5.1, 표시 13쪽 | 초기 작성 자료의 보관 상태를 본문에서 해명 | 최종 질의 60개·대상 문서·원문 페이지·근거를 직접 설명 | 원고 5.1, 실제 PDF 물리 21쪽, A→B 6번 |
| 2.3 | 그림 2-2은 | 그림 2-2는 | 원고·HWPX·PDF 대조 및 조사 오류 주입 시험 |
| 2.4 | 실행 시간과 품질을 모두 5.7절로 참조 | 시간 요인 효과 5.6, 품질 대응 비교 5.7 | 교차참조 오류 주입 시험 |
| 2.6 | 대응 설계를 5.2절로 참조, 이론 절에 bootstrap 중심 절차 | 지표 정의에 집중, 대응 설계 3.3·통계 5.4 참조 | 이론/통계 배치 회귀 검사 |
| 5.4 | 기존 코드·공개 절차를 설명하는 문장 | 분모 0 답변의 기록 규칙과 n=59 민감도 분석을 직접 기술 | 통계 원자료와 재현 검사 |
| 5.8~5.9, 6.1 | 추상적 상호작용·중복·판정 과정 설명 | 실제 시간 차이·p·평가 입력·반복 평가 대상을 명시 | A→B 16구간, PDF 수정 문구 대조 |
| 5장 끝 | 두 줄만 별도 쪽으로 이월 | 중복 문장과 장황한 평가 설명을 통합 | 새 PDF 47쪽, 결론 물리 29쪽 시작 |
| 목차 표시 -6- | 이전 화면의 하단 여백이 빈 페이지처럼 보임 | 12개 목차 항목이 있는 정상 계속 쪽으로 확인, 점선 유지 | 최종 PDF 물리 6쪽 전체 렌더 |
| 표지 | 제출 정보·미정 인준 항목 | 확인된 개인 정보·2026-10-15 반영, 인준일·주심·부심 입력 칸 유지 | 개인 제출본 표지 1~2쪽 시각 확인 |

### 포스터

| 위치 | 실제 문제 | 적용한 수정 | 검증 근거 |
|---|---|---|---|
| 01 | 연구 주체 생략 | 본 연구·한국어 질의·영어 문서·평가 대상 명시 | 표시 문구/PDF 대조 |
| 04 | 점수가 높으면 점수가 높다는 반복 | 근거 지지·질문 관련성·근거 활용의 뜻을 지표 정의와 연결 | 정의·점수 의미·예시 순서 시각 확인 |
| 06 | 요약 파편문과 CAD 변동성의 추상적 설명 | 평균 차이·SD·p를 완전한 문장으로 표기 | 통계 JSON과 PDF 일치 |
| 07 | 세 기법이 무엇을 구분했다는지 모호 | 본 연구의 평가 항목과 유의한 요인 효과를 명시 | 주어·대상·통계 해석 검토 |
| 표 4개 | 수치 가운데 정렬 | 숫자 88셀 오른쪽, 코드 가운데, 설명 왼쪽, 머리글 가운데 | 전체 159셀 PPTX XML·SVG 독립 검사, 오류 주입 시험, PDF 확대 |

## C. 문체 감사

원고 538단위(일반 문장 단위 397개와 제목·목차·캡션 141개), 포스터 204개 표시 단위를 확인했다. 원고의 16개 변경 구간에서 이전 27단위를 새 24단위로 교정·통합했다. 포스터 문장 블록 4개를 수정했다. 상세 위치·A→B·분류·근거는 `PROFESSOR_PROSE_AB_20261016.md` 및 `POSITIVE_PROSE_CHANGES_20261016.json`에 기록한다.

대표 변경: “문서별 초기 질문 3개와 LLM 요약 대화 원본은 미보관 상태이며 …”를 “질의 구성의 최종 검증 자료는 한국어 질의 60개, 대상 문서, 원문 페이지 및 정답 근거로 구성된다.”로 교정했다. 보존 사실은 `DATA_AVAILABILITY_60Q.md`와 질의 구성 기록에서 정확하게 관리한다.

작성 이력·방어형 금지 패턴은 원고 검토 승인 목록과 별도로 검사한다. 금지 문장을 승인 목록에 추가한 변형도 검증 실패로 판정한다. 원자료 인용과 실험 질문은 원문으로 보존한다. 감소 사례와 선행연구의 관련성 레이블 조건 2단위는 측정·기술 사실로 검토했다. 문장 품질은 실제 읽기 검토와 자동 회귀 검사를 구분한다.

## D. 통계 및 구현 대조

60개 질의·8조건·480개 생성, RAGAS 1,920셀 중 1,915 유효값과 결측 5셀을 유지했다. 원정밀도 통계 JSON·XLSX 1,229셀·원고·HWPX·포스터의 값이 일치한다. 38개 요인 검정·10개 대응 비교, 실행 시간 후속 비교·Holm·효과크기·민감도 결과를 독립 재계산했다.

| 비교 | 평균 차이 | 검정·해석 |
|---|---:|---|
| HyDE 답변 관련성 | +0.080495 | t(59)=2.236, p=0.029, Holm p=0.117 |
| CAD 근거 충실도 | +0.028838 | t(57)=0.862, p=0.393, Holm p=1.000 |
| SCD H0 동일 문맥 | +0.218224 | 120쌍을 질의별 평균, n=60, Holm p<0.001 |
| SCD 전체 상태 일치 | +0.228941 | 240쌍을 질의별 평균, n=60, Holm p<0.001 |

품질 24개 요인 검정의 Holm p는 모두 0.05 이상이다. 한국어 문자 비율의 S 주효과와 시간의 H·C·C×S 효과는 보정 후 유의하다. 결측은 검정별 완전 대응 질의를 사용하며, 숫자 반복 답변의 기록값 0과 n=59 민감도 분석을 보존한다. 영문/국문초록의 수치·검정 단위·보정 여부가 같다.

구현 대조: `main_generation_executor.py:111~147`의 원질의 검색·재정렬·상위5·압축, `:209~268`의 번역·HyDE·생성 및 로짓 처리, `:336`의 시간 기록을 확인했다. `chunker.py`와 `context_compressor.py`의 split 기반 단어 수를 생성 토큰 수와 구분한다. 실험 설정은 512 생성 토큰·CAD α=0.5·SCD α=1.1/β=0.9/Tstart=5다. 기본 서비스 MAX_NEW_TOKENS와 실험 override를 구분한다. 생성·평가 API 호출은 추가하지 않았다. 원자료·통계 JSON·XLSX·실험/서비스 코드는 이 브랜치에서 변경하지 않았다.

## E. 산출물 검증

논문: 47쪽, 표 14개·그림 13개·편집 수식 11개·참고문헌 22편. 학교 양식의 명명 스타일·용지·단 정의를 보존한다. 목차 번호 적용 전후의 픽셀 차이는 5~8쪽뿐이다. 공개/개인 제출본은 표지 1~2쪽만 다르다. 실제 PDF에 수정된 16구간이 존재함을 공간순서 텍스트로 확인했다. 사례 그림 6개는 원본 픽셀과 같고 글자 9pt 이상, 부록 60행·360셀 및 반복 머리글 검사를 통과했다.

포스터: 594×841mm 1쪽·편집 표4개·204개 표시 단위·7016×9933 PNG. 전체 구성과 확대 표, 네이티브 렌더링을 대조했다. 패키지/재가져오기/레이아웃 검사 결과는 `PPTX_FINALIZATION_CHECKS.json`, 정렬·텍스트·크기 결과는 `ACADEMIC_POLISH_VALIDATION.json`에 기록한다.

### 최종 공개 파일: 실제 경로와 SHA-256

| 경로 | SHA-256 (현재 호스트 원본 바이트) |
|---|---|
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx` | `1dbdf4ab853198d0afa0555d55c5a7ee03c6ae85f1be881173918d02343d2fc5` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf` | `82f81cb7c994631cdb878907e8f331a996b5ad84ff29cea735a61cfc124cd837` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/M_RAG_A1_FINAL_EDITABLE.pptx` | `5a35fdd47be5a05401a590ca3b1391754be5aa419e8b8e94ebd4bb3a008062f8` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/M_RAG_A1_FINAL_EDITABLE.svg` | `26bd56d8cbc549d091749adce9290bd12046ebed621246922c92252b0112b8b6` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/M_RAG_A1_FINAL_PRINT.pdf` | `6814ec3469c0aead825444e2f9d363578f25af4ad64e9371d00a9c47ec7eec06` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/M_RAG_A1_FINAL_300DPI.png` | `b40330fdb9a595411241e6ce49b58c220ad2cfd18f13e1e03f4c4d44457c9d9d` |
| `C:/Users/KiKi/Desktop/CODE/M_RAG/FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/M_RAG_A1_FINAL_DELIVERY.zip` | `342b475e921fabeb6575492502ae7b67e142501e501bf744ba915d51e49b95fa` |

개인 제출본은 `C:/Users/KiKi/Downloads/M_RAG_FINAL_REVIEW_20261016/THESIS/`, 개인 포스터는 같은 폴더의 `POSTER/`다. 각각 로컬 SHA256_MANIFEST에 실제 파일 해시를 기록한다. 공개 Git에는 전체 학번과 개인 제출 파일을 포함하지 않는다.

### 실행한 검증

```powershell
python -X utf8 FINALDOCS/VALIDATION/verify_statistics_reproduction.py
python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
python -X utf8 FINALDOCS/BUILD/verify_print_pdf.py
.venv-hwpx/Scripts/python.exe -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'
python -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p 'test_*.py'
python -X utf8 FINALDOCS/POSTER/A1_FINAL_TITLE_CONFIRMED_20261010/rebuild_exports.py
python -X utf8 -m compileall -q -x node_modules FINALDOCS/BUILD FINALDOCS/VALIDATION
```

구조·통계·문장 회귀 검사와 실제 PDF 읽기/시각 확인은 별개다. PPTX는 네이티브 편집 객체·재가져오기·렌더링으로 확인했다. 사용자의 지시에 따라 PowerPoint 설치 프로그램 대신 PDF를 확인했다.

## F. 최종 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 연구 논리와 서론 | 통과 | RAG 정의·기법 역할·교차언어 문제·RQ와 비교 조건 연결 |
| 연구 방법 및 재현성 | 수정 완료 | 초기 구성 기록과 최종 검증 자료 분리, 자료 가용성 명시, 저장 통계 재현 |
| 통계적 정확성 | 통과 | 38 요인·10 대응 비교, 결측·Holm·효과크기·민감도 독립 일치 |
| 결과 해석 | 수정 완료 | 실제 평균·p·상호작용으로 서술, 비유의 품질 결과 보존 |
| 문체의 자연스러움 | 수정 완료 | 전체 읽기, 16구간 A→B, 금지 패턴 재유입 차단 |
| 표·그림의 학술적 완성도 | 수정 완료 | 교차참조·조사·정렬·출처·그림 픽셀 및 반복 머리글 확인 |
| 인쇄 가독성 | 추가 확인 필요 | 디지털 PDF 확대·300dpi 확인 완료, 실물 색상·재단·거리별 가독성은 현장 확인 |
| 제출 산출물 정합성 | 수정 완료 | 실제 웹 PDF·HWPX·PPTX·SVG·표·원자료 대조와 SHA 기록 |

추가 확인 항목은 실제 인쇄 환경과 타 환경의 글꼴 대체다. 미정 인준일·심사위원 성명은 학교 확정 후 입력한다. main 병합은 이 브랜치의 최종 검토에 남긴다.
