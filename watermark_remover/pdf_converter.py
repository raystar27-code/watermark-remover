import cv2
import numpy as np
from pathlib import Path
import fitz


class PDFConverter:
    DPI_HIGH = 300
    DPI_EFFICIENT = 150

    def __init__(self, dpi=None, memory_mode="high_quality"):
        self.dpi = dpi or (self.DPI_HIGH if memory_mode == "high_quality" else self.DPI_EFFICIENT)
        self.memory_mode = memory_mode

    def pdf_to_images(self, pdf_path):
        images = []
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            img = self._page_to_image(doc, page_num)
            images.append(img)
        doc.close()
        return images

    def pdf_to_images_streaming(self, pdf_path):
        doc = fitz.open(str(pdf_path))
        try:
            for page_num in range(len(doc)):
                img = self._page_to_image(doc, page_num)
                yield img
        finally:
            doc.close()

    def _page_to_image(self, doc, page_num):
        page = doc[page_num]
        mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img_data = np.frombuffer(pix.samples, dtype=np.uint8)
        img_data = img_data.reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
        else:
            img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
        return img_data

    def save_images(self, images, output_dir, base_name):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        for i, img in enumerate(images):
            output_path = output_dir / f"{base_name}_page_{i + 1:03d}.png"
            cv2.imwrite(str(output_path), img)
            saved_paths.append(output_path)
        return saved_paths