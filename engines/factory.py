"""
OCR 引擎工廠模組

根據配置建立對應的 OCR 引擎實例。
"""

import logging
from typing import Optional, TYPE_CHECKING

from .base import BaseOCREngine
from .glm_ocr import GLMOCREngine
from .llama_cpp_engine import LlamaCppEngine

if TYPE_CHECKING:
    from config import ConfigManager

logger = logging.getLogger(__name__)


class OCREngineFactory:
    """OCR 引擎工廠"""
    
    @staticmethod
    def create(config_manager: "ConfigManager") -> Optional[BaseOCREngine]:
        """
        根據配置建立 OCR 引擎
        
        Args:
            config_manager: 配置管理器實例
            
        Returns:
            Optional[BaseOCREngine]: OCR 引擎實例，建立失敗時返回 None
        """
        try:
            config = config_manager.config
            engine_type = config.ocr_engine.type
            
            logger.info(f"正在建立 OCR 引擎，類型: {engine_type}")
            
            if engine_type == "cloud":
                return OCREngineFactory._create_cloud_engine(config_manager)
            
            elif engine_type == "local":
                return OCREngineFactory._create_local_engine(config_manager)
            
            else:
                logger.error(f"未知的 OCR 引擎類型: {engine_type}")
                return None
                
        except Exception as e:
            logger.error(f"建立 OCR 引擎時發生錯誤: {e}")
            return None
    
    @staticmethod
    def _create_cloud_engine(config_manager: "ConfigManager") -> Optional[GLMOCREngine]:
        """
        建立雲端 OCR 引擎
        
        Args:
            config_manager: 配置管理器實例
            
        Returns:
            Optional[GLMOCREngine]: GLM-OCR 引擎實例
        """
        config = config_manager.config
        glm_config = config.ocr_engine.glm_cloud
        
        # 取得 API Key（已解密）
        api_key = glm_config.api_key
        
        if not api_key:
            logger.error("雲端 OCR 需要 API Key，請在配置中設定")
            return None
        
        engine = GLMOCREngine(
            api_key=api_key,
            timeout=glm_config.timeout_seconds
        )
        
        logger.info("GLM-OCR 雲端引擎已建立")
        return engine
    
    @staticmethod
    def _create_local_engine(config_manager: "ConfigManager") -> Optional[LlamaCppEngine]:
        """
        建立本地 OCR 引擎
        
        Args:
            config_manager: 配置管理器實例
            
        Returns:
            Optional[LlamaCppEngine]: llama.cpp 引擎實例
        """
        config = config_manager.config
        llama_config = config.ocr_engine.llama_cpp
        
        model_path = llama_config.model_path
        
        if not model_path:
            logger.error("本地 OCR 需要指定模型路徑，請在配置中設定")
            return None
        
        engine = LlamaCppEngine(
            model_path=model_path,
            n_ctx=llama_config.n_ctx,
            n_gpu_layers=llama_config.n_gpu_layers,
            temperature=llama_config.temperature
        )
        
        logger.info(f"llama.cpp 本地引擎已建立，模型: {model_path}")
        return engine
