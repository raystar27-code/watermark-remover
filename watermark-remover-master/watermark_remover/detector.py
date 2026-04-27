import cv2
import pytesseract
import numpy as np

import config

WATERMARK_KEYWORDS = [
    ("notebooklm", 8),
    ("notebook", 6),
    ("note book", 6),
    ("nb", 2),
    ("gemini", 5),
    ("google ai", 6),
    ("ai powered", 8)
]

OCR_PSM_MODES = [6, 11]


class WatermarkDetector:
    def __init__(self, search_ratio=None):
        self.search_ratio = search_ratio or config.SEARCH_REGION_RATIO

    def detect(self, image_path):
        img = cv2.imread(str(image_path))
        if img is None:
            return None

        h, w = img.shape[:2]

        search_x_start = int(w * (1 - self.search_ratio))
        search_y_start = int(h * (1 - self.search_ratio))
        search_roi = img[search_y_start:h, search_x_start:w]

        result = self._detect_by_ocr(search_roi, search_x_start, search_y_start)
        if result:
            return result

        result = self._detect_by_color(search_roi, search_x_start, search_y_start)
        return result

    def _detect_by_ocr(self, search_roi, search_x_start, search_y_start):
        for psm in OCR_PSM_MODES:
            custom_config = rf"--oem 3 --psm {psm}"
            data = pytesseract.image_to_data(
                search_roi, config=custom_config, output_type=pytesseract.Output.DICT
            )

            texts = data.get("text", [])
            confidences = data.get("conf", [])

            notebooklm_boxes = []
            for i, text in enumerate(texts):
                text_lower = text.lower().strip()
                conf = confidences[i]

                for keyword, min_len in WATERMARK_KEYWORDS:
                    if len(text_lower) >= min_len and keyword in text_lower and conf > 0:
                        x = search_x_start + data["left"][i]
                        y = search_y_start + data["top"][i]
                        bw = data["width"][i]
                        bh = data["height"][i]
                        notebooklm_boxes.append(
                            {"bbox": (x, y, bw, bh), "confidence": conf, "matched": keyword}
                        )
                        break

            if notebooklm_boxes:
                best = max(notebooklm_boxes, key=lambda b: b["confidence"])
                return best

        return None

    def _detect_by_color(self, search_roi, search_x_start, search_y_start):
        h, w = search_roi.shape[:2]
        gray = cv2.cvtColor(search_roi, cv2.COLOR_BGR2GRAY)

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        roi_h, roi_w = h, w
        candidates = []
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch

            if area < roi_w * roi_h * 0.01:
                continue
            if cw > roi_w * 0.03 and ch > roi_h * 0.02:
                if y > roi_h * 0.6 or x > roi_w * 0.5:
                    candidates.append((cnt, x, y, cw, ch, area))

        if not candidates:
            return None

        largest = max(candidates, key=lambda c: c[5])
        x, y, cw, ch = largest[1], largest[2], largest[3], largest[4]

        global_x = search_x_start + x
        global_y = search_y_start + y

        return {
            "bbox": (global_x, global_y, cw, ch),
            "confidence": 50,
            "matched": "color_detect"
        }

    def expand_bbox(self, bbox_info, image_height, image_width, expand_ratio=None):
        expand_ratio = expand_ratio or config.EXPAND_RATIO
        x, y, w, h = bbox_info["bbox"]

        new_w = int(w * expand_ratio)
        new_h = int(h * expand_ratio)

        new_x = x
        new_y = y

        new_x = min(new_x, image_width - new_w)
        new_y = min(new_y, image_height - new_h)
        new_w = min(new_w, image_width - new_x)
        new_h = min(new_h, image_height - new_y)

        return {"bbox": (new_x, new_y, new_w, new_h), "original": bbox_info["bbox"]}