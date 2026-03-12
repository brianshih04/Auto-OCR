"""
OCR 引擎模組

提供雙軌 OCR 引擎系統：
- GLM-OCR Cloud API（雲端）
- llama.cpp GGUF 模型（本地）
"""

from .base import BaseOCREngine, OCRResult
from .factory import OCREngineFactory
from .glm_ocr import GLMOCREngine
from .llama_cpp_engine import LlamaCppEngine

__all__ = [
    "BaseOCREngine",
    "OCRResult",
    "OCREngineFactory",
    "GLMOCREngine",
    "LlamaCppEngine",
]
