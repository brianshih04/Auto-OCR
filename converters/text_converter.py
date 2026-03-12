"""
純文字轉換器模組

提供純文字格式的 OCR 結果輸出功能。
"""

import logging
from datetime import datetime
from pathlib import Path

from .base import BaseConverter, ConversionResult

logger = logging.getLogger(__name__)


class TextConverter(BaseConverter):
    """純文字轉換器"""
    
    def convert(self, image_path: Path, ocr_text: str, output_path: Path) -> ConversionResult:
        """
        將 OCR 結果轉換為純文字格式
        
        Args:
            image_path: 原始圖片路徑
            ocr_text: OCR 辨識文字
            output_path: 輸出檔案路徑
            
        Returns:
            ConversionResult: 轉換結果
        """
        try:
            # 確保輸出目錄存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 建立輸出內容
            content = f"# OCR Result: {image_path.name}\n"
            content += f"# Source: {image_path}\n"
            content += f"# Generated: {datetime.now().isoformat()}\n"
            content += "#" + "=" * 40 + "\n\n"
            content += ocr_text
            
            # 寫入文字檔（UTF-8 編碼）
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"文字檔已生成: {output_path}")
            return ConversionResult(success=True, output_path=output_path)
            
        except Exception as e:
            error_msg = f"生成文字檔失敗: {str(e)}"
            logger.error(error_msg)
            return ConversionResult(success=False, error=error_msg)
