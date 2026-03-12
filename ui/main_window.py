"""
主視窗模組

提供應用程式的主視窗實作。
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config import ConfigManager
from core import OCRTask, TaskQueue, TaskWorker
from monitors import FolderMonitor
from ui.widgets import (
    FolderPathSelector,
    LogGroupBox,
    ModelPathSelector,
    ProgressGroupBox,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    應用程式主視窗
    
    包含 OCR 引擎設定、資料夾設定、輸出設定、控制面板和日誌顯示。
    """
    
    # 訊號
    monitoringStarted = pyqtSignal()
    monitoringStopped = pyqtSignal()
    
    def __init__(self, config_manager: Optional[ConfigManager] = None) -> None:
        """
        初始化主視窗
        
        Args:
            config_manager: 配置管理器實例，如果為 None 則建立新實例
        """
        super().__init__()
        
        self.config_manager = config_manager or ConfigManager()
        self._is_monitoring = False
        
        # 任務佇列和監控相關
        self.task_queue = TaskQueue()
        self.folder_monitor: Optional[FolderMonitor] = None
        self.task_worker: Optional[TaskWorker] = None
        
        self._setup_window()
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
        
        logger.info("主視窗初始化完成")
    
    def _setup_window(self) -> None:
        """設定視窗屬性"""
        self.setWindowTitle("🖼️ Smart OCR Folder Monitor")
        self.setMinimumSize(700, 800)
        self.resize(800, 900)
        
        # 設定視窗圖示（如果有的話）
        # self.setWindowIcon(QIcon("resources/icon.png"))
    
    def _setup_ui(self) -> None:
        """建立所有 UI 元件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 建立分頁元件
        self._tab_widget = QTabWidget()
        self._tab_widget.setDocumentMode(True)
        main_layout.addWidget(self._tab_widget)
        
        # 建立各個分頁
        self._setup_monitor_tab()
        self._setup_settings_tab()
        self._setup_log_tab()
    
    def _setup_monitor_tab(self) -> None:
        """建立監控主頁分頁"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # 控制與進度區
        self._setup_control_group(layout)
        
        # 當前狀態卡片 (可選，這裡先放進度面板)
        layout.addStretch()
        
        self._tab_widget.addTab(tab, "🏠 監控主頁")
    
    def _setup_settings_tab(self) -> None:
        """建立設定分頁"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        self._setup_engine_group(layout)
        self._setup_folder_group(layout)
        self._setup_output_group(layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        self._tab_widget.addTab(tab, "⚙️ 系統設定")
    
    def _setup_log_tab(self) -> None:
        """建立日誌分頁"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self._setup_log_group(layout)
        
        self._tab_widget.addTab(tab, "📝 運行日誌")
    
    def _setup_engine_group(self, parent_layout: QVBoxLayout) -> None:
        """建立 OCR 引擎設定群組"""
        self._engine_group = QGroupBox("OCR 引擎設定")
        engine_layout = QVBoxLayout(self._engine_group)
        engine_layout.setSpacing(12)
        
        # 引擎類型選擇
        self._engine_button_group = QButtonGroup(self._engine_group)
        
        # GLM-OCR Cloud 選項
        cloud_layout = QVBoxLayout()
        self._cloud_radio = QRadioButton("GLM-OCR Cloud")
        self._cloud_radio.setChecked(True)
        self._engine_button_group.addButton(self._cloud_radio, 0)
        
        # API Key 輸入
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_label.setFixedWidth(80)
        self._api_key_input = QLineEdit()
        self._api_key_input.setPlaceholderText("輸入您的 API Key")
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self._api_key_input)
        
        cloud_layout.addWidget(self._cloud_radio)
        cloud_layout.addLayout(api_layout)
        
        # Local LLM 選項
        local_layout = QVBoxLayout()
        self._local_radio = QRadioButton("Local LLM (llama.cpp)")
        self._engine_button_group.addButton(self._local_radio, 1)
        
        # 模型路徑選擇
        self._model_path_selector = ModelPathSelector()
        
        local_layout.addWidget(self._local_radio)
        local_layout.addWidget(self._model_path_selector)
        
        engine_layout.addLayout(cloud_layout)
        engine_layout.addLayout(local_layout)
        
        parent_layout.addWidget(self._engine_group)
    
    def _setup_folder_group(self, parent_layout: QVBoxLayout) -> None:
        """建立資料夾設定群組"""
        self._folder_group = QGroupBox("資料夾設定")
        folder_layout = QVBoxLayout(self._folder_group)
        folder_layout.setSpacing(12)
        
        # 輸入資料夾
        self._input_folder_selector = FolderPathSelector(
            label="輸入資料夾:",
            placeholder="選擇要監控的資料夾",
        )
        
        # 輸出資料夾
        self._output_folder_selector = FolderPathSelector(
            label="輸出資料夾:",
            placeholder="選擇輸出資料夾",
        )
        
        folder_layout.addWidget(self._input_folder_selector)
        folder_layout.addWidget(self._output_folder_selector)
        
        parent_layout.addWidget(self._folder_group)
    
    def _setup_output_group(self, parent_layout: QVBoxLayout) -> None:
        """建立輸出與後處理設定群組"""
        self._output_group = QGroupBox("輸出與後處理")
        output_layout = QVBoxLayout(self._output_group)
        output_layout.setSpacing(12)
        
        # 輸出格式
        format_label = QLabel("輸出格式:")
        format_layout = QHBoxLayout()
        self._format_button_group = QButtonGroup(self._output_group)
        
        self._pdf_radio = QRadioButton("Searchable PDF")
        self._pdf_radio.setChecked(True)
        self._txt_radio = QRadioButton("純文字 (.txt)")
        
        self._format_button_group.addButton(self._pdf_radio, 0)
        self._format_button_group.addButton(self._txt_radio, 1)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self._pdf_radio)
        format_layout.addWidget(self._txt_radio)
        format_layout.addStretch()
        
        # 後處理選項
        postprocess_label = QLabel("後處理:")
        postprocess_layout = QHBoxLayout()
        self._postprocess_button_group = QButtonGroup(self._output_group)
        
        self._post_none_radio = QRadioButton("無")
        self._post_delete_radio = QRadioButton("刪除原檔")
        self._post_move_radio = QRadioButton("移動至備份")
        self._post_move_radio.setChecked(True)
        
        self._postprocess_button_group.addButton(self._post_none_radio, 0)
        self._postprocess_button_group.addButton(self._post_delete_radio, 1)
        self._postprocess_button_group.addButton(self._post_move_radio, 2)
        
        postprocess_layout.addWidget(postprocess_label)
        postprocess_layout.addWidget(self._post_none_radio)
        postprocess_layout.addWidget(self._post_delete_radio)
        postprocess_layout.addWidget(self._post_move_radio)
        postprocess_layout.addStretch()
        
        # 備份資料夾（動態顯示）
        self._backup_folder_selector = FolderPathSelector(
            label="備份資料夾:",
            placeholder="選擇備份資料夾",
        )
        
        output_layout.addLayout(format_layout)
        output_layout.addLayout(postprocess_layout)
        output_layout.addWidget(self._backup_folder_selector)
        
        # 連接後處理選項變更
        self._postprocess_button_group.idClicked.connect(self._on_postprocess_changed)
        
        parent_layout.addWidget(self._output_group)
        
        # 初始設定備份資料夾可見性
        self._on_postprocess_changed(self._postprocess_button_group.checkedId())
    
    def _setup_control_group(self, parent_layout: QVBoxLayout) -> None:
        """建立控制與進度群組"""
        control_group = ProgressGroupBox("控制 & 進度")
        control_layout = control_group.layout()
        
        # 主要控制按鈕
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self._start_button = QPushButton("啟動監控")
        self._start_button.setObjectName("primaryButton")
        self._start_button.setFixedSize(200, 48)
        
        self._stop_button = QPushButton("停止監控")
        self._stop_button.setObjectName("stopButton")
        self._stop_button.setFixedSize(200, 48)
        self._stop_button.setVisible(False)
        
        button_layout.addWidget(self._start_button)
        button_layout.addWidget(self._stop_button)
        button_layout.addStretch()
        
        # 在進度面板之前插入按鈕
        control_layout.insertLayout(0, button_layout)
        
        parent_layout.addWidget(control_group)
        
        # 儲存進度面板引用
        self._progress_panel = control_group.progress_panel
    
    def _setup_log_group(self, parent_layout: QVBoxLayout) -> None:
        """建立日誌顯示群組"""
        self._log_group = LogGroupBox("系統日誌")
        self._log_group.setMinimumHeight(150)
        
        parent_layout.addWidget(self._log_group, 1)  # 可伸展
    
    def _connect_signals(self) -> None:
        """連接訊號與槽"""
        # 引擎與格式選擇變更時儲存設定
        self._engine_button_group.idClicked.connect(self._on_engine_changed)
        self._format_button_group.idClicked.connect(lambda _: self._save_settings())
        self._api_key_input.textChanged.connect(lambda _: self._save_settings())
        
        # 按鈕點擊
        self._start_button.clicked.connect(self.start_monitoring)
        self._stop_button.clicked.connect(self.stop_monitoring)
        
        # 路徑變更時儲存設定
        self._input_folder_selector.pathChanged.connect(self._save_settings)
        self._output_folder_selector.pathChanged.connect(self._save_settings)
        self._backup_folder_selector.pathChanged.connect(self._save_settings)
        self._model_path_selector.pathChanged.connect(self._save_settings)
    
    def _load_settings(self) -> None:
        """從 ConfigManager 載入設定"""
        config = self.config_manager.config
        
        # OCR 引擎設定
        engine_type = config.ocr_engine.type
        if engine_type == "cloud":
            self._cloud_radio.setChecked(True)
        else:
            self._local_radio.setChecked(True)
        
        # API Key
        self._api_key_input.setText(config.ocr_engine.glm_cloud.api_key)
        
        # 模型路徑
        self._model_path_selector.set_path(config.ocr_engine.llama_cpp.model_path)
        
        # 資料夾設定
        self._input_folder_selector.set_path(config.monitor.input_folder)
        self._output_folder_selector.set_path(config.monitor.output_folder)
        self._backup_folder_selector.set_path(config.postprocess.move_destination)
        
        # 輸出格式
        output_format = config.output.format
        if output_format == "pdf":
            self._pdf_radio.setChecked(True)
        else:
            self._txt_radio.setChecked(True)
        
        # 後處理
        post_action = config.postprocess.action
        if post_action == "none":
            self._post_none_radio.setChecked(True)
        elif post_action == "delete":
            self._post_delete_radio.setChecked(True)
        else:
            self._post_move_radio.setChecked(True)
        
        # 更新備份資料夾可見性
        self._on_postprocess_changed(self._postprocess_button_group.checkedId())
        
        # 更新引擎設定可見性
        self._on_engine_changed(self._engine_button_group.checkedId())
        
        logger.info("設定已載入")
    
    def _save_settings(self) -> None:
        """儲存設定到 ConfigManager"""
        config = self.config_manager.config
        
        # OCR 引擎設定
        config.ocr_engine.type = "cloud" if self._cloud_radio.isChecked() else "local"
        config.ocr_engine.glm_cloud.api_key = self._api_key_input.text()
        config.ocr_engine.llama_cpp.model_path = self._model_path_selector.path()
        
        # 資料夾設定
        config.monitor.input_folder = self._input_folder_selector.path()
        config.monitor.output_folder = self._output_folder_selector.path()
        config.postprocess.move_destination = self._backup_folder_selector.path()
        
        # 輸出格式
        config.output.format = "pdf" if self._pdf_radio.isChecked() else "txt"
        
        # 後處理
        post_id = self._postprocess_button_group.checkedId()
        if post_id == 0:
            config.postprocess.action = "none"
        elif post_id == 1:
            config.postprocess.action = "delete"
        else:
            config.postprocess.action = "move"
        
        # 儲存到檔案
        self.config_manager.save()
        
        logger.debug("設定已儲存")
    
    def _on_engine_changed(self, engine_id: int) -> None:
        """
        引擎選擇變更事件
        
        Args:
            engine_id: 選中的引擎 ID (0: cloud, 1: local)
        """
        # 更新 UI 狀態
        is_cloud = engine_id == 0
        
        # 啟用/停用相關輸入
        self._api_key_input.setEnabled(is_cloud)
        self._model_path_selector.set_enabled(not is_cloud)
        
        # 儲存設定
        self._save_settings()
    
    def _on_postprocess_changed(self, action_id: int) -> None:
        """
        後處理選項變更事件
        
        Args:
            action_id: 選中的動作 ID (0: none, 1: delete, 2: move)
        """
        # 顯示/隱藏備份資料夾選擇器
        show_backup = action_id == 2
        self._backup_folder_selector.setVisible(show_backup)
        
        # 儲存設定
        self._save_settings()
    
    def start_monitoring(self) -> None:
        """啟動監控"""
        # 驗證設定
        if not self._validate_settings():
            return
        
        # 儲存設定
        self._save_settings()
        
        # 更新 UI 狀態
        self._is_monitoring = True
        self._start_button.setVisible(False)
        self._stop_button.setVisible(True)
        
        # 禁用設定控制項
        self._set_settings_enabled(False)
        
        # 更新進度面板
        self._progress_panel.set_status("啟動中...")
        self._progress_panel.set_progress(0)
        
        # 記錄日誌
        self._log_group.append_info("正在啟動監控...")
        
        # 啟動資料夾監控
        input_folder = self._input_folder_selector.path()
        if input_folder:
            self.folder_monitor = FolderMonitor(input_folder)
            self.folder_monitor.file_detected.connect(self.on_file_detected)
            self.folder_monitor.error_occurred.connect(self.on_monitor_error)
            self.folder_monitor.started_monitoring.connect(self.on_monitoring_started)
            self.folder_monitor.stopped_monitoring.connect(self.on_monitoring_stopped)
            self.folder_monitor.start()
        
        # 啟動任務工作者
        self.task_worker = TaskWorker(self.task_queue, self.config_manager)
        self.task_worker.progress_updated.connect(self.on_progress_updated)
        self.task_worker.task_started.connect(self.on_task_started)
        self.task_worker.task_completed.connect(self.on_task_completed)
        self.task_worker.task_failed.connect(self.on_task_failed)
        self.task_worker.log_message.connect(self.on_worker_log)
        self.task_worker.start()
        
        # 發出訊號
        self.monitoringStarted.emit()
        
        logger.info("監控已啟動")
    
    def stop_monitoring(self) -> None:
        """停止監控"""
        # 更新 UI 狀態
        self._is_monitoring = False
        self._start_button.setVisible(True)
        self._stop_button.setVisible(False)
        
        # 啟用設定控制項
        self._set_settings_enabled(True)
        
        # 更新進度面板
        self._progress_panel.set_status("正在停止監控...")
        
        # 記錄日誌
        self._log_group.append_info("正在停止監控...")
        
        # 停止資料夾監控
        if self.folder_monitor:
            self.folder_monitor.stop()
            self.folder_monitor = None
        
        # 停止任務工作者
        if self.task_worker:
            self.task_worker.stop()
            self.task_worker = None
        
        # 清空任務佇列
        self.task_queue.clear()
        
        # 更新進度面板
        self._progress_panel.set_status("監控已停止")
        
        # 記錄日誌
        self._log_group.append_info("監控已停止")
        
        # 發出訊號
        self.monitoringStopped.emit()
        
        logger.info("監控已停止")
    
    def on_file_detected(self, file_path: str) -> None:
        """
        檔案偵測事件處理
        
        Args:
            file_path: 偵測到的檔案路徑
        """
        logger.info(f"偵測到新檔案: {file_path}")
        self._log_group.append_info(f"偵測到新檔案: {Path(file_path).name}")
        
        # 建立任務並加入佇列
        task = OCRTask(input_path=Path(file_path))
        task_id = self.task_queue.add_task(task)
        
        # 更新佇列狀態顯示
        queue_size = self.task_queue.get_queue_size()
        self._progress_panel.set_status(f"監控中... (佇列: {queue_size})")
    
    def on_monitor_error(self, error_message: str) -> None:
        """
        監控錯誤事件處理
        
        Args:
            error_message: 錯誤訊息
        """
        logger.error(f"監控錯誤: {error_message}")
        self._log_group.append_error(error_message)
    
    def on_monitoring_started(self) -> None:
        """監控啟動事件處理"""
        self._log_group.append_info(f"輸入資料夾: {self._input_folder_selector.path()}")
        self._log_group.append_info(f"輸出資料夾: {self._output_folder_selector.path()}")
        self._progress_panel.set_status("監控中...")
    
    def on_monitoring_stopped(self) -> None:
        """監控停止事件處理"""
        pass
    
    def on_progress_updated(self, progress: int, status: str) -> None:
        """
        任務進度更新事件處理
        
        Args:
            progress: 進度百分比
            status: 狀態訊息
        """
        self._progress_panel.set_progress(progress)
        self._progress_panel.set_status(status)
    
    def on_task_started(self, task_id: str, filename: str) -> None:
        """
        任務開始事件處理
        
        Args:
            task_id: 任務 ID
            filename: 檔案名稱
        """
        logger.info(f"開始處理任務: {filename}")
        self._log_group.append_info(f"正在處理: {filename}")
    
    def on_task_completed(self, task_id: str, result_path: str) -> None:
        """
        任務完成事件處理
        
        Args:
            task_id: 任務 ID
            result_path: 結果檔案路徑
        """
        logger.info(f"任務完成: {task_id}")
        if result_path:
            self._log_group.append_success(f"處理完成: {Path(result_path).name}")
        else:
            self._log_group.append_success(f"任務完成: {task_id}")
        
        # 更新佇列狀態顯示
        queue_size = self.task_queue.get_queue_size()
        if queue_size > 0:
            self._progress_panel.set_status(f"監控中... (佇列: {queue_size})")
        else:
            self._progress_panel.set_status("監控中...")
    
    def on_task_failed(self, task_id: str, error_message: str) -> None:
        """
        任務失敗事件處理
        
        Args:
            task_id: 任務 ID
            error_message: 錯誤訊息
        """
        logger.error(f"任務失敗: {task_id} - {error_message}")
        self._log_group.append_error(f"處理失敗: {error_message}")
        
        # 更新佇列狀態顯示
        queue_size = self.task_queue.get_queue_size()
        if queue_size > 0:
            self._progress_panel.set_status(f"監控中... (佇列: {queue_size})")
        else:
            self._progress_panel.set_status("監控中...")
    
    def on_worker_log(self, level: str, message: str) -> None:
        """
        工作者日誌事件處理
        
        Args:
            level: 日誌級別
            message: 日誌訊息
        """
        if level == "DEBUG":
            self._log_group.append_debug(message)
        elif level == "INFO":
            self._log_group.append_info(message)
        elif level == "WARNING":
            self._log_group.append_warning(message)
        elif level == "ERROR":
            self._log_group.append_error(message)
    
    def _validate_settings(self) -> bool:
        """
        驗證設定是否有效
        
        Returns:
            設定是否有效
        """
        errors = []
        
        # 檢查輸入資料夾
        if not self._input_folder_selector.path():
            errors.append("請選擇輸入資料夾")
        
        # 檢查輸出資料夾
        if not self._output_folder_selector.path():
            errors.append("請選擇輸出資料夾")
        
        # 檢查引擎設定
        if self._cloud_radio.isChecked():
            if not self._api_key_input.text():
                errors.append("請輸入 API Key")
        else:
            if not self._model_path_selector.path():
                errors.append("請選擇模型檔案")
        
        # 檢查備份資料夾（如果選擇移動）
        if self._postprocess_button_group.checkedId() == 2:
            if not self._backup_folder_selector.path():
                errors.append("請選擇備份資料夾")
        
        # 顯示錯誤
        if errors:
            for error in errors:
                self._log_group.append_error(error)
            return False
        
        return True
    
    def _set_settings_enabled(self, enabled: bool) -> None:
        """
        設定設定控制項是否啟用
        
        Args:
            enabled: 是否啟用
        """
        # 1. 先切換群組容器的啟用狀態（影響視覺灰化與防止交互）
        self._engine_group.setEnabled(enabled)
        self._folder_group.setEnabled(enabled)
        self._output_group.setEnabled(enabled)
        
        # 2. 逐個處理內部控制項的細節（解決 Bug1: 確保狀態恢復完整性）
        # 即使群組被禁用，明確設定子元件狀態可防止在重新啟用時出現邏輯不一致
        is_cloud = self._cloud_radio.isChecked()
        self._api_key_input.setEnabled(enabled and is_cloud)
        self._model_path_selector.set_enabled(enabled and not is_cloud)
        
        self._input_folder_selector.set_enabled(enabled)
        self._output_folder_selector.set_enabled(enabled)
        
        is_move = self._post_move_radio.isChecked()
        self._backup_folder_selector.set_enabled(enabled and is_move)
        
        # 其他單選按鈕
        self._cloud_radio.setEnabled(enabled)
        self._local_radio.setEnabled(enabled)
        self._pdf_radio.setEnabled(enabled)
        self._txt_radio.setEnabled(enabled)
        self._post_none_radio.setEnabled(enabled)
        self._post_delete_radio.setEnabled(enabled)
        self._post_move_radio.setEnabled(enabled)
    
    @property
    def is_monitoring(self) -> bool:
        """是否正在監控"""
        return self._is_monitoring
    
    @property
    def log_viewer(self):
        """取得日誌顯示器"""
        return self._log_group.log_viewer
    
    def closeEvent(self, event) -> None:
        """
        視窗關閉事件
        
        Args:
            event: 關閉事件
        """
        # 如果正在監控，先停止
        if self._is_monitoring:
            self.stop_monitoring()
        
        # 儲存設定
        self._save_settings()
        
        logger.info("應用程式關閉")
        
        event.accept()
