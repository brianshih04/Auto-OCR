"""
配置管理模組

提供應用程式配置的結構定義與管理功能。
"""

from .manager import ConfigManager
from .schema import (
    AppConfig,
    GLMCloudConfig,
    LlamaCppConfig,
    LoggingConfig,
    MonitorConfig,
    OCREngineConfig,
    OutputConfig,
    PDFSettingsConfig,
    PostProcessConfig,
    UIConfig,
    # 別名
    OCRConfig,
    FolderConfig,
    # 列舉
    OCREngineType,
    OutputFormat,
    PostAction,
    ThemeType,
    LogLevel,
)

__all__ = [
    # 管理器
    "ConfigManager",
    # 配置類別
    "AppConfig",
    "OCREngineConfig",
    "GLMCloudConfig",
    "LlamaCppConfig",
    "MonitorConfig",
    "OutputConfig",
    "PDFSettingsConfig",
    "PostProcessConfig",
    "UIConfig",
    "LoggingConfig",
    # 別名
    "OCRConfig",
    "FolderConfig",
    # 列舉
    "OCREngineType",
    "OutputFormat",
    "PostAction",
    "ThemeType",
    "LogLevel",
]
