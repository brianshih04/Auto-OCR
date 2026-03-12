"""
刪除處理器模組

提供將檔案移至資源回收桶的功能。
"""

import logging
from pathlib import Path

from .base import BasePostProcessor, PostProcessResult

logger = logging.getLogger(__name__)


class DeleteProcessor(BasePostProcessor):
    """刪除處理器（移至資源回收桶）"""
    
    def process(self, file_path: Path) -> PostProcessResult:
        """
        將檔案移至資源回收桶
        
        Args:
            file_path: 要刪除的檔案路徑
            
        Returns:
            PostProcessResult: 處理結果
        """
        try:
            if not file_path.exists():
                error_msg = f"檔案不存在: {file_path}"
                logger.warning(error_msg)
                return PostProcessResult(success=False, error=error_msg)
            
            # 嘗試移至資源回收桶
            try:
                import send2trash
                send2trash.send2trash(str(file_path))
                logger.info(f"檔案已移至資源回收桶: {file_path}")
            except ImportError:
                # send2trash 未安裝，永久刪除
                logger.warning("send2trash 未安裝，將永久刪除檔案")
                if file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                logger.info(f"檔案已永久刪除: {file_path}")
            except Exception as e:
                # send2trash 失敗，嘗試永久刪除
                logger.warning(f"移至資源回收桶失敗: {e}，將永久刪除檔案")
                if file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                logger.info(f"檔案已永久刪除: {file_path}")
            
            return PostProcessResult(success=True)
            
        except Exception as e:
            error_msg = f"刪除檔案失敗: {str(e)}"
            logger.error(error_msg)
            return PostProcessResult(success=False, error=error_msg)
