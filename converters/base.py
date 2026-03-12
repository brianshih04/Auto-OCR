"""
轉換器基底模組

提供輸出轉換器的抽象基底類別。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ConversionResult:
    """轉換結果"""
    success: bool
    output_path: Optional[Path] = None
    error: Optional[str] = None


class BaseConverter(ABC):
    """輸出轉換器抽象基底類別"""
    
    @abstractmethod
    def convert(self, image_path: Path, ocr_text: str, output_path: Path) -> ConversionResult:
        """
        將 OCR 結果轉換為輸出格式
        
        Args:
            image_path: 原始圖片路徑
            ocr_text: OCR 辨識文字
            output_path: 輸出檔案路徑
            
        Returns:
            ConversionResult: 轉換結果
        """
        ...
