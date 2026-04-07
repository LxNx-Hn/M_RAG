"""
DEPRECATED: contrastive_decoder.py

GuideV2 기준으로 MODULE 13이 분리되었습니다:
  - MODULE 13A: cad_decoder.py  (파라메트릭 지식 개입 억제)
  - MODULE 13B: scd_decoder.py  (Language Drift 억제)

이 파일은 이전 import를 위한 호환성 shim입니다.
직접 사용하지 마세요 — cad_decoder 또는 scd_decoder를 import하세요.
"""
from modules.cad_decoder import CADDecoder as ContrastiveDecoder, create_cad_processor  # noqa: F401

__all__ = ["ContrastiveDecoder", "create_cad_processor"]
