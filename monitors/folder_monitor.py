"""
資料夾監控模組

使用 watchdog 函式庫實現資料夾監控功能。
"""

import logging
import time
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class FileEventSignal(QObject):
    """
    用於執行緒間通訊的訊號類別
    
    此類別用於從 watchdog 事件處理器向主執行緒發送訊號。
    """
    
    file_detected = pyqtSignal(str)  # 檔案路徑
    error_occurred = pyqtSignal(str)  # 錯誤訊息


class ImageFileHandler(FileSystemEventHandler):
    """
    圖片檔案事件處理器
    
    繼承自 watchdog 的 FileSystemEventHandler，處理檔案建立事件。
    """
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    
    def __init__(self, signal_emitter: FileEventSignal, debounce_delay: float = 0.5):
        """
        初始化圖片檔案處理器
        
        Args:
            signal_emitter: 用於發送訊號的物件
            debounce_delay: 防抖延遲時間（秒），確保檔案完全寫入
        """
        super().__init__()
        self.signal_emitter = signal_emitter
        self.debounce_delay = debounce_delay
    
    def on_created(self, event):
        """
        檔案建立事件處理
        
        Args:
            event: watchdog 檔案事件物件
        """
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
            logger.info(f"偵測到新圖片檔案: {path}")
            
            # 防抖：等待檔案完全寫入
            time.sleep(self.debounce_delay)
            
            # 確認檔案仍然存在
            if path.exists():
                self.signal_emitter.file_detected.emit(str(path))
            else:
                logger.warning(f"檔案已消失: {path}")
    
    def on_moved(self, event):
        """
        檔案移動事件處理
        
        Args:
            event: watchdog 檔案事件物件
        """
        if event.is_directory:
            return
        
        path = Path(event.dest_path)
        if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
            logger.info(f"偵測到移動的圖片檔案: {path}")
            
            # 防抖：等待檔案完全寫入
            time.sleep(self.debounce_delay)
            
            # 確認檔案仍然存在
            if path.exists():
                self.signal_emitter.file_detected.emit(str(path))
            else:
                logger.warning(f"檔案已消失: {path}")


class FolderMonitor(QThread):
    """
    資料夾監控執行緒
    
    在背景執行緒中運行 watchdog Observer，監控指定資料夾中的新檔案。
    """
    
    # 訊號定義
    file_detected = pyqtSignal(str)  # 檔案路徑
    error_occurred = pyqtSignal(str)  # 錯誤訊息
    started_monitoring = pyqtSignal()  # 監控已啟動
    stopped_monitoring = pyqtSignal()  # 監控已停止
    
    def __init__(
        self,
        watch_path: str,
        debounce_delay: float = 0.5,
        parent=None
    ):
        """
        初始化資料夾監控器
        
        Args:
            watch_path: 要監控的資料夾路徑
            debounce_delay: 防抖延遲時間（秒）
            parent: 父物件
        """
        super().__init__(parent)
        
        self._watch_path = Path(watch_path)
        self._debounce_delay = debounce_delay
        self._observer: Observer | None = None
        self._signal_emitter = FileEventSignal()
        self._is_running = False
        
        # 連接內部訊號
        self._signal_emitter.file_detected.connect(self._on_file_detected)
        self._signal_emitter.error_occurred.connect(self._on_error)
    
    def _on_file_detected(self, file_path: str):
        """內部訊號轉發：檔案偵測"""
        self.file_detected.emit(file_path)
    
    def _on_error(self, error_message: str):
        """內部訊號轉發：錯誤"""
        self.error_occurred.emit(error_message)
    
    @property
    def watch_path(self) -> Path:
        """取得監控路徑"""
        return self._watch_path
    
    def run(self):
        """
        執行監控執行緒
        
        此方法在背景執行緒中運行，啟動 watchdog Observer。
        """
        try:
            # 驗證監控路徑
            if not self._watch_path.exists():
                self.error_occurred.emit(f"監控路徑不存在: {self._watch_path}")
                return
            
            if not self._watch_path.is_dir():
                self.error_occurred.emit(f"監控路徑不是資料夾: {self._watch_path}")
                return
            
            # 建立事件處理器
            event_handler = ImageFileHandler(
                self._signal_emitter,
                debounce_delay=self._debounce_delay
            )
            
            # 建立並啟動 Observer
            self._observer = Observer()
            self._observer.schedule(
                event_handler,
                str(self._watch_path),
                recursive=False
            )
            
            self._is_running = True
            self._observer.start()
            
            logger.info(f"開始監控資料夾: {self._watch_path}")
            self.started_monitoring.emit()
            
            # 保持執行緒運行
            while self._is_running:
                time.sleep(0.1)
                
                # 檢查 Observer 是否異常停止
                if self._observer and not self._observer.is_alive():
                    self.error_occurred.emit("監控器意外停止")
                    break
        
        except Exception as e:
            error_msg = f"監控執行錯誤: {str(e)}"
            logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
        
        finally:
            self._cleanup()
    
    def stop(self):
        """
        停止監控
        
        安全地停止 watchdog Observer 並結束執行緒。
        """
        logger.info("正在停止監控...")
        self._is_running = False
        
        # 等待執行緒結束
        self.wait(3000)  # 最多等待 3 秒
        
        logger.info("監控已停止")
        self.stopped_monitoring.emit()
    
    def _cleanup(self):
        """清理資源"""
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
            except Exception as e:
                logger.warning(f"停止 Observer 時發生錯誤: {e}")
            finally:
                self._observer = None
