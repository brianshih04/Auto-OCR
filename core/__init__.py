"""
核心模組

提供任務定義、任務佇列管理和任務處理功能。
"""

from .task import OCRTask, TaskStatus
from .task_queue import TaskQueue
from .task_worker import TaskWorker

__all__ = [
    "OCRTask",
    "TaskStatus",
    "TaskQueue",
    "TaskWorker",
]
