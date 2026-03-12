"""
任務定義模組

定義 OCR 處理任務的資料結構。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class TaskStatus(Enum):
    """任務狀態列舉"""
    
    PENDING = "pending"  # 等待處理
    PROCESSING = "processing"  # 處理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗


@dataclass
class OCRTask:
    """
    OCR 處理任務
    
    儲存單個 OCR 處理任務的所有相關資訊。
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    input_path: Optional[Path] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_path: Optional[Path] = None
    
    def __post_init__(self):
        """
        初始化後處理
        
        確保 input_path 和 result_path 是 Path 物件。
        """
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.result_path, str):
            self.result_path = Path(self.result_path)
    
    def start(self) -> None:
        """將任務標記為處理中"""
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.now()
    
    def complete(self, result_path: Optional[Path] = None) -> None:
        """
        將任務標記為已完成
        
        Args:
            result_path: 處理結果的路徑
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        if result_path:
            if isinstance(result_path, str):
                result_path = Path(result_path)
            self.result_path = result_path
    
    def fail(self, error_message: str) -> None:
        """
        將任務標記為失敗
        
        Args:
            error_message: 錯誤訊息
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    @property
    def duration(self) -> Optional[float]:
        """
        計算任務處理時間
        
        Returns:
            處理時間（秒），如果任務尚未完成則返回 None
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def input_filename(self) -> Optional[str]:
        """取得輸入檔案名稱"""
        if self.input_path:
            return self.input_path.name
        return None
    
    def to_dict(self) -> dict:
        """
        將任務轉換為字典
        
        Returns:
            任務的字典表示
        """
        return {
            "id": self.id,
            "input_path": str(self.input_path) if self.input_path else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "result_path": str(self.result_path) if self.result_path else None,
            "duration": self.duration,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OCRTask":
        """
        從字典建立任務
        
        Args:
            data: 任務的字典表示
            
        Returns:
            OCRTask 實例
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            input_path=Path(data["input_path"]) if data.get("input_path") else None,
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message"),
            result_path=Path(data["result_path"]) if data.get("result_path") else None,
        )
