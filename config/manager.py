"""
配置管理器模組

提供配置的載入、儲存、驗證與 API Key 加密功能。
"""

import base64
import json
import logging
import sys
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Dict, Optional

from .schema import AppConfig

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    配置管理器類別

    負責應用程式配置的載入、儲存、驗證與 API Key 簡單加密。
    執行緒安全的單例模式實作。
    """

    _instance: Optional["ConfigManager"] = None
    _lock: Lock = Lock()

    def __new__(cls, config_path: Optional[Path] = None) -> "ConfigManager":
        """
        單例模式實作

        Args:
            config_path: 配置檔案路徑，預設為當前目錄下的 config.json

        Returns:
            ConfigManager 實例
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        初始化配置管理器

        Args:
            config_path: 配置檔案路徑，預設為當前目錄下的 config.json
        """
        if self._initialized:
            return

        self._config_path = config_path or Path("config.json")
        self._config: Optional[AppConfig] = None
        self._config_lock = RLock()
        self._initialized = True

        logger.info(f"ConfigManager 初始化，配置檔案路徑: {self._config_path}")

    @property
    def config(self) -> AppConfig:
        """
        取得當前配置

        Returns:
            AppConfig 配置物件
        """
        with self._config_lock:
            if self._config is None:
                self._config = self.load()
            return self._config

    @property
    def config_path(self) -> Path:
        """取得配置檔案路徑"""
        return self._config_path

    def load(self) -> AppConfig:
        """
        載入配置檔案

        如果配置檔案不存在，將建立預設配置並儲存。

        Returns:
            AppConfig 配置物件
        """
        with self._config_lock:
            try:
                if self._config_path.exists():
                    with open(self._config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    logger.info(f"成功載入配置檔案: {self._config_path}")

                    # 解密 API Key
                    if "ocr_engine" in data and "glm_cloud" in data["ocr_engine"]:
                        encrypted_key = data["ocr_engine"]["glm_cloud"].get("api_key", "")
                        if encrypted_key:
                            data["ocr_engine"]["glm_cloud"]["api_key"] = self.decrypt_api_key(
                                encrypted_key
                            )

                    self._config = AppConfig.from_dict(data)
                else:
                    logger.warning(f"配置檔案不存在，建立預設配置: {self._config_path}")
                    self._config = AppConfig()
                    self.save()

                return self._config

            except json.JSONDecodeError as e:
                logger.error(f"配置檔案 JSON 格式錯誤: {e}")
                logger.warning("使用預設配置")
                self._config = AppConfig()
                return self._config

            except Exception as e:
                logger.error(f"載入配置檔案時發生錯誤: {e}")
                logger.warning("使用預設配置")
                self._config = AppConfig()
                return self._config

    def save(self, config: Optional[AppConfig] = None) -> bool:
        """
        儲存配置到檔案

        Args:
            config: 要儲存的配置物件，如果為 None 則儲存當前配置

        Returns:
            bool: 儲存是否成功
        """
        with self._config_lock:
            try:
                config_to_save = config or self._config or AppConfig()

                # 轉換為字典
                data = config_to_save.to_dict()

                # 加密 API Key
                if "ocr_engine" in data and "glm_cloud" in data["ocr_engine"]:
                    plain_key = data["ocr_engine"]["glm_cloud"].get("api_key", "")
                    if plain_key:
                        data["ocr_engine"]["glm_cloud"]["api_key"] = self.encrypt_api_key(
                            plain_key
                        )

                # 確保目錄存在
                self._config_path.parent.mkdir(parents=True, exist_ok=True)

                # 寫入檔案
                with open(self._config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self._config = config_to_save
                logger.info(f"配置已儲存至: {self._config_path}")
                return True

            except Exception as e:
                logger.error(f"儲存配置時發生錯誤: {e}")
                return False

    def validate(self, config: Optional[AppConfig] = None) -> tuple[bool, list[str]]:
        """
        驗證配置的有效性

        Args:
            config: 要驗證的配置物件，如果為 None 則驗證當前配置

        Returns:
            tuple[bool, list[str]]: (是否有效, 錯誤訊息列表)
        """
        config_to_validate = config or self.config
        errors: list[str] = []

        # 驗證 OCR 引擎類型
        valid_engine_types = ["cloud", "local"]
        if config_to_validate.ocr_engine.type not in valid_engine_types:
            errors.append(
                f"無效的 OCR 引擎類型: {config_to_validate.ocr_engine.type}, "
                f"有效選項: {valid_engine_types}"
            )

        # 驗證雲端 API 配置
        if config_to_validate.ocr_engine.type == "cloud":
            glm_config = config_to_validate.ocr_engine.glm_cloud
            if not glm_config.api_key:
                errors.append("使用雲端 OCR 時，API Key 為必填欄位")
            if glm_config.timeout_seconds <= 0:
                errors.append("API 逾時時間必須大於 0")
            if glm_config.max_retries < 0:
                errors.append("最大重試次數不能為負數")

        # 驗證本地模型配置
        if config_to_validate.ocr_engine.type == "local":
            llama_config = config_to_validate.ocr_engine.llama_cpp
            if not llama_config.model_path:
                errors.append("使用本地 OCR 時，模型路徑為必填欄位")
            if llama_config.n_ctx <= 0:
                errors.append("上下文長度 (n_ctx) 必須大於 0")
            if not (0.0 <= llama_config.temperature <= 2.0):
                errors.append("溫度參數 (temperature) 必須在 0.0 到 2.0 之間")

        # 驗證監控資料夾
        monitor_config = config_to_validate.monitor
        if monitor_config.input_folder:
            input_path = Path(monitor_config.input_folder)
            if not input_path.exists():
                errors.append(f"輸入資料夾不存在: {monitor_config.input_folder}")
        else:
            errors.append("輸入資料夾路徑為必填欄位")

        if monitor_config.output_folder:
            output_path = Path(monitor_config.output_folder)
            if not output_path.exists():
                logger.warning(f"輸出資料夾不存在，將自動建立: {monitor_config.output_folder}")
        else:
            errors.append("輸出資料夾路徑為必填欄位")

        if monitor_config.debounce_seconds < 0:
            errors.append("防抖秒數不能為負數")

        # 驗證輸出格式
        valid_formats = ["pdf", "txt"]
        if config_to_validate.output.format not in valid_formats:
            errors.append(
                f"無效的輸出格式: {config_to_validate.output.format}, "
                f"有效選項: {valid_formats}"
            )

        # 驗證後處理動作
        valid_actions = ["none", "delete", "move"]
        if config_to_validate.postprocess.action not in valid_actions:
            errors.append(
                f"無效的後處理動作: {config_to_validate.postprocess.action}, "
                f"有效選項: {valid_actions}"
            )

        if (
            config_to_validate.postprocess.action == "move"
            and not config_to_validate.postprocess.move_destination
        ):
            errors.append("後處理動作為「移動」時，必須指定目標資料夾")

        # 驗證日誌級別
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if config_to_validate.logging.level not in valid_log_levels:
            errors.append(
                f"無效的日誌級別: {config_to_validate.logging.level}, "
                f"有效選項: {valid_log_levels}"
            )

        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"配置驗證失敗: {errors}")
        else:
            logger.debug("配置驗證通過")

        return is_valid, errors

    def get_default_config(self) -> AppConfig:
        """
        取得預設配置

        Returns:
            AppConfig 預設配置物件
        """
        return AppConfig()

    def reset_to_default(self) -> bool:
        """
        重置配置為預設值

        Returns:
            bool: 重置是否成功
        """
        logger.info("重置配置為預設值")
        self._config = AppConfig()
        return self.save()

    def update_config(self, **kwargs: Any) -> bool:
        """
        更新配置的部分欄位

        Args:
            **kwargs: 要更新的配置欄位，使用點號分隔巢狀欄位
                     例如: update_config(ocr_engine__type="local")

        Returns:
            bool: 更新是否成功
        """
        with self._config_lock:
            try:
                config_dict = self.config.to_dict()

                for key, value in kwargs.items():
                    # 支援巢狀更新，使用雙底線分隔
                    keys = key.split("__")
                    current = config_dict

                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]

                    current[keys[-1]] = value

                self._config = AppConfig.from_dict(config_dict)
                logger.info(f"配置已更新: {kwargs}")
                return True

            except Exception as e:
                logger.error(f"更新配置時發生錯誤: {e}")
                return False

    @staticmethod
    def encrypt_api_key(plain_key: str) -> str:
        """
        使用 Base64 編碼加密 API Key

        注意：這只是簡單的混淆，不是真正的加密。
        對於更高的安全需求，應使用 cryptography 套件。

        Args:
            plain_key: 明文 API Key

        Returns:
            str: 編碼後的 API Key
        """
        if not plain_key:
            return ""

        # 加入前綴以識別編碼格式
        encoded = base64.b64encode(plain_key.encode("utf-8")).decode("utf-8")
        return f"enc:{encoded}"

    @staticmethod
    def decrypt_api_key(encrypted_key: str) -> str:
        """
        解密 API Key

        Args:
            encrypted_key: 編碼後的 API Key

        Returns:
            str: 明文 API Key
        """
        if not encrypted_key:
            return ""

        # 檢查是否有編碼前綴
        if encrypted_key.startswith("enc:"):
            encoded = encrypted_key[4:]
            try:
                return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
            except Exception:
                logger.warning("API Key 解密失敗，返回原始值")
                return encrypted_key

        # 沒有前綴，可能是明文
        return encrypted_key

    @classmethod
    def reset_instance(cls) -> None:
        """
        重置單例實例（主要用於測試）
        """
        with cls._lock:
            cls._instance = None
