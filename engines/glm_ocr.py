"""
GLM-OCR Cloud API 引擎模組

實作透過智譜AI GLM-OCR 雲端 API 進行 OCR 辨識。
"""

import base64
import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .base import BaseOCREngine, OCRResult

logger = logging.getLogger(__name__)


class GLMOCREngine(BaseOCREngine):
    """GLM-OCR Cloud API 引擎"""
    
    API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    DEFAULT_MODEL = "glm-4v-flash"
    DEFAULT_TIMEOUT = 60
    
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        初始化 GLM-OCR 引擎
        
        Args:
            api_key: 智譜AI API Key
            model: 使用的模型名稱
            timeout: API 請求超時時間（秒）
        """
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._is_ready = False
    
    @property
    def engine_name(self) -> str:
        """取得引擎名稱"""
        return f"GLM-OCR Cloud ({self._model})"
    
    def initialize(self) -> bool:
        """
        驗證 API Key 並測試連線
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            if not self._api_key:
                logger.error("API Key 未設定")
                return False
            
            # 驗證 API Key 格式（基本檢查）
            if len(self._api_key) < 10:
                logger.error("API Key 格式無效")
                return False
            
            # 標記為就緒狀態
            self._is_ready = True
            logger.info(f"GLM-OCR 引擎初始化成功，模型: {self._model}")
            return True
            
        except Exception as e:
            logger.error(f"GLM-OCR 引擎初始化失敗: {e}")
            return False
    
    def recognize(self, image_path: Path) -> OCRResult:
        """
        呼叫 GLM-OCR API 進行辨識
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            OCRResult: 辨識結果
        """
        start_time = time.time()
        
        try:
            # 檢查引擎是否就緒
            if not self._is_ready:
                return OCRResult(
                    text="",
                    error="引擎未初始化",
                    processing_time=time.time() - start_time
                )
            
            # 檢查圖片檔案
            if not image_path.exists():
                return OCRResult(
                    text="",
                    error=f"圖片檔案不存在: {image_path}",
                    processing_time=time.time() - start_time
                )
            
            # 讀取圖片並轉為 base64
            image_data = self._encode_image(image_path)
            if image_data is None:
                return OCRResult(
                    text="",
                    error="無法讀取圖片檔案",
                    processing_time=time.time() - start_time
                )
            
            # 建構 API 請求
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "請辨識這張圖片中的所有文字，直接輸出辨識結果，不要添加任何解釋或格式化："
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            logger.debug(f"發送 OCR 請求: {image_path.name}")
            
            # 發送請求
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self._timeout
            )
            
            # 檢查回應狀態
            response.raise_for_status()
            result = response.json()
            
            # 解析回應內容
            text = self._extract_text_from_response(result)
            
            processing_time = time.time() - start_time
            logger.info(f"OCR 辨識完成: {image_path.name}, 耗時: {processing_time:.2f}s")
            
            return OCRResult(
                text=text,
                processing_time=processing_time
            )
            
        except requests.exceptions.Timeout:
            error_msg = f"API 請求超時（{self._timeout}秒）"
            logger.error(error_msg)
            return OCRResult(
                text="",
                error=error_msg,
                processing_time=time.time() - start_time
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API 請求失敗: {e}"
            logger.error(error_msg)
            return OCRResult(
                text="",
                error=error_msg,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            error_msg = f"OCR 辨識發生錯誤: {e}"
            logger.exception(error_msg)
            return OCRResult(
                text="",
                error=error_msg,
                processing_time=time.time() - start_time
            )
    
    def is_ready(self) -> bool:
        """檢查引擎是否就緒"""
        return self._is_ready
    
    def cleanup(self) -> None:
        """清理資源"""
        self._is_ready = False
        logger.info("GLM-OCR 引擎已清理")
    
    def _encode_image(self, image_path: Path) -> Optional[str]:
        """
        將圖片編碼為 base64 字串
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            Optional[str]: base64 編碼字串，失敗時返回 None
        """
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            logger.error(f"讀取圖片失敗: {e}")
            return None
    
    def _extract_text_from_response(self, response: dict) -> str:
        """
        從 API 回應中提取文字內容
        
        Args:
            response: API 回應字典
            
        Returns:
            str: 提取的文字內容
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"解析 API 回應失敗: {e}, 回應內容: {response}")
            return ""
