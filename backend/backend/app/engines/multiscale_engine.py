"""
Multi-Scale Difference Detection Engine
Detects changes at multiple image resolutions for comprehensive anomaly detection.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


def build_gaussian_pyramid(image: np.ndarray, levels: int = 4) -> List[np.ndarray]:
    """Build Gaussian pyramid for multi-scale analysis."""
    pyramid = [image]
    for _ in range(levels - 1):
        image = cv2.pyrDown(image)
        pyramid.append(image)
    return pyramid


def compute_multiscale_difference(
    diff_map: np.ndarray,
    levels: int = 4
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Compute difference at multiple scales and combine.
    
    Returns:
        - List of difference maps at each scale
        - Combined multi-scale difference map
    """
    # Build pyramid of difference map
    pyramid = build_gaussian_pyramid(diff_map, levels)
    
    # Normalize each scale
    normalized_pyramid = []
    for scale_map in pyramid:
        scale_norm = cv2.normalize(scale_map, None, 0, 1, cv2.NORM_MINMAX)
        normalized_pyramid.append(scale_norm)
    
    # Resize all back to original size (largest scale)
    h, w = diff_map.shape[:2]
    resized_pyramid = []
    for scale_map in normalized_pyramid:
        resized = cv2.resize(scale_map, (w, h))
        resized_pyramid.append(resized)
    
    # Combine: weight higher scales (finer details) higher
    weights = np.linspace(0.15, 0.25, levels)  # sum to 1.0
    combined = np.zeros((h, w), dtype=np.float32)
    for scale_map, weight in zip(resized_pyramid, weights):
        combined += scale_map * weight
    
    return resized_pyramid, combined


def detect_multiscale_anomalies(
    diff_map: np.ndarray,
    thresh: float = 0.2,
    min_area: int = 200
) -> Dict[str, any]:
    """
    Detect anomalies using multi-scale approach.
    """
    levels = 4
    scale_maps, combined_map = compute_multiscale_difference(diff_map, levels)
    
    # Binary threshold on combined map
    gray = (combined_map * 255).astype(np.uint8)
    _, bw = cv2.threshold(gray, int(thresh * 255), 255, cv2.THRESH_BINARY)
    
    # Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=2)
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    mask = np.zeros_like(bw, dtype=np.uint8)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        if w < 5 or h < 5:
            continue
        
        # Check aspect ratio to filter thin artifacts
        aspect_ratio = float(w) / max(h, 1)
        if aspect_ratio < 0.1 or aspect_ratio > 10:  # too elongated
            continue
        
        regions.append({
            "bbox": [int(x), int(y), int(w), int(h)],
            "area": int(area),
            "contour": contour,
            "aspect_ratio": float(aspect_ratio),
        })
        
        cv2.drawContours(mask, [contour], 0, 255, -1)
    
    return {
        "regions": regions,
        "mask": mask,
        "scale_maps": scale_maps,
        "combined_map": combined_map,
        "region_count": len(regions),
    }
