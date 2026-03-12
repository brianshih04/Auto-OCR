"""
後處理器工廠模組

提供後處理器實例的工廠方法。
"""

import logging
from pathlib import Path
from typing import Optional

from .base import BasePostProcessor
from .delete_processor import DeleteProcessor
from .move_processor import MoveProcessor

logger = logging.getLogger(__name__)


class PostProcessorFactory:
    """後處理器工廠"""
    
    @staticmethod
    def create(action: str, archive_folder: Optional[Path] = None) -> Optional[BasePostProcessor]:
        """
        建立後處理器實例
        
        Args:
            action: 後處理動作（"delete" 或 "move"）
            archive_folder: 備份資料夾路徑（用於移動處理器）
            
        Returns:
            BasePostProcessor: 後處理器實例，若動作不支援則返回 None
        """
        action = action.lower()
        
        if action == "delete":
            logger.debug("建立刪除處理器")
            return DeleteProcessor()
        elif action == "move":
            if not archive_folder:
                logger.warning("移動處理器需要指定備份資料夾")
                return None
            logger.debug(f"建立移動處理器，備份資料夾: {archive_folder}")
            return MoveProcessor(archive_folder=archive_folder)
        elif action == "none" or action == "":
            logger.debug("不執行後處理")
            return None
        else:
            logger.warning(f"不支援的後處理動作: {action}")
            return None
