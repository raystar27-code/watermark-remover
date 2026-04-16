# Watermark Remover

Remove NotebookLM watermarks from images using OCR detection and OpenCV inpainting.

## Installation

```bash
pip install -r requirements.txt
```

Requires Tesseract OCR to be installed:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Usage

```bash
python skill.py <folder_path> [--suffix _no_watermark]
```

## Examples

```bash
# Process all images in a folder
python skill.py /path/to/images

# Custom output suffix
python skill.py /path/to/images --suffix _clean
```

## How It Works

1. Scans folder for images (.png, .jpg, .jpeg, .webp)
2. Uses Tesseract OCR to detect "NotebookLM" text in bottom-right region
3. Expands text bounding box to cover logo and frame
4. Applies OpenCV Telea inpainting to fill watermark area
5. Saves result as `<filename>_no_watermark.<ext>`

## Output

- Original images are preserved
- Processed images saved with suffix (default: `_no_watermark`)
- Example: `image01.png` -> `image01_no_watermark.png`
