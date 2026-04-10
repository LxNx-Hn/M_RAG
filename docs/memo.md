### MIDM 중요이슈

RAG 시스템에서 검색 결과 문서가 LLM 입력으로 함께 주어질 때, 답변 생성에 참조한 정확한 문서나 문서의 부분을 표기하고 싶다는 의미로 이해하였습니다.
현재 공개된 Mi:dm Base 모델은 모델 내에 이를 위한 지도학습이 수행되지 않아 이 기능(Citation)이 다소 제한적일 것으로 생각됩니다.
검색을 통해 얻을 수 있는 문서의 형식과 길이, LLM 입력 시 Context 구성 등을 고려한 데이터를 구성한 후,
추가 학습을 수행 하여야 지정한 형식과 높은 정확도로 출처 표기가 가능합니다.\
 - MIDM 사용시 고려하기
  
> **답변**: MIDM SFT 없이 우회 가능한 방법 채택. 검색 청크에 `[출처1]`, `[출처2]` 인덱스를 붙여 프롬프트에 전달하고, 답변 후처리로 매핑. 완벽하지 않지만 SFT 없이 현실적으로 가능한 최선. 배포 전 출처 표기 데이터셋 구성 후 SFT 고려 필요.

### 오케스트레이션
- Kubernetis 사용, Be,Fe,Lm,Db Layer 각각 Compose 후 관리시스템 생각중

> **답변**: 구조적으로 맞는 방향. BE(FastAPI) / FE(Nginx+React) / LM(vLLM) / DB(PostgreSQL+ChromaDB) 4레이어로 분리. 각 레이어를 별도 Deployment로 관리하고 HPA로 LM 레이어만 스케일아웃 가능. CLAUDE.md 배포 계획 섹션에 이미 반영됨.

Q- 진행할려면 바꿔야하는 문서/ 코드가 존재하는지?

> **답변**: 코드 변경 필요한 파일 목록:
> - `backend/generator.py` — HuggingFace pipeline → vLLM OpenAI-compatible client로 교체
> - `backend/config.py` — `LLM_ENDPOINT_URL`, `USE_VLLM` 환경변수 기반 분리
> - `backend/app.py` — FastAPI 엔드포인트 정리 (BE/FE 분리 필요)
> - 신규 작성 필요: `docker-compose.yml` × 4 (BE/FE/LM/DB), Kubernetes Deployment/Service/HPA manifest, Nginx 설정, `docs/DEPLOY.md`
> - CLAUDE.md에 배포 계획 섹션은 이미 반영되어 있어 별도 수정 불필요

### VLLM
- 동시서빙을 위한 최적화 기술 연구필요
- 런팟 / 프렌들리 AI 비교필요

> **답변 - vLLM이 뭐야?**: vLLM은 LLM 추론 전용 고성능 서빙 프레임워크. HuggingFace transformers로 직접 서빙하면 요청 1개씩 처리하지만, vLLM은 "PagedAttention + Continuous Batching"으로 여러 요청을 GPU에서 동시에 처리해 처리량(throughput)이 수십 배 향상됨. OpenAI API 호환 인터페이스를 제공해서 `generator.py`의 HuggingFace 코드를 vLLM API 클라이언트로 교체하면 됨.
>
> **RunPod vs 프렌들리AI**: RunPod이 UI/UX 좋고 한국에서 접근성 좋음. 가격은 Vast.ai(프렌들리 AI 계열) 쪽이 저렴할 수 있으나 안정성 차이 있음. MIDM-2.0(11.5B, bfloat16)은 A100 80GB 1장에서 vLLM 서빙 가능. 졸업작품 수준이면 RunPod 단기 인스턴스(시간제 과금)로 충분.
>
> **파이프라인에 포함되나요?**: vLLM은 배포 인프라 레이어. 파이프라인 로직에 들어가는 게 아니라 `generator.py`가 vLLM의 OpenAI-compatible API를 호출하도록 교체하면 됨. `GenerationConfig` 파라미터들(temperature, top_p 등)은 그대로 사용 가능. 지금 당장 구현할 필요 없고 RunPod 서버 띄울 때 전환.

-Q : 코드수정소요가 있는지? vLLM으로 수정시에 기본LLM에 비해 단점은 없는지와, 선택실행이 가능한지?

