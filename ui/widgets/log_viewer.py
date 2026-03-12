"""
日誌顯示元件

提供支援自動滾動和顏色標記的日誌顯示元件。
"""

import logging
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QGroupBox, QPlainTextEdit, QVBoxLayout, QWidget


class LogViewer(QPlainTextEdit):
    """
    日誌顯示元件
    
    支援自動滾動、顏色標記和日誌級別格式化的純文字編輯器。
    """
    
    # 日誌級別顏色對應
    LEVEL_COLORS = {
        "DEBUG": QColor("#6a9955"),    # 綠色
        "INFO": QColor("#569cd6"),     # 藍色
        "WARNING": QColor("#dcdcaa"),  # 黃色
        "ERROR": QColor("#f14c4c"),    # 紅色
        "CRITICAL": QColor("#f14c4c"), # 紅色
    }
    
    # 預設時間格式
    DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化日誌顯示元件"""
        super().__init__(parent)
        
        self._time_format = self.DEFAULT_TIME_FORMAT
        self._max_lines = 1000
        self._auto_scroll = True
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """設定 UI"""
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setMaximumBlockCount(self._max_lines)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 設定等寬字體
        font = self.font()
        font.setFamily("Consolas, 'Courier New', monospace")
        font.setPointSize(10)
        self.setFont(font)
    
    def append_log(self, level: str, message: str) -> None:
        """
        附加日誌訊息
        
        Args:
            level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: 日誌訊息
        """
        timestamp = datetime.now().strftime(self._time_format)
        level = level.upper()
        
        # 格式化日誌行
        log_line = f"[{timestamp}] {level}: {message}\n"
        
        # 取得顏色
        color = self.LEVEL_COLORS.get(level, QColor("#d4d4d4"))
        
        # 建立文字格式
        text_format = QTextCharFormat()
        text_format.setForeground(color)
        
        # 移動游標到結尾
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 插入帶格式的文字
        cursor.insertText(log_line, text_format)
        
        # 自動滾動到底部
        if self._auto_scroll:
            self._scroll_to_bottom()
    
    def append_message(self, message: str, color: Optional[QColor] = None) -> None:
        """
        附加一般訊息（不帶級別格式）
        
        Args:
            message: 訊息內容
            color: 可選的顏色
        """
        # 建立文字格式
        text_format = QTextCharFormat()
        if color:
            text_format.setForeground(color)
        
        # 移動游標到結尾
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 插入帶格式的文字
        cursor.insertText(message + "\n", text_format)
        
        # 自動滾動到底部
        if self._auto_scroll:
            self._scroll_to_bottom()
    
    def append_info(self, message: str) -> None:
        """附加 INFO 級別日誌"""
        self.append_log("INFO", message)
    
    def append_warning(self, message: str) -> None:
        """附加 WARNING 級別日誌"""
        self.append_log("WARNING", message)
    
    def append_error(self, message: str) -> None:
        """附加 ERROR 級別日誌"""
        self.append_log("ERROR", message)
    
    def append_debug(self, message: str) -> None:
        """附加 DEBUG 級別日誌"""
        self.append_log("DEBUG", message)
    
    def clear_logs(self) -> None:
        """清除所有日誌"""
        self.clear()
    
    def _scroll_to_bottom(self) -> None:
        """滾動到底部"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_auto_scroll(self, enabled: bool) -> None:
        """
        設定是否自動滾動
        
        Args:
            enabled: 是否啟用自動滾動
        """
        self._auto_scroll = enabled
    
    def set_max_lines(self, max_lines: int) -> None:
        """
        設定最大行數
        
        Args:
            max_lines: 最大行數
        """
        self._max_lines = max_lines
        self.setMaximumBlockCount(max_lines)
    
    def set_time_format(self, time_format: str) -> None:
        """
        設定時間格式
        
        Args:
            time_format: 時間格式字串
        """
        self._time_format = time_format


class LogGroupBox(QGroupBox):
    """
    帶有群組框的日誌顯示元件
    
    包含標題和日誌顯示器的群組框元件。
    """
    
    def __init__(
        self,
        title: str = "系統日誌",
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        初始化日誌群組框
        
        Args:
            title: 群組框標題
            parent: 父元件
        """
        super().__init__(title, parent)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """建立 UI 元件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 日誌顯示器
        self._log_viewer = LogViewer()
        
        layout.addWidget(self._log_viewer)
    
    @property
    def log_viewer(self) -> LogViewer:
        """取得日誌顯示器"""
        return self._log_viewer
    
    def append_log(self, level: str, message: str) -> None:
        """附加日誌"""
        self._log_viewer.append_log(level, message)
    
    def append_info(self, message: str) -> None:
        """附加 INFO 日誌"""
        self._log_viewer.append_info(message)
    
    def append_warning(self, message: str) -> None:
        """附加 WARNING 日誌"""
        self._log_viewer.append_warning(message)
    
    def append_error(self, message: str) -> None:
        """附加 ERROR 日誌"""
        self._log_viewer.append_error(message)
    
    def append_debug(self, message: str) -> None:
        """附加 DEBUG 日誌"""
        self._log_viewer.append_debug(message)
    
    def clear_logs(self) -> None:
        """清除日誌"""
        self._log_viewer.clear_logs()


class LogHandler(logging.Handler):
    """
    自訂日誌處理器
    
    將 Python logging 模組的日誌導向到 LogViewer 元件。
    """
    
    def __init__(self, log_viewer: LogViewer) -> None:
        """
        初始化日誌處理器
        
        Args:
            log_viewer: LogViewer 元件實例
        """
        super().__init__()
        self._log_viewer = log_viewer
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        發出日誌記錄
        
        Args:
            record: 日誌記錄
        """
        try:
            msg = self.format(record)
            level = record.levelname
            self._log_viewer.append_log(level, msg)
        except Exception:
            self.handleError(record)
