"""
llama.cpp 本地引擎模組

實作使用 llama.cpp 載入 GGUF 模型進行本地 OCR 辨識。
"""

import base64
import logging
import time
from pathlib import Path
from typing import Optional

from .base import BaseOCREngine, OCRResult

logger = logging.getLogger(__name__)


class LlamaCppEngine(BaseOCREngine):
    """llama.cpp 本地 GGUF 模型引擎"""
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,
        temperature: float = 0.1
    ):
        """
        初始化 llama.cpp 引擎
        
        Args:
            model_path: GGUF 模型檔案路徑
            n_ctx: 上下文長度
            n_gpu_layers: GPU 層數（-1 = 全部載入 GPU，0 = 僅 CPU）
            temperature: 生成溫度參數
        """
        self._model_path = Path(model_path)
        self._n_ctx = n_ctx
        self._n_gpu_layers = n_gpu_layers
        self._temperature = temperature
        self._model = None
        self._is_ready = False
    
    @property
    def engine_name(self) -> str:
        """取得引擎名稱"""
        model_name = self._model_path.name if self._model_path.exists() else "未知模型"
        return f"llama.cpp Local ({model_name})"
    
    def initialize(self) -> bool:
        """
        載入 GGUF 模型
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 檢查模型檔案是否存在
            if not self._model_path.exists():
                logger.error(f"模型檔案不存在: {self._model_path}")
                return False
            
            # 嘗試匯入 llama_cpp
            try:
                from llama_cpp import Llama
            except ImportError:
                logger.error(
                    "無法匯入 llama_cpp 模組，請確保已安裝 llama-cpp-python。"
                    "安裝指令: pip install llama-cpp-python"
                )
                return False
            
            # 載入模型
            logger.info(f"正在載入模型: {self._model_path}")
            logger.info(f"參數: n_ctx={self._n_ctx}, n_gpu_layers={self._n_gpu_layers}")
            
            self._model = Llama(
                model_path=str(self._model_path),
                n_ctx=self._n_ctx,
                n_gpu_layers=self._n_gpu_layers,
                verbose=False
            )
            
            self._is_ready = True
            logger.info("llama.cpp 引擎初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"llama.cpp 引擎初始化失敗: {e}")
            self._is_ready = False
            return False
    
    def recognize(self, image_path: Path) -> OCRResult:
        """
        使用本地模型進行 OCR 辨識
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            OCRResult: 辨識結果
        """
        start_time = time.time()
        
        try:
            # 檢查引擎是否就緒
            if not self._is_ready or self._model is None:
                return OCRResult(
                    text="",
                    error="模型未載入或引擎未初始化",
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
            image_base64 = self._encode_image(image_path)
            if image_base64 is None:
                return OCRResult(
                    text="",
                    error="無法讀取圖片檔案",
                    processing_time=time.time() - start_time
                )
            
            # 建構提示詞
            prompt = "請辨識這張圖片中的所有文字，直接輸出辨識結果，不要添加任何解釋或格式化："
            
            logger.debug(f"開始 OCR 辨識: {image_path.name}")
            
            # 呼叫模型（支援視覺模型的 llama.cpp）
            response = self._model.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                temperature=self._temperature
            )
            
            # 提取文字內容
            text = self._extract_text_from_response(response)
            
            processing_time = time.time() - start_time
            logger.info(f"OCR 辨識完成: {image_path.name}, 耗時: {processing_time:.2f}s")
            
            return OCRResult(
                text=text,
                processing_time=processing_time
            )
            
        except Exception as e:
            error_msg = f"OCR 辨識發生錯誤: {e}"
            if "chat_handler" in str(e).lower() or "vision" in str(e).lower():
                error_msg += " (提示：本地 OCR 需要支援視覺的模型與對應的 CLIP 模型，請確保您的 GGUF 模型支援視覺推論。)"
            logger.exception(error_msg)
            return OCRResult(
                text="",
                error=error_msg,
                processing_time=time.time() - start_time
            )
    
    def is_ready(self) -> bool:
        """檢查引擎是否就緒"""
        return self._is_ready and self._model is not None
    
    def cleanup(self) -> None:
        """清理資源"""
        if self._model is not None:
            try:
                del self._model
                logger.info("模型已釋放")
            except Exception as e:
                logger.warning(f"釋放模型時發生錯誤: {e}")
            finally:
                self._model = None
        
        self._is_ready = False
        logger.info("llama.cpp 引擎已清理")
    
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
        從模型回應中提取文字內容
        
        Args:
            response: 模型回應字典
            
        Returns:
            str: 提取的文字內容
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"解析模型回應失敗: {e}, 回應內容: {response}")
            return ""
    
    def __del__(self):
        """解構函數，確保資源被釋放"""
        self.cleanup()
