"""
後處理器基底模組

提供後處理器的抽象基底類別。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PostProcessResult:
    """後處理結果"""
    success: bool
    error: Optional[str] = None


class BasePostProcessor(ABC):
    """後處理器抽象基底類別"""
    
    @abstractmethod
    def process(self, file_path: Path) -> PostProcessResult:
        """
        執行後處理
        
        Args:
            file_path: 要處理的檔案路徑
            
        Returns:
            PostProcessResult: 處理結果
        """
        ...
