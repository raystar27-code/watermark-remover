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
# Local mode (process files in local folder)
python watermark_remover/skill.py /path/to/folder --source-type local

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

## Supported Formats

- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **PDF**: `.pdf` (each page is converted to image, then processed)

## Examples

```bash
# Process local folder
python watermark_remover/skill.py /path/to/images --source-type local

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