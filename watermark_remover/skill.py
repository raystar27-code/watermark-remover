import argparse
import sys
import shutil
import tempfile
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

    return True, str(output_dir)


def process_local_folder(folder_path, detector, restorer, output_suffix):
    folder = Path(folder_path)
    files = []
    for f in folder.iterdir():
        if (
            f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
            or f.suffix.lower() in SUPPORTED_PDF_EXTENSIONS
        ):
            files.append(f)

    if not files:
        print(f"No images or PDFs found in {folder}")
        return 0, 0

    total = len(files)
    print(f"Found {total} file(s) to process\n")

    success = 0
    failed = 0

    for idx, file_path in enumerate(files, 1):
        try:
            if file_path.suffix.lower() in SUPPORTED_PDF_EXTENSIONS:
                ok, result = process_pdf_file(
                    file_path, detector, restorer, output_suffix
                )
            else:
                ok, result = process_image_file(
                    file_path, detector, restorer, output_suffix
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

    return success, failed


def main():
    parser = argparse.ArgumentParser(
        description="Remove NotebookLM watermarks from images or PDFs"
    )
    parser.add_argument("source", nargs="?", help="Local folder path")
    parser.add_argument(
        "--suffix", default="_no_watermark", help="Suffix for output files"
    )
    parser.add_argument(
        "--source-type",
        choices=["local", "google-drive"],
        default="local",
        help="Source type: local folder or Google Drive folder",
    )
    parser.add_argument(
        "--gd-source",
        help="Google Drive folder ID containing PDFs to process",
    )
    parser.add_argument(
        "--gd-output",
        help="Google Drive folder ID to upload results (default: same as --gd-source)",
    )
    parser.add_argument(
        "--output",
        choices=["local", "google-drive"],
        default="local",
        help="Output destination",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up temporary files after upload"
    )
    args = parser.parse_args()

    if args.source_type == "google-drive" and not args.gd_source:
        parser.error("--gd-source is required when --source-type is google-drive")

    temp_dir = None
    try:
        if args.source_type == "google-drive":
            from cloud_storage import GoogleDriveManager

            print("Connecting to Google Drive...")
            drive = GoogleDriveManager()

            source_folder = args.gd_output or args.gd_source
            print(f"Listing PDFs in Google Drive folder: {source_folder}")
            pdf_files = drive.list_pdfs(args.gd_source)
            if not pdf_files:
                print("No PDF files found in the specified folder")
                sys.exit(0)

            print(f"Found {len(pdf_files)} PDF(s)\n")

            temp_dir = tempfile.mkdtemp()
            print(f"Downloading to temporary folder: {temp_dir}\n")

            success = 0
            failed = 0

            for idx, pdf_file in enumerate(pdf_files, 1):
                try:
                    print(f"[{idx}/{len(pdf_files)}] Downloading: {pdf_file['name']}")
                    local_pdf = drive.download_file(pdf_file["id"])
                    print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_file['name']}")

                    temp_pdf_path = Path(temp_dir) / pdf_file["name"]
                    shutil.move(local_pdf, str(temp_pdf_path))

                    detector = WatermarkDetector()
                    restorer = ImageRestorer()
                    ok, result = process_pdf_file(
                        temp_pdf_path, detector, restorer, args.suffix
                    )

                    if ok:
                        print(
                            f"[{idx}/{len(pdf_files)}] ✓ Processed: {pdf_file['name']}"
                        )
                        success += 1
                    else:
                        print(
                            f"[{idx}/{len(pdf_files)}] ✗ Skipped: {pdf_file['name']} ({result})"
                        )
                        failed += 1
                except Exception as e:
                    print(f"[{idx}/{len(pdf_files)}] ✗ Error: {pdf_file['name']} ({e})")
                    failed += 1

            print(
                f"\nProcessing complete: {success}/{len(pdf_files)} succeeded, {failed} failed"
            )

            if args.output == "google-drive" and success > 0:
                print("\nUploading results to Google Drive...")
                result_folder = (
                    Path(temp_dir).parent / f"watermark_removed_{Path(temp_dir).name}"
                )
                result_folder.mkdir(exist_ok=True)
                for item in Path(temp_dir).iterdir():
                    if item.is_dir():
                        shutil.move(str(item), str(result_folder / item.name))
                upload_folder_id = args.gd_output or args.gd_source
                folder_id, folder_link = drive.upload_folder(
                    result_folder, upload_folder_id
                )
                print(f"Results uploaded: {folder_link}")
                if args.cleanup:
                    shutil.rmtree(result_folder)

        else:
            if not args.source:
                parser.error("source folder is required for local mode")
            detector = WatermarkDetector()
            restorer = ImageRestorer()
            success, failed = process_local_folder(
                args.source, detector, restorer, args.suffix
            )

        print(f"\nDone: {success}/{success + failed} succeeded, {failed} failed")

    finally:
        if temp_dir and args.output == "local":
            print(f"\nResults saved in: {temp_dir}")


if __name__ == "__main__":
    main()
