"""
日誌工具模組

提供可配置的日誌系統，支援檔案與控制台輸出。
"""

import logging
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# 執行緒鎖，確保日誌初始化的執行緒安全
_logger_lock = threading.Lock()
_initialized_loggers: dict[str, logging.Logger] = {}


class ColoredFormatter(logging.Formatter):
    """
    彩色日誌格式化器

    為控制台輸出添加顏色，便於區分不同級別的日誌。
    """

    # ANSI 顏色代碼
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 綠色
        "WARNING": "\033[33m",  # 黃色
        "ERROR": "\033[31m",  # 紅色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄"""
        # 儲存原始格式
        original_levelname = record.levelname

        # 添加顏色
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        # 格式化
        result = super().format(record)

        # 恢復原始格式
        record.levelname = original_levelname

        return result


class LoggerManager:
    """
    日誌管理器

    提供日誌系統的初始化與配置功能。
    """

    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def setup_logger(
        name: str = "AutoOCR",
        level: str = "INFO",
        log_to_file: bool = True,
        log_file_path: Optional[Path] = None,
        max_log_size_mb: int = 10,
        backup_count: int = 5,
        console_output: bool = True,
    ) -> logging.Logger:
        """
        設定並返回日誌記錄器

        Args:
            name: 日誌記錄器名稱
            level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: 是否輸出到檔案
            log_file_path: 日誌檔案路徑，如果為 None 則使用預設路徑
            max_log_size_mb: 單個日誌檔案最大大小 (MB)
            backup_count: 保留的備份日誌檔案數量
            console_output: 是否輸出到控制台

        Returns:
            logging.Logger: 配置好的日誌記錄器
        """
        with _logger_lock:
            # 如果已經初始化過，直接返回
            if name in _initialized_loggers:
                return _initialized_loggers[name]

            # 建立日誌記錄器
            logger = logging.getLogger(name)

            # 設定日誌級別
            log_level = getattr(logging, level.upper(), logging.INFO)
            logger.setLevel(log_level)

            # 清除現有的處理器
            logger.handlers.clear()

            # 控制台處理器
            if console_output:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(log_level)

                # 使用彩色格式化器
                colored_formatter = ColoredFormatter(
                    LoggerManager.DEFAULT_FORMAT,
                    datefmt=LoggerManager.DEFAULT_DATE_FORMAT,
                )
                console_handler.setFormatter(colored_formatter)
                logger.addHandler(console_handler)

            # 檔案處理器
            if log_to_file:
                # 確定日誌檔案路徑
                if log_file_path is None:
                    from .path_adapter import PathAdapter

                    log_dir = PathAdapter.get_logs_path()
                    log_dir.mkdir(parents=True, exist_ok=True)
                    log_file_path = log_dir / f"{name.lower()}.log"
                else:
                    log_file_path = Path(log_file_path)
                    log_file_path.parent.mkdir(parents=True, exist_ok=True)

                # 建立滾動檔案處理器
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=max_log_size_mb * 1024 * 1024,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
                file_handler.setLevel(log_level)

                # 檔案使用標準格式化器（不包含顏色）
                file_formatter = logging.Formatter(
                    LoggerManager.DEFAULT_FORMAT,
                    datefmt=LoggerManager.DEFAULT_DATE_FORMAT,
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

            # 防止日誌傳播到根記錄器
            logger.propagate = False

            # 記錄已初始化的日誌記錄器
            _initialized_loggers[name] = logger

            logger.debug(f"日誌系統已初始化: {name}, 級別: {level}")

            return logger

    @staticmethod
    def get_logger(name: str = "AutoOCR") -> logging.Logger:
        """
        取得日誌記錄器

        如果日誌記錄器尚未初始化，將使用預設配置進行初始化。

        Args:
            name: 日誌記錄器名稱

        Returns:
            logging.Logger: 日誌記錄器
        """
        with _logger_lock:
            if name in _initialized_loggers:
                return _initialized_loggers[name]

            # 使用預設配置初始化
            return LoggerManager.setup_logger(name=name)

    @staticmethod
    def update_level(name: str, level: str) -> bool:
        """
        更新日誌級別

        Args:
            name: 日誌記錄器名稱
            level: 新的日誌級別

        Returns:
            bool: 更新是否成功
        """
        with _logger_lock:
            if name not in _initialized_loggers:
                return False

            logger = _initialized_loggers[name]
            log_level = getattr(logging, level.upper(), None)

            if log_level is None:
                return False

            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)

            return True

    @staticmethod
    def shutdown() -> None:
        """
        關閉所有日誌處理器
        """
        with _logger_lock:
            for name, logger in _initialized_loggers.items():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)

            _initialized_loggers.clear()


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_file_path: Optional[str] = None,
    max_log_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """
    便捷函數：設定應用程式日誌

    Args:
        level: 日誌級別
        log_to_file: 是否輸出到檔案
        log_file_path: 日誌檔案路徑
        max_log_size_mb: 單個日誌檔案最大大小 (MB)
        backup_count: 保留的備份日誌檔案數量

    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    return LoggerManager.setup_logger(
        name="AutoOCR",
        level=level,
        log_to_file=log_to_file,
        log_file_path=Path(log_file_path) if log_file_path else None,
        max_log_size_mb=max_log_size_mb,
        backup_count=backup_count,
    )


def get_logger(module_name: str = "AutoOCR") -> logging.Logger:
    """
    便捷函數：取得模組日誌記錄器

    Args:
        module_name: 模組名稱

    Returns:
        logging.Logger: 日誌記錄器
    """
    # 確保主日誌記錄器已初始化
    if "AutoOCR" not in _initialized_loggers:
        LoggerManager.setup_logger()

    # 返回帶有模組名稱的子記錄器
    return logging.getLogger(f"AutoOCR.{module_name}")
