"""
移動處理器模組

提供將檔案移動至備份資料夾的功能。
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from .base import BasePostProcessor, PostProcessResult

logger = logging.getLogger(__name__)


class MoveProcessor(BasePostProcessor):
    """移動處理器（搬移至備份資料夾）"""
    
    def __init__(self, archive_folder: Path):
        """
        初始化移動處理器
        
        Args:
            archive_folder: 備份資料夾路徑
        """
        self._archive_folder = Path(archive_folder)
    
    def process(self, file_path: Path) -> PostProcessResult:
        """
        將檔案移動至備份資料夾
        
        Args:
            file_path: 要移動的檔案路徑
            
        Returns:
            PostProcessResult: 處理結果
        """
        try:
            if not file_path.exists():
                error_msg = f"檔案不存在: {file_path}"
                logger.warning(error_msg)
                return PostProcessResult(success=False, error=error_msg)
            
            # 確保備份資料夾存在
            self._archive_folder.mkdir(parents=True, exist_ok=True)
            
            # 建立目標路徑（避免重名）
            dest_path = self._archive_folder / file_path.name
            
            if dest_path.exists():
                # 檔案名稱衝突，加入時間戳
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = file_path.stem
                suffix = file_path.suffix
                dest_path = self._archive_folder / f"{stem}_{timestamp}{suffix}"
                logger.debug(f"檔案名稱衝突，重新命名為: {dest_path.name}")
            
            # 移動檔案
            shutil.move(str(file_path), str(dest_path))
            logger.info(f"檔案已移動至: {dest_path}")
            
            return PostProcessResult(success=True)
            
        except Exception as e:
            error_msg = f"移動檔案失敗: {str(e)}"
            logger.error(error_msg)
            return PostProcessResult(success=False, error=error_msg)
