import cv2
import pytesseract
import numpy as np
from PIL import Image


class WatermarkDetector:
    SEARCH_REGION_RATIO = 0.15

    def __init__(self, search_ratio=None):
        self.search_ratio = search_ratio or self.SEARCH_REGION_RATIO

    def detect(self, image_path):
        img = cv2.imread(str(image_path))
        if img is None:
            return None

        h, w = img.shape[:2]

        search_x_start = int(w * (1 - self.search_ratio))
        search_y_start = int(h * (1 - self.search_ratio))
        search_roi = img[search_y_start:h, search_x_start:w]

        custom_config = r"--oem 3 --psm 6"
        data = pytesseract.image_to_data(
            search_roi, config=custom_config, output_type=pytesseract.Output.DICT
        )

        texts = data.get("text", [])
        confidences = data.get("conf", [])

        notebooklm_boxes = []
        for i, text in enumerate(texts):
            if "notebooklm" in text.lower():
                conf = confidences[i]
                if conf > 0:
                    x = search_x_start + data["left"][i]
                    y = search_y_start + data["top"][i]
                    bw = data["width"][i]
                    bh = data["height"][i]
                    notebooklm_boxes.append(
                        {"bbox": (x, y, bw, bh), "confidence": conf}
                    )

        if not notebooklm_boxes:
            return None

        best = max(notebooklm_boxes, key=lambda b: b["confidence"])
        return best

    def expand_bbox(self, bbox_info, image_height, image_width, expand_ratio=2.5):
        x, y, w, h = bbox_info["bbox"]

        new_w = int(w * expand_ratio)
        new_h = int(h * expand_ratio)

        center_x = x + w // 2
        center_y = y + h // 2

        new_x = max(0, center_x - new_w // 2)
        new_y = max(0, center_y - new_h // 2)

        new_x = min(new_x, image_width - new_w)
        new_y = min(new_y, image_height - new_h)
        new_w = min(new_w, image_width - new_x)
        new_h = min(new_h, image_height - new_y)

        return {"bbox": (new_x, new_y, new_w, new_h), "original": bbox_info["bbox"]}
