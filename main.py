#!/usr/bin/env python3
"""
Auto-OCR 主程式入口

跨平台智慧 OCR 監控轉檔系統
"""

import logging
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ConfigManager
from ui import MainWindow
from ui.styles import FLUENT_STYLE
from utils import PathAdapter, setup_logging


def check_dependencies() -> bool:
    """
    檢查必要的依賴套件是否已安裝

    Returns:
        bool: 所有依賴是否都已安裝
    """
    logger = logging.getLogger("AutoOCR")
    missing_deps = []

    required_packages = [
        ("PyQt6", "PyQt6"),
        ("watchdog", "watchdog"),
        ("PIL", "Pillow"),
        ("reportlab", "reportlab"),
        ("fitz", "PyMuPDF"),
        ("requests", "requests"),
    ]

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append(package_name)

    if missing_deps:
        logger.warning(f"缺少以下依賴套件: {', '.join(missing_deps)}")
        logger.warning("請執行: pip install -r requirements.txt")
        return False

    logger.debug("所有依賴套件檢查通過")
    return True


def initialize_app() -> bool:
    """
    初始化應用程式

    Returns:
        bool: 初始化是否成功
    """
    logger = logging.getLogger("AutoOCR")
    logger.info("正在初始化 Auto-OCR...")

    # 確保系統目錄存在
    try:
        PathAdapter.ensure_directories()
        logger.info("系統目錄初始化完成")
    except Exception as e:
        logger.error(f"建立系統目錄時發生錯誤: {e}")
        return False

    # 載入配置
    try:
        config_manager = ConfigManager()
        config = config_manager.load()
        logger.info(f"配置載入完成 (版本: {config.version})")

        # 驗證配置
        is_valid, errors = config_manager.validate()
        if not is_valid:
            logger.warning("配置驗證發現以下問題:")
            for error in errors:
                logger.warning(f"  - {error}")
            logger.warning("部分功能可能無法正常運作，請檢查配置設定")
        else:
            logger.debug("配置驗證通過")

    except Exception as e:
        logger.error(f"載入配置時發生錯誤: {e}")
        return False

    logger.info("應用程式初始化完成")
    return True


def main() -> int:
    """
    應用程式主入口

    Returns:
        int: 結束代碼 (0 表示成功)
    """
    # 初始化日誌系統
    logger = setup_logging(
        level="INFO",
        log_to_file=True,
        max_log_size_mb=10,
        backup_count=5,
    )

    logger.info("=" * 50)
    logger.info("Auto-OCR 跨平台智慧 OCR 監控轉檔系統")
    logger.info("=" * 50)

    # 顯示平台資訊
    platform_info = PathAdapter.get_platform_info()
    logger.info(f"作業系統: {platform_info['platform']}")
    logger.info(f"基礎目錄: {platform_info['base_dir']}")

    # 檢查依賴
    if not check_dependencies():
        logger.error("依賴檢查失敗，請安裝缺少的套件")
        return 1

    # 初始化應用程式
    if not initialize_app():
        logger.error("應用程式初始化失敗")
        return 1

    # 啟動 PyQt6 UI
    try:
        from PyQt6.QtWidgets import QApplication
        
        # 建立 Qt 應用程式
        app = QApplication(sys.argv)
        app.setApplicationName("Auto-OCR")
        app.setApplicationDisplayName("Smart OCR Folder Monitor")
        
        # 套用 Fluent Design 樣式
        app.setStyleSheet(FLUENT_STYLE)
        
        # 建立並顯示主視窗
        config_manager = ConfigManager()
        window = MainWindow(config_manager)
        window.show()
        
        logger.info("UI 已啟動")
        logger.info("應用程式準備就緒")
        
        # 執行 Qt 事件循環
        return app.exec()
        
    except ImportError as e:
        logger.error(f"無法載入 PyQt6: {e}")
        logger.error("請執行: pip install PyQt6")
        return 1
    except Exception as e:
        logger.error(f"啟動 UI 時發生錯誤: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