> **답변 - 코드 수정 소요**: `generator.py` 약 20줄 수정. HuggingFace `pipeline()` 호출을 `openai.OpenAI(base_url="http://vllm-server:8000/v1")` 클라이언트로 교체. `GenerationConfig`의 temperature, top_p 등 파라미터는 그대로 호환됨.
>
> **답변 - vLLM 단점**: ① vLLM 서버를 별도로 실행해야 함(로컬 GPU 직접 사용 불가) ② cold start 있음(서버 뜨는 데 수십 초) ③ CAD(Contrastive Decoding)처럼 커스텀 LogitsProcessor를 쓰는 기능은 vLLM에서 지원 제한적 — CAD 우회 방법 별도 검토 필요.
>
> **답변 - 선택 실행**: `config.py`에 `USE_VLLM = False` 플래그 추가, `generator.py`에서 분기 처리하면 로컬 HuggingFace / vLLM 서버 중 선택 가능. 개발 환경은 HuggingFace, 배포 환경은 vLLM으로 분리 운용 가능.

### 기능
 - 참고논문도 뷰어에서 보고, 다운로드 받거나 가져올수있는 방법이 있는지 궁금함 (이거 다운로드 모듈 추가해서, 다운로드 요청 들어왔을때, 참고문헌 가져오고, 사용자가 다운로드 받을수있게 하는거도 괜찮을거같음)

> **답변**: Pipeline D(인용 추적)가 이미 arXiv 자동 다운로드를 하고 있음 (`citation_tracker.py`). arXiv 논문은 무료 공개라 다운로드 제공 가능. `/api/citations/download` 엔드포인트 추가 + 프론트엔드 다운로드 버튼이면 구현 가능. 현재는 미구현 상태로 유지.
  
 - 뷰어의 UX가 상당히 중요함, 일반적인  PDF뷰어를 대체할수있는 기능이 있었음 좋겠음 (형광펜같은 필기기능..?)
    -  현재는 청킹이 논문기준으로 수행되는데, 일반문서에도 수행될수있을지 궁금함

> **답변 - 형광펜**: PDF.js 기반 뷰어에서 출처 하이라이트는 구현됨. 사용자 직접 필기는 PDF annotation API(pdf-lib 등)가 필요하고 난이도 높음. 우선순위 낮게 보는 게 맞음.
>
> **답변 - 일반문서 청킹**: 섹션 인식기(M2)가 논문 헤더 패턴을 감지 못하면 자동으로 `fixed` 청킹 전략 fallback. 기술적으로 이미 동작함. 단, 섹션별 필터 검색(B경로)은 논문 전용이라 일반문서에서는 A경로(단순QA)로 라우팅됨.

- 노트북  LM처럼 다이어그램화, PPT제작은 비용이 얼마나 추가로 드는지?
- 노트북  LM <- 요약에 차별화되어있음, 우리 서비스 <- PDF확인 및 추가정보 제공에 초점
  - 일반적인 자료와 달리 논문은, 레퍼런스가 중요하기때문

> **답변 - 다이어그램/PPT 비용**: 로컬 MIDM으로 하면 API 비용 없음. `python-pptx`(PPT) + Mermaid/D2(다이어그램) 라이브러리 추가 비용만. LLM 호출 1회 추가(구조화 텍스트 → 슬라이드 내용 생성) + 후처리. E경로(요약)에 파이프라인 단계로 붙이면 됨. 현재는 미구현 상태 유지.
>
> **답변 - 서비스 차별화**: 정확한 포지셔닝. NotebookLM = 일반 문서 요약 중심. 우리 = 논문 도메인 특화 (레퍼런스 추적, 섹션별 정밀 검색, 한/영 갭 연구). 졸업작품 contribution(C1~C3)과 일치.

- 사용자가 제공한 논문 자료를 꼭 서버에서 저장해야할까 싶음, 로컬에 저장하게 하면 안되나? <- 근데 이러면 서버에 DB가 필요한가싶음? 로그인..?

> **답변**: 서버 저장 필요. 이유: 인덱싱 결과(ChromaDB 벡터)가 서버에 있고, 여러 세션에서 같은 논문을 재사용하려면 서버 경로 필요. 로그인/대화 기록도 서버 DB 필요. 다만 인덱싱 완료 후 원본 PDF는 삭제 옵션 가능(`backend/data/` 정리). 1인 사용 데모라면 SQLite로 단순화 가능.

