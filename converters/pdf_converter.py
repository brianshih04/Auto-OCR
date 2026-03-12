"""
Searchable PDF 轉換器模組

提供可搜尋 PDF 格式的 OCR 結果輸出功能。
"""

import logging
from pathlib import Path
from typing import Optional

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .base import BaseConverter, ConversionResult

logger = logging.getLogger(__name__)


class PDFConverter(BaseConverter):
    """Searchable PDF 轉換器"""
    
    def __init__(self, font_path: Optional[Path] = None):
        """
        初始化 PDF 轉換器
        
        Args:
            font_path: 中文字體路徑（可選）
        """
        self._font_path = font_path
        self._font_name = "ChineseFont"
        self._initialized = False
    
    def _initialize_font(self) -> bool:
        """
        初始化中文字體
        
        Returns:
            bool: 初始化是否成功
        """
        if self._initialized:
            return True
        
        try:
            if self._font_path and self._font_path.exists():
                suffix = self._font_path.suffix.lower()
                if suffix == ".ttc":
                    # TTC 檔案可能包含多個字體，ReportLab 需要特別處理
                    # 這裡簡化處理，僅嘗試註冊
                    pdfmetrics.registerFont(TTFont(self._font_name, str(self._font_path)))
                else:
                    pdfmetrics.registerFont(TTFont(self._font_name, str(self._font_path)))
                
                logger.info(f"已註冊字體: {self._font_path}")
                self._initialized = True
                return True
        except Exception as e:
            logger.warning(f"註冊字體失敗: {e}")
        
        # 使用預設字體
        self._font_name = "Helvetica"
        self._initialized = True
        logger.info("使用預設字體: Helvetica")
        return True
    
    def convert(self, image_path: Path, ocr_text: str, output_path: Path) -> ConversionResult:
        """
        將 OCR 結果轉換為 Searchable PDF 格式
        
        Args:
            image_path: 原始圖片路徑
            ocr_text: OCR 辨識文字
            output_path: 輸出檔案路徑
            
        Returns:
            ConversionResult: 轉換結果
        """
        try:
            # 初始化字體
            self._initialize_font()
            
            # 確保輸出目錄存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 獲取圖片尺寸
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                # 轉換為 RGB 模式（如果需要）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
            
            # 建立 PDF
            c = canvas.Canvas(str(output_path), pagesize=A4)
            page_width, page_height = A4
            
            # 計算圖片縮放比例（保持比例，留邊距）
            margin = 0.5 * 72  # 0.5 inch 邊距
            available_width = page_width - 2 * margin
            available_height = page_height - 2 * margin
            
            scale = min(available_width / img_width, available_height / img_height)
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # 計算置中位置
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            # 繪製圖片
            c.drawImage(
                str(image_path),
                x, y,
                scaled_width, scaled_height,
                preserveAspectRatio=True
            )
            
            # 在圖片上繪製透明文字層（用於搜尋）
            c.saveState()
            c.setFont(self._font_name, 1)  # 極小字體
            c.setFillColorRGB(1, 1, 1, alpha=0)  # 完全透明
            
            # 將 OCR 文字分散在頁面上（不可見但可搜尋）
            # 限制文字長度以避免 PDF 過大
            searchable_text = ocr_text[:5000] if len(ocr_text) > 5000 else ocr_text
            
            # 將文字放在頁面底部區域
            text_y = margin
            c.drawString(margin, text_y, searchable_text)
            
            c.restoreState()
            c.save()
            
            logger.info(f"Searchable PDF 已生成: {output_path}")
            return ConversionResult(success=True, output_path=output_path)
            
        except Exception as e:
            error_msg = f"生成 PDF 失敗: {str(e)}"
            logger.error(error_msg)
            return ConversionResult(success=False, error=error_msg)
