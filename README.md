# Watermark Remover

Remove NotebookLM watermarks from images or PDFs using OCR detection and OpenCV inpainting.

[中文说明](README_zh.md)

## Installation

```bash
pip install -r watermark_remover/requirements.txt
```

Requires Tesseract OCR to be installed:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Usage

```bash
python watermark_remover/skill.py <folder_path> [--suffix _no_watermark]
```

## Supported Formats

- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **PDF**: `.pdf` (each page is converted to image, then processed)

## Examples

```bash
# Process all images and PDFs in a folder
python watermark_remover/skill.py /path/to/images

# Custom output suffix
python watermark_remover/skill.py /path/to/images --suffix _clean
```

## How It Works

1. Scans folder for images and PDFs
2. **For images**: Directly process each image
3. **For PDFs**: Convert each page to image (300 DPI), then process
4. Uses Tesseract OCR to detect "NotebookLM" text in bottom-right region
5. Expands text bounding box to cover logo and frame
6. Applies OpenCV Telea inpainting to fill watermark area
7. Saves result with suffix (default: `_no_watermark`)

## Output

- Original files are preserved
- **Images**: `image01.png` -> `image01_no_watermark.png`
- **PDFs**: Creates `<filename>_images/` folder with:
  - `filename_page_001_no_watermark.png`
  - `filename_page_002_no_watermark.png`
  - ...

## Testing

```bash
export TEST_IMAGE_PATH="/path/to/sample_image.png"
pytest tests/
```
