"""
路徑選擇元件

提供標籤 + 文字框 + 瀏覽按鈕的路徑選擇元件。
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class PathSelector(QWidget):
    """
    路徑選擇元件
    
    包含標籤、文字框和瀏覽按鈕，用於選擇資料夾或檔案路徑。
    
    Signals:
        pathChanged: 路徑變更時發出，帶有新路徑字串
    """
    
    pathChanged = pyqtSignal(str)
    
    def __init__(
        self,
        label: str,
        mode: str = "folder",
        parent: Optional[QWidget] = None,
        placeholder: str = "",
        browse_text: str = "選擇",
    ) -> None:
        """
        初始化路徑選擇元件
        
        Args:
            label: 標籤文字
            mode: 選擇模式，"folder" 或 "file"
            parent: 父元件
            placeholder: 文字框佔位符
            browse_text: 瀏覽按鈕文字
        """
        super().__init__(parent)
        
        self._mode = mode
        self._label_text = label
        
        self._setup_ui(label, placeholder, browse_text)
        self._connect_signals()
    
    def _setup_ui(self, label: str, placeholder: str, browse_text: str) -> None:
        """建立 UI 元件"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 標籤
        self._label = QLabel(label)
        self._label.setMinimumWidth(80)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 文字框
        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText(placeholder)
        self._line_edit.setReadOnly(True)
        
        # 瀏覽按鈕
        self._browse_button = QPushButton(browse_text)
        self._browse_button.setObjectName("browseButton")
        self._browse_button.setFixedWidth(70)
        
        layout.addWidget(self._label)
        layout.addWidget(self._line_edit, 1)
        layout.addWidget(self._browse_button)
    
    def _connect_signals(self) -> None:
        """連接訊號"""
        self._browse_button.clicked.connect(self._on_browse)
        self._line_edit.textChanged.connect(self._on_text_changed)
    
    def _on_browse(self) -> None:
        """瀏覽按鈕點擊事件"""
        current_path = self._line_edit.text()
        
        if self._mode == "folder":
            selected_path = QFileDialog.getExistingDirectory(
                self,
                f"選擇{self._label_text}",
                current_path,
                QFileDialog.Option.ShowDirsOnly,
            )
        else:
            selected_path, _ = QFileDialog.getOpenFileName(
                self,
                f"選擇{self._label_text}",
                current_path,
                "所有檔案 (*.*);;模型檔案 (*.gguf)",
            )
        
        if selected_path:
            self._line_edit.setText(selected_path)
    
    def _on_text_changed(self, text: str) -> None:
        """文字變更事件"""
        self.pathChanged.emit(text)
    
    def path(self) -> str:
        """
        取得當前路徑
        
        Returns:
            當前路徑字串
        """
        return self._line_edit.text()
    
    def set_path(self, path: str) -> None:
        """
        設定路徑
        
        Args:
            path: 要設定的路徑
        """
        self._line_edit.setText(path)
    
    def set_path_from_pathlib(self, path: Path) -> None:
        """
        從 Path 物件設定路徑
        
        Args:
            path: pathlib.Path 物件
        """
        self._line_edit.setText(str(path))
    
    def clear(self) -> None:
        """清除路徑"""
        self._line_edit.clear()
    
    def set_enabled(self, enabled: bool) -> None:
        """
        設定元件是否啟用
        
        Args:
            enabled: 是否啟用
        """
        self._line_edit.setEnabled(enabled)
        self._browse_button.setEnabled(enabled)
    
    def set_label_width(self, width: int) -> None:
        """
        設定標籤寬度
        
        Args:
            width: 標籤寬度（像素）
        """
        self._label.setFixedWidth(width)
    
    def set_browse_button_text(self, text: str) -> None:
        """
        設定瀏覽按鈕文字
        
        Args:
            text: 按鈕文字
        """
        self._browse_button.setText(text)


class ModelPathSelector(PathSelector):
    """
    模型路徑選擇元件
    
    專門用於選擇 GGUF 模型檔案的元件。
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化模型路徑選擇元件"""
        super().__init__(
            label="模型路徑:",
            mode="file",
            parent=parent,
            placeholder="選擇 .gguf 模型檔案",
        )
        self._label.setText("模型路徑:")


class FolderPathSelector(PathSelector):
    """
    資料夾路徑選擇元件
    
    專門用於選擇資料夾的元件。
    """
    
    def __init__(
        self,
        label: str = "資料夾:",
        parent: Optional[QWidget] = None,
        placeholder: str = "選擇資料夾",
    ) -> None:
        """初始化資料夾路徑選擇元件"""
        super().__init__(
            label=label,
            mode="folder",
            parent=parent,
            placeholder=placeholder,
        )
