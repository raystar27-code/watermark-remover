# 水印去除器

使用 OCR 检测和 OpenCV 图像修复技术批量去除 NotebookLM 图片中的水印。

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
python watermark_remover/skill.py <图片文件夹路径> [--suffix _no_watermark]
```

## 示例

```bash
# 处理文件夹中的所有图片
python watermark_remover/skill.py /path/to/images

# 自定义输出文件后缀
python watermark_remover/skill.py /path/to/images --suffix _clean
```

## 工作原理

1. 扫描文件夹中的图片 (.png, .jpg, .jpeg, .webp)
2. 使用 Tesseract OCR 在右下角区域检测 "NotebookLM" 文字
3. 扩展文字边界框以覆盖 logo 和边框
4. 使用 OpenCV Telea 图像修复算法填充水印区域
5. 保存为 `<filename>_no_watermark.<ext>`

## 输出说明

- 原图保留
- 处理后的图片添加后缀（默认: `_no_watermark`）
- 示例: `image01.png` -> `image01_no_watermark.png`

## 测试

```bash
export TEST_IMAGE_PATH="/path/to/sample_image.png"
pytest tests/
```
