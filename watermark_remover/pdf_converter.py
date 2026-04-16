import cv2
import numpy as np
from PIL import Image
import fitz


class PDFConverter:
    def __init__(self, dpi=300):
        self.dpi = dpi

    def pdf_to_images(self, pdf_path):
        images = []
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img_data = np.frombuffer(pix.samples, dtype=np.uint8)
            img_data = img_data.reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
            else:
                img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
            images.append(img_data)
        doc.close()
        return images

    def save_images(self, images, output_dir, base_name):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        for i, img in enumerate(images):
            output_path = output_dir / f"{base_name}_page_{i + 1:03d}.png"
            cv2.imwrite(str(output_path), img)
            saved_paths.append(output_path)
        return saved_paths
