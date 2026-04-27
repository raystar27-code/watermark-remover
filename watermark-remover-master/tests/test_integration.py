import os


def test_full_pipeline():
    from watermark_remover.detector import WatermarkDetector
    from watermark_remover.restorer import ImageRestorer

    image_path = os.environ.get("TEST_IMAGE_PATH")
    if not image_path:
        return

    detector = WatermarkDetector()
    detection = detector.detect(image_path)

    if detection:
        expanded = detector.expand_bbox(detection, image_height=720, image_width=1280)
        assert expanded is not None
