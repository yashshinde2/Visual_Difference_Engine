"""
Advanced RGB Difference Engine - Research Grade
Implements mathematically consistent difference detection with multiple metrics.
"""

import numpy as np
import cv2
from typing import Dict, Tuple
import time

try:
    from skimage.metrics import structural_similarity as ssim
except Exception:
    ssim = None


def compute_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute PSNR (Peak Signal-to-Noise Ratio)."""
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    if mse == 0:
        return 100.0
    
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return float(psnr)


def normalize_illumination(gray: np.ndarray) -> np.ndarray:
    """Apply CLAHE for illumination robustness."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray.astype(np.uint8))


def remove_border_artifacts(shape: Tuple[int, int], border_percent: float = 0.05) -> np.ndarray:
    """Create mask to ignore image borders."""
    h, w = shape
    mask = np.zeros((h, w), dtype=np.uint8)
    y_start = int(h * border_percent)
    y_end = int(h * (1 - border_percent))
    mask[y_start:y_end, :] = 1
    return mask


def compute_edge_difference(gray_b: np.ndarray, gray_a: np.ndarray) -> np.ndarray:
    """Compute difference in edge maps (gradient-based)."""
    sobel_b = cv2.Sobel(gray_b, cv2.CV_32F, 1, 1, ksize=3)
    sobel_a = cv2.Sobel(gray_a, cv2.CV_32F, 1, 1, ksize=3)
    
    edge_diff = cv2.absdiff(sobel_b, sobel_a)
    edge_diff = cv2.normalize(edge_diff, None, 0, 1, cv2.NORM_MINMAX)
    return edge_diff


def compute_rgb_diff_advanced(
    img_before: np.ndarray, 
    img_after: np.ndarray,
    remove_borders: bool = True
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Advanced RGB difference computation with multiple metrics.
    
    Returns:
        - combined difference map (0-1)
        - comprehensive metrics dictionary
    """
    start_time = time.time()
    
    # Ensure same shape
    if img_before.shape != img_after.shape:
        img_after = cv2.resize(img_after, (img_before.shape[1], img_before.shape[0]))
    
    # Convert to grayscale
    gray_b = cv2.cvtColor(img_before, cv2.COLOR_RGB2GRAY) if img_before.ndim == 3 else img_before
    gray_a = cv2.cvtColor(img_after, cv2.COLOR_RGB2GRAY) if img_after.ndim == 3 else img_after
    
    gray_b = gray_b.astype(np.uint8)
    gray_a = gray_a.astype(np.uint8)
    
    # Border mask to remove artifacts
    border_mask = remove_border_artifacts(gray_b.shape) if remove_borders else np.ones_like(gray_b)
    
    # Illumination normalization for robustness
    gray_b_norm = normalize_illumination(gray_b)
    gray_a_norm = normalize_illumination(gray_a)
    
    # Absolute pixel difference
    absd = cv2.absdiff(gray_b_norm, gray_a_norm).astype(float)
    absd = absd * border_mask.astype(float)
    
    # Apply median filter to remove noise
    absd_filtered = cv2.medianBlur((absd).astype(np.uint8), 5).astype(float)
    
    # Metrics
    mse = float(np.mean(absd_filtered ** 2))
    psnr = compute_psnr(gray_b, gray_a)
    
    # Percentage of changed pixels (10% intensity threshold)
    threshold_val = 255 * 0.10
    changed_pixels = np.sum((absd_filtered > threshold_val) & (border_mask == 1))
    total_pixels = np.sum(border_mask)
    difference_percent = float((changed_pixels / max(total_pixels, 1)) * 100)
    
    # Normalize difference map to 0-1
    absd_norm = absd_filtered / 255.0
    
    # SSIM Score (on normalized images)
    ssim_score = 0.0
    ssim_map = np.zeros_like(absd_norm)
    
    if ssim is not None:
        try:
            ssim_score, ssim_map = ssim(gray_b_norm, gray_a_norm, full=True, data_range=255)
            ssim_map = (1.0 - np.clip(ssim_map, 0, 1))  # convert to difference map
        except Exception as e:
            print(f"SSIM calculation failed: {e}")
            ssim_score = float(1.0 - (mse / 65025))
    else:
        ssim_score = float(1.0 - (mse / 65025))
    
    ssim_score = np.clip(ssim_score, 0.0, 1.0)
    
    # Edge-based difference
    edge_diff = compute_edge_difference(gray_b_norm, gray_a_norm)
    
    # Histogram similarity
    hist_b = cv2.calcHist([gray_b_norm], [0], None, [256], [0, 256])
    hist_a = cv2.calcHist([gray_a_norm], [0], None, [256], [0, 256])
    hist_similarity = float(cv2.compareHist(hist_b, hist_a, cv2.HISTCMP_BHATTACHARYYA))
    
    # Combined difference map (multi-component)
    combined = (
        0.5 * absd_norm +          # 50% raw pixel difference
        0.3 * ssim_map +           # 30% structural difference
        0.2 * edge_diff            # 20% edge difference
    )
    combined = np.clip(combined, 0, 1)
    
    elapsed_time = time.time() - start_time
    
    metrics = {
        "ssim_score": float(ssim_score),
        "ssim_score_percent": float(ssim_score * 100),
        "mse": float(mse),
        "psnr": float(psnr),
        "difference_percentage": float(difference_percent),
        "changed_pixels": int(changed_pixels),
        "total_pixels": int(total_pixels),
        "histogram_similarity": float(hist_similarity),
        "edge_difference": float(np.mean(edge_diff)),
        "processing_time_ms": float(elapsed_time * 1000),
    }
    
    return combined, metrics
