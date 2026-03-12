"""
任務佇列模組

提供執行緒安全的任務佇列管理功能。
"""

import logging
from queue import Queue
from threading import Lock
from typing import Dict, List, Optional

from .task import OCRTask, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    執行緒安全的任務佇列
    
    管理待處理的 OCR 任務，提供任務的添加、獲取和狀態更新功能。
    """
    
    def __init__(self):
        """初始化任務佇列"""
        self._queue: Queue[OCRTask] = Queue()
        self._lock = Lock()
        self._tasks: Dict[str, OCRTask] = {}  # 所有任務的映射
        self._pending_count = 0  # 待處理任務計數
    
    def add_task(self, task: OCRTask) -> str:
        """
        添加任務到佇列
        
        Args:
            task: 要添加的任務
            
        Returns:
            任務 ID
        """
        with self._lock:
            self._tasks[task.id] = task
            self._queue.put(task)
            self._pending_count += 1
            logger.info(f"任務已加入佇列: {task.id} - {task.input_filename}")
        
        return task.id
    
    def add_task_by_path(self, input_path: str) -> str:
        """
        根據檔案路徑建立並添加任務
        
        Args:
            input_path: 輸入檔案路徑
            
        Returns:
            任務 ID
        """
        from pathlib import Path
        
        task = OCRTask(input_path=Path(input_path))
        return self.add_task(task)
    
    def get_next_task(self) -> Optional[OCRTask]:
        """
        獲取下一個待處理任務
        
        此方法是非阻塞的，如果佇列為空則返回 None。
        
        Returns:
            下一個待處理的任務，如果沒有則返回 None
        """
        try:
            task = self._queue.get_nowait()
            with self._lock:
                self._pending_count -= 1
            return task
        except:
            return None
    
    def task_done(self, task_id: str) -> None:
        """
        標記任務完成（從佇列角度）
        
        這會通知佇列任務已處理完成。
        
        Args:
            task_id: 任務 ID
        """
        self._queue.task_done()
        logger.debug(f"任務佇列標記完成: {task_id}")
    
    def get_task(self, task_id: str) -> Optional[OCRTask]:
        """
        根據 ID 獲取任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            任務實例，如果不存在則返回 None
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def update_task(self, task: OCRTask) -> None:
        """
        更新任務狀態
        
        Args:
            task: 更新後的任務實例
        """
        with self._lock:
            if task.id in self._tasks:
                self._tasks[task.id] = task
                logger.debug(f"任務已更新: {task.id} - 狀態: {task.status.value}")
    
    def get_queue_size(self) -> int:
        """
        獲取佇列大小
        
        Returns:
            待處理任務的數量
        """
        with self._lock:
            return self._pending_count
    
    def get_all_tasks(self) -> List[OCRTask]:
        """
        獲取所有任務
        
        Returns:
            所有任務的列表
        """
        with self._lock:
            return list(self._tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[OCRTask]:
        """
        根據狀態獲取任務
        
        Args:
            status: 任務狀態
            
        Returns:
            符合狀態的任務列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == status]
    
    def get_pending_tasks(self) -> List[OCRTask]:
        """獲取所有待處理任務"""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_processing_tasks(self) -> List[OCRTask]:
        """獲取所有處理中任務"""
        return self.get_tasks_by_status(TaskStatus.PROCESSING)
    
    def get_completed_tasks(self) -> List[OCRTask]:
        """獲取所有已完成任務"""
        return self.get_tasks_by_status(TaskStatus.COMPLETED)
    
    def get_failed_tasks(self) -> List[OCRTask]:
        """獲取所有失敗任務"""
        return self.get_tasks_by_status(TaskStatus.FAILED)
    
    def clear(self) -> None:
        """清空佇列"""
        with self._lock:
            # 清空佇列
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except:
                    break
            
            self._tasks.clear()
            self._pending_count = 0
            logger.info("任務佇列已清空")
    
    def clear_completed(self) -> int:
        """
        清除已完成的任務
        
        Returns:
            清除的任務數量
        """
        with self._lock:
            completed_ids = [
                task_id for task_id, task in self._tasks.items()
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
            ]
            
            for task_id in completed_ids:
                del self._tasks[task_id]
            
            if completed_ids:
                logger.info(f"已清除 {len(completed_ids)} 個已完成的任務")
            
            return len(completed_ids)
    
    def has_pending_tasks(self) -> bool:
        """
        檢查是否有待處理任務
        
        Returns:
            是否有待處理任務
        """
        return self.get_queue_size() > 0
    
    def get_statistics(self) -> dict:
        """
        獲取佇列統計資訊
        
        Returns:
            統計資訊字典
        """
        with self._lock:
            stats = {
                "total": len(self._tasks),
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
            }
            
            for task in self._tasks.values():
                if task.status == TaskStatus.PENDING:
                    stats["pending"] += 1
                elif task.status == TaskStatus.PROCESSING:
                    stats["processing"] += 1
                elif task.status == TaskStatus.COMPLETED:
                    stats["completed"] += 1
                elif task.status == TaskStatus.FAILED:
                    stats["failed"] += 1
            
            return stats
