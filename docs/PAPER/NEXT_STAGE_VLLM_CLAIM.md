# 다음 단계 연구 후보: vLLM 기반 생성 제어

## 현재 논문과의 관계

현재 논문은 `transformers + CAD/SCD` 경로를 기준으로 한다.
vLLM은 다음 단계 추론 최적화 연구의 중심 후보로 분리한다.

## 왜 별도 연구인가

CAD와 SCD는 현재 `LogitsProcessor`를 통해 직접 generation logits에 개입한다. vLLM은 고효율 배치 추론 엔진이므로 동일한 제어를 그대로 옮기려면 별도 설계와 검증이 필요하다.

## 기대 장점

- 동시 요청 처리 효율 개선
- GPU 메모리 사용 효율 개선
- 서비스 배포 시 추론 처리량 향상 가능

## 연구 질문 후보

- vLLM 환경에서 SCD와 유사한 언어 제어를 유지할 수 있는가
- vLLM 환경에서 CAD와 유사한 문서 근거 강화 제어를 재현할 수 있는가
- 처리량 증가와 생성 제어 품질 사이의 trade-off는 어느 정도인가

## 단계별 접근

1. plain generation vLLM 서버 연결
2. 기존 transformers 경로와 답변 품질/속도 비교
3. SCD 유사 제어 이식 가능성 검토
4. CAD 유사 제어 재설계
5. `transformers + CAD/SCD`와 `vLLM + 제어 경로` 비교

## 현재 문서에서 금지할 표현

- 현재 저장소가 vLLM을 지원한다는 표현
- vLLM 경로에서 CAD/SCD 효과가 이미 검증되었다는 표현
- 외부 API 또는 vLLM이 현재 논문 기본 경로라는 표현

## 연결 코드

- 현재 생성기 `backend/modules/generator.py`
- 현재 CAD `backend/modules/cad_decoder.py`
- 현재 SCD `backend/modules/scd_decoder.py`
- 현재 실험 실행 `backend/scripts/master_run.py`
