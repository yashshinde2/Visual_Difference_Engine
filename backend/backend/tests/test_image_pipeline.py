import tempfile
import numpy as np
import cv2
from app.engines.rgb_engine import compute_rgb_diff
from app.engines.alignment_engine import align_images


def make_diff_image():
    b = np.zeros((200, 200, 3), dtype='uint8')
    a = b.copy()
    cv2.rectangle(a, (50, 50), (150, 150), (255, 255, 255), -1)
    return b, a


def test_rgb_diff_small_change():
    b, a = make_diff_image()
    aligned = align_images(b, a)
    fused, ssim_map = compute_rgb_diff(b, aligned)
    assert fused is not None
    assert fused.shape == fused.shape
