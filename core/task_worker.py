"""
任務工作者模組

提供背景任務處理執行緒功能。
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from engines import BaseOCREngine, OCREngineFactory, OCRResult
from converters import ConverterFactory
from postprocess import PostProcessorFactory
from utils.path_adapter import PathAdapter
from .task import OCRTask, TaskStatus
from .task_queue import TaskQueue

if TYPE_CHECKING:
    from config import ConfigManager

logger = logging.getLogger(__name__)


class TaskWorker(QThread):
    """
    背景任務處理執行緒
    
    從任務佇列中獲取任務並執行 OCR 處理。
    """
    
    # 訊號定義
    progress_updated = pyqtSignal(int, str)  # 進度百分比, 狀態訊息
    task_completed = pyqtSignal(str, str)  # 任務ID, 結果路徑
    task_failed = pyqtSignal(str, str)  # 任務ID, 錯誤訊息
    task_started = pyqtSignal(str, str)  # 任務ID, 檔案名稱
    log_message = pyqtSignal(str, str)  # 級別, 訊息
    queue_empty = pyqtSignal()  # 佇列已空
    
    def __init__(
        self,
        task_queue: TaskQueue,
        config_manager: "ConfigManager",
        parent=None
    ):
        """
        初始化任務工作者
        
        Args:
            task_queue: 任務佇列實例
            config_manager: 配置管理器實例
            parent: 父物件
        """
        super().__init__(parent)
        
        self._task_queue = task_queue
        self._config_manager = config_manager
        self._is_running = False
        self._current_task: Optional[OCRTask] = None
        self._ocr_engine: Optional[BaseOCREngine] = None
    
    def run(self):
        """
        執行任務處理執行緒
        
        持續從佇列中獲取任務並處理。
        """
        self._is_running = True
        self._log("INFO", "任務工作者已啟動")
        
        # 初始化 OCR 引擎
        if not self._initialize_ocr_engine():
            self._log("ERROR", "OCR 引擎初始化失敗，無法處理任務")
            self._is_running = False
            return
        
        while self._is_running:
            try:
                # 獲取下一個任務
                task = self._task_queue.get_next_task()
                
                if task is None:
                    # 佇列為空，等待一段時間
                    self.queue_empty.emit()
                    time.sleep(0.5)
                    continue
                
                # 處理任務
                self._process_task(task)
                
            except Exception as e:
                error_msg = f"任務處理發生錯誤: {str(e)}"
                logger.exception(error_msg)
                self._log("ERROR", error_msg)
                
                # 如果有當前任務，標記為失敗
                if self._current_task:
                    self._current_task.fail(str(e))
                    self._task_queue.update_task(self._current_task)
                    self.task_failed.emit(self._current_task.id, str(e))
                    self._task_queue.task_done(self._current_task.id)
                    self._current_task = None
        
        # 清理 OCR 引擎
        self._cleanup_ocr_engine()
        self._log("INFO", "任務工作者已停止")
    
    def _initialize_ocr_engine(self) -> bool:
        """
        初始化 OCR 引擎
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self._log("INFO", "正在初始化 OCR 引擎...")
            
            # 使用工廠建立 OCR 引擎
            self._ocr_engine = OCREngineFactory.create(self._config_manager)
            
            if self._ocr_engine is None:
                self._log("ERROR", "無法建立 OCR 引擎，請檢查配置")
                return False
            
            # 初始化引擎
            if not self._ocr_engine.initialize():
                self._log("ERROR", f"OCR 引擎初始化失敗: {self._ocr_engine.engine_name}")
                return False
            
            self._log("INFO", f"OCR 引擎已就緒: {self._ocr_engine.engine_name}")
            return True
            
        except Exception as e:
            error_msg = f"初始化 OCR 引擎時發生錯誤: {e}"
            logger.exception(error_msg)
            self._log("ERROR", error_msg)
            return False
    
    def _cleanup_ocr_engine(self) -> None:
        """清理 OCR 引擎資源"""
        if self._ocr_engine is not None:
            try:
                self._ocr_engine.cleanup()
                self._log("INFO", "OCR 引擎資源已釋放")
            except Exception as e:
                logger.warning(f"清理 OCR 引擎時發生錯誤: {e}")
            finally:
                self._ocr_engine = None
    
    def _process_task(self, task: OCRTask) -> None:
        """
        處理單個任務
        
        Args:
            task: 要處理的任務
        """
        self._current_task = task
        task.start()
        self._task_queue.update_task(task)
        
        filename = task.input_filename or "未知檔案"
        self._log("INFO", f"開始處理任務: {filename}")
        self.task_started.emit(task.id, filename)
        
        try:
            # 使用真實 OCR 引擎處理
            result_path = self._process_ocr(task)
            
            # 標記任務完成
            task.complete(result_path)
            self._task_queue.update_task(task)
            self._task_queue.task_done(task.id)
            
            self._log("INFO", f"任務完成: {filename}")
            self.task_completed.emit(task.id, str(result_path) if result_path else "")
            
        except Exception as e:
            error_msg = f"處理失敗: {str(e)}"
            task.fail(error_msg)
            self._task_queue.update_task(task)
            self._task_queue.task_done(task.id)
            
            self._log("ERROR", f"任務失敗: {filename} - {error_msg}")
            self.task_failed.emit(task.id, error_msg)
        
        finally:
            self._current_task = None
    
    def _process_ocr(self, task: OCRTask) -> Optional[Path]:
        """
        使用 OCR 引擎處理任務
        
        Args:
            task: 要處理的任務
            
        Returns:
            結果檔案路徑
        """
        # 更新進度：開始
        self.progress_updated.emit(0, "正在載入圖片...")
        
        # 檢查輸入檔案
        if not task.input_path or not task.input_path.exists():
            raise FileNotFoundError(f"輸入檔案不存在: {task.input_path}")
        
        # 檢查 OCR 引擎
        if self._ocr_engine is None or not self._ocr_engine.is_ready():
            raise RuntimeError("OCR 引擎未就緒")
        
        # 更新進度：處理中
        self.progress_updated.emit(30, f"正在使用 {self._ocr_engine.engine_name} 進行辨識...")
        
        # 執行 OCR 辨識
        result: OCRResult = self._ocr_engine.recognize(task.input_path)
        
        # 檢查辨識結果
        if not result.success:
            raise RuntimeError(f"OCR 辨識失敗: {result.error or '未知錯誤'}")
        
        # 更新進度：生成輸出
        self.progress_updated.emit(70, "正在生成輸出檔案...")
        
        # 取得配置
        config = self._config_manager.config
        output_folder = Path(config.monitor.output_folder)
        
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
        
        # 生成輸出檔案名稱
        input_stem = task.input_path.stem
        output_format = config.output.format
        
        if output_format == "pdf":
            output_path = output_folder / f"{input_stem}_ocr.pdf"
        else:
            output_path = output_folder / f"{input_stem}_ocr.txt"
        
        # 使用轉換器生成輸出檔案
        output_path = self._convert_output(task.input_path, result.text, output_path, output_format)
        
        # 更新進度：後處理
        self.progress_updated.emit(90, "正在執行後處理...")
        
        # 執行後處理
        self._post_process(task.input_path)
        
        # 更新進度：完成
        self.progress_updated.emit(100, f"處理完成（耗時: {result.processing_time:.2f}s）")
        
        return output_path
    
    def _convert_output(self, image_path: Path, ocr_text: str, output_path: Path, output_format: str) -> Optional[Path]:
        """
        使用轉換器生成輸出檔案
        
        Args:
            image_path: 原始圖片路徑
            ocr_text: OCR 辨識文字
            output_path: 輸出檔案路徑
            output_format: 輸出格式
            
        Returns:
            輸出檔案路徑，失敗則返回 None
        """
        try:
            # 取得字體路徑（用於 PDF）
            font_path = None
            if output_format == "pdf":
                font_path = PathAdapter.get_fonts_path() / "NotoSansCJK.ttf"
                if not font_path.exists():
                    font_path = None
                    self._log("WARNING", "中文字體檔案不存在，將使用預設字體")
            
            # 建立轉換器
            converter = ConverterFactory.create(output_format, font_path)
            
            if converter is None:
                # 回退到舊的寫入方式
                self._log("WARNING", f"不支援的輸出格式: {output_format}，使用預設文字輸出")
                self._write_output_file(output_path, ocr_text, image_path)
                return output_path
            
            # 執行轉換
            result = converter.convert(image_path, ocr_text, output_path)
            
            if not result.success:
                raise RuntimeError(f"輸出轉換失敗: {result.error}")
            
            self._log("INFO", f"輸出檔案已生成: {result.output_path}")
            return result.output_path
            
        except Exception as e:
            error_msg = f"轉換輸出時發生錯誤: {str(e)}"
            logger.exception(error_msg)
            self._log("ERROR", error_msg)
            # 嘗試回退到基本文字輸出
            try:
                self._write_output_file(output_path, ocr_text, image_path)
                return output_path
            except Exception:
                return None
    
    def _write_output_file(self, output_path: Path, text: str, image_path: Path) -> None:
        """
        寫入輸出檔案（基本文字格式，作為回退方案）
        
        Args:
            output_path: 輸出檔案路徑
            text: OCR 辨識文字
            image_path: 原始圖片路徑
        """
        # 建立輸出內容
        content = f"OCR Result for {image_path.name}\n"
        content += f"Source: {image_path}\n"
        content += "=" * 40 + "\n\n"
        content += text
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _post_process(self, file_path: Path) -> None:
        """
        執行後處理
        
        Args:
            file_path: 要處理的檔案路徑
        """
        try:
            config = self._config_manager.config
            post_action = config.postprocess.action
            
            # 如果沒有設定後處理動作，則不執行
            if not post_action or post_action.lower() == "none":
                self._log("DEBUG", "未設定後處理動作，跳過後處理")
                return
            
            # 取得備份資料夾路徑
            archive_folder = None
            if post_action.lower() == "move":
                if config.postprocess.move_destination:
                    archive_folder = Path(config.postprocess.move_destination)
                elif config.monitor.archive_folder:
                    archive_folder = Path(config.monitor.archive_folder)
                else:
                    self._log("WARNING", "未設定備份資料夾，無法執行移動後處理")
                    return
            
            # 建立後處理器
            processor = PostProcessorFactory.create(post_action, archive_folder)
            
            if processor is None:
                self._log("WARNING", f"無法建立後處理器: {post_action}")
                return
            
            # 執行後處理
            result = processor.process(file_path)
            
            if result.success:
                self._log("INFO", f"後處理完成: {post_action}")
            else:
                self._log("ERROR", f"後處理失敗: {result.error}")
            
        except Exception as e:
            error_msg = f"執行後處理時發生錯誤: {str(e)}"
            logger.exception(error_msg)
            self._log("ERROR", error_msg)
    
    def stop(self):
        """
        停止任務工作者
        
        設置停止標誌並等待執行緒結束。
        """
        logger.info("正在停止任務工作者...")
        self._is_running = False
        
        # 等待執行緒結束
        self.wait(5000)  # 最多等待 5 秒
        
        logger.info("任務工作者已停止")
    
    def _log(self, level: str, message: str) -> None:
        """
        發送日誌訊號
        
        Args:
            level: 日誌級別
            message: 日誌訊息
        """
        self.log_message.emit(level, message)
        
        # 同時寫入 Python logging
        if level == "DEBUG":
            logger.debug(message)
        elif level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
    
    @property
    def is_busy(self) -> bool:
        """檢查是否正在處理任務"""
        return self._current_task is not None
    
    @property
    def current_task(self) -> Optional[OCRTask]:
        """取得當前處理中的任務"""
        return self._current_task
