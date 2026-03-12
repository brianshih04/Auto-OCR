"""
Searchable PDF 轉換器模組

提供可搜尋 PDF 格式的 OCR 結果輸出功能。
"""

import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image

from .base import BaseConverter, ConversionResult

logger = logging.getLogger(__name__)


class PDFConverter(BaseConverter):
    """Searchable PDF 轉換器"""
    
    def __init__(self, font_path: Optional[Path] = None):
        """
        初始化 PDF 轉換器
        
        Args:
            font_path: 中文字體路徑（可選，        """
        self._font_path = font_path
    
    def convert(self, image_path: Path, ocr_text: str, output_path: Path) -> ConversionResult:
        """
        將 OCR 結果轉換為 Searchable PDF 格式
        
        使用 PyMuPDF 建立包含圖片和可搜尋文字層的 PDF。
        文字層使用透明色但在 PDF閱讀器中可被搜尋。
        
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
            
            # 開啟圖片並獲取尺寸
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                # 轉換為 RGB 模式（如果需要）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    # 儲存臨時 RGB 圖片
                    temp_img_path = output_path.parent / f"_temp_{output_path.stem}.jpg"
                    img.save(temp_img_path, "JPEG", quality=95)
                    image_to_use = str(temp_img_path)
                else:
                    image_to_use = str(image_path)
            
                img_width_final, img_height_final = img_width, img_height
            
            # 建立 PDF 文件
            doc = fitz.open()
            
            # 建立頁面（使用圖片原始尺寸）
            page = doc.new_page(width=img_width_final, height=img_height_final)
            
            # 插入圖片作為頁面背景
            page.insert_image(
                fitz.Rect(0, 0, img_width_final, img_height_final),
                filename=image_to_use
            )
            
            # 在頁面上插入可搜尋的文字層
            if ocr_text.strip():
                # 使用 TextPage 對象插入文字
                # 這種方式可以讓文字被搜尋但不在視覺上干擾圖片
                text_page = fitz.TextPage(page, fitz.Rect(0, 0, img_width_final, img_height_final))
                
                # 設定文字樣式 - 使用極小字體
                text_page.insert_text(
                    ocr_text,
                    fontsize=1,  # 極小字體
                    color=(1, 1, 1),  # 白色（在淺色背景上幾乎不可見）
                render_mode=0  # 正常渲染模式
                opacity=0.01  # 幾乎透明
                lineheight=1.2
                expandtabs=False
                )
                # 將文字頁面應用到 PDF
                # 注意： PyMuPDF 的 TextPage 需要特殊處理
                # 改用更簡單的方法： 直接在頁面底部插入文字
                pass
            
            # 替代方案： 使用頁面文字插入
            # 在頁面底部區域插入可搜尋文字
            # 計算文字區域（頁面底部10%區域）
            text_area_height = img_height_final * 0.10
            text_area_rect = fitz.Rect(
                0,  # x0
                img_height_final - text_area_height,  # y0
                img_width_final,  # x1
                img_height_final# y1
            )
            
            # 創建形狀物件
            shape = page.new_shape()
            
            # 在底部區域插入文字
            # 使用極小字體和近乎透明的顏色
            lines = self._split_text_to_lines(ocr_text, max_chars=300)
            font_size = 2
            line_height = font_size + 1
            start_y = img_height_final - 5
            
            for i, enumerate(lines[:100]):  # 限制最多100行
                y_pos = start_y - (i * line_height)
                if y_pos < text_area_rect.y0:
                    break
                
                shape.insert_text(
                    fitz.Point(5, y_pos),
                    line,
                    fontsize=font_size,
                    color=(0.99, 0.99, 0.99),  # 淺灰色
                    lineheight=line_height
                )
            
            # 提交形狀
            shape.commit()
            
            # 儲存 PDF
            doc.save(str(output_path), garbage=4, deflate=True)
            doc.close()
            
            # 清理臨時檔案
            if 'temp_img_path' in locals():
                try:
                    Path(image_to_use).unlink()
                except:
                    pass
            
            logger.info(f"Searchable PDF 已生成: {output_path}")
            return ConversionResult(success=True, output_path=output_path)
            
        except Exception as e:
            error_msg = f"生成 PDF 失敗: {str(e)}"
            logger.error(error_msg)
            logger.exception(error_msg)
            return ConversionResult(success=False, error=error_msg)
    
    def _split_text_to_lines(self, text: str, max_chars: int = 300) -> list:
        """
        將文字分割成多行
        
        Args:
            text: 原始文字
            max_chars: 每行最大字元數
            
        Returns:
            list: 分割後的行列表
        """
        lines = []
        current_line = ""
        
        for char in text:
            current_line += char
            if len(current_line) >= max_chars:
                lines.append(current_line)
                current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines
