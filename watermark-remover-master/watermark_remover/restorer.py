import cv2
import numpy as np

import config


class ImageRestorer:
    def __init__(self, method=None):
        self.method = method or config.INPAINT_METHOD

    def restore(self, image, mask):
        result = cv2.inpaint(image, mask, 3, self._get_flags())
        return result

    def _get_flags(self):
        if self.method == "telea":
            return cv2.INPAINT_TELEA
        elif self.method == "navierstokes":
            return cv2.INPAINT_NS
        return cv2.INPAINT_TELEA
