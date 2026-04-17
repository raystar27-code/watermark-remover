# Watermark Remover

Remove NotebookLM watermarks from images or PDFs using OCR detection and OpenCV inpainting. Supports both local files and Google Drive.

[中文说明](README_zh.md)

## Installation

```bash
pip install -r watermark_remover/requirements.txt
```

Requires Tesseract OCR to be installed:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Configuration

All settings are in `watermark_remover/config.py`. Key options:

| Setting | Default | Description |
|---------|---------|-------------|
| `PDF_DPI` | 300 | PDF conversion quality (150 for low memory servers) |
| `MEMORY_MODE` | "high_quality" | "high_quality" or "efficient" |
| `SEARCH_REGION_RATIO` | 0.15 | Bottom-right search area ratio |
| `EXPAND_RATIO` | 2.5 | Watermark box expansion factor |
| `INPAINT_METHOD` | "telea" | Inpainting algorithm |

For 2GB RAM servers, set:
```python
PDF_DPI = 150
MEMORY_MODE = "efficient"
```

## Google Drive Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Drive API**
4. Go to **APIs & Services** → **Credentials**
5. Click **Create Credentials** → **OAuth client ID**
6. Application type: **Desktop app**
7. Download the JSON file and rename it to `credentials.json`
8. Place `credentials.json` in the `watermark_remover/` folder

On first run, a browser window will open for OAuth authorization.

## Usage

```bash
# Local mode (process files in local folder, high quality)
python watermark_remover/skill.py /path/to/folder --source-type local

# Local mode (efficient, low memory usage for servers with limited RAM)
python watermark_remover/skill.py /path/to/folder --source-type local --memory-mode efficient

# Google Drive mode (download from GD, save results locally)
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "your_gd_folder_id" \
  --output local

# Google Drive mode (download from GD, upload results back to GD)
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "your_gd_folder_id" \
  --gd-output "your_gd_output_folder_id" \
  --output google-drive
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--suffix` | Suffix for output files (default: `_no_watermark`) |
| `--source-type` | Source type: `local` or `google-drive` |
| `--gd-source` | Google Drive folder ID containing PDFs to process |
| `--gd-output` | Google Drive folder ID for output (default: same as `--gd-source`) |
| `--output` | Output destination: `local` or `google-drive` |
| `--cleanup` | Remove local temp files after GD upload |
| `--memory-mode` | Memory mode: `high_quality` (300 DPI, more memory) or `efficient` (150 DPI, streaming, less memory) |

## Supported Formats

- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **PDF**: `.pdf` (each page is converted to image, then processed)

## Memory Modes

| Mode | DPI | Memory Usage | Best For |
|------|-----|--------------|----------|
| `high_quality` | 300 | Higher | Local processing, quality-first scenarios |
| `efficient` | 150 | Low | Servers with limited RAM (2GB), batch processing |

### Memory Usage Guide

- **2GB RAM server**: Use `--memory-mode efficient` to process PDFs one page at a time
- **Local desktop**: Use default `high_quality` for better image quality

## Examples

```bash
# Process local folder with high quality (300 DPI)
python watermark_remover/skill.py /path/to/images --source-type local

# Process local folder with efficient mode (150 DPI, low memory)
python watermark_remover/skill.py /path/to/images --source-type local --memory-mode efficient

# Custom output suffix
python watermark_remover/skill.py /path/to/images --suffix _clean

# Process PDFs from Google Drive and save locally
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --output local

# Process PDFs from GD and upload results back to GD
python watermark_remover/skill.py --source-type google-drive \
  --gd-source "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --gd-output "1hKCHoN-aaykHKzv4z40_q_OI3fs123Ft" \
  --output google-drive
```

## How It Works

1. Scans folder for images and PDFs
2. **For images**: Directly process each image
3. **For PDFs**: Convert each page to image (150/300 DPI depending on mode), then process
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
- **Google Drive output**: Results are uploaded as a folder to your specified GD folder

## Testing

```bash
# Test image processing
export TEST_IMAGE_PATH="/path/to/sample_image.png"
pytest tests/

# Test PDF processing (optional)
# Put a PDF file in a folder and run:
python watermark_remover/skill.py /path/to/pdf_folder --source-type local
```