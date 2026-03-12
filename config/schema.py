"""
配置結構定義模組

使用 dataclass 定義應用程式配置的資料結構。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class OCREngineType(str, Enum):
    """OCR 引擎類型"""
    CLOUD = "cloud"
    LOCAL = "local"


class OutputFormat(str, Enum):
    """輸出格式"""
    PDF = "pdf"
    TXT = "txt"


class PostAction(str, Enum):
    """後處理動作"""
    NONE = "none"
    DELETE = "delete"
    MOVE = "move"


class ThemeType(str, Enum):
    """UI 主題"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class LogLevel(str, Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class GLMCloudConfig:
    """GLM-OCR 雲端 API 配置"""
    api_key: str = ""
    endpoint: str = "https://api.glm-ocr.example.com/v1/recognize"
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class LlamaCppConfig:
    """llama.cpp 本地模型配置"""
    model_path: str = ""
    n_ctx: int = 4096
    n_gpu_layers: int = 0
    temperature: float = 0.1


@dataclass
class OCREngineConfig:
    """OCR 引擎配置"""
    type: str = "cloud"
    glm_cloud: GLMCloudConfig = field(default_factory=GLMCloudConfig)
    llama_cpp: LlamaCppConfig = field(default_factory=LlamaCppConfig)


@dataclass
class MonitorConfig:
    """檔案監控配置"""
    input_folder: str = ""
    output_folder: str = ""
    archive_folder: str = ""
    supported_formats: List[str] = field(
        default_factory=lambda: ["jpeg", "jpg", "bmp", "tiff", "tif", "png"]
    )
    recursive: bool = False
    debounce_seconds: float = 2.0


@dataclass
class PDFSettingsConfig:
    """PDF 輸出設定"""
    font_path: str = ""
    font_size: int = 12
    embed_text_layer: bool = True


@dataclass
class OutputConfig:
    """輸出配置"""
    format: str = "pdf"
    formats: List[str] = field(default_factory=lambda: ["pdf", "txt"])
    naming_rule: str = "original_name"
    pdf_settings: PDFSettingsConfig = field(default_factory=PDFSettingsConfig)
    post_action: str = "move"


@dataclass
class PostProcessConfig:
    """後處理配置"""
    action: str = "none"
    move_destination: str = ""
    confirm_before_delete: bool = True


@dataclass
class UIConfig:
    """使用者介面配置"""
    theme: str = "system"
    language: str = "zh-TW"
    minimize_to_tray: bool = True
    show_notifications: bool = True


@dataclass
class LoggingConfig:
    """日誌配置"""
    level: str = "INFO"
    log_to_file: bool = True
    file_path: str = ""
    max_log_size_mb: int = 10
    backup_count: int = 5


@dataclass
class AppConfig:
    """應用程式主配置"""
    version: str = "1.0.0"
    ocr_engine: OCREngineConfig = field(default_factory=OCREngineConfig)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    postprocess: PostProcessConfig = field(default_factory=PostProcessConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def to_dict(self) -> dict:
        """將配置轉換為字典"""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """從字典建立配置物件"""
        # 處理巢狀 dataclass
        ocr_data = data.get("ocr_engine", {})
        glm_cloud_data = ocr_data.get("glm_cloud", {})
        llama_cpp_data = ocr_data.get("llama_cpp", {})

        monitor_data = data.get("monitor", {})
        output_data = data.get("output", {})
        pdf_settings_data = output_data.get("pdf_settings", {})
        postprocess_data = data.get("postprocess", {})
        ui_data = data.get("ui", {})
        logging_data = data.get("logging", {})

        return cls(
            version=data.get("version", "1.0.0"),
            ocr_engine=OCREngineConfig(
                type=ocr_data.get("type", "cloud"),
                glm_cloud=GLMCloudConfig(
                    api_key=glm_cloud_data.get("api_key", ""),
                    endpoint=glm_cloud_data.get(
                        "endpoint", "https://api.glm-ocr.example.com/v1/recognize"
                    ),
                    timeout_seconds=glm_cloud_data.get("timeout_seconds", 30),
                    max_retries=glm_cloud_data.get("max_retries", 3),
                ),
                llama_cpp=LlamaCppConfig(
                    model_path=llama_cpp_data.get("model_path", ""),
                    n_ctx=llama_cpp_data.get("n_ctx", 4096),
                    n_gpu_layers=llama_cpp_data.get("n_gpu_layers", 0),
                    temperature=llama_cpp_data.get("temperature", 0.1),
                ),
            ),
            monitor=MonitorConfig(
                input_folder=monitor_data.get("input_folder", ""),
                output_folder=monitor_data.get("output_folder", ""),
                archive_folder=monitor_data.get("archive_folder", ""),
                supported_formats=monitor_data.get(
                    "supported_formats", ["jpeg", "jpg", "bmp", "tiff", "tif", "png"]
                ),
                recursive=monitor_data.get("recursive", False),
                debounce_seconds=monitor_data.get("debounce_seconds", 2.0),
            ),
            output=OutputConfig(
                format=output_data.get("format", "pdf"),
                formats=output_data.get("formats", ["pdf", "txt"]),
                naming_rule=output_data.get("naming_rule", "original_name"),
                pdf_settings=PDFSettingsConfig(
                    font_path=pdf_settings_data.get("font_path", ""),
                    font_size=pdf_settings_data.get("font_size", 12),
                    embed_text_layer=pdf_settings_data.get("embed_text_layer", True),
                ),
                post_action=output_data.get("post_action", "move"),
            ),
            postprocess=PostProcessConfig(
                action=postprocess_data.get("action", "none"),
                move_destination=postprocess_data.get("move_destination", ""),
                confirm_before_delete=postprocess_data.get("confirm_before_delete", True),
            ),
            ui=UIConfig(
                theme=ui_data.get("theme", "system"),
                language=ui_data.get("language", "zh-TW"),
                minimize_to_tray=ui_data.get("minimize_to_tray", True),
                show_notifications=ui_data.get("show_notifications", True),
            ),
            logging=LoggingConfig(
                level=logging_data.get("level", "INFO"),
                log_to_file=logging_data.get("log_to_file", True),
                file_path=logging_data.get("file_path", ""),
                max_log_size_mb=logging_data.get("max_log_size_mb", 10),
                backup_count=logging_data.get("backup_count", 5),
            ),
        )


# 為了向後相容，提供別名
OCRConfig = OCREngineConfig
FolderConfig = MonitorConfig
