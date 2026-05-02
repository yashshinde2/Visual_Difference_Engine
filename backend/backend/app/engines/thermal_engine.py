import numpy as np
import cv2


def compute_thermal_diff(thermal_before, thermal_after):
    # Convert to grayscale if needed
    if thermal_before.ndim == 3:
        tb = cv2.cvtColor(thermal_before, cv2.COLOR_RGB2GRAY)
    else:
        tb = thermal_before
    if thermal_after.ndim == 3:
        ta = cv2.cvtColor(thermal_after, cv2.COLOR_RGB2GRAY)
    else:
        ta = thermal_after

    diff = cv2.absdiff(tb, ta).astype(float)
    # normalize to 0-1
    if diff.max() > 0:
        diff = diff / diff.max()
    return diff
