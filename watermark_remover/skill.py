import argparse
import sys
from pathlib import Path
import cv2
import numpy as np

from detector import WatermarkDetector
from restorer import ImageRestorer
from pdf_converter import PDFConverter

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


def process_single_image(
    img, img_path, detector, restorer, output_suffix="_no_watermark"
):
    h, w = img.shape[:2]

    detection = detector.detect(img_path)
    if not detection:
        return False, "No watermark detected"

    expanded = detector.expand_bbox(detection, image_height=h, image_width=w)
    x, y, bw, bh = expanded["bbox"]

    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y : y + bh, x : x + bw] = 255

    restored = restorer.restore(img, mask)

    return True, restored


def process_image_file(image_path, detector, restorer, output_suffix="_no_watermark"):
    img = cv2.imread(str(image_path))
    if img is None:
        return False, "Failed to read image"

    ok, result = process_single_image(
        img, str(image_path), detector, restorer, output_suffix
    )
    if not ok:
        return False, result

    stem = image_path.stem
    ext = image_path.suffix
    output_path = image_path.parent / f"{stem}{output_suffix}{ext}"
    cv2.imwrite(str(output_path), result)

    return True, str(output_path)


def process_pdf_file(pdf_path, detector, restorer, output_suffix="_no_watermark"):
    converter = PDFConverter()
    try:
        images = converter.pdf_to_images(str(pdf_path))
    except Exception as e:
        return False, f"Failed to convert PDF: {e}"

    if not images:
        return False, "PDF has no pages"

    base_name = pdf_path.stem
    output_dir = pdf_path.parent / f"{base_name}_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0
    saved_paths = []

    for i, img in enumerate(images):
        temp_path = str(output_dir / f"{base_name}_temp_page_{i + 1:03d}.png")
        cv2.imwrite(temp_path, img)
        ok, result = process_single_image(
            img, temp_path, detector, restorer, output_suffix
        )
        if ok:
            stem = pdf_path.stem
            output_path = output_dir / f"{stem}_page_{i + 1:03d}{output_suffix}.png"
            cv2.imwrite(str(output_path), result)
            saved_paths.append(str(output_path))
            success += 1
        else:
            failed += 1
        Path(temp_path).unlink(missing_ok=True)

    return True, f"{success} pages processed, {failed} failed"


def main():
    parser = argparse.ArgumentParser(
        description="Remove NotebookLM watermarks from images or PDFs"
    )
    parser.add_argument("folder", help="Folder containing images or PDFs to process")
    parser.add_argument(
        "--suffix", default="_no_watermark", help="Suffix for output files"
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder {folder} does not exist")
        sys.exit(1)

    files = []
    for f in folder.iterdir():
        if (
            f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
            or f.suffix.lower() in SUPPORTED_PDF_EXTENSIONS
        ):
            files.append(f)

    if not files:
        print(f"No images or PDFs found in {folder}")
        sys.exit(0)

    total = len(files)
    print(f"Found {total} file(s) to process\n")

    detector = WatermarkDetector()
    restorer = ImageRestorer()

    success = 0
    failed = 0

    for idx, file_path in enumerate(files, 1):
        try:
            if file_path.suffix.lower() in SUPPORTED_PDF_EXTENSIONS:
                ok, result = process_pdf_file(
                    file_path, detector, restorer, args.suffix
                )
            else:
                ok, result = process_image_file(
                    file_path, detector, restorer, args.suffix
                )

            if ok:
                print(f"[{idx}/{total}] ✓ Processed: {file_path.name}")
                success += 1
            else:
                print(f"[{idx}/{total}] ✗ Skipped: {file_path.name} ({result})")
                failed += 1
        except Exception as e:
            print(f"[{idx}/{total}] ✗ Error: {file_path.name} ({e})")
            failed += 1

    print(f"\nDone: {success}/{total} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
