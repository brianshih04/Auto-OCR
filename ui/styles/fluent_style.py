"""
Fluent Design 樣式表

提供 Windows 10/11 Fluent Design 風格的 PyQt6 樣式表。
"""

FLUENT_STYLE = """
/* ========================================
   全域設定
   ======================================== */

QMainWindow {
    background-color: #f3f3f3;
}

QWidget {
    font-family: "Segoe UI", "Microsoft JhengHei UI", sans-serif;
    font-size: 13px;
    color: #1a1a1a;
}

/* ========================================
   群組框 (QGroupBox)
   ======================================== */

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 24px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    background-color: #ffffff;
    color: #0078d4;
    font-weight: 600;
    font-size: 14px;
}

QGroupBox:hover {
    border-color: #0078d4;
}

/* ========================================
   按鈕 (QPushButton)
   ======================================== */

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #c4c4c4;
    color: #a0a0a0;
}

/* 主要按鈕（大型啟動按鈕） */
QPushButton#primaryButton {
    background-color: #0078d4;
    color: white;
    font-size: 16px;
    font-weight: 600;
    padding: 16px 48px;
    border-radius: 8px;
    min-width: 200px;
    min-height: 48px;
}

QPushButton#primaryButton:hover {
    background-color: #106ebe;
}

QPushButton#primaryButton:pressed {
    background-color: #005a9e;
}

/* 停止按鈕 */
QPushButton#stopButton {
    background-color: #d13438;
}

QPushButton#stopButton:hover {
    background-color: #a4262c;
}

QPushButton#stopButton:pressed {
    background-color: #811a1e;
}

/* 瀏覽按鈕 */
QPushButton#browseButton {
    background-color: #ffffff;
    color: #0078d4;
    border: 1px solid #0078d4;
    min-width: 60px;
}

QPushButton#browseButton:hover {
    background-color: #f0f6fc;
    border-color: #106ebe;
}

/* ========================================
   單選按鈕 (QRadioButton)
   ======================================== */

QRadioButton {
    spacing: 8px;
    padding: 4px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #8a8a8a;
    background-color: white;
}

QRadioButton::indicator:hover {
    border-color: #0078d4;
}

QRadioButton::indicator:checked {
    border-color: #0078d4;
    background-color: white;
}

QRadioButton::indicator:checked::after {
    background-color: #0078d4;
}

/* ========================================
   核取方塊 (QCheckBox)
   ======================================== */

QCheckBox {
    spacing: 8px;
    padding: 4px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid #8a8a8a;
    background-color: white;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}

QCheckBox::indicator:checked {
    border-color: #0078d4;
    background-color: #0078d4;
}

/* ========================================
   文字輸入框 (QLineEdit)
   ======================================== */

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 8px 12px;
    selection-background-color: #0078d4;
    selection-color: white;
}

QLineEdit:hover {
    border-color: #8a8a8a;
}

QLineEdit:focus {
    border-color: #0078d4;
    border-width: 2px;
    padding: 7px 11px;
}

QLineEdit:disabled {
    background-color: #f3f3f3;
    color: #a0a0a0;
}

/* ========================================
   純文字編輯區 (QPlainTextEdit)
   ======================================== */

QPlainTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 8px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #264f78;
    selection-color: white;
}

QPlainTextEdit:focus {
    border-color: #0078d4;
}

/* ========================================
   進度條 (QProgressBar)
   ======================================== */

QProgressBar {
    background-color: #e0e0e0;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 4px;
}

/* ========================================
   標籤 (QLabel)
   ======================================== */

QLabel {
    color: #1a1a1a;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 16px;
    font-weight: 600;
    color: #0078d4;
}

QLabel#statusLabel {
    color: #616161;
    font-size: 12px;
}

QLabel#filenameLabel {
    color: #0078d4;
    font-weight: 500;
}

/* ========================================
   下拉選單 (QComboBox)
   ======================================== */

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 8px 12px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #8a8a8a;
}

QComboBox:focus {
    border-color: #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #616161;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    selection-background-color: #f0f6fc;
    selection-color: #1a1a1a;
}

/* ========================================
   捲軸 (QScrollBar)
   ======================================== */

QScrollBar:vertical {
    background-color: #f3f3f3;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #c4c4c4;
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f3f3f3;
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #c4c4c4;
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ========================================
   分隔線
   ======================================== */

QFrame[frameShape="4"] { /* HLine */
    background-color: #e0e0e0;
    border: none;
    height: 1px;
}

QFrame[frameShape="5"] { /* VLine */
    background-color: #e0e0e0;
    border: none;
    width: 1px;
}

/* ========================================
   工具提示 (QToolTip)
   ======================================== */

QToolTip {
    background-color: #1a1a1a;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ========================================
   選項頁籤 (QTabWidget, QTabBar)
   ======================================== */

QTabWidget::pane {
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f3f3f3;
    color: #616161;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0078d4;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    background-color: #e0e0e0;
}

/* ========================================
   訊息框 (QMessageBox)
   ======================================== */

QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1a1a1a;
}
"""

# 顏色常數
class FluentColors:
    """Fluent Design 顏色常數"""
    
    # 主要色彩
    PRIMARY = "#0078d4"
    PRIMARY_HOVER = "#106ebe"
    PRIMARY_PRESSED = "#005a9e"
    
    # 危險/錯誤色彩
    DANGER = "#d13438"
    DANGER_HOVER = "#a4262c"
    DANGER_PRESSED = "#811a1e"
    
    # 成功色彩
    SUCCESS = "#107c10"
    SUCCESS_HOVER = "#0b5e0b"
    
    # 警告色彩
    WARNING = "#ffb900"
    WARNING_HOVER = "#e6a700"
    
    # 背景色彩
    BACKGROUND_LIGHT = "#f3f3f3"
    BACKGROUND_WHITE = "#ffffff"
    BACKGROUND_DARK = "#1e1e1e"
    
    # 文字色彩
    TEXT_PRIMARY = "#1a1a1a"
    TEXT_SECONDARY = "#616161"
    TEXT_DISABLED = "#a0a0a0"
    TEXT_ON_PRIMARY = "#ffffff"
    
    # 邊框色彩
    BORDER_LIGHT = "#d1d1d1"
    BORDER_MEDIUM = "#8a8a8a"
    BORDER_FOCUS = "#0078d4"
