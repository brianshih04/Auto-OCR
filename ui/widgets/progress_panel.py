"""
進度面板元件

提供進度條 + 狀態標籤 + 檔名標籤的進度顯示元件。
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ProgressPanel(QWidget):
    """
    進度面板元件
    
    包含進度條、狀態標籤和檔名標籤，用於顯示處理進度。
    
    Signals:
        progressChanged: 進度變更時發出
    """
    
    progressChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化進度面板元件"""
        super().__init__(parent)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """建立 UI 元件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 進度條
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        self._progress_bar.setFixedHeight(20)
        
        # 狀態標籤
        self._status_label = QLabel("等待啟動...")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 檔名標籤
        self._filename_label = QLabel("")
        self._filename_label.setObjectName("filenameLabel")
        self._filename_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._filename_label.setWordWrap(True)
        
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._status_label)
        layout.addWidget(self._filename_label)
    
    def progress(self) -> int:
        """
        取得當前進度
        
        Returns:
            當前進度值 (0-100)
        """
        return self._progress_bar.value()
    
    def set_progress(self, value: int) -> None:
        """
        設定進度
        
        Args:
            value: 進度值 (0-100)
        """
        value = max(0, min(100, value))
        self._progress_bar.setValue(value)
        self.progressChanged.emit(value)
    
    def status(self) -> str:
        """
        取得當前狀態文字
        
        Returns:
            狀態文字
        """
        return self._status_label.text()
    
    def set_status(self, status: str) -> None:
        """
        設定狀態文字
        
        Args:
            status: 狀態文字
        """
        self._status_label.setText(status)
    
    def filename(self) -> str:
        """
        取得當前檔名
        
        Returns:
            檔名
        """
        return self._filename_label.text()
    
    def set_filename(self, filename: str) -> None:
        """
        設定檔名
        
        Args:
            filename: 檔名
        """
        if filename:
            self._filename_label.setText(f"正在處理: {filename}")
            self._filename_label.show()
        else:
            self._filename_label.hide()
    
    def reset(self) -> None:
        """重置進度面板"""
        self._progress_bar.setValue(0)
        self._status_label.setText("等待啟動...")
        self._filename_label.setText("")
        self._filename_label.hide()
    
    def set_idle(self) -> None:
        """設定為閒置狀態"""
        self._progress_bar.setValue(0)
        self._status_label.setText("等待啟動...")
        self._filename_label.setText("")
        self._filename_label.hide()
    
    def set_processing(self, filename: str = "", progress: int = 0) -> None:
        """
        設定為處理中狀態
        
        Args:
            filename: 正在處理的檔名
            progress: 當前進度
        """
        self.set_status("處理中...")
        self.set_filename(filename)
        self.set_progress(progress)
    
    def set_completed(self) -> None:
        """設定為完成狀態"""
        self._progress_bar.setValue(100)
        self._status_label.setText("處理完成")
        self._filename_label.setText("")
        self._filename_label.hide()
    
    def set_error(self, error_message: str = "處理失敗") -> None:
        """
        設定為錯誤狀態
        
        Args:
            error_message: 錯誤訊息
        """
        self._status_label.setText(f"錯誤: {error_message}")
        self._filename_label.setText("")


class ProgressGroupBox(QGroupBox):
    """
    帶有群組框的進度面板
    
    包含標題和進度面板的群組框元件。
    """
    
    def __init__(
        self,
        title: str = "控制 & 進度",
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        初始化進度群組框
        
        Args:
            title: 群組框標題
            parent: 父元件
        """
        super().__init__(title, parent)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """建立 UI 元件"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # 進度面板
        self._progress_panel = ProgressPanel()
        
        layout.addWidget(self._progress_panel)
    
    @property
    def progress_panel(self) -> ProgressPanel:
        """取得進度面板"""
        return self._progress_panel
    
    def set_progress(self, value: int) -> None:
        """設定進度"""
        self._progress_panel.set_progress(value)
    
    def set_status(self, status: str) -> None:
        """設定狀態"""
        self._progress_panel.set_status(status)
    
    def set_filename(self, filename: str) -> None:
        """設定檔名"""
        self._progress_panel.set_filename(filename)
    
    def reset(self) -> None:
        """重置進度"""
        self._progress_panel.reset()
