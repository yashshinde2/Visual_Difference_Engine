import numpy as np
import cv2
from typing import Dict, Tuple
try:
    from skimage.metrics import structural_similarity as ssim
except Exception:
    ssim = None


def compute_rgb_diff(img_before, img_after) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Compute RGB difference and return:
    - combined difference map (0-1)
    - metrics dictionary with SSIM, MSE, difference %, etc.
    """
    # ensure same shape
    if img_before.shape != img_after.shape:
        img_after = cv2.resize(img_after, (img_before.shape[1], img_before.shape[0]))

    gray_b = cv2.cvtColor(img_before, cv2.COLOR_RGB2GRAY) if img_before.ndim == 3 else img_before
    gray_a = cv2.cvtColor(img_after, cv2.COLOR_RGB2GRAY) if img_after.ndim == 3 else img_after

    # ensure uint8
    gray_b = gray_b.astype(np.uint8)
    gray_a = gray_a.astype(np.uint8)

    # absolute difference
    absd = cv2.absdiff(gray_b, gray_a).astype(float)
    
    # Mean Squared Error
    mse = float(np.mean(absd ** 2))
    
    # Percentage of changed pixels (threshold at 5% intensity difference)
    threshold_val = 255 * 0.05  # 5% threshold
    changed_pixels = np.sum(absd > threshold_val)
    total_pixels = absd.size
    difference_percent = float((changed_pixels / total_pixels) * 100) if total_pixels > 0 else 0.0

    # Normalize difference map to 0-1
    absd_norm = absd / 255.0

    # SSIM calculation
    ssim_score = 0.0
    ssim_map = np.zeros_like(absd_norm)
    
    if ssim is not None:
        try:
            ssim_score, ssim_map = ssim(gray_b, gray_a, full=True, data_range=255)
            ssim_map = (1.0 - ssim_map)  # convert to difference map
        except Exception as e:
            print(f"SSIM calculation failed: {e}")
            ssim_score = float(np.mean(1.0 - (absd_norm ** 2)))  # fallback
    else:
        # fallback: estimate SSIM from inverse of normalized difference
        ssim_score = float(np.mean(1.0 - (absd_norm ** 2)))

    # Ensure SSIM is in valid range [0, 1]
    ssim_score = max(0.0, min(1.0, ssim_score))

    # Combined difference map: weighted combination
    combined = absd_norm * 0.7 + ssim_map * 0.3
    
    metrics = {
        "ssim_score": ssim_score,
        "mse": mse,
        "difference_percentage": difference_percent,
        "changed_pixels": int(changed_pixels),
        "total_pixels": int(total_pixels),
    }
    
    return combined, metrics
