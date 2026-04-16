import pytest
import numpy as np
from watermark_remover.restorer import ImageRestorer


def test_restorer_init():
    restorer = ImageRestorer()
    assert restorer.method == "telea"


def test_restore_creates_mask_and_inpaints():
    restorer = ImageRestorer()
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    test_img[80:100, 80:100] = [255, 255, 255]

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[80:100, 80:100] = 255

    result = restorer.restore(test_img, mask)
    assert result is not None
    assert result.shape == test_img.shape
