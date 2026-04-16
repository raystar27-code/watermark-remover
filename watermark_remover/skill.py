import argparse
import sys
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

from detector import WatermarkDetector
from restorer import ImageRestorer

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def process_image(image_path, detector, restorer, output_suffix="_no_watermark"):
    img = cv2.imread(str(image_path))
    if img is None:
        return False, "Failed to read image"

    h, w = img.shape[:2]

    detection = detector.detect(str(image_path))
    if not detection:
        return False, "No watermark detected"

    expanded = detector.expand_bbox(detection, image_height=h, image_width=w)
    x, y, bw, bh = expanded["bbox"]

    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y : y + bh, x : x + bw] = 255

    restored = restorer.restore(img, mask)

    stem = image_path.stem
    ext = image_path.suffix
    output_path = image_path.parent / f"{stem}{output_suffix}{ext}"
    cv2.imwrite(str(output_path), restored)

    return True, str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Remove NotebookLM watermarks from images"
    )
    parser.add_argument("folder", help="Folder containing images to process")
    parser.add_argument(
        "--suffix", default="_no_watermark", help="Suffix for output files"
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder {folder} does not exist")
        sys.exit(1)

    images = [f for f in folder.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not images:
        print(f"No images found in {folder}")
        sys.exit(0)

    total = len(images)
    print(f"Found {total} image(s) to process\n")

    detector = WatermarkDetector()
    restorer = ImageRestorer()

    success = 0
    failed = 0

    for idx, img_path in enumerate(images, 1):
        try:
            ok, result = process_image(img_path, detector, restorer, args.suffix)
            if ok:
                print(f"[{idx}/{total}] ✓ Processed: {img_path.name}")
                success += 1
            else:
                print(f"[{idx}/{total}] ✗ Skipped: {img_path.name} ({result})")
                failed += 1
        except Exception as e:
            print(f"[{idx}/{total}] ✗ Error: {img_path.name} ({e})")
            failed += 1

    print(f"\nDone: {success}/{total} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
