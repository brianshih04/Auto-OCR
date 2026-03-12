"""
轉換器工廠模組

提供轉換器實例的工廠方法。
"""

import logging
from pathlib import Path
from typing import Optional

from .base import BaseConverter
from .text_converter import TextConverter
from .pdf_converter import PDFConverter

logger = logging.getLogger(__name__)


class ConverterFactory:
    """轉換器工廠"""
    
    @staticmethod
    def create(format_type: str, font_path: Optional[Path] = None) -> Optional[BaseConverter]:
        """
        建立轉換器實例
        
        Args:
            format_type: 輸出格式類型（"txt" 或 "pdf"）
            font_path: 字體路徑（用於 PDF 轉換器）
            
        Returns:
            BaseConverter: 轉換器實例，若格式不支援則返回 None
        """
        format_type = format_type.lower()
        
        if format_type == "txt" or format_type == "text":
            logger.debug("建立純文字轉換器")
            return TextConverter()
        elif format_type == "pdf":
            logger.debug(f"建立 PDF 轉換器，字體路徑: {font_path}")
            return PDFConverter(font_path=font_path)
        else:
            logger.warning(f"不支援的輸出格式: {format_type}")
            return None
