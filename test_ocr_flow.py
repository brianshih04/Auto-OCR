#!/usr/bin/env python3
"""
OCR 完整流程測試腳本

測試：放入圖片 → OCR → 輸出
"""

import sys
import shutil
import time
from pathlib import Path

# 確保 UTF-8 輸出
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from config import ConfigManager
from core import TaskQueue, TaskWorker, OCRTask
from engines import OCREngineFactory
from converters import ConverterFactory
from utils.path_adapter import PathAdapter


def test_full_flow():
    """測試完整的 OCR 流程"""
    print("=" * 60)
    print("OCR 完整流程測試")
    print("=" * 60)
    
    # 1. 載入配置
    print("\n[步驟 1] 載入配置...")
    config_manager = ConfigManager()
    config = config_manager.load()
    print(f"  - OCR 引擎類型: {config.ocr_engine.type}")
    print(f"  - 輸入資料夾: {config.monitor.input_folder}")
    print(f"  - 輸出資料夾: {config.monitor.output_folder}")
    print(f"  - 輸出格式: {config.output.format}")
    print(f"  - 後處理動作: {config.postprocess.action}")
    
    # 2. 初始化 OCR 引擎
    print("\n[步驟 2] 初始化 OCR 引擎...")
    engine = OCREngineFactory.create(config_manager)
    if not engine:
        print("  ✗ 建立 OCR 引擎失敗")
        return False
    
    if not engine.initialize():
        print("  ✗ 初始化 OCR 引擎失敗")
        return False
    
    print(f"  ✓ OCR 引擎已就緒: {engine.engine_name}")
    
    # 3. 準備測試圖片
    input_folder = Path(config.monitor.input_folder)
    output_folder = Path(config.monitor.output_folder)
    
    # 確保資料夾存在
    input_folder.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # 尋找測試圖片
    test_images = list(input_folder.glob("*.jpg")) + list(input_folder.glob("*.jpeg"))
    if not test_images:
        print(f"  ✗ 在 {input_folder} 中找不到測試圖片")
        return False
    
    test_image = test_images[0]
    print(f"\n[步驟 3] 使用測試圖片: {test_image.name}")
    
    # 4. 執行 OCR
    print("\n[步驟 4] 執行 OCR 識別...")
    result = engine.recognize(test_image)
    
    if not result.success:
        print(f"  ✗ OCR 失敗: {result.error}")
        return False
    
    print(f"  ✓ OCR 成功")
    print(f"  - 處理時間: {result.processing_time:.2f} 秒")
    print(f"  - 識別文字 (前200字):\n{result.text[:200]}...")
    
    # 5. 轉換輸出
    print("\n[步驟 5] 轉換輸出...")
    converter = ConverterFactory.create(config.output.format, config)
    if not converter:
        print(f"  ✗ 建立轉換器失敗: {config.output.format}")
        return False
    
    output_path = output_folder / f"{test_image.stem}.{config.output.format}"
    if converter.convert(result.text, output_path, test_image.stem):
        print(f"  ✓ 輸出已儲存: {output_path}")
    else:
        print(f"  ✗ 輸出失敗")
        return False
    
    # 6. 檢查輸出檔案
    print("\n[步驟 6] 驗證輸出檔案...")
    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"  ✓ 輸出檔案存在")
        print(f"  - 檔案大小: {file_size} bytes")
    else:
        print(f"  ✗ 輸出檔案不存在")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 完整流程測試成功！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_full_flow()
    sys.exit(0 if success else 1)
