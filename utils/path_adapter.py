"""
跨平台路徑適配器模組

提供跨平台的系統路徑解析功能。
"""

import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PathAdapter:
    """
    跨平台路徑適配器

    根據作業系統解析對應的系統路徑：
    - Windows: C:\\OCR\\
    - macOS/Linux: ~/.ocr/
    """

    # Windows 系統目錄前綴
    WINDOWS_BASE_DIR = Path("C:/OCR")

    # Unix 系統目錄名稱
    UNIX_BASE_DIR_NAME = ".ocr"

    @staticmethod
    def _is_windows() -> bool:
        """檢查是否為 Windows 系統"""
        return sys.platform == "win32"

    @staticmethod
    def _get_base_dir() -> Path:
        """
        取得基礎目錄路徑

        Returns:
            Path: 基礎目錄路徑
        """
        if PathAdapter._is_windows():
            return PathAdapter.WINDOWS_BASE_DIR
        else:
            return Path.home() / PathAdapter.UNIX_BASE_DIR_NAME

    @staticmethod
    def get_models_path() -> Path:
        """
        取得模型目錄路徑

        - Windows: C:\\OCR\\models\\
        - macOS/Linux: ~/.ocr/models/

        Returns:
            Path: 模型目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "models"

    @staticmethod
    def get_binaries_path() -> Path:
        """
        取得執行檔目錄路徑

        - Windows: C:\\OCR\\bin\\
        - macOS/Linux: ~/.ocr/bin/

        Returns:
            Path: 執行檔目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "bin"

    @staticmethod
    def get_fonts_path() -> Path:
        """
        取得字型目錄路徑

        - Windows: C:\\OCR\\fonts\\
        - macOS/Linux: ~/.ocr/fonts/

        Returns:
            Path: 字型目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "fonts"

    @staticmethod
    def get_logs_path() -> Path:
        """
        取得日誌目錄路徑

        - Windows: C:\\OCR\\logs\\
        - macOS/Linux: ~/.ocr/logs/

        Returns:
            Path: 日誌目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "logs"

    @staticmethod
    def get_config_path() -> Path:
        """
        取得配置目錄路徑

        - Windows: C:\\OCR\\config\\
        - macOS/Linux: ~/.ocr/config/

        Returns:
            Path: 配置目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "config"

    @staticmethod
    def get_cache_path() -> Path:
        """
        取得快取目錄路徑

        - Windows: C:\\OCR\\cache\\
        - macOS/Linux: ~/.ocr/cache/

        Returns:
            Path: 快取目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "cache"

    @staticmethod
    def get_temp_path() -> Path:
        """
        取得暫存目錄路徑

        - Windows: C:\\OCR\\temp\\
        - macOS/Linux: ~/.ocr/temp/

        Returns:
            Path: 暫存目錄路徑
        """
        base = PathAdapter._get_base_dir()
        return base / "temp"

    @staticmethod
    def get_default_font_path() -> Optional[Path]:
        """
        取得預設中文字型路徑

        嘗試在字型目錄中尋找可用的中文字型。

        Returns:
            Optional[Path]: 字型路徑，如果找不到則返回 None
        """
        fonts_dir = PathAdapter.get_fonts_path()

        # 支援的中文字型列表（按優先順序）
        font_names = [
            "NotoSansCJK-Regular.ttc",
            "NotoSansSC-Regular.otf",
            "SourceHanSansSC-Regular.otf",
            "Microsoft YaHei.ttf",
            "SimHei.ttf",
            "msyh.ttc",  # 微軟正黑體
            "PingFang.ttc",  # 蘋方字型 (macOS)
        ]

        for font_name in font_names:
            font_path = fonts_dir / font_name
            if font_path.exists():
                logger.debug(f"找到預設字型: {font_path}")
                return font_path

        # 嘗試在系統字型目錄中尋找
        system_font_paths = PathAdapter._get_system_font_paths()
        for sys_font_dir in system_font_paths:
            for font_name in font_names:
                font_path = sys_font_dir / font_name
                if font_path.exists():
                    logger.debug(f"找到系統字型: {font_path}")
                    return font_path

        logger.warning("找不到預設中文字型")
        return None

    @staticmethod
    def _get_system_font_paths() -> list[Path]:
        """
        取得系統字型目錄列表

        Returns:
            list[Path]: 系統字型目錄列表
        """
        if PathAdapter._is_windows():
            return [
                Path("C:/Windows/Fonts"),
                Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
            ]
        elif sys.platform == "darwin":  # macOS
            return [
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ]
        else:  # Linux
            return [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / ".local" / "share" / "fonts",
            ]

    @staticmethod
    def ensure_directories() -> None:
        """
        確保所有必要的系統目錄存在

        建立以下目錄：
        - models: 模型檔案目錄
        - bin: 執行檔目錄
        - fonts: 字型目錄
        - logs: 日誌目錄
        - config: 配置目錄
        - cache: 快取目錄
        - temp: 暫存目錄
        """
        directories = [
            PathAdapter.get_models_path(),
            PathAdapter.get_binaries_path(),
            PathAdapter.get_fonts_path(),
            PathAdapter.get_logs_path(),
            PathAdapter.get_config_path(),
            PathAdapter.get_cache_path(),
            PathAdapter.get_temp_path(),
        ]

        for directory in directories:
            try:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    logger.info(f"已建立目錄: {directory}")
                else:
                    logger.debug(f"目錄已存在: {directory}")
            except PermissionError:
                logger.error(f"無法建立目錄 (權限不足): {directory}")
            except Exception as e:
                logger.error(f"建立目錄時發生錯誤: {directory}, 錯誤: {e}")

    @staticmethod
    def get_platform_info() -> dict[str, str]:
        """
        取得平台資訊

        Returns:
            dict[str, str]: 平台資訊字典
        """
        return {
            "platform": sys.platform,
            "base_dir": str(PathAdapter._get_base_dir()),
            "models_dir": str(PathAdapter.get_models_path()),
            "binaries_dir": str(PathAdapter.get_binaries_path()),
            "fonts_dir": str(PathAdapter.get_fonts_path()),
            "logs_dir": str(PathAdapter.get_logs_path()),
            "config_dir": str(PathAdapter.get_config_path()),
        }

    @staticmethod
    def resolve_path(path_str: str) -> Path:
        """
        解析路徑字串

        支援以下特殊路徑前綴：
        - $MODELS: 模型目錄
        - $BIN: 執行檔目錄
        - $FONTS: 字型目錄
        - $LOGS: 日誌目錄
        - $CONFIG: 配置目錄
        - $CACHE: 快取目錄
        - $TEMP: 暫存目錄
        - $HOME: 使用者主目錄

        Args:
            path_str: 路徑字串

        Returns:
            Path: 解析後的路徑
        """
        if not path_str:
            return Path("")

        path_mappings = {
            "$MODELS": PathAdapter.get_models_path(),
            "$BIN": PathAdapter.get_binaries_path(),
            "$FONTS": PathAdapter.get_fonts_path(),
            "$LOGS": PathAdapter.get_logs_path(),
            "$CONFIG": PathAdapter.get_config_path(),
            "$CACHE": PathAdapter.get_cache_path(),
            "$TEMP": PathAdapter.get_temp_path(),
            "$HOME": Path.home(),
        }

        for prefix, resolved_path in path_mappings.items():
            if path_str.startswith(prefix):
                remaining = path_str[len(prefix) :].lstrip("/\\")
                return resolved_path / remaining

        return Path(path_str)


# 為了向後相容，提供別名
PathResolver = PathAdapter
