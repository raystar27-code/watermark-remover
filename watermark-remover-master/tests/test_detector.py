import os
import pytest
from watermark_remover.detector import WatermarkDetector


def test_detector_init():
    detector = WatermarkDetector()
    assert detector is not None


def test_expand_bbox_to_watermark_area():
    detector = WatermarkDetector()
    small_bbox = {"bbox": (100, 100, 50, 20), "confidence": 80}
    expanded = detector.expand_bbox(small_bbox, image_height=200, image_width=200)
    assert expanded["bbox"][2] > 50
    assert expanded["bbox"][3] > 20


def test_detect_notebooklm_text():
    detector = WatermarkDetector()
    image_path = os.environ.get("TEST_IMAGE_PATH")
    if not image_path:
        pytest.skip("TEST_IMAGE_PATH not set")
    result = detector.detect(image_path)
    assert result is not None
    assert "bbox" in result