- 지금 SQL ALchemi 기반인데, PostGre랑 비교해서 무슨 장단점이있는지 궁금해

> **답변**: 비교 대상이 다름. SQLAlchemy는 **ORM 라이브러리**(Python에서 DB 테이블을 객체로 다루는 도구), PostgreSQL은 **DB 엔진**. 현재 코드는 `SQLAlchemy ORM + PostgreSQL`을 함께 씀. 만약 SQLite로 바꾸고 싶다면 `DATABASE_URL`만 `sqlite:///./mrag.db`로 바꾸면 SQLAlchemy가 알아서 처리. 다중 사용자 동시접속 없는 데모라면 SQLite가 훨씬 간단(별도 DB 서버 불필요).


### 도메인포함 배포 필요

> **답변**: 배포 순서 제안 — ① Docker Compose 로컬 검증 → ② RunPod A100 인스턴스 띄우고 vLLM 서빙 테스트 → ③ 도메인 연결(Nginx + Let's Encrypt) + HTTPS. `docs/DEPLOY.md`에 가이드 있음. 도메인은 가비아/Cloudflare에서 구매 후 RunPod Public IP에 A레코드 연결.

---

### 배포 흐름 요약 (A: 로컬 테스트 / B: 실제 배포)

#### A. 로컬에서 돌려보기 (GPU 없어도 검색까지는 됨)

1. Python 가상환경 만들고 `pip install -r backend/requirements.txt` 실행
2. Node.js 설치 후 `frontend/` 폴더에서 `npm install` 실행
3. 터미널 두 개 열어서 — 하나는 백엔드(`uvicorn api.main:app --port 8000`), 하나는 프론트(`npm run dev`)
4. 브라우저에서 `http://localhost:5173` 접속
5. GPU 없으면 LLM 생성 불가 → 검색 결과만 반환됨 (정상)

#### B. RunPod에 실제 배포하기

##### B-1. 서버 빌리기

1. runpod.io 가입 → 크레딧 충전
2. GPU Pods → Deploy → GPU: `A100 80GB` 선택 (MIDM 11.5B가 ~23GB 필요)
3. Template: `RunPod PyTorch 2.1` 선택, Storage 50GB 이상 설정
4. 포드 생성 → 대시보드에서 SSH 접속 정보 확인

##### B-2. 코드 올리기

1. SSH로 서버 접속
2. GitHub에서 `git clone`으로 코드 가져오기
3. `pip install -r backend/requirements.txt` 실행
4. `python backend/scripts/download_models.py` 실행 (MIDM 다운로드, 시간 오래 걸림)

##### B-3. 서버 실행

1. `LOAD_GPU_MODELS=true uvicorn api.main:app --host 0.0.0.0 --port 8000` 실행
2. RunPod 대시보드 → Connect → HTTP 8000 포트 열기
3. 브라우저에서 `http://<pod-ip>:8000/docs` 접속해서 API 확인

##### B-4. 도메인 연결하고 싶다면 (선택)

1. 가비아/Cloudflare에서 도메인 구매
2. DNS A레코드를 RunPod 서버 IP로 설정
3. Nginx 띄워서 80/443 → 8000 리버스 프록시 설정
4. Let's Encrypt로 HTTPS 인증서 발급 (`certbot`)

> **비용 팁**: RunPod는 시간제 과금. 발표할 때만 켜고 평소엔 꺼두면 됨. 포드 Stop하면 디스크 비용(약 $0.1/일)만 나감. 모델 다운로드는 Volume에 저장해두면 재시작해도 다시 안 받아도 됨.

### 논문도메인 지적발생
일부 아카이브에서 열람이 불가능한 논문이나, 실제 퍼블리싱/ 아카이브가 다른 논문도 있을건데 그건 어케할거냐.
-> 차라리 학습도우미쪽으로 가보는건 어떠냐. 교재 PDF를 넣으면 알려주고, 문제 만드는 모듈을 추가하는거지, 청킹변형해서, 여러문서 커버되도록.
혹시 이러면 바뀌거나, 변형될 로직이 있는지 궁금함. <- 이러면 유사논문 검색이 아니라, 관련자료 웹검색? 이런걸 해야하나?
-> 섹션감지가 실패하면 단순 QA로 돌아가는데, 방향성이 헷갈림
- 논문마다도 글자크기, 위치가 다를건데 그것도 해석 가능한가?
-전체 모듈, 프로젝트에서, 논문특화를 맞추는 부분이 어디있는지랑, 그걸빼도 유효연구인지 파악필요

> **답변 - 학습도우미 전환 시 변경 범위**: 크게 바뀌는 로직은 없음. M2(section_detector)에 교재 목차 패턴(예: "1장", "Chapter") 추가, ROUTE_MAP에 "문제", "퀴즈", "연습" 키워드 추가, 문제 생성용 Pipeline F 신규 추가 정도. Pipeline D(인용추적/arXiv)는 비활성화. 나머지 M1~M10은 그대로 재사용 가능.
>
> **답변 - 웹검색 필요 여부**: 현재 시스템은 업로드된 PDF 내에서만 검색. "관련 자료 웹검색"은 별도 모듈 필요(SerpAPI, Tavily 등). 학습도우미 포지션이라면 업로드 교재 중심으로 가고, 웹검색은 선택 기능으로 추후 추가하는 게 범위 관리에 유리함.
>
> **답변 - 섹션감지 실패 방향성**: 의도된 설계. 논문/교재 구조 인식 성공 → B경로(섹션필터) 활용. 실패 → A경로(단순QA) fallback. 일반 교재는 섹션 인식 실패율이 높아 A경로 위주로 동작하게 되는데, 이게 오히려 범용 문서에는 더 안정적임.
>
> **답변 - 논문마다 레이아웃 차이**: M1(PDFParser)의 pymupdf가 블록 단위로 텍스트 추출하고, M2가 폰트 크기 기준으로 헤더 판별하기 때문에 2단 레이아웃, 글자 크기 차이, 위치 다른 경우도 어느 정도 커버됨. 단, 스캔 PDF(이미지 기반)는 OCR 없이 파싱 불가 — 이건 pymupdf 한계.
>
> **답변 - 논문특화 부분 목록 및 제거 시 유효성**:
> 논문특화 코드: `section_detector.py`(논문 헤더 패턴), `pipeline_b_section.py`(섹션필터), `pipeline_d_citation.py`(arXiv), `citation_tracker.py`, `query_expander.py`의 학술 HyDE 프롬프트, ROUTE_MAP의 비교/인용 키워드.
> 이 부분을 빼면 일반 Modular RAG가 됨 — contribution이 크게 약해짐. 논문특화(레퍼런스 추적 C2, 섹션 인식 C1)가 이 프로젝트의 핵심 차별점이므로 유지 권장.
>
>Q2 - 아카이브에 없는논문과 다른논문에 대한 답변 아직 안달려있고, 이 프로젝트의 핵심은 특화된청킹과 환각제거이지, 논문에 고정할필요가 있나싶음

-CAD<- 이거 한국어에서 적용후 평가한 논문있나? 없음 이걸로 가고싶은데

> **답변**: CAD 원논문(Shi et al., 2023)은 영어 중심이고, 한국어 RAG에 CAD를 적용·평가한 논문은 현재(2026년 기준) 공개된 것이 없거나 매우 드묾. 이게 contribution이 될 수 있음. "한국어 학술 RAG에서 CAD의 환각 억제 효과 실증" 자체가 새로운 실험적 기여. RAGAS 평가(`backend/evaluation/ragas_eval.py`)에 CAD on/off 비교 항목 추가하면 논문 contribution(C3)으로 직접 연결됨. 가져가도 좋은 방향.


-통번역, 전체요약도 가능한지?

> **답변 - 통번역**: `query_expander.py`에 한→영 번역 기능이 이미 구현되어 있음(M7). 전체 문서 번역은 별도 파이프라인 필요하지만 LLM 호출 비용이 크고 졸업작품 범위를 벗어남. 현실적으로는 "이 논문의 Abstract를 번역해줘" 같은 섹션 단위 요청을 A경로에서 처리하는 수준이 적합.
>
> **답변 - 전체요약**: Pipeline E(`pipeline_e_summary.py`)가 섹션별 5회 검색 후 구조화 요약을 이미 수행함. "요약", "summarize" 키워드 쿼리 시 자동 라우팅됨.

-해당프로젝트에 속도이슈는 없는지?

> **답변**: 속도 병목 지점 3곳:
>
> 1. **인덱싱**: BGE-M3 임베딩이 CPU에서 매우 느림(논문 1편 수 분). GPU 있으면 수십 초로 단축.
> 2. **추론(생성)**: MIDM-2.0 11.5B bfloat16이 GPU 없으면 사실상 동작 안 함. GPU 24GB 있어도 첫 토큰까지 수 초 소요.
> 3. **HyDE + Reranker**: 쿼리당 LLM 추론 1회(HyDE) + cross-encoder 재랭킹 추가. A경로 기준 전체 응답 시간 10~30초 예상(GPU 환경).
>
> vLLM 전환 시 throughput은 크게 향상되지만 latency(첫 응답 시간) 자체는 크게 줄지 않음. 데모/졸업작품 수준에서는 허용 가능한 범위.


-ios, 안드로이드로도 출시하고싶고, 출시정도의 예산파악필요함

> **답변**: 앱 출시 기준 예산 항목:
>
> - **앱스토어 등록비**: Apple $99/년, Google $25 일회
> - **서버 비용**: RunPod A100 80GB 약 $2~3/시간(시간제). 상시 서빙 시 월 $1,500~2,000 수준 — 졸업작품이면 발표 때만 켜는 방식으로 비용 최소화.
> - **개발 비용**: React Native 또는 Flutter로 1인 개발 시 2~3개월. FastAPI 백엔드 분리 + 프론트엔드 재작성 필요.
> - **현실적 대안**: PWA(Progressive Web App)로 모바일 대응. 별도 앱 없이 브라우저에서 앱처럼 동작. 스토어 등록 불필요, 추가 개발 최소화. 졸업작품 수준이면 PWA로 충분.
- 모델이 마크다운으로 답변하면 표시되는지 궁금함

> **답변**: React 등 프론트엔드에서 `react-markdown` 라이브러리로 마크다운 렌더링 가능. **굵게**, 표, 코드블록 전부 지원됨. MIDM 모델이 마크다운 형식으로 답변하도록 `generator.py`의 시스템 프롬프트에 "답변은 마크다운 형식으로 작성하세요" 한 줄 추가로 해결.

- 모듈러 RAG에 대한 설명이 빈약한거같음, 이게 그냥 RAG파이프라인인지 모듈러 AI인지 모르겠음

> **답변**: 구분 기준은 "파이프라인이 고정되어 있냐, 쿼리에 따라 동적으로 바뀌냐".
>
> - **일반 RAG**: 모든 쿼리가 동일한 Retrieve → Generate 파이프라인을 통과. 모듈 조합이 고정.
> - **Modular RAG** (이 프로젝트): `QueryRouter(M6)`가 쿼리 유형을 분류해서 5개 파이프라인(A~E) 중 하나로 분기. 각 파이프라인은 서로 다른 모듈 조합을 사용. "단순 질문"은 HyDE+하이브리드검색, "비교 질문"은 병렬 검색+비교 템플릿, "요약"은 섹션별 반복 검색 등.
>
> 즉, 이 프로젝트는 **쿼리 적응형 파이프라인 분기**가 핵심이라 Modular RAG가 맞음. "Modular AI"(에이전트가 도구를 자율 선택)와는 다름 — 라우팅 로직이 규칙 기반(키워드 스코어)으로 명시적으로 설계되어 있기 때문. 논문에서 인용할 때는 Gao et al. (2023) "Modular RAG" 또는 Ma et al. (2023) "Query Routing" 계열 레퍼런스 활용 가능.



PHASE 0: T0f~T0i+T0r — 문서 업데이트 (4개 docs + CLAUDE.md + ARCHITECTURE.md)

PHASE 0: T0j+T0q — test_queries.json lecture 8개 + patent 6개 추가

PHASE 1: T1 — CRITIQUE markdown lint 수정

PHASE 2: T2+T3 — ground_truth 전략 + None-aware 평가

PHASE 3: T4+T5+T6 — citation_tracker fallback + citations API 분리

PHASE 4: T7~T11 — Pipeline F 퀴즈 생성

PHASE 5: T12~T14 — 프론트엔드 인용 뷰어 패널

PHASE 6: T15+T16 — C3 실험 스크립트 + 배포 검증

PHASE 6: T17 — docker-compose 검증