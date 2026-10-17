# M-RAG 최종 제출 자료

현재 논문은 **국·영문초록과 주제어를 삭제한49쪽**, 표14개·그림13개·편집 수식11개·정식 학술문헌22편이다. 내용 확정 기준은 main `86a4a8d623201ee4bf925ae873513e8797b1dbd7`이며, 저장소 정리는 별도 PR에서 검증한다.

- [논문 PDF](DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf) · [편집 HWPX](DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx) · [원고](MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md)
- [A1 포스터 원본·인쇄본](POSTER/FINAL/README.md)
- [표14개 XLSX](TABLES/TABLES_60Q.xlsx) · [최종 통계](DATA/FACTORIAL_STATISTICS_60Q.json) · [60개 질의 근거](APPENDIX/QUERY_60_AUDIT.md)
- [최종 검사·정리 감사](VALIDATION/CURRENT_AUDIT.md) · [교수 피드백·A→B·예상 질문](VALIDATION/PROFESSOR_FEEDBACK.md)
- [학술·모델·실험자료 출처](VALIDATION/REFERENCES.md) · [질의 작성·자료 보관·주장 근거](VALIDATION/RESEARCH_PROVENANCE.md)
- [재생성 방법](BUILD/README.md) · [검사 책임과 실행](VALIDATION/README.md)

```powershell
python -m pip install -r FINALDOCS/BUILD/requirements.txt -r FINALDOCS/VALIDATION/requirements-statistics.txt
python -m FINALDOCS.VALIDATION.validate_all
```

검사 보고서·로그·렌더·내보내기 묶음은 기본적으로 `tmp/finaldocs/`에 생성한다. 원자료는 `experiments/data/`·`experiments/results/`에 보존한다. 이전 세대 자료는 복구 태그 `pre-finaldocs-cleanup-20261018`에서 찾는다. 현재 작업 트리에 HISTORY 복제본을 유지하지 않는다.

공개 논문에는 개인정보 입력 표시를 유지한다. 개인 제출본은 저장소 밖에서 관리하며 인준일·주심·부심·날인은 미정이다. 실물 인쇄·A1 발표거리·색상과 설치형 PowerPoint 열기·편집은 디지털 검사와 별도 확인 사항이다.
