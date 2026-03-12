#!/usr/bin/env python3
"""
資料夾監控測試腳本

測試 FolderMonitor 的檔案偵測功能
"""

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

#確保 UTF-8 輸出
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from PyQt6.QtCore import QCoreApplication, QTimer
from monitors import FolderMonitor
from config import ConfigManager


#全域變數
detected_files = []
errors = []
test_completed = False
monitor = None
app = None
watch_folder = None


def on_file_detected(file_path: str):
    """檔案偵測回調"""
    global detected_files
    print(f"  ✓ 偵測到新檔案: {file_path}")
    detected_files.append(file_path)


def on_error(error_msg: str):
    """錯誤回調"""
    global errors
    print(f"  ✗ 錯誤: {error_msg}")
    errors.append(error_msg)


def on_started():
    print("  ✓ 監控已啟動")


def on_stopped():
    print("  ✓ 監控已停止")


def add_test_file():
    """新增測試檔案"""
    global watch_folder
    
    print("\n[步驟 5] 模擬新增圖片檔案...")
    
    # 尋找現有的測試圖片
    test_images = list(watch_folder.glob("*.jpg")) + list(watch_folder.glob("*.jpeg"))
    
    if test_images:
        # 複製現有圖片作為新檔案
        source_image = test_images[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_image_path = watch_folder / f"test_{timestamp}.jpg"
        
        print(f"  - 複製 {source_image.name} -> {new_image_path.name}")
        shutil.copy2(source_image, new_image_path)
        print("  - 等待監控器偵測...")
    else:
        print("  ✗ 找不到測試圖片，跳過檔案偵測測試")
        cleanup_and_exit()


def cleanup_and_exit():
    """清理並退出"""
    global monitor, test_completed
    
    test_completed = True
    
    # 清理測試檔案
    print("\n[步驟 6] 清理測試檔案...")
    for f in watch_folder.glob("test_*.jpg"):
        f.unlink()
        print(f"  - 已刪除: {f.name}")
    
    # 停止監控
    print("\n[步驟 7] 停止監控...")
    if monitor:
        monitor.stop()
    
    # 退出應用程式
    QTimer.singleShot(500, lambda: app.quit())


def check_detection():
    """檢查是否偵測到檔案"""
    if detected_files:
        print(f"  ✓ 成功偵測到 {len(detected_files)} 個檔案")
        cleanup_and_exit()
    else:
        # 繼續等待
        pass


def test_folder_monitor():
    """測試資料夾監控功能"""
    global monitor, app, watch_folder
    
    print("=" * 60)
    print("資料夾監控測試")
    print("=" * 60)
    
    # 1. 載入配置
    print("\n[步驟 1] 載入配置...")
    config_manager = ConfigManager()
    config = config_manager.load()
    
    watch_folder = Path(config.monitor.input_folder)
    print(f"  - 監控資料夾: {watch_folder}")
    
    # 確保資料夾存在
    watch_folder.mkdir(parents=True, exist_ok=True)
    
    # 2. 建立 Qt 應用程式（監控器需要 Qt事件循環）
    print("\n[步驟 2] 初始化 Qt 應用程式...")
    app = QCoreApplication(sys.argv)
    
    # 3. 建立監控器
    print("\n[步驟 3] 建立資料夾監控器...")
    
    monitor = FolderMonitor(
        watch_path=str(watch_folder),
        debounce_delay=config.monitor.debounce_seconds
    )
    
    # 連接訊號
    monitor.file_detected.connect(on_file_detected)
    monitor.error_occurred.connect(on_error)
    monitor.started_monitoring.connect(on_started)
    monitor.stopped_monitoring.connect(on_stopped)
    
    # 4. 啟動監控
    print("\n[步驟 4] 啟動監控...")
    monitor.start()
    
    # 延遲新增測試檔案（等待監控器完全啟動）
    QTimer.singleShot(2000, add_test_file)
    
    # 定時檢查偵測結果
    check_timer = QTimer()
    check_timer.timeout.connect(check_detection)
    check_timer.start(1000)  # 每秒檢查一次
    
    # 設定超時（15秒後強制結束）
    QTimer.singleShot(15000, cleanup_and_exit)
    
    # 執行事件循環
    app.exec()
    
    # 停止定時器
    check_timer.stop()
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("測試結果")
    print("=" * 60)
    print(f"  - 偵測到的檔案數: {len(detected_files)}")
    print(f"  - 錯誤數: {len(errors)}")
    
    if detected_files:
        print("\n  偵測到的檔案:")
        for f in detected_files:
            print(f"    • {f}")
    
    if errors:
        print("\n  錯誤:")
        for e in errors:
            print(f"    • {e}")
    
    success = len(detected_files) > 0 and len(errors) == 0
    print("\n" + "=" * 60)
    if success:
        print("✓ 資料夾監控測試成功！")
    else:
        print("✗ 資料夾監控測試失敗")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = test_folder_monitor()
    sys.exit(0 if success else 1)
