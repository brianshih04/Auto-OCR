"""
OCR 引擎抽象基底類別模組

定義所有 OCR 引擎必須實作的介面。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OCRResult:
    """OCR 辨識結果"""
    text: str
    confidence: float = 1.0
    processing_time: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """檢查辨識是否成功"""
        return self.error is None and bool(self.text)


class BaseOCREngine(ABC):
    """OCR 引擎抽象基底類別"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化引擎（載入模型、驗證 API 等）
        
        Returns:
            bool: 初始化是否成功
        """
        ...
    
    @abstractmethod
    def recognize(self, image_path: Path) -> OCRResult:
        """
        執行 OCR 辨識
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            OCRResult: 辨識結果
        """
        ...
    
    @abstractmethod
    def is_ready(self) -> bool:
        """
        檢查引擎是否就緒
        
        Returns:
            bool: 引擎是否就緒
        """
        ...
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理資源"""
        ...
    
    @property
    @abstractmethod
    def engine_name(self) -> str:
        """
        取得引擎名稱
        
        Returns:
            str: 引擎名稱
        """
        ...
