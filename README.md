# Smart OCR Folder Monitor

跨平台智慧 OCR 監控轉檔系統

## 功能特色

- **雙軌 OCR 引擎**：支援 GLM-OCR Cloud API 和本地 llama.cpp GGUF 模型
- **自動資料夾監控**：使用 watchdog 即時監控輸入資料夾
- **多種輸出格式**：支援 Searchable PDF 和純文字檔
- **後處理功能**：處理完成後可自動刪除或移動原始圖片
- **設定持久化**：所有設定自動儲存，重啟後還原
- **現代化介面**：採用 Windows 10/11 Fluent Design 風格

## 系統需求

- Python 3.10+
- 支援作業系統：Windows 10/11, macOS, Linux

## 安裝步驟

### 1. 複製專案
```bash
git clone https://github.com/your-repo/smart-ocr-monitor.git
cd smart-ocr-monitor
```

### 2. 建立虛擬環境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 準備依賴目錄
程式會自動建立以下目錄：
- Windows: `C:\OCR\models\`, `C:\OCR\bin\`, `C:\OCR\fonts\`
- macOS/Linux: `~/.ocr/models/`, `~/.ocr/bin/`, `~/.ocr/fonts/`

### 5. 執行程式
```bash
python main.py
```

## 使用說明

### GLM-OCR Cloud 模式
1. 選擇「GLM-OCR Cloud」選項
2. 輸入您的 API Key（會加密儲存）
3. 設定輸入/輸出資料夾
4. 點擊「啟動監控」

### Local LLM 模式
1. 選擇「Local LLM」選項
2. 指定 GGUF 模型路徑
3. 設定輸入/輸出資料夾
4. 點擊「啟動監控」

## 配置檔說明

配置檔位於 `config.json`，包含：
- OCR 引擎設定
- 資料夾路徑設定
- 輸出格式設定
- 後處理動作設定

## 支援的圖片格式

- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## 專案結構

```
smart-ocr-monitor/
├── main.py                 # 主程式入口
├── requirements.txt        # Python 依賴
├── config/                 # 配置管理模組
│   ├── manager.py         # 配置管理器
│   └── schema.py          # 配置結構定義
├── core/                   # 核心處理模組
│   ├── task.py            # 任務定義
│   ├── task_queue.py      # 任務佇列
│   └── task_worker.py     # 任務工作者
├── engines/                # OCR 引擎模組
│   ├── glm_ocr.py         # GLM-OCR Cloud API
│   └── llama_cpp_engine.py # 本地 LLM 引擎
├── converters/             # 轉換器模組
│   ├── pdf_converter.py   # PDF 轉換器
│   └── text_converter.py  # 文字轉換器
├── monitors/               # 監控模組
│   └── folder_monitor.py  # 資料夾監控
├── postprocess/            # 後處理模組
│   ├── delete_processor.py # 刪除處理器
│   └── move_processor.py  # 移動處理器
├── ui/                     # 使用者介面
│   ├── main_window.py     # 主視窗
│   ├── styles/            # 樣式定義
│   └── widgets/           # UI 元件
└── utils/                  # 工具模組
    ├── logger.py          # 日誌工具
    └── path_adapter.py    # 路徑適配器
```

## 授權

MIT License
