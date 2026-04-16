# 水印去除器

使用 OCR 检测和 OpenCV 图像修复技术批量去除 NotebookLM 图片或 PDF 中的水印。支持本地文件和 Google Drive。

[English Version](README.md)

## 安装

```bash
pip install -r watermark_remover/requirements.txt
```

需要安装 Tesseract OCR：
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载

## Google Drive 配置（可选）

1. 进入 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 **Google Drive API**
4. 进入 **APIs & Services** → **Credentials**
5. 点击 **Create Credentials** → **OAuth client ID**
6. Application type 选择: **Desktop app**
7. 下载 JSON 文件并重命名为 `credentials.json`
8. 将 `credentials.json` 放到 `watermark_remover/` 目录下

首次运行时会打开浏览器进行 OAuth 授权。

## 使用方法

```bash
# 本地模式（处理本地文件夹中的文件）
python watermark_remover/skill.py /path/to/folder --source-type local

# Google Drive 模式（从 GD 下载，处理后保存到本地）
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "你的GD文件夹ID" \
  --output local

# Google Drive 模式（从 GD 下载，处理后上传回 GD）
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "你的GD文件夹ID" \
  --gd-output "你的GD输出文件夹ID" \
  --output google-drive
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--suffix` | 输出文件后缀（默认: `_no_watermark`） |
| `--source-type` | 数据源类型: `local` 或 `google-drive` |
| `--gd-source` | Google Drive 文件夹 ID（包含要处理的 PDF） |
| `--gd-output` | Google Drive 输出文件夹 ID（默认: 与 `--gd-source` 相同） |
| `--output` | 输出位置: `local` 或 `google-drive` |
| `--cleanup` | 上传后删除本地临时文件 |

## 支持格式

- **图片**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **PDF**: `.pdf`（每页转换为图片后处理）

## 示例

```bash
# 处理本地文件夹
python watermark_remover/skill.py /path/to/images --source-type local

# 自定义输出后缀
python watermark_remover/skill.py /path/to/images --suffix _clean

# 从 Google Drive 处理 PDF 并保存到本地
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --output local

# 从 GD 处理并上传回 GD
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --gd-output "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --output google-drive
```

## 工作原理

1. 扫描文件夹中的图片和 PDF
2. **对于图片**：直接处理每张图片
3. **对于 PDF**：将每页转换为图片（300 DPI）后处理
4. 使用 Tesseract OCR 在右下角区域检测 "NotebookLM" 文字
5. 扩展文字边界框以覆盖 logo 和边框
6. 使用 OpenCV Telea 图像修复算法填充水印区域
7. 保存为带后缀的文件（默认: `_no_watermark`）

## 输出说明

- 原文件保留
- **图片**: `image01.png` -> `image01_no_watermark.png`
- **PDF**: 创建 `<filename>_images/` 文件夹，包含：
  - `filename_page_001_no_watermark.png`
  - `filename_page_002_no_watermark.png`
  - ...
- **Google Drive 输出**: 结果会以文件夹形式上传到指定的 GD 文件夹

## 测试

```bash
# 测试图片处理
export TEST_IMAGE_PATH="/path/to/sample_image.png"
pytest tests/

# 测试 PDF 处理（可选）
# 将 PDF 文件放入文件夹后运行：
python watermark_remover/skill.py /path/to/pdf_folder --source-type local
```