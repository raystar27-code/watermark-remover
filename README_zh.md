# 水印去除器

使用 OCR 检测和 OpenCV 图像修复技术批量去除 NotebookLM 图片或 PDF 中的水印。

[English Version](README.md)

## 安装

```bash
pip install -r watermark_remover/requirements.txt
```

需要安装 Tesseract OCR：
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载

## 使用方法

```bash
python watermark_remover/skill.py <文件夹路径> [--suffix _no_watermark]
```

## 支持格式

- **图片**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **PDF**: `.pdf`（每页转换为图片后处理）

## 示例

```bash
# 处理文件夹中的所有图片和 PDF
python watermark_remover/skill.py /path/to/images

# 自定义输出文件后缀
python watermark_remover/skill.py /path/to/images --suffix _clean
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
  - `原文件名_page_001_no_watermark.png`
  - `原文件名_page_002_no_watermark.png`
  - ...

## 测试

```bash
# 测试图片处理
export TEST_IMAGE_PATH="/path/to/sample_image.png"
pytest tests/

# 测试 PDF 处理（可选）
# 将 PDF 文件放入文件夹后运行：
python watermark_remover/skill.py /path/to/pdf_folder
```
